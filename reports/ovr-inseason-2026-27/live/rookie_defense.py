"""新秀賽中防守（2026-10-30 使用者：「一有數據就馬上更新數值，不準的話後面場次自然會回落」）。

用整季累計的防守追蹤表（scripts/fetch_defense_tracking.mjs）照 card 0.2.7 的同一套公式算 onBall／help，新秀一有數據就直接取代起點（w=1）。
公式本身就帶樣本量收縮，所以少量樣本會被拉回平均，不需要另加 k：
- help＝inverse(PLUSMINUS·n/(n+200), CURVE_DEF_RIM)，n＝FGA_LT_06（scripts/build_season_league.js:100-108，夾 40–99）。
- onBall＝E-060 的 r＝zC3＋zB−zT（reports/card-0.1.1+E060-onball-targeting/components.py），收縮常數同 E-060；
  組平均、聯盟平均與 z 的平均／標準差凍結在 2025-26（stability.json stats['2025-26']），尺度才和 card 0.2.7 一致、開季也不會因池太小亂跳。
  r → 屬性：card 0.2.7（E-101 合併池百分位＋頂底尾巴）在 2025-26 的 (r, onBall) 對照做線性內插；超出範圍用 E-101 的尾巴公式（tail-summary.json）。
用法：python -I -X utf8 rookie_defense.py [--check]（--check：拿 2025-26 原始表重算，對照 card 0.2.7 先驗卡）
"""
import bisect
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E060 = ROOT / 'reports/card-0.1.1+E060-onball-targeting'
TAIL = ROOT / 'reports/card-0.2.5+E101-crossera/tail-summary.json'
PRIOR_CARD = HERE / 'prior-2025-26-card027.json'
K_C3, K_B, K_T, K_HELP = 500.0, 1000.0, 1000.0, 200.0
CURVE_DEF_RIM = [(0, 0.150), (40, 0.105), (55, 0.050), (70, 0.004), (85, -0.048), (99, -0.095), (120, -0.125), (150, -0.150)]
CEIL, K_SD = 150.0, 1.96


def table(path):
    d = json.load(open(path, encoding='utf-8'))['data']
    s = d['resultSets'][0] if isinstance(d['resultSets'], list) else d['resultSets']
    return [dict(zip(s['headers'], r)) for r in s['rowSet']]


def inverse(p, curve):
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if min(y0, y1) <= p <= max(y0, y1):
            return max(40.0, min(99.0, x0 + (p - y0) / (y1 - y0) * (x1 - x0)))
    return 40.0 if abs(p - curve[0][1]) < abs(p - curve[-1][1]) else 99.0


def help_of(rim_rows):
    out = {}
    for r in rim_rows:
        n, d = r.get('FGA_LT_06'), r.get('PLUSMINUS')
        if n and n > 0 and d is not None:
            out[r['CLOSE_DEF_PERSON_ID']] = inverse(d * n / (n + K_HELP), CURVE_DEF_RIM)
    return out


def frozen_stats():
    return json.load(open(E060 / 'stability.json', encoding='utf-8'))['stats']['2025-26']


def onball_r(tabs, st, pos_fallback=None):
    """E-060 components.compute 的單一球員部分，組平均／z 用凍結的 st。回傳 {pid: r}（缺任何一個分量就不給）。"""
    pos_fallback = pos_fallback or {}
    adv = {}
    for r in tabs['advanced']:
        u = r.get('USG_PCT')
        if u is not None:
            adv[r['PLAYER_ID']] = u * 100 if u <= 1 else u
    pos = {}
    for r in tabs['three']:
        pos.setdefault(r['CLOSE_DEF_PERSON_ID'], (r['PLAYER_POSITION'] or '').split('-')[0])
    hus = {}
    for r in tabs['hustle']:
        if r['CONTESTED_SHOTS_3PT'] is None or not r['MIN']:
            continue
        h = hus.setdefault(r['PLAYER_ID'], [0.0, 0.0])
        h[0] += r['CONTESTED_SHOTS_3PT']; h[1] += r['MIN']
    acc, pair = {}, {}
    for r in tabs['matchups']:
        d = r['DEF_PLAYER_ID']; a = acc.setdefault(d, dict(pp=0.0, ppu=0.0, load=0.0))
        a['pp'] += r['PARTIAL_POSS'] or 0
        u = adv.get(r['OFF_PLAYER_ID'])
        if u is not None:
            a['ppu'] += r['PARTIAL_POSS'] or 0; a['load'] += (r['PARTIAL_POSS'] or 0) * u
        q = pair.setdefault((d, r['OFF_PLAYER_ID']), [0.0, 0.0])
        q[0] += r['MATCHUP_FGA'] or 0; q[1] += r['PARTIAL_POSS'] or 0
    tot = {}
    for (d, o), (f_, p_) in pair.items():
        t = tot.setdefault(o, [0.0, 0.0]); t[0] += f_; t[1] += p_
    tx = {}
    for (d, o), (f_, p_) in pair.items():
        if p_ <= 0:
            continue
        F, P = tot[o]
        if P - p_ <= 0:
            continue
        x = tx.setdefault(d, [0.0, 0.0]); x[0] += f_; x[1] += p_ * (F - f_) / (P - p_)
    gm, zc, zb, zt, lmb = st['groupMeanC3'], st['zC3'], st['zB'], st['zT'], st['leagueMeanB']
    out = {}
    for pid in adv:
        g = pos.get(pid) or pos_fallback.get(pid)
        c3, m = hus.get(pid), acc.get(pid)
        if g not in gm or not c3 or not m or m['ppu'] <= 0 or m['pp'] <= 0 or pid not in tx:
            continue
        C3 = (c3[1] * (36 * c3[0] / c3[1]) + K_C3 * gm[g]) / (c3[1] + K_C3)
        B = (m['ppu'] * (m['load'] / m['ppu']) + K_B * lmb) / (m['ppu'] + K_B)
        T = (m['pp'] / (m['pp'] + K_T)) * (100 * (tx[pid][0] - tx[pid][1]) / m['pp'])
        out[pid] = (C3 - zc[g][0]) / zc[g][1] + (B - zb[0]) / zb[1] - (T - zt[0]) / zt[1]
    return out


class OnBallScale:
    """r → card 0.2.7 onBall：2025-26 的 (r, onBall) 對照內插；範圍外用 E-101 尾巴。"""

    def __init__(self):
        card = {p['playerId']: p['onBall'] for p in json.load(open(PRIOR_CARD, encoding='utf-8'))['players']}
        pts = {}
        for r in csv.DictReader(open(E060 / 'components-2025-26.csv', encoding='utf-8')):
            pid = int(r['pid'])
            if pid in card and '' not in (r['zC3'], r['zB'], r['zT']):
                pts[float(r['zC3']) + float(r['zB']) - float(r['zT'])] = float(card[pid])
        self.xs = sorted(pts)
        self.ys = [pts[x] for x in self.xs]
        self.tail = json.load(open(TAIL, encoding='utf-8'))['e101']['onBall']

    def __call__(self, r):
        t, xs, ys = self.tail, self.xs, self.ys
        if r > xs[-1]:
            return 99 + (CEIL - 99) * (1 - math.exp(-max(0.0, r - t['r99']) / (K_SD * t['S'])))
        if r < xs[0]:
            return 40 - 15 * (1 - math.exp(-max(0.0, t['r1'] - r) / t['SD_pool']))
        i = bisect.bisect_left(xs, r)
        if xs[i] == r:
            return ys[i]
        return ys[i - 1] + (r - xs[i - 1]) / (xs[i] - xs[i - 1]) * (ys[i] - ys[i - 1])


def inseason(season='2026-27', pos_fallback=None):
    """{pid: {'onBall': v 或缺, 'help': v 或缺, 'n3': 守三分出手, 'nRim': 守禁區出手}}；沒抓到表回傳 {}。"""
    d = ROOT / 'data/defense-seventh' / season / 'tracking'
    kinds = ('rim', 'three', 'hustle', 'advanced', 'matchups')
    if not all((d / f'{k}.json').exists() for k in kinds):
        return {}
    tabs = {k: table(d / f'{k}.json') for k in kinds}
    scale = OnBallScale()
    out = {}
    for pid, v in help_of(tabs['rim']).items():
        out.setdefault(pid, {})['help'] = v
    for pid, r in onball_r(tabs, frozen_stats(), pos_fallback).items():
        out.setdefault(pid, {})['onBall'] = scale(r)
    for r in tabs['rim']:
        out.get(r['CLOSE_DEF_PERSON_ID'], {}).update(nRim=r['FGA_LT_06'])
    for r in tabs['three']:
        if r['CLOSE_DEF_PERSON_ID'] in out:
            out[r['CLOSE_DEF_PERSON_ID']]['n3'] = r.get('FG3A')
    return out


def check():
    """2025-26 原始表重算 → 對照 card 0.2.7 先驗卡（help、onBall 都應逐人吻合）。"""
    raw = ROOT / 'reports/defense-tenth/step4-t2/raw/2025-26'
    tabs = {k: table(raw / f'0-{k}.json') for k in ('rim', 'three', 'hustle', 'advanced', 'matchups')}
    card = {p['playerId']: p for p in json.load(open(PRIOR_CARD, encoding='utf-8'))['players']}
    hp = help_of(tabs['rim'])
    rr = onball_r(tabs, frozen_stats())
    scale = OnBallScale()
    dh = [abs(hp[p] - float(card[p]['help'])) for p in card if p in hp]
    do = [abs(scale(rr[p]) - float(card[p]['onBall'])) for p in card if p in rr]
    res = {'help': {'n': len(dh), 'maxAbs': max(dh), 'n>0.1': sum(x > 0.1 for x in dh)},
           'onBall': {'n': len(do), 'maxAbs': max(do), 'n>0.1': sum(x > 0.1 for x in do)}}
    print(json.dumps(res, ensure_ascii=False))
    return res


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if '--check' in sys.argv:
        check()
    else:
        print(json.dumps(inseason(), ensure_ascii=False)[:2000])

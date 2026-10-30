"""E-116 §4：run_c4_live.py 的新秀版包裝（D1：不改共用檔，讀它的原始碼、在記憶體做一處替換後執行）。

唯一替換：main() 寫 ranking.csv 那一行 → 先把「沒有先驗卡、但 bio 是 2026 新秀」的人算成一列併進去；
並把這些人從 nopr（no-prior.csv）拿掉。老將的列、統計、檢查完全沿用原程式（rank 會因新秀插入而位移，相對順序不變）。
用法同原程式：python -I -X utf8 run_c4_live_rookie.py <輸出資料夾>
也供 backtest.py 匯入：load_ns() 回傳已 exec 的命名空間（不執行 main）。
"""
import copy
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rookie_defense as RD  # noqa: E402

HERE = Path(__file__).resolve().parent
ORIG = HERE / 'run_c4_live.py'
ROOKIE_JSON = HERE / 'rookie-prior-2026.json'
G_GAMES = 82
DPOS = {'G': 'SG', 'F': 'SF', 'C': 'C'}          # D5：G／F／C → 設計矩陣用的 SG／SF／C（回測與上線同一張表）
SKIP = ('pressure', 'drive')                     # live 凍結的兩項（同老將）
DEF_ATTRS = ('onBall', 'help')                   # 2026-10-30 使用者：新秀防守一有數據就換成當季值（w=1，rookie_defense.py）

OLD_LINE = "    C.write_csv(out_dir / 'ranking.csv', [{k: r[k] for k in head} for r in rows], head)\n"
NEW_LINE = "    _E116.write_outputs(globals(), locals(), out_dir, rows, head, nopr)\n"
# 2026-10-30 使用者：老將防守解凍，「用 TUL 類似的做法」→ onBall／help 改四季窗口逐場線性遞減（rookie_defense.veteran）
OLD_DEF = "    attrs = live_predict(delta2, rel_, undefined, frozen, diag=diag)\n"
NEW_DEF = OLD_DEF + "    _E116.vet_defense(sd26, attrs, prior_cards)\n"
GAMES_PER_SEASON = 1230


def load_ns():
    src = ORIG.read_text(encoding='utf-8')
    assert src.count(OLD_LINE) == 1, 'run_c4_live.py 的 ranking.csv 寫入行對不上'
    assert src.count(OLD_DEF) == 1, 'run_c4_live.py 的 live_predict 呼叫行對不上'
    src = src.replace(OLD_LINE, NEW_LINE).replace(OLD_DEF, NEW_DEF)
    ns = {'__name__': 'run_c4_live_exec', '__file__': str(ORIG), '_E116': sys.modules[__name__]}
    exec(compile(src, str(ORIG), 'exec'), ns)
    return ns


# ------------------------------------------------------------------ 新秀計算
def xhat_of(ns, x0, k, rec, arm, rel, dfn=None):
    """回傳 (xhat {15 項}, w {項: w}, 取樣 n {項: n})。arm：e116（k=σ²/τ²）、frozen（k=50·nRef）、own（w=1）。
    dfn：rookie_defense.inseason() 的這個人（{'onBall','help','n3','nRim'}）；有值就直接取代 onBall／help（w=1）。"""
    C, F, IC, SA = ns['C'], ns['F'], ns['IC'], ns['SA']
    out, ws, ns_ = dict(x0), {}, {}
    for a in DEF_ATTRS:
        if dfn and dfn.get(a) is not None:
            out[a] = C.clip(dfn[a])
            ws[a], ns_[a] = 1.0, dfn.get('n3' if a == 'onBall' else 'nRim')
    if rec is None:
        return out, ws, ns_
    f = min(rec['GP'] / G_GAMES, 1.0)
    card = {a: float(v) for a, v in x0.items()}

    def wt(a, n, kk, src):
        if arm == 'own':
            return 1.0
        kv = 50.0 * rel[src]['nRef'] if arm == 'frozen' else kk
        return f + (1.0 - f) * n / (n + kv)

    for a in C.UPD:
        if a in SKIP:
            continue
        n = IC.sample_of(rec, a)
        if n < SA.SEASON_MIN_SAMPLE[a]:
            continue
        y = F.y_adj_of(card, rec, a, 0.0)               # usg0＝0 → 不做用球率調整（D2）
        w = wt(a, n, k.get(a), a)
        out[a] = C.clip(x0[a] + w * (y - x0[a]))
        ws[a], ns_[a] = w, n
    a = 'foulDraw'
    if rec.get(a) is not None and IC.sample_of(rec, 'drive') >= SA.SEASON_MIN_SAMPLE['drive']:
        n = IC.sample_of(rec, 'drive')
        w = wt(a, n, k.get(a), 'drive')
        out[a] = C.clip(x0[a] + w * (float(rec[a]) - x0[a]))
        ws[a], ns_[a] = w, n
    return out, ws, ns_


def ovr_of(ns, pw, anc, r_repl, x, pos, mpg_hat, height):
    P = copy.copy(pw.pipe)
    P.pos = [DPOS[pos]]
    xx = dict(x, heightInches=float(height))      # 身高凍結（bio）
    raw = np.array([[xx[a] for a in ns['ATTRS']]], float)
    pred0 = float(P.design(raw)[0])
    g = (pred0 - r_repl) * ns['sat_w'](mpg_hat)
    return pred0, g, ns['e064_map'](g, anc)


def eval_rookie(ns, pw, anc, r_repl, rk, rec, arm, rel, dfn=None):
    """rk：x0、k、pos、mpg0。回傳 dict（xhat、w、pred0、mpgHat、ovr）。"""
    x, ws, _ = xhat_of(ns, rk['x0'], rk['k'], rec, arm, rel, dfn)
    m0 = rk['mpg0']
    if 'stamina' in ws and rec is not None and rec['GP'] > 0:
        mh = m0 + ws['stamina'] * (rec['MIN'] / rec['GP'] - m0)
    else:
        mh = m0
    pred0, g, ovr = ovr_of(ns, pw, anc, r_repl, x, rk['pos'], mh, rk['heightInches'])
    return {'x': x, 'w': ws, 'pred0': pred0, 'g': g, 'mpgHat': mh, 'ovr': ovr}


def fake_cards(rookies):
    return {r['playerId']: {'playerId': r['playerId'], 'name': r['name'], 'pos': DPOS[r['pos']],
                            'creation': r['x0']['creation'], 'e2': None} for r in rookies}


def rookie_windows(ns, sd, mapping, rookies, n):
    IC = ns['IC']
    received = IC.received_prior(ns['PRIOR'])
    return ns['m26_window_cards'](sd, n, mapping, fake_cards(rookies), received)


# ------------------------------------------------------------------ main() 內呼叫
VET_DEF_INFO = {}


def vet_defense(sd26, attrs, prior_cards):
    """老將 onBall／help：四季窗口逐場線性遞減（rookie_defense.veteran）。c＝聯盟已賽場數／1230·82 格；算不出的人維持先驗卡。
    只改 attrs（之後 pw.predict 用）；lastOVR／檢查 (a) 仍用先驗卡，所以 dOVR 含「單季卡 → 四季窗口」的換算差。"""
    games = {r['GAME_ID'] for b in sd26['box'].values() for r in b['rows']}
    c = len(games) / GAMES_PER_SEASON * G_GAMES
    vd, ww = RD.veteran(c, '2026-27', {p: {'PG': 'G', 'SG': 'G', 'SF': 'F', 'PF': 'F', 'C': 'C'}.get(pc.get('pos')) for p, pc in prior_cards.items()})
    n = 0
    for pid, x in attrs.items():
        v = vd.get(pid)
        if not v:
            continue
        for a in DEF_ATTRS:
            if v.get(a) is not None:
                x[a] = v[a]
        n += 1
    VET_DEF_INFO.update(games=len(games), c=c, weights=ww, players=n)
    print(f'老將防守四季窗口：聯盟 {len(games)} 場（c={c:.2f} 格），權重 {ww}，更新 {n} 人', file=sys.stderr)


def write_outputs(g, loc, out_dir, rows, head, nopr):
    C, ATTRS = g['C'], g['ATTRS']
    doc = json.load(open(ROOKIE_JSON, encoding='utf-8'))
    rookies = doc['players']
    assert g['SAT'] and g['USAGE_MODE'] and g['E064_MODE'] == 'G1', '新秀版只支援 027 live 設定'
    pw, anc, r_repl, sd26, team = loc['pw'], loc['anc064'], loc['r_repl064'], loc['sd26'], loc['team']
    rel = g['V2'].load_reliability()
    prior_pids = set(loc['prior_cards'])
    rookies = [r for r in rookies if r['playerId'] not in prior_pids]       # 保險：有卡的不當新秀
    wins = rookie_windows(g, sd26, C.mapping_for(g['PRIOR']), rookies, g['ALL_N'])
    dfns = RD.inseason('2026-27', {r['playerId']: r['pos'] for r in rookies})
    rk_rows = []
    for rk in rookies:
        pid = rk['playerId']
        b = sd26['box'].get(pid)
        gp = len(b['rows']) if b else 0
        mins = sum(r['MIN'] for r in b['rows']) if b else 0.0
        rec = wins.get(pid)
        cur = eval_rookie(g, pw, anc, r_repl, rk, rec, 'e116', rel, dfns.get(pid) if gp > 0 else None)
        base = eval_rookie(g, pw, anc, r_repl, rk, None, 'e116', rel)
        row = {k: '' for k in head}
        row.update({'ovr': g['r1'](cur['ovr']), 'name': rk['name'], 'pos': rk['pos'], 'MIN': 0,
                    'predictedPer36': round(cur['pred0'], 3), 'defenseBonus': 0.0, 'align': 0.0,
                    'pred0': round(cur['pred0'], 3), 'playerId': pid, 'N': gp, 'team': team.get(pid, rk['team']),
                    'MIN26': round(mins, 1), 'lastOVR': g['r1'](base['ovr']),
                    'dOVR': round(cur['ovr'] - base['ovr'], 2), 'MPG0': round(rk['mpg0'], 2),
                    'MPGhat': round(cur['mpgHat'], 2), 'g': round(cur['g'], 3), 'ovrPer36': '',
                    'predNew': round(cur['pred0'], 4)})
        if rec is not None and rec['GP'] > 0:
            row['MPGwin'] = round(rec['MIN'] / rec['GP'], 2)
            if 'stamina' in cur['w']:
                row['wMPG'] = round(cur['w']['stamina'], 4)
        for a in ATTRS:
            row[a] = g['r1'](cur['x'][a] if a != 'heightInches' else rk['heightInches'])
        row['_ovr'] = cur['ovr']
        row['_cur'], row['_base'], row['_pick'] = cur, base, rk['pick']
        rk_rows.append(row)
    loc_rookies = {r['playerId'] for r in rk_rows}
    nopr[:] = [r for r in nopr if r['playerId'] not in loc_rookies]
    # 老將列複製一份重排名次（原 rows 不動，後面的統計照舊只含老將）
    merged = [dict(r) for r in rows] + [dict(r) for r in rk_rows]
    merged.sort(key=lambda r: -r['_ovr'])
    for i, r in enumerate(merged, 1):
        r['rank'] = i
    # 沒打球的新秀（N=0）不進排名：OVR 只是先驗值，仍寫入 rookies 檔
    C.write_csv(out_dir / 'ranking.csv', [{k: r[k] for k in head} for r in merged if r['N'] > 0 or r['playerId'] not in loc_rookies], head)
    slim = []
    for r in rk_rows:
        slim.append({'playerId': r['playerId'], 'name': r['name'], 'team': r['team'], 'pick': r['_pick'],
                     'pos': r['pos'], 'N': r['N'], 'ovr': r['ovr'], 'lastOVR': r['lastOVR'],
                     'rank': next(m['rank'] for m in merged if m['playerId'] == r['playerId']),
                     'x0': r['_base']['x'], 'xhat': r['_cur']['x'], 'w': r['_cur']['w']})
    json.dump(slim, open(out_dir / 'rookies-detail.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    _ns = load_ns()
    raise SystemExit(_ns['main']())

"""inseason 0.2.0（v5 Path A C4，E-033；先驗卡 x0＝card 0.1.2 能力值；OVR 為每場，R-028 / E-064 G1）的 2026-27 即時版：逐球員用自己的已打場數 N 更新能力值與 OVR。

S*：先驗季 2025-26（card 0.1.2 先驗 live/prior-2025-26-card012.json，build_prior_012.py 由 card 0.1.2 ranking.csv 轉成）、目標季 2026-27。
- c = 1 凍結；δ²、rel（σ²、nRef）沿用既有函式（c4_v5.delta2_info；只用嚴格早於 S* 的起點 Y1..Y6、D1..D3）。
- 每位球員 f = min(GP / 82, 1)，GP 是他自己在 2026-27 已出賽場數（視窗＝他的全部已打場次）。
- 沒有 2025-26 先驗卡的球員不給 OVR，列在 no-prior.csv。
- OVR 走逐點管線 pointwise_pipeline（pr、封頂 T 固定為開季先驗卡）。
- 不改 v4/v5 既有檔；本檔在記憶體裡覆寫 v4_common 的 CHAIN / 映射 / RAPM 路徑 / 目標季載入（同 pathA_common 的做法）。

用法：python -I reports/ovr-inseason-2026-27/live/run_c4_live.py [輸出資料夾名，預設用資料截止日]
輸入（唯讀）：data/defense-seventh/2026-27/{player-games,team-games}.json、pbp/；先驗卡與 2025-26 原始資料。
不得依 2026-27 結果調參數（L-026）：c、G、k、w 都是凍結值。
"""
import csv
import json
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(REPORT / 'v5' / 'tools'))

import pathA_common as PA  # noqa: E402
from pathA_common import base as C, SA  # noqa: E402
import c4_v5 as C4  # noqa: E402
import fit_w_grid_v4 as F  # noqa: E402
import inseason_common_v4 as IC  # noqa: E402
import v2_common as V2  # noqa: E402
import pointwise_pipeline as PW  # noqa: E402
from ovr_common import ATTRS, load_json  # noqa: E402

import os  # noqa: E402
# card 0.1.2 有 16 個屬性（drive 之後多一欄 foulDraw）；ATTRS 在原地加欄，凍結管線／summary 依此順序讀係數。
if 'foulDraw' not in ATTRS:
    ATTRS.insert(ATTRS.index('drive') + 1, 'foulDraw')
import e062_switch as _E062  # noqa: E402
E062_MODE = os.environ.get('E062_MODE', 'off')   # off | C4s | C4r（E-062，預設關）
_E062.install(E062_MODE)

# E-064 每場 OVR。G1（預設，R-028）：副版（相對替補水準）、MPG_hat＝MPG0 + w·(MPG_win − MPG0)，w＝stamina 的 C4 w；
# G0：只換單位（舊試跑，MPG_hat＝MPG0、基準＝平均）；off：每 36 分鐘 OVR（2026-10-27 頁面，逐位元重現用）。
E064_MODE = os.environ.get('E064_MODE', 'G1')   # G1 | G0 | off
if E064_MODE not in ('off', 'G0', 'G1'):
    raise SystemExit('E064_MODE 只接受 off、G0 或 G1')
if E064_MODE == 'G1':
    # 預註冊 §4.1：stamina 最小樣本 1 場（本身的能力值與 w 都用；其餘 15 屬性照 C4 現行）。只在 G1 生效，off 不動。
    SA.SEASON_MIN_SAMPLE['stamina'] = 1
VERSION = 'inseason 0.2.0'  # 第一個字面值會被 daily_inseason_update.probe_base_version 以正規式讀取，勿改成括號／條件式開頭
if E064_MODE != 'G1':
    VERSION = 'inseason 0.1.2'  # off／G0：重現舊頁用
VERSION += ('' if E062_MODE == 'off' else '+E062-' + E062_MODE) + ('+E064-G0' if E064_MODE == 'G0' else '')
CARD_VERSION = 'card 0.2.0' if E064_MODE == 'G1' else 'card 0.1.2'
PRIOR = '2025-26'
TARGET = '2026-27'
G_GAMES = 82
C_PARAM = 1.0
ALL_N = 99                      # 視窗＝全部已打場次
DATA26 = ROOT / 'data/defense-seventh' / TARGET
PRIOR_CARD = HERE / 'prior-2025-26-card012.json'      # build_prior_012.py 產出（x0＝card 0.1.2）
CARD_DIR = ROOT / 'reports/card-0.1.1+E060-onball-targeting/primary'
CARD_SUMMARY = CARD_DIR / 'summary.json'                # card 0.1.2 的凍結迴歸係數／錨點
RAPM_STAR = ROOT / 'reports/impact-rapm/rapm.csv'
BIO25 = ROOT / 'data/benchmark-source/bio.json'
FORMAL_RANKING = (ROOT / 'reports/card-0.2.0/ranking.csv') if E064_MODE == 'G1' else CARD_DIR / 'ranking.csv'
# E-064（預註冊 §2、§4、§5）：每場 g = pred × MPG_hat / 36，兩段式映射錨點＝V2.FROZEN_SUMMARY（此處＝card 0.1.2 摘要）
# 原本算 scaleAnchorsPer36 的 MIN>=500 池，改用 g 重算的 PR1/PR50/PR99（card-0.1.2+E064-pergame/primary/pergame-summary.json
# 的 anchors.main，與 summary.json 同一個 card 0.1.2 管線與池）。算一次、凍結。
E064_ANCHORS_FILE = ROOT / 'reports/card-0.1.2+E064-pergame/primary/pergame-summary.json'
THREE_PRIOR = ROOT / 'reports/ovr-v62-3pt-difficulty-2025-26/new-long.json'   # abilityC（難度調整準度）＝上季先驗
THREE_K = 294.667                 # E-057：v62 方法 (c) 的 k（出手數單位）
THREE_REP_GAP = 0.03              # rep = 聯盟 3P% − 0.03
THREE_POOL_MIN = 500              # 池：合併 MIN >= 500 且有先驗卡
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ------------------------------------------------------------------ 環境設定
def setup():
    PA.install()
    # 0) card 0.1.2：先驗卡與凍結 OVR 管線係數（不重擬合）
    C.PRIOR_PATH[PRIOR] = PRIOR_CARD
    V2.FROZEN_SUMMARY = CARD_SUMMARY
    F.CACHE.clear()
    # 1) 2025-26 凍結映射（既有檔沒有涵蓋 2025-26）：用 build_season_cards 同一套流程重建
    sd25 = IC.load_target_season()                      # 2025-26 box / shots / teamRows
    bio25 = {int(r['PLAYER_ID']): r for r in SA.result_set(BIO25)}
    dep25 = {int(r['playerId']): r for s in load_json(IC.DEPENDENCE)['seasons']
             if s['season'] == PRIOR for r in s['rows']}
    box = {p: b for p, b in sd25['box'].items() if p in bio25}
    sdm = {'season': PRIOR, 'box': box, 'bio': bio25, 'dep': dep25, 'ff': {}, 'v3': {}, 'fed': {},
           'shots': sd25['shots'], 'teamRows': sd25['teamRows']}
    stats = SA.aggregate(sdm)
    raw = SA.raw_with_box(sdm, stats)
    mapping = SA.build_mapping(sdm, stats, raw)
    cards25 = {p: {'usg': SA._f(bio25[p]['USG_PCT'])} for p in stats}
    prev_sc, prev_scc = C.season_cards, C.season_cards_cards

    def season_cards(season):
        if season == PRIOR:
            return mapping['priors'], mapping['pools']
        return prev_sc(season)

    def season_cards_cards(season):
        if season == PRIOR:
            return cards25
        return prev_scc(season)

    C.season_cards, C.season_cards_cards = season_cards, season_cards_cards
    # 1b) prior-2025-26-v5.json 由正式卡轉成，sample 沒有 midA／shortA（全是 0）→ k_eff 取上界、
    #     近框／中距離等於凍結。歷年先驗卡（2021-25）都有這兩欄，這裡用同一份 2025-26 出手分區補上。
    prior_cards, _ = F.load_prior(PRIOR)
    filled = 0
    for pid, pc in prior_cards.items():
        s = stats.get(pid)
        if s is not None and pc.get('sample') is not None:
            pc['sample']['midA'], pc['sample']['shortA'] = float(s['midA']), float(s['shortA'])
            filled += 1

    info = {'boxPlayersDroppedNoBio': len(sd25['box']) - len(box), 'poolSize': len(mapping['pool']),
            'priors': mapping['priors'], 'mappingStats': stats, 'mapping': mapping,
            'priorShotSampleFilled': filled, 'priorCards': len(prior_cards)}

    # 2) 鏈：加上 S*
    chain = dict(PA.CHAIN_U)
    chain['S*'] = {'prior': PRIOR, 'target': TARGET, 'pred': '2022-23_2025-26', 'ans': None, 'judge': False}
    C.CHAIN = chain
    C.CHAIN_BY_PRIOR = {v['prior']: v['target'] for v in chain.values()}
    prev_hfa = C.history_for_attr

    def history_for_attr(s, a):
        if s != 'S*':
            return prev_hfa(s, a)
        hs = [h for h in PA.ORDER if h in PA.BUILT]            # Y1..Y6, D1..D3（Y0 無先驗卡）
        return [h for h in hs if not (h.startswith('Y') and a in C.W_MISSING)]

    C.history_for_attr = history_for_attr

    # 3) S* 的預測 RAPM：§R.2 四季合併欄
    prev_rp = C.rapm_path
    C.rapm_path = lambda name: RAPM_STAR if name == '2022-23_2025-26' else prev_rp(name)
    C._PIPE_CACHE.clear()
    PW._CACHE.clear()

    # 4) 例行賽場數與 2026-27 目標季資料
    PA.G_SEASON[TARGET] = G_GAMES
    old = (IC.TARGET_BOX, IC.TARGET_TEAM, IC.TARGET_PBP)
    IC.TARGET_BOX, IC.TARGET_TEAM, IC.TARGET_PBP = (DATA26 / 'player-games.json',
                                                    DATA26 / 'team-games.json', DATA26 / 'pbp')
    try:
        sd26 = IC.load_target_season()
    finally:
        IC.TARGET_BOX, IC.TARGET_TEAM, IC.TARGET_PBP = old
    sd26['season'] = TARGET
    C._CACHE[('target', TARGET)] = sd26
    return sd26, info


# ------------------------------------------------------------------ threeValue（R-024，顯示用；不進 OVR）
def _gamelog_sums(path):
    out = {}
    for r in SA.result_set(path):
        d = out.setdefault(int(r['PLAYER_ID']), [0.0, 0.0, 0.0])
        d[0] += float(r['MIN'] or 0)
        d[1] += float(r['FG3M'] or 0)
        d[2] += float(r['FG3A'] or 0)
    return out


def three_value_columns(prior_ids):
    """回傳 ({pid: dict}, info)。vol＝合併 3PA/MIN×36；acc＝k 收縮（上季 abilityC 當 k 個出手的先驗＋本季原始 3PM/3PA；
    本季沒有出手難度資料，用原始命中）；rep＝合併聯盟 3P%−0.03；value＝vol×(acc−rep)；池內（合併 MIN>=500 且有先驗卡）百分位→attr()。"""
    s25 = _gamelog_sums(IC.TARGET_BOX)          # 2025-26
    s26 = _gamelog_sums(DATA26 / 'player-games.json')
    m_all = sum(v[1] for d in (s25, s26) for v in d.values())
    a_all = sum(v[2] for d in (s25, s26) for v in d.values())
    mu = m_all / a_all
    rep = mu - THREE_REP_GAP
    prior = {int(k): v['abilityC'] for k, v in load_json(THREE_PRIOR).items()}

    def pct(x, arr):
        return 100 * (sum(v < x for v in arr) + .5 * sum(v == x for v in arr)) / (len(arr) or 1)

    def attr(p):
        return max(40, min(99, 40 + (p - 1) * 30 / 49 if p < 50 else 70 + (p - 50) * 29 / 49))

    cols = {}
    for pid in prior_ids:
        mn25, m25, a25 = s25.get(pid, (0.0, 0.0, 0.0))
        mn26, m26, a26 = s26.get(pid, (0.0, 0.0, 0.0))
        mn, a = mn25 + mn26, a25 + a26
        c = {'min26': mn26, 'fg3m26': m26, 'fg3a26': a26, 'minAll': mn, 'ok': pid in prior and mn > 0}
        if c['ok']:
            acc = (THREE_K * prior[pid] + m26) / (THREE_K + a26)
            vol = a / mn * 36
            c.update(acc=acc, vol=vol, value=vol * (acc - rep))
        cols[pid] = c
    pool = [c['value'] for c in cols.values() if c['ok'] and c['minAll'] >= THREE_POOL_MIN]
    for c in cols.values():
        c['threeValue'] = attr(pct(c['value'], pool)) if c['ok'] else None
    return cols, {'mu': mu, 'rep': rep, 'k': THREE_K, 'poolMin': THREE_POOL_MIN, 'poolSize': len(pool),
                  'leagueFG3M': m_all, 'leagueFG3A': a_all}


# ------------------------------------------------------------------ C4（逐球員 N）
def live_predict(delta2, rel, undefined=(), frozen=(), f_force=None, k_max=False, diag=None):
    prior_cards, _ = F.load_prior(PRIOR)
    _, attrs0 = C.deployment('S*')
    w, _ = F.windows_of(PRIOR, ALL_N)
    usg = C.usg_prior(PRIOR)
    out = {}
    for pid, x0 in attrs0.items():
        rec = w.get(pid)
        pc = prior_cards.get(pid)
        n_games = rec['GP'] if rec else 0
        f = f_force if f_force is not None else min(n_games / G_GAMES, 1.0)
        vals = {}
        for a in C.UPD:
            if pc is None or a in undefined or a in frozen:
                vals[a] = x0[a]
                continue
            if rec is None or IC.sample_of(rec, a) < SA.SEASON_MIN_SAMPLE[a]:
                vals[a] = x0[a]
                continue
            y = F.y_adj_of(pc, rec, a, usg.get(pid, 0.0))
            n = IC.sample_of(rec, a)
            if k_max:
                k = 50.0 * rel[a]['nRef']
            else:
                k = C_PARAM * V2.k_eff(delta2[a], rel[a]['sigma2'], V2.sample_n(pc, a), rel[a]['nRef'])
            b = n / (n + k)
            wt = f + (1.0 - f) * b
            vals[a] = C.clip(x0[a] + wt * (y - x0[a]))
            if diag is not None:
                diag.append({'pid': pid, 'attr': a, 'x0': x0[a], 'y': y, 'n': n, 'k': k, 'b': b,
                             'f': f, 'w': wt, 'xhat': vals[a]})
        # foulDraw（card 0.1.2 新欄）：y 用舊 drive 的同一個原始量（FTA/FGA 百分位，視窗 rec['drive']），
        # 樣本／最小樣本／δ²／rel 沿用 drive 的；不新增公式。drive 本身（0.1.2 改 PBP 版）凍結。
        a = 'foulDraw'
        vals[a] = x0[a]
        if not (pc is None or 'drive' in undefined or a in frozen or rec is None
                or IC.sample_of(rec, 'drive') < SA.SEASON_MIN_SAMPLE['drive']):
            y = C.usage_adjust({'drive': x0[a]}, rec, 'drive', usg.get(pid, 0.0))
            n = IC.sample_of(rec, 'drive')
            if k_max:
                k = 50.0 * rel['drive']['nRef']
            else:
                k = C_PARAM * V2.k_eff(delta2['drive'], rel['drive']['sigma2'], V2.sample_n(pc, 'drive'),
                                       rel['drive']['nRef'])
            b = n / (n + k)
            wt = f + (1.0 - f) * b
            vals[a] = C.clip(x0[a] + wt * (y - x0[a]))
            if diag is not None:
                diag.append({'pid': pid, 'attr': a, 'x0': x0[a], 'y': y, 'n': n, 'k': k, 'b': b,
                             'f': f, 'w': wt, 'xhat': vals[a]})
        out[pid] = {**x0, **vals}
    return out


# ------------------------------------------------------------------ 小工具
def git_head():
    r = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True,
                       creationflags=NO_WINDOW)
    return r.stdout.strip()


def rel(p):
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(p).resolve().as_posix()


def e064_anchors():
    """回傳 (錨點 [PR1, PR50, PR99], r_repl)。G1＝副版錨點與 r_repl（同 card 0.2.0 summary.json）；G0＝平均基準、r_repl＝0。"""
    d = load_json(E064_ANCHORS_FILE)
    a = d['anchors']['repl' if E064_MODE == 'G1' else 'main']
    return [a['PR1'], a['PR50'], a['PR99']], (d['rRepl_PR10_of_pred'] if E064_MODE == 'G1' else 0.0)


def e064_map(g, anc):
    p1, p50, p99 = anc
    return 40 + 30 * (g - p1) / (p50 - p1) if g <= p50 else 70 + 29 * (g - p50) / (p99 - p50)


def e064_convert(entries, mpg_by_pid, anc, r_repl=0.0):
    """entries＝{pid: pw.predict 輸出}；回傳同結構但 ovr 改為每場 OVR（ovrPer36 保留原值）。
    g = (pred − r_repl)·MPG/36（G0：r_repl＝0 即 pred·MPG/36）。"""
    out = {}
    for pid, e in entries.items():
        if not isinstance(e, dict):      # ref 帶 '_capIterations'
            out[pid] = e
            continue
        g = (e['pred'] - r_repl) * mpg_by_pid.get(pid, 0.0) / 36.0
        out[pid] = {**e, 'ovrPer36': e['ovr'], 'g': g, 'ovr': e064_map(g, anc)}
    return out


def latest_team(path):
    out = {}
    for r in sorted(SA.result_set(path), key=lambda r: (r['GAME_DATE'], r['GAME_ID'])):
        out[int(r['PLAYER_ID'])] = r['TEAM_ABBREVIATION']
    return out


def r1(v):
    return round(float(v), 1)


def med(xs):
    return statistics.median(xs) if xs else None


def md_table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '|'.join('---' for _ in head) + '|']
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)


# ------------------------------------------------------------------ 主流程
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sd26, mp = setup()
    cutoff = max(r['GAME_DATE'] for b in sd26['box'].values() for r in b['rows'])
    out_dir = HERE / (sys.argv[1] if len(sys.argv) > 1 else cutoff)
    out_dir.mkdir(parents=True, exist_ok=True)

    rel_ = V2.load_reliability()
    delta2, undefined, d_info = C4.delta2_info('S*')
    frozen = ['pressure', 'drive']      # drive：card 0.1.2 改 PBP 版（需前 41 場），賽中重建不了 → 凍結
    prior_cards, prior_doc = F.load_prior(PRIOR)
    _, attrs0 = C.deployment('S*')
    pw = PW.for_start(C, 'S*')
    ref = pw.ref
    w26, _ = F.windows_of(PRIOR, ALL_N)

    diag = []
    attrs = live_predict(delta2, rel_, undefined, frozen, diag=diag)
    res = pw.predict(attrs)
    mpg0, anc064, r_repl064 = {}, None, 0.0
    mpg_hat, mpg_win, w_mpg, mpg_nodata = {}, {}, {}, []
    if E064_MODE != 'off':
        # MPG0＝先驗卡那一季的 MIN／GP；ref（lastOVR 基準）一律用 MPG0 換成每場
        mpg0 = {pid: (float(c['observed']['MIN']) / float(c['observed']['GP']) if float(c['observed']['GP']) > 0 else 0.0)
                for pid, c in prior_cards.items()}
        anc064, r_repl064 = e064_anchors()
        mpg_hat = dict(mpg0)            # G0：MPG_hat＝MPG0（不更新）
        if E064_MODE == 'G1':
            # 預註冊 §4.1：MPG_hat = MPG0 + w·(MPG_win − MPG0)；w＝stamina 的 C4 w（f＋(1−f)·n/(n+c·k_eff)）。
            # 沒有 2026-27 視窗紀錄、沒有 stamina 的 w（無先驗卡等）→ 退回 MPG0（backtest_e064.mpg_hat 同款）。
            w_mpg = {d['pid']: d['w'] for d in diag if d['attr'] == 'stamina'}
            for pid in attrs0:
                rec = w26.get(pid)
                m0 = mpg0.get(pid, 0.0)
                if pid in w_mpg and rec is not None and rec['GP'] > 0:
                    mpg_win[pid] = rec['MIN'] / rec['GP']
                    mpg_hat[pid] = m0 + w_mpg[pid] * (mpg_win[pid] - m0)
                else:
                    mpg_hat[pid] = m0
                    mpg_nodata.append(pid)
        res = e064_convert(res, mpg_hat, anc064, r_repl064)
        ref = e064_convert(ref, mpg0, anc064, r_repl064)

    # ---- 檢查 (a)：f=0、k 取上界 → 與上季卡逐球員 OVR 差 <0.5（c4_v5 T1）
    a1 = live_predict(delta2, rel_, undefined, frozen, f_force=0.0, k_max=True)
    o1 = pw.predict(a1)
    if E064_MODE != 'off':
        o1 = e064_convert(o1, mpg0, anc064, r_repl064)
    t1 = max(abs(o1[p]['ovr'] - ref[p]['ovr']) for p in attrs0)
    a1_ref = C4.c4_predict('S*', ALL_N, delta2, rel_, 1.0, undefined, frozen, f_force=0.0, k_max=True)
    t1_same = max(abs(a1[p][a] - a1_ref[p][a]) for p in attrs0 for a in C.UPD)
    a2 = live_predict(delta2, rel_, undefined, frozen, f_force=0.0)
    r2 = F.c2_predict('S*', ALL_N, delta2, rel_, undefined=undefined, frozen=frozen)
    t2 = max(abs(a2[p][a] - r2[p][a]) for p in attrs0 for a in C.UPD)

    # ---- 映射重建是否與上季卡一致（只看僅由 box 決定的 long / ft）
    from ovr_common import CURVES, shooting
    st = mp['mappingStats']
    dl, df = [], []
    for pid, pc in prior_cards.items():
        s = st.get(pid)
        if not s or s['FG3A'] < 1:
            continue
        dl.append(abs(shooting(s['FG3M'], s['FG3A'], mp['priors']['long'], CURVES['CURVE_3PT']) - float(pc['long'])))
        if s['FTA'] >= 1:
            df.append(abs(shooting(s['FTM'], s['FTA'], mp['priors']['ft'], CURVES['CURVE_FT']) - float(pc['ft'])))

    # ---- 排名
    team = latest_team(DATA26 / 'player-games.json')
    formal_rows = C.load_csv(FORMAL_RANKING)
    formal = {}
    for r in formal_rows:
        formal.setdefault(r['name'], float(r['ovr']))
    tv_cols, tv_info = three_value_columns([pid for pid in sd26['box'] if prior_cards.get(pid) is not None])
    rows, nopr = [], []
    for pid, b in sd26['box'].items():
        pc = prior_cards.get(pid)
        gp = len(b['rows'])
        mins = sum(r['MIN'] for r in b['rows'])
        if pc is None:
            nopr.append({'playerId': pid, 'name': b['name'], 'team': team.get(pid, ''), 'N': gp,
                         'MIN26': round(mins, 1)})
            continue
        p = res[pid]
        row = {'ovr': r1(p['ovr']), 'name': pc['name'], 'pos': pc['pos'],
               'MIN': round(float(pc['observed']['MIN'])), 'predictedPer36': round(p['pred'], 3),
               'simulatedPer36': '', 'defenseBonus': round(p['bonus'], 3), 'align': round(p['align'], 3),
               'pred0': round(p['pred0'], 3), 'pr': round(p['pr'], 2)}
        for a in ATTRS:
            row[a] = r1(attrs[pid][a])
        if E064_MODE != 'off':
            row.update({'MPG0': round(mpg0.get(pid, 0.0), 2), 'MPGhat': round(mpg_hat.get(pid, 0.0), 2),
                        'g': round(p['g'], 3), 'ovrPer36': r1(p['ovrPer36'])})
            if E064_MODE == 'G1':
                row.update({'MPGwin': round(mpg_win[pid], 2) if pid in mpg_win else '',
                            'wMPG': round(w_mpg[pid], 4) if pid in w_mpg else ''})
        row.update({'playerId': pid, 'N': gp, 'team': team.get(pid, ''), 'MIN26': round(mins, 1),
                    'lastOVR': r1(ref[pid]['ovr']), 'dOVR': round(p['ovr'] - ref[pid]['ovr'], 2),
                    'formalOVR': formal.get(pc['name'], ''),
                    'threeValue': '' if tv_cols[pid]['threeValue'] is None else r1(tv_cols[pid]['threeValue']),
                    'fg3a26': int(tv_cols[pid]['fg3a26']), 'fg3m26': int(tv_cols[pid]['fg3m26']),
                    'fg3Pct26': round(tv_cols[pid]['fg3m26'] / tv_cols[pid]['fg3a26'], 4) if tv_cols[pid]['fg3a26'] else '',
                    '_ovr': p['ovr'], '_d': p['ovr'] - ref[pid]['ovr'],
                    '_lastCmp': r1(ref[pid]['ovr'] if E064_MODE != 'G0' else ref[pid].get('ovrPer36', ref[pid]['ovr']))})
        rows.append(row)
    rows.sort(key=lambda r: -r['_ovr'])
    for i, r in enumerate(rows, 1):
        r['rank'] = i
    head = (['rank', 'ovr', 'name', 'pos', 'MIN', 'predictedPer36', 'simulatedPer36', 'defenseBonus', 'align',
             'pred0', 'pr'] + list(ATTRS) + ['playerId', 'N', 'team', 'MIN26', 'lastOVR', 'dOVR', 'formalOVR',
             'threeValue', 'fg3a26', 'fg3m26', 'fg3Pct26'])
    if E064_MODE != 'off':
        head = head + ['MPG0', 'MPGhat', 'g', 'ovrPer36'] + (['MPGwin', 'wMPG'] if E064_MODE == 'G1' else [])
    C.write_csv(out_dir / 'ranking.csv', [{k: r[k] for k in head} for r in rows], head)
    nopr.sort(key=lambda r: (-r['N'], -r['MIN26']))
    C.write_csv(out_dir / 'no-prior.csv', nopr, ['playerId', 'name', 'team', 'N', 'MIN26'])

    # ---- 檢查 (b)：|ΔOVR|
    ds = [r['_d'] for r in rows]
    ad = [abs(d) for d in ds]
    by_n = {}
    for r in rows:
        by_n.setdefault(r['N'], []).append(abs(r['_d']))
    ordered = sorted(rows, key=lambda r: r['_d'])
    movers = sorted(rows, key=lambda r: -abs(r['_d']))[:10]
    pid_name = {r['playerId']: r['name'] for r in rows}
    changed_attrs = {}
    for d in diag:
        if abs(d['xhat'] - d['x0']) > 1e-9:
            changed_attrs.setdefault(d['attr'], 0)
            changed_attrs[d['attr']] += 1
    big = [r for r in rows if abs(r['_d']) >= 1.0]
    prior_game_pids = {r['playerId'] for r in rows}
    not_played = [p for p in prior_cards if p not in prior_game_pids]
    formal_diff = [abs(r['_lastCmp'] - r['formalOVR']) for r in rows if r['formalOVR'] != '']
    n_dist = {}
    for r in rows:
        n_dist[r['N']] = n_dist.get(r['N'], 0) + 1

    sanity = {
        'a_f0_kmax_maxAbsOvrDiff': t1, 'a_liveEqualsC4predict_maxAttrDiff': t1_same,
        'a_f0_equalsC2_maxAttrDiff': t2,
        'b_n': len(rows), 'b_median_abs': med(ad), 'b_max_abs': max(ad), 'b_mean_abs': statistics.mean(ad),
        'b_by_N': {n: {'players': len(v), 'median': med(v), 'max': max(v)} for n, v in sorted(by_n.items())},
        'b_ge_1': [(r['name'], r['N'], round(r['_d'], 3)) for r in big],
        'mapping_long_maxAbsDiff': max(dl), 'mapping_ft_maxAbsDiff': max(df),
        'pointwiseCheck': pw.check, 'lastOVR_vs_formal_maxAbs': max(formal_diff) if formal_diff else None,
        'lastOVR_vs_formal_matched': len(formal_diff),
    }

    # ---- meta.json
    inputs = {
        '2026-27 player-games': DATA26 / 'player-games.json', '2026-27 team-games': DATA26 / 'team-games.json',
        '2026-27 bio': DATA26 / 'bio.json', 'prior card': PRIOR_CARD, 'S* RAPM': RAPM_STAR,
        '2025-26 player-games': IC.TARGET_BOX, '2025-26 team-games': IC.TARGET_TEAM,
        '2025-26 bio': BIO25, 'threeValue prior (abilityC)': THREE_PRIOR, 'dependence-audit': IC.DEPENDENCE, 'formal ranking (cross-check)': FORMAL_RANKING,
        'reliability': V2.RELIABILITY if hasattr(V2, 'RELIABILITY') else None,
    }
    sha = {k: {'path': rel(v), 'sha256': C.sha256_file(v)} for k, v in inputs.items() if v}
    pbp_files = sorted(p.stem for p in (DATA26 / 'pbp').glob('*.json'))
    games = sorted({r['GAME_ID'] for r in sd26['teamRows']})
    meta = {
        'version': VERSION, 'e064Mode': E064_MODE, 'e064Anchors': anc064, 'e064RRepl': r_repl064 if E064_MODE == 'G1' else None,
        'e064MpgNoDataPlayers': len(mpg_nodata) if E064_MODE == 'G1' else None, 'priorCard': CARD_VERSION, 'dataCutoff': cutoff,
        'dataFirstDate': min(r['GAME_DATE'] for b in sd26['box'].values() for r in b['rows']),
        'games': len(games), 'pbpGames': len(pbp_files), 'missingPbp': sorted(set(games) - set(pbp_files)),
        'gitHead': git_head(), 'start': 'S*', 'prior': PRIOR, 'target': TARGET, 'c': C_PARAM, 'G': G_GAMES,
        'frozenAttrs': frozen + list(IC.FROZEN_ATTRS), 'updatableAttrs': list(C.UPD) + ['foulDraw'],
        'delta2Undefined': undefined, 'delta2': delta2,
        'players': {'ranked': len(rows), 'noPrior': len(nopr), 'priorCardNotPlayed': len(not_played)},
        'inputs': sha, 'mapping2025_26': {'priors': mp['priors'], 'poolSize': mp['poolSize'],
                                          'boxPlayersDroppedNoBio': mp['boxPlayersDroppedNoBio'],
                                          'priorShotSampleFilled': [mp['priorShotSampleFilled'], mp['priorCards']]},
        'sanity': sanity,
        'threeValue': {**tv_info, 'formula': 'vol*(acc-rep); vol=合併(2025-26+2026-27)3PA/MIN*36; acc=(k*abilityC_2025-26+FG3M_2026-27)/(k+FG3A_2026-27)'
                       '（本季無出手難度資料，用原始命中）; rep=合併聯盟3P%-0.03; 池=合併MIN>=500且有先驗卡; 百分位→attr() 40-99',
                       'note': '顯示用，不進 OVR（R-024）；long 欄仍留在 ranking.csv 並進 OVR，但表格不顯示'},
    }
    (out_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

    # ---- README.md
    def trow(r):
        return [r['name'], r['team'], r['N'], r['lastOVR'], r['ovr'], f"{r['_d']:+.2f}"]

    mv_detail = []
    for r in movers:
        ch = [d for d in diag if d['pid'] == r['playerId'] and abs(d['xhat'] - d['x0']) > 1e-9]
        txt = '；'.join(f"{d['attr']} {d['x0']:.1f}→{d['xhat']:.1f}（觀測 {d['y']:.1f}、n={d['n']:.0f}、k={d['k']:.0f}、w={d['w']:.3f}）"
                       for d in ch) or '（無屬性變動）'
        mv_detail.append(f"- {r['name']}（{r['team']}，N={r['N']}，ΔOVR {r['_d']:+.2f}）：{txt}")
    OVR_NOTE = {
        'G1': (f"- OVR 為每場（R-028，E-064 副版）：g = (預測每 36 分鐘淨值 − r_repl)·MPG_hat/36，r_repl＝{r_repl064:.4f}（替補水準 PR10），"
               f"兩段映射錨點 PR1/PR50/PR99＝{anc064[0]:.4f}/{anc064[1]:.4f}/{anc064[2]:.4f}（card 0.2.0 summary.json 同組）。"
               f"MPG_hat = MPG0 + w·(本季場均分鐘 − MPG0)，w＝stamina 的 C4 w（stamina 最小樣本 1 場）；"
               f"沒有本季視窗紀錄的 {len(mpg_nodata)} 人（含沒出賽者，不在排名內）退回 MPG0。`ovrPer36` 是同一預測的每 36 分鐘 OVR。"),
        'G0': '- OVR 為每場（E-064 G0 試跑）：g = pred·MPG0/36，MPG_hat＝MPG0 不更新，錨點為平均基準。',
        'off': '- OVR 為每 36 分鐘（inseason 0.1.x 做法）。'}[E064_MODE]
    md = f"""# {VERSION} 2026-27 即時結果（資料截至 {cutoff}）

- OVR：賽中 C4（{VERSION}），先驗 {CARD_VERSION}（live/prior-2025-26-card012.json）；N = 該球員 2026-27 已打場數。
- 資料：{meta['dataFirstDate']}..{cutoff}、{len(games)} 場、{len(pbp_files)} 份 PBP；缺 PBP：{', '.join(meta['missingPbp']) or '無'}。
- git HEAD：`{meta['gitHead'][:12]}`；c={C_PARAM}（凍結）、G={G_GAMES}、f = min(N/{G_GAMES}, 1)。
- 排名 {len(rows)} 人（有先驗卡且已出賽）；沒有先驗卡 {len(nopr)} 人（`no-prior.csv`，不給 OVR）；有先驗卡但 2026-27 還沒出賽 {len(not_played)} 人（不列入）。
- N 分布：{', '.join(f'N={n}: {c} 人' for n, c in sorted(n_dist.items()))}。
- 3PT 欄 = threeValue（R-024，顯示用、不進 OVR）：vol＝合併（2025-26＋2026-27）3PA/MIN×36；acc＝(k·上季 abilityC＋本季 3PM)/(k＋本季 3PA)，k={THREE_K}（本季沒有出手難度資料，用原始命中）；rep＝合併聯盟 3P%（{tv_info['mu']:.4f}）−0.03；value＝vol×(acc−rep)，在合併 MIN≥500 且有先驗卡的 {tv_info['poolSize']} 人池內取百分位並套 attr()。`long` 欄仍在 ranking.csv 並進 OVR 計算，只是表格不顯示。
- card 0.1.2 的屬性處理：foulDraw 用舊 drive 的同一個原始量（FTA/FGA 百分位）做 C4 更新；drive（改 PBP 版）、onBall（E-060 重定義）、pressure、help、physique、heightInches 凍結。
- 降級的資料層見 `../README.md`。`simulatedPer36` 空白（此流程不跑模擬）。
- `lastOVR` = 同一逐點管線對先驗卡算出的 OVR（ΔOVR 的基準）；`formalOVR` = {CARD_VERSION} `ranking.csv` 同名球員的 OVR（只供對照）。
{OVR_NOTE}

## 檢查 (a)：f=0、k 取上界 → 與上季卡一致（c4_v5 T1 同款）

| 項目 | 結果 |
|---|---|
| 逐球員 \\|OVR 差\\| 最大值（門檻 <0.5） | {t1:.6f} → {'通過' if t1 < 0.5 else '失敗'} |
| 本檔 live_predict 與 c4_v5.c4_predict（f=0, k 上界）屬性最大差 | {t1_same:.3e} |
| 本檔 live_predict（f=0, c=1）與 fit_w_grid_v4.c2_predict 屬性最大差（T2 同款，門檻 1e-9） | {t2:.3e} |
| 逐點管線 A 參考與原管線差（建構時檢查，門檻 1e-8） | {pw.check:.2e} |
| 重建的 2025-26 映射 vs 上季卡 long／ft 最大差（只由 box 決定，應接近 0） | {max(dl):.3f} ／ {max(df):.3f} |
| lastOVR vs 正式卡 OVR（同名 {len(formal_diff)} 人）最大差 | {max(formal_diff) if formal_diff else 'n/a'} |

## 檢查 (b)：ΔOVR = 賽中 OVR − lastOVR

- 人數 {len(rows)}；\\|ΔOVR\\| 中位數 {sanity['b_median_abs']:.3f}、平均 {sanity['b_mean_abs']:.3f}、最大 {sanity['b_max_abs']:.3f}。
- \\|ΔOVR\\| >= 1.0 的人：{len(big)} 人{('：' + '、'.join(f"{n}（N={k}，{d:+.2f}）" for n, k, d in sanity['b_ge_1'])) if big else ''}。
- 有屬性被更新的（屬性：人次）：{', '.join(f'{a} {c}' for a, c in sorted(changed_attrs.items(), key=lambda kv: -kv[1])) or '無'}。

依 N 分組的 \\|ΔOVR\\|：

{md_table(['N', '人數', '中位數', '最大'], [[n, v['players'], f"{v['median']:.3f}", f"{v['max']:.3f}"] for n, v in sanity['b_by_N'].items()])}

ΔOVR 最高 10 人：

{md_table(['球員', '隊', 'N', 'lastOVR', 'OVR', 'ΔOVR'], [trow(r) for r in ordered[::-1][:10]])}

ΔOVR 最低 10 人：

{md_table(['球員', '隊', 'N', 'lastOVR', 'OVR', 'ΔOVR'], [trow(r) for r in ordered[:10]])}

\\|ΔOVR\\| 最大 10 人的屬性變動明細（x0→x̂；觀測 y 已做 usage 調整）：

{chr(10).join(mv_detail)}
"""
    (out_dir / 'README.md').write_text(md, encoding='utf-8')
    print(json.dumps({'out': rel(out_dir), 'ranked': len(rows), 'noPrior': len(nopr), 'sanity': {
        k: v for k, v in sanity.items() if k != 'b_by_N'}}, ensure_ascii=False, indent=1, default=str))
    return 0 if (t1 < 0.5 and t1_same < 1e-9 and t2 < 1e-9) else 4


if __name__ == '__main__':
    raise SystemExit(main())

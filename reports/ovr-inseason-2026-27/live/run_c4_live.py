"""inseason 0.2.5（R-050 起新賽季版號＝先驗正式卡版號；E-095 採用，R-052；v5 Path A C4，E-033；先驗卡 x0＝card 0.2.5／0.2.4 能力值＝card 0.2.2 能力值；OVR 為每場，R-028 / E-064 G1；E-074、E-091）的 2026-27 即時版：逐球員用自己的已打場數 N 更新能力值與 OVR。

E-095（CARD_MODE=025，預設）：同 E-091，但先驗換 card 0.2.5、分鐘權重 mpg/36 改為飽和 W(mpg)，錨點／r_repl 取 E-089 results.json report_only.card.new。
E-091（CARD_MODE=024，inseason 0.2.4）：OVR 那一層換成 card 0.2.4（R-044）= card 0.2.2 屬性 p → 用人回歸 predNew（E-075/E-084）→ g = (predNew − r_repl)·mpg/36 → 兩段映射。
  用人特徵（L、a、y、v、d、has）凍結在 2025-26（live/usage-2025-26-card024.json，build_usage_024.py 呼叫 e084.py 產生），賽中只有 p 隨 C4 更新；
  MPG0＝card 0.2.4 ranking.csv 的 mpg 欄（mpgAvail），先驗卡沒有的人退回舊規則（MIN／GP）；r_repl、錨點取 E-084 results.json 的 card 段。換版不擬合新參數。
CARD_MODE=022：inseason 0.2.1 行為（逐位元重現），不套 predNew。
S*：先驗季 2025-26（CARD_MODE=022／024：card 0.2.2 先驗 live/prior-2025-26-card022.json，build_prior_022.py 由 card 0.2.2 ranking.csv 轉成（0.2.4 能力值欄與 0.2.2 逐欄相同）；
  CARD_MODE=020：card 0.2.0 階段的 prior-2025-26-card012.json，逐位元重現 inseason 0.2.0c）、目標季 2026-27。
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
import math
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
# E-074：賽中先驗換成 card 0.2.2（022）；E-091：OVR 層再換成 card 0.2.4（024，預設）；020＝inseason 0.2.0c 行為（先驗屬性 card 0.1.2、係數／錨點 card 0.1.2／0.2.0 階段）。
CARD_MODE = os.environ.get('CARD_MODE', '027b')  # 027b（預設，E-128 使用者破例採用，R-085）| 027（inseason 0.2.7，E-111）| 025（inseason 0.2.5a，E-095）| 026 | 024 | 022 | 020
if CARD_MODE not in ('025', '024', '022', '020', '026', '027', '027b'):
    raise SystemExit('CARD_MODE 只接受 025、024、022、020、026、027 或 027b')
M27B_MODE = CARD_MODE == '027b'                  # E-128（2026-10-30 使用者破例採用，預設，R-085）：card 0.2.7b 先驗＋pass 量×率＋help／threeValue 尾巴；OVR 層沿用 027 的 UL 機制
M27_MODE = CARD_MODE in ('027', '027b')                    # E-111（2026-10-30 採用；027b 沿用）：card 0.2.7 先驗＋UL6 OVR 層＋合併池映射（026 機制＋errata）
M26_MODE = CARD_MODE in ('026', '027', '027b')           # E-107（實驗中，預設不開）：card 0.2.6 先驗＋E-101 OVR 層＋0.2.6 量尺的賽中映射；027 沿用其合併池機制
USAGE_MODE = CARD_MODE in ('024', '025', '026', '027', '027b')         # 用人回歸層（E-091）
NEW_PRIOR = CARD_MODE in ('022', '024', '025', '026', '027', '027b')          # card 0.2.2 能力值先驗（foulDraw E-070 公式、presDisplay／foulDisc 顯示）
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
if NEW_PRIOR and E064_MODE != 'G1':
    raise SystemExit('CARD_MODE=022／024 只支援 E064_MODE=G1（錨點是每場副版）')
VERSION = 'inseason 0.2.7b'  # R-050／R-085：跟先驗 card 0.2.7b 同號（E-128 使用者破例採用）； 第一個字面值會被 daily_inseason_update.probe_base_version 以正規式讀取，勿改成括號／條件式開頭
if CARD_MODE == '027':
    VERSION = 'inseason 0.2.7'  # E-111 行為（逐位元重現 inseason 0.2.7）
if CARD_MODE == '026':
    VERSION = 'inseason 0.2.6'  # E-107（實驗中）：第一個字面值採用時才改
if CARD_MODE == '025':
    VERSION = 'inseason 0.2.5'  # E-095 行為（逐位元重現 inseason 0.2.5a）
if CARD_MODE == '024':
    VERSION = 'inseason 0.2.4'  # E-091 行為（逐位元重現 inseason 0.2.4a，原名 0.2.2a）
if CARD_MODE == '022':
    VERSION = 'inseason 0.2.1'  # E-074 行為（逐位元重現用）
if CARD_MODE == '020':
    VERSION = 'inseason 0.2.0' if E064_MODE == 'G1' else 'inseason 0.1.2'  # 020：重現 0.2.0c；off／G0：重現舊頁用
VERSION += ('' if E062_MODE == 'off' else '+E062-' + E062_MODE) + ('+E064-G0' if E064_MODE == 'G0' else '')
CARD_VERSION = ({'025': 'card 0.2.5', '024': 'card 0.2.4', '026': 'card 0.2.6', '027': 'card 0.2.7', '027b': 'card 0.2.7b'}.get(CARD_MODE, 'card 0.2.2')) if NEW_PRIOR else ('card 0.2.0' if E064_MODE == 'G1' else 'card 0.1.2')
SAT = CARD_MODE in ('025', '026', '027', '027b')      # 026／027 沿用 W（scale 15）
PRIOR = '2025-26'
TARGET = '2026-27'
G_GAMES = 82
C_PARAM = 1.0
ALL_N = 99                      # 視窗＝全部已打場次
DATA26 = ROOT / 'data/defense-seventh' / TARGET
E101_DIR = ROOT / 'reports/card-0.2.5+E101-crossera'
if M26_MODE:
    PRIOR_CARD = HERE / 'prior-2025-26-card026.json'  # build_prior_026.py 產出（x0＝card 0.2.6，尾巴原樣）
    CARD_DIR = E101_DIR / 'cards/e101/P1/primary'     # E-107 §2.2：屬性迴歸＝E-101 P1 primary summary.json 的 formula
elif NEW_PRIOR:
    PRIOR_CARD = HERE / 'prior-2025-26-card022.json'  # build_prior_022.py 產出（x0＝card 0.2.2；0.2.4 能力值欄與 0.2.2 逐欄相同）
    CARD_DIR = ROOT / 'reports/card-0.2.2/cards/P1/primary'
else:
    PRIOR_CARD = HERE / 'prior-2025-26-card012.json'  # build_prior_012.py 產出（x0＝card 0.1.2）
    CARD_DIR = ROOT / 'reports/card-0.1.1+E060-onball-targeting/primary'
CARD_SUMMARY = CARD_DIR / 'summary.json'                # 凍結迴歸係數／錨點（022：card 0.2.2 P1 primary）
RAPM_STAR = ROOT / 'reports/impact-rapm/rapm.csv'
BIO25 = ROOT / 'data/benchmark-source/bio.json'
FORMAL_RANKING = (ROOT / 'reports/card-0.2.6/ranking.csv') if M26_MODE else (ROOT / 'reports/card-0.2.5/ranking.csv') if CARD_MODE == '025' else (ROOT / 'reports/card-0.2.4/ranking.csv') if CARD_MODE == '024' else (
    (ROOT / 'reports/card-0.2.2/ranking.csv') if CARD_MODE == '022' else (
        (ROOT / 'reports/card-0.2.0/ranking.csv') if E064_MODE == 'G1' else CARD_DIR / 'ranking.csv'))
# E-091：card 0.2.4 的用人層（係數、r_repl、錨點）與凍結特徵
E084_RESULTS = (E101_DIR / 'cards/e101/e084/results.json') if M26_MODE else ROOT / 'reports/card-0.2.3+E084-current-target/results.json'
CARD024_SUMMARY = ROOT / ('reports/card-0.2.6/summary.json' if M26_MODE else 'reports/card-0.2.5/summary.json' if CARD_MODE == '025' else 'reports/card-0.2.4/summary.json')
# E-095：card 0.2.5 的錨點／r_repl 在 E-089 results.json 的 report_only.card.new；分鐘權重 W(m)（R-047，尺度 15 凍結）
E089_RESULTS = ROOT / 'reports/card-0.2.4+E089-minutes-saturation/results.json'
CARD024_RANKING = ROOT / 'reports/card-0.2.4/ranking.csv'
W_TAU, W_REF = 15.0, 36.0


def sat_w(m):
    """card 0.2.5 的分鐘權重 W(m) = (1 − e^(−m/15)) / (1 − e^(−36/15))；W(0)=0、W(36)=1。"""
    return (1.0 - math.exp(-m / W_TAU)) / (1.0 - math.exp(-W_REF / W_TAU))

USAGE_FILE = HERE / ('usage-2025-26-card026.json' if M26_MODE else 'usage-2025-26-card024.json')      # build_usage_024.py（026：build_usage_026.py）產出
POOL026 = HERE / 'pool-026.json'                      # E-107 §2.3：build_pool_026.py 產出的凍結合併池
# E-111（CARD_MODE=027，預註冊 e111-card027/preregistration.md）：以下覆寫 026 的路徑；其他模式不經過這段
UL_DIR = ROOT / 'reports/card-0.2.6+E107-defense-UL'
DEF_L_PRIMARY = ROOT / 'reports/card-0.2.5+E104-defense-pergame-decay/def-L-primary.csv'   # card 0.2.7 UL6 primary 的 --defRapm
UL_PHASE2 = UL_DIR / 'phase2.json'
if M27_MODE:
    PRIOR_CARD = HERE / 'prior-2025-26-card027.json'  # build_prior_027.py 產出（x0＝card 0.2.7 產生器未四捨五入值）
    CARD_DIR = UL_DIR / 'cards/UL6/primary'           # 屬性迴歸＝UL6 primary summary.json 的 formula
    CARD_SUMMARY = CARD_DIR / 'summary.json'
    FORMAL_RANKING = ROOT / 'reports/card-0.2.7/ranking.csv'
    CARD024_SUMMARY = ROOT / 'reports/card-0.2.7/summary.json'
    USAGE_FILE = HERE / 'usage-2025-26-card027.json'  # build_usage_027.py 產出（係數、r_repl、錨點＝UL6 pipeline）
    E084_RESULTS = USAGE_FILE                        # 027 沒有 e084 results.json；錨點／r_repl 取 usage 檔並對 phase2.json UL6 核對
    E064_ANCHORS_FILE = USAGE_FILE
    POOL026 = HERE / 'pool-027.json'                  # e111-card027/build_pool_027.py 產出
# E-128（CARD_MODE=027b，預註冊 e128-card027b/preregistration.md §1＋errata-1/2）：覆寫 027 的路徑；UL 防守加成層（m27_*）沿用 027
E128_RB = ROOT / 'reports/card-0.2.7+E123-tail-3pt-rim-pres/rebase-027a'
E128_CARD_SUMMARY = ROOT / 'reports/card-0.2.7b/summary.json'
E128_THREE_CSV = ROOT / 'reports/card-0.2.7b/three-value.csv'      # errata-2：threeValue 的 acc 先驗（acc 欄）
if M27B_MODE:
    PRIOR_CARD = HERE / 'prior-2025-26-card027b.json'  # build_prior_027b.py 產出（x0＝card 0.2.7b 產生器未四捨五入值）
    CARD_DIR = E128_RB / 'cards/e123a/primary'         # 屬性迴歸＝rebase-027a e123a primary summary.json
    CARD_SUMMARY = CARD_DIR / 'summary.json'
    FORMAL_RANKING = ROOT / 'reports/card-0.2.7b/ranking.csv'
    CARD024_SUMMARY = E128_CARD_SUMMARY
    USAGE_FILE = HERE / 'usage-2025-26-card027b.json'  # build_usage_027b.py 產出
    E084_RESULTS = USAGE_FILE
    E064_ANCHORS_FILE = USAGE_FILE
    POOL026 = HERE / 'pool-027b.json'                  # e128-card027b/build_pool_027b.py 產出
# E-064（預註冊 §2、§4、§5）：每場 g = pred × MPG_hat / 36，兩段式映射錨點＝V2.FROZEN_SUMMARY（此處＝card 0.1.2 摘要）
# 原本算 scaleAnchorsPer36 的 MIN>=500 池，改用 g 重算的 PR1/PR50/PR99（card-0.1.2+E064-pergame/primary/pergame-summary.json
# 的 anchors.main，與 summary.json 同一個 card 0.1.2 管線與池）。算一次、凍結。
E064_ANCHORS_FILE = E084_RESULTS if M26_MODE else E089_RESULTS if CARD_MODE == '025' else E084_RESULTS if CARD_MODE == '024' else ((CARD_DIR / 'pergame-summary.json') if CARD_MODE == '022' else (
    ROOT / 'reports/card-0.1.2+E064-pergame/primary/pergame-summary.json'))
THREE_PRIOR = ROOT / 'reports/ovr-v62-3pt-difficulty-2025-26/new-long.json'   # abilityC（難度調整準度）＝上季先驗
THREE_K = 294.667                 # E-057：v62 方法 (c) 的 k（出手數單位）
THREE_REP_GAP = 0.03              # rep = 聯盟 3P% − 0.03
THREE_POOL_MIN = 500              # 池：合併 MIN >= 500 且有先驗卡
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ==== E-107 026 BEGIN ====
# CARD_MODE=026（E-107，預註冊 reports/ovr-inseason-2026-27/e107-card026/preregistration.md §2.3–2.4）專用的純函式。
# 只有 026 模式會呼叫；其他模式逐位元不變。build_pool_026.py、check_prereq.py、backtest_e107.py 讀這兩行標記之間的文字 exec 共用，
# 執行時命名空間要有 SA、IC、math、json（bisect、hashlib 本段自己 import）。尾巴常數、池門檻照 E-101（build_e101.py）凍結值。
import bisect  # noqa: E402
import hashlib  # noqa: E402
M26_CEIL, M26_K_SD, M26_Z9990 = 150.0, 1.96, 1.044
M26_PCT = ('tovSkill', 'pass', 'rebound', 'creation', 'stamina', 'foulDraw')
M26_CURVE = {'long': 'CURVE_3PT', 'mid': 'CURVE_MID', 'short': 'CURVE_SHORT', 'ft': 'CURVE_FT'}
M26 = {}      # m26_load_pool() 載入的 live/pool-026.json


def m26_zone_of(action):
    """SA.zone_of ＋ E-101 規則：有 area 且 area=='Mid-Range' 且 (shotDistance or 0) < 8 → short（同 extract_pbp_e101.py）。"""
    area = action.get('area')
    if area:
        if area == 'Mid-Range' and (action.get('shotDistance') or 0.0) < 8.0:
            return 'short'
        return 'mid' if area == 'Mid-Range' else 'short'
    x, y = action.get('xLegacy'), action.get('yLegacy')
    if x is None or y is None:
        return 'short'
    if x == 0 and y == 0:
        return 'short'
    return 'short' if (abs(x) <= 80 and y <= 138) else 'mid'


def m26_attr_of(p):
    return max(40.0, min(99.0, 40 + (p - 1) * 30 / 49 if p < 50 else 70 + (p - 50) * 29 / 49))


def m26_top_tail(d, sd):
    return 99 + (M26_CEIL - 99) * (1 - math.exp(-max(0.0, d) / (M26_K_SD * sd)))


def m26_bot_tail(d, sd):
    return 40 - 15 * (1 - math.exp(-max(0.0, d) / sd))


def m26_inverse_open(p, curve, lo, hi):
    """同 build_e101.inverse_open（= build_e090.inverse_open）。"""
    for i in range(1, len(curve)):
        x0, y0 = curve[i - 1]
        x1, y1 = curve[i]
        if min(y0, y1) <= p <= max(y0, y1):
            return max(lo, min(hi, x0 + (p - y0) / (y1 - y0) * (x1 - x0)))
    x = curve[0][0] if abs(p - curve[0][1]) < abs(p - curve[-1][1]) else curve[-1][0]
    return max(lo, min(hi, x))


def m26_pct(x, s):
    """小於者 + 0.5·相等者（同 ovr_common.percentile、build_e101.Pool.pct）；s 已排序。"""
    lo, hi = bisect.bisect_left(s, x), bisect.bisect_right(s, x)
    return 100 * (lo + 0.5 * (hi - lo)) / len(s)


def m26_anchors(vals):
    """同 build_e101.Pool.anchors('max')。"""
    s = sorted(float(v) for v in vals)
    n = len(s)
    r90 = min(v for v in s if m26_pct(v, s) >= 90)
    r99 = min(v for v in s if m26_pct(v, s) >= 99)
    r1 = max(v for v in s if m26_pct(v, s) <= 1)
    m = sum(s) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in s) / n)
    gap = (r99 - r90) / M26_Z9990
    return {'r90': r90, 'r99': r99, 'r1': r1, 'SD_pool': sd, 'gapScale': gap, 'S': max(gap, sd),
            'insuranceActive': bool(sd > gap), 'poolN': n}


def m26_pct_attr(x, ent):
    """百分位型（build_e101.percentile_attr_merged，mode max）：PR≥99 且開頂端→top_tail(x−r99, S)；PR≤1 且開底端→bot_tail(r1−x, SD_pool)。"""
    p = m26_pct(x, ent['sorted'])
    an = ent['anchors']
    if p >= 99 and ent['top']:
        return m26_top_tail(x - an['r99'], an['S'])
    if p <= 1 and ent['bot']:
        return m26_bot_tail(an['r1'] - x, an['SD_pool'])
    return m26_attr_of(p)


def m26_curve_attr(p, ent, curve):
    """命中率型（build_e101.build 的 curve 分支）：p > a99 且開頂端→99＋51·(1−e^(−(p−a99)/s))/(1−e^(−(1−a99)/s))，s＝1.96·S_p；否則反查曲線夾 [lo, 99]。"""
    a99, s = ent['a99'], ent['s']
    if ent['top'] and p > a99:
        return 99 + (M26_CEIL - 99) * (1 - math.exp(-(p - a99) / s)) / (1 - math.exp(-(1 - a99) / s))
    return m26_inverse_open(p, curve, ent['lo'], 99.0)


def m26_shrunk(makes, attempts, mean):
    """ovr_common.shooting 的收縮命中率（固定 100 次偽出手），還沒反查曲線。"""
    return (makes + 100 * mean) / (attempts + 100)


def m26_e2_short(base, prior_card, creation_prior, lo):
    """IC._e2_short，只把夾值 [40, 99] 換成 [lo, 150]（2025-26 先驗卡沒有 e2 → 直接回傳 base）。"""
    e2 = prior_card.get('e2') if prior_card else None
    if not e2:
        return base
    s_tilde = float(e2['sTilde'])
    pos = prior_card.get('pos')
    exempt = 0.0
    if pos in ('PF', 'C') and creation_prior is not None:
        exempt = max(0.0, min(1.0, (creation_prior - 55.0) / 10.0))
    eff = SA.E2_LAMBDA + (1 - SA.E2_LAMBDA) * exempt
    factor = s_tilde + eff * (1 - s_tilde)
    return max(lo, min(M26_CEIL, 70.0 + (base - 70.0) * factor))


def m26_foul_comp(fta, fga, mn, fz):
    """E-070 合成值，常數凍結自 2025-26（同 run_c4_live.foul_draw_y 的算式與運算順序）。"""
    z_vol = (fta / mn * 36.0 - fz['vol']['mean']) / fz['vol']['std']
    z_rate = (fta / fga - fz['rate']['mean']) / fz['rate']['std']
    return fz['wVol'] * z_vol + fz['wRate'] * z_rate


def m26_range(a):
    """026 模式各屬性的合法範圍（照開關）：百分位型 bot→25、命中率型 bot→0、否則 40；top→150、否則 99。"""
    ent = M26['attrs'][a]
    lo = (25.0 if ent['type'] == 'percentile' else 0.0) if ent['bot'] else 40.0
    return lo, (M26_CEIL if ent['top'] else 99.0)


def m26_clip(v):
    """026 模式取代 v4_common.clip：x̂ 是 x0 與 y_adj 的凸組合，兩者都在 m26_range 內，故只防數值意外；放寬到 [0, 150]。"""
    return max(0.0, min(M26_CEIL, v))


def m26_payload_sha(doc):
    body = json.dumps({k: v for k, v in doc.items() if k != 'payloadSha256'}, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'))
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def m26_load_pool(path):
    doc = json.loads(open(path, encoding='utf-8').read())
    if m26_payload_sha(doc) != doc['payloadSha256']:
        raise SystemExit(f'{path} payload sha256 不符')
    M26.clear()
    M26.update(doc)
    return doc


def m26_pass_027b(s, ast_pct100, pf, ent):
    """E-128 errata-1：視窗 pass＝百分位型映射(0.5·z(AST/MIN·36)+0.5·z(AST/astCh))；視窗不收縮；z 常數＝pool 的 passFreeze。
    pb['pass'] 是 AST%×100，÷100 回到 AST/astCh。"""
    y_vol = s['AST'] / s['MIN'] * 36.0 if s['MIN'] > 0 else 0.0
    y_rate = ast_pct100 / 100.0
    z = (pf['wVol'] * (y_vol - pf['vol']['mean']) / pf['vol']['std']
         + pf['wRate'] * (y_rate - pf['rate']['mean']) / pf['rate']['std'])
    return m26_pct_attr(z, ent)


def m26_window_cards(sd, n, mapping, prior_cards, received, season_min_sample=None):
    """IC.window_cards 的 026 版：原始值、樣本、u_proxy 逐字照抄；映射改成 pool-026 合併池＋E-101 尾巴；另帶 foulDraw 觀測值。
    命中率型的收縮先驗仍用 mapping['priors']（先驗季聯盟命中率，同 IC）；drive 照舊（凍結屬性，不進更新）。"""
    P, CV = M26['attrs'], IC.CURVES
    gm = IC.window_game_map(sd, n)
    stats = SA.aggregate(sd, gm)
    totals = SA.team_totals(sd)
    pb = SA.pass_rebound_raw(sd, gm)
    pr = mapping['priors']
    fz = M26['foulDrawConstants']
    out = {}
    for pid, s in stats.items():
        pc = prior_cards.get(pid)
        if pc is None:
            continue
        if not received:
            creation = float(pc['creation'])
        else:
            rec = received.get(pid, 0.5)
            creation = m26_pct_attr((1.0 - rec) * s['FGA'] / max(s['MIN'], 1.0) * 36.0, P['creation'])
        base_short = m26_curve_attr(m26_shrunk(s['shortM'], s['shortA'], pr['short']), P['short'], CV['CURVE_SHORT'])
        onfloor = 0.0
        for r in sd['box'][pid]['rows']:
            if r['GAME_ID'] not in gm[pid]:
                continue
            t = totals.get(r['GAME_ID'], {}).get(r['TEAM_ID'])
            if t:
                onfloor += SA.team_possessions(t) * r['MIN'] / 48.0
        events = s['FGA'] + 0.44 * s['FTA'] + s['TOV']
        card = {
            'playerId': pid,
            'long': m26_curve_attr(m26_shrunk(s['FG3M'], s['FG3A'], pr['long']), P['long'], CV['CURVE_3PT']),
            'mid': m26_curve_attr(m26_shrunk(s['midM'], s['midA'], pr['mid']), P['mid'], CV['CURVE_MID']),
            'shortBase': base_short,
            'short': m26_e2_short(base_short, pc, pc.get('creation'), P['short']['lo']),
            'ft': m26_curve_attr(m26_shrunk(s['FTM'], s['FTA'], pr['ft']), P['ft'], CV['CURVE_FT']),
            'drive': IC.attr(IC.percentile(SA.safe(s['FTA'], s['FGA']), mapping['pools']['drive'])),
            'tovSkill': m26_pct_attr(-SA.safe(s['TOV'], s['possDen']), P['tovSkill']),
            'pass': (m26_pass_027b(s, pb['pass'][pid], M26['passFreeze'], P['pass']) if 'passFreeze' in M26
                     else m26_pct_attr(pb['pass'][pid], P['pass'])),
            'rebound': m26_pct_attr(pb['rebound'][pid], P['rebound']),
            'stamina': (m26_pct_attr(s['MPG'], P['stamina']) if 'stamina' in P      # 027（E-111 §1.3）：池裡沒有 stamina
                        else IC.attr(IC.percentile(s['MPG'], mapping['pools']['stamina']))),   # → 照 IC.window_cards 單季映射
            'creation': creation,
            'foulDraw': (m26_pct_attr(m26_foul_comp(s['FTA'], s['FGA'], s['MIN'], fz), P['foulDraw'])
                         if s['FGA'] > 0 and s['MIN'] > 0 else None),
            'sample': {'fg3a': s['FG3A'], 'midA': s['midA'], 'shortA': s['shortA'], 'fta': s['FTA'],
                       'fga': s['FGA'], 'possDen': s['possDen'], 'min': s['MIN'], 'gp': s['GP'],
                       'defensePossessions': 0.0},
            'MIN': s['MIN'], 'GP': s['GP'],
            'u_proxy': 100.0 * events / onfloor if onfloor > 0 else 0.0,
            'u_proxy_per36': events / max(s['MIN'], 1.0) * 36.0,
        }
        out[pid] = card
    return out
# ==== E-107 026 END ====


# ==== E-111 027 BEGIN ====
# CARD_MODE=027（E-111，預註冊 reports/ovr-inseason-2026-27/e111-card027/preregistration.md §1）專用；其他模式不呼叫。
# build_pool_027.py、check_prereq.py、backtest_e111.py 連同上面的 E-107 段一起 exec（命名空間要有 SA、IC、math、json）。
M27_AREA_PBP = {('defense-seventh', '2022-23'), ('defense-seventh', '2023-24'), ('defense-seventh', '2024-25'),
                ('defense-seventh', '2025-26'), ('data', 'defense-a-source')}     # 有 area 欄的季（2022-23～2025-26）的 PBP 目錄
M27_ZONE_DROPPED = {}       # {PBP 目錄: 被跳過的 area 缺值 2pt 出手數}
M27_DEF = {}                # {rapm.csv 絕對路徑: 該起點 UL 防守加成用的單季 D 檔（def-L）}


def m27_area_dir(path):
    """PBP 檔所在目錄若屬於有 area 欄的季，回傳該目錄字串；否則 None（2021-22 以前、2026-27 照座標規則）。"""
    from pathlib import Path as _P
    d = _P(path).resolve().parent
    if d.name != 'pbp':
        return None
    key = (d.parent.parent.name, d.parent.name)
    return d.as_posix() if key in M27_AREA_PBP else None


def m27_install_zone_filter():
    """E-111 §1.4：有 area 欄的季，area 缺值的 2pt 投籃動作在載入時丟掉（同 E-101 跳過：不算 mid 也不算 short）；
    分區規則用 m26_zone_of（Mid-Range 且 shotDistance<8 → short；沒有 area 欄的季照座標）。包 SA／IC 的 load_json，冪等。"""
    SA.zone_of = m26_zone_of
    for mod in (SA, IC):
        if getattr(mod.load_json, '_m27', False):
            continue
        orig = mod.load_json

        def lj(path, _orig=orig):
            doc = _orig(path)
            key = m27_area_dir(path)
            if key is None:
                return doc
            acts = doc['data']['game']['actions']
            keep = [a for a in acts if not (a.get('isFieldGoal') == 1 and a.get('actionType') == '2pt' and not a.get('area'))]
            if len(keep) != len(acts):
                M27_ZONE_DROPPED[key] = M27_ZONE_DROPPED.get(key, 0) + len(acts) - len(keep)
                doc['data']['game']['actions'] = keep
            return doc
        lj._m27 = True
        mod.load_json = lj


def m27_ul_bonus(pipe):
    """card 0.2.7（UL6 primary：--bonusShape none --defWindow season --defPossFactor 0.5）的防守加成，逐 pipe.pids：
    Dw／possW＝def-L 檔的 D／poss（沒有的人 Dw=NaN、possW=0）；posMeanD(pos)＝Σ MIN·0.75·Dw／Σ MIN（同 pos、possW≥500）；
    centeredD＝0.75·Dw − posMeanD（possW≥500，否則 NaN）；bonus＝max(0, centeredD)（possW≥2500 且非 NaN，否則 0），不乘 taper。
    MIN＝先驗卡 observed.MIN（= 產生器 MIN）。賽中凍結（onBall、help 凍結，D 不逐場更新）。"""
    import csv as _csv
    key = str(__import__('pathlib').Path(pipe.rapm_path).resolve())
    if key not in M27_DEF:
        raise SystemExit(f'E-111：{key} 沒有對應的 def-L 檔（M27_DEF）')
    src = {int(r['playerId']): r for r in _csv.DictReader(open(M27_DEF[key], encoding='utf-8'))}
    n = len(pipe.pids)
    dw = [float(src[p]['D']) if p in src else float('nan') for p in pipe.pids]
    pw = [float(src[p]['poss']) if p in src else 0.0 for p in pipe.pids]
    blend_w, min_w = 1000 * 0.5, 5000 * 0.5
    mean = {}
    for pos in set(pipe.pos):
        idx = [i for i in range(n) if pipe.pos[i] == pos and pw[i] >= blend_w]
        mean[pos] = sum(pipe.minutes[i] * 0.75 * dw[i] for i in idx) / sum(pipe.minutes[i] for i in idx)
    out = []
    for i in range(n):
        if pw[i] >= min_w and pw[i] >= blend_w and not math.isnan(dw[i]):
            out.append(max(0.0, 0.75 * dw[i] - mean[pipe.pos[i]]))
        else:
            out.append(0.0)
    return out, mean


def m27_bonus_of(pipe):
    if not hasattr(pipe, '_m27_bonus'):
        pipe._m27_bonus, pipe._m27_posMeanD = m27_ul_bonus(pipe)
    return pipe._m27_bonus


def m27_ovr_predict(self, attrs_by_pid):
    """OVRPipeline.predict 的 027 版：bonus 換成 m27_bonus_of（UL，不乘 taper），align（poss≥5000）、H1 封頂照舊。"""
    import numpy as np
    import ovr_pipeline as OP
    from ovr_common import ATTRS as _A
    raw = np.array([[attrs_by_pid[p][a] for a in _A] for p in self.pids], float)
    pred0 = self.design(raw)
    pr_pool = sorted(pred0[i] for i in range(len(pred0)) if self.pr_mask[i])
    pr = np.array([OP.percentile_rank(v, pr_pool) for v in pred0])
    bonus = np.array(m27_bonus_of(self), float)
    align = np.zeros(len(pred0))
    for i in range(len(pred0)):
        if self.poss[i] >= OP.BONUS_MIN_POSS:
            align[i] = 0.25 * (self.r[i] - pred0[i])
    lift = bonus + align
    pred = pred0 + bonus + align
    pred, iters = OP.cap_total_lift(pred, pred0, lift, self.allowed)
    p1, p50, p99 = self.anchors
    ovr = np.where(pred <= p50, 40 + 30 * (pred - p1) / (p50 - p1), 70 + 29 * (pred - p50) / (p99 - p50))
    out = {}
    for i, p in enumerate(self.pids):
        out[p] = {'pred0': float(pred0[i]), 'bonus': float(bonus[i]), 'align': float(align[i]),
                  'pred': float(pred[i]), 'ovr': float(ovr[i]), 'pr': float(pr[i])}
    out['_capIterations'] = iters
    return out


def m27_pw_predict(self, attrs_by_pid):
    """PointwisePipeline.predict 的 027 版：bonus＝m27_bonus_of（不乘 taper，固定）；align、逐點封頂 T(A) 照舊。"""
    import numpy as np
    import ovr_pipeline as OP
    from ovr_common import ATTRS as _A
    P = self.pipe
    raw = np.array([[attrs_by_pid[p][a] for a in _A] for p in P.pids], float)
    pred0 = P.design(raw)
    ub = m27_bonus_of(P)
    out = {}
    p1, p50, p99 = P.anchors
    for i, p in enumerate(P.pids):
        bonus, align = ub[i], 0.0
        if P.poss[i] >= OP.BONUS_MIN_POSS:
            align = 0.25 * (P.r[i] - pred0[i])
        pred = pred0[i] + bonus + align
        a = P.allowed[i]
        if a is not None and bonus + align > 0:
            pred = min(pred, max(pred0[i], self.T[a]))
        ovr = 40 + 30 * (pred - p1) / (p50 - p1) if pred <= p50 else 70 + 29 * (pred - p50) / (p99 - p50)
        out[p] = {'pred0': float(pred0[i]), 'bonus': float(bonus), 'align': float(align),
                  'pred': float(pred), 'ovr': float(ovr), 'pr': float(self.pr0[i])}
    return out


def m27_install_ul(def_by_rapm):
    """換掉 OVRPipeline.predict／PointwisePipeline.predict（類別層，只在 027 呼叫）；def_by_rapm＝{rapm.csv 絕對路徑: def-L 檔}。"""
    import ovr_pipeline as OP
    import pointwise_pipeline as PWM
    M27_DEF.update({str(__import__('pathlib').Path(k).resolve()): v for k, v in def_by_rapm.items()})
    OP.OVRPipeline.predict = m27_ovr_predict
    PWM.PointwisePipeline.predict = m27_pw_predict
    if not getattr(OP.OVRPipeline.__init__, '_m27', False):     # E-111 errata 1：RAPM 名次同分照卡片產生器
        orig_init = OP.OVRPipeline.__init__

        def init(self, summary_path, rapm_path, prior_cards):
            orig_init(self, summary_path, rapm_path, prior_cards)
            self.allowed = m27_card_allowed(self, rapm_path)
        init._m27 = True
        OP.OVRPipeline.__init__ = init


def m27_card_allowed(pipe, rapm_path):
    """E-111 errata 1：H1 封頂的 allowed（margin 0）＝card 產生器 calibrate-wing.py attach_external_ranks＋cap_allowed 的 rapmRank：
    rapm.csv 以 name 為 key（同名最後一列覆蓋、dict 保留首次出現位置）；池＝pooledPoss≥5000；依 pooledNet 降冪 stable sort（同分照列序）；
    球員以先驗卡 name 對應；poss（playerId 對應）< 5000 或名字不在池內 → None。"""
    import csv as _csv
    import ovr_pipeline as OP
    rapm = {}
    for r in _csv.DictReader(open(rapm_path, encoding='utf-8')):
        rapm[r['name']] = r
    pool = [r for r in rapm.values() if float(r['pooledPoss']) >= OP.BONUS_MIN_POSS]
    net = {r['name']: i + 1 for i, r in enumerate(sorted(pool, key=lambda x: -float(x['pooledNet'])))}
    out = []
    for i, p in enumerate(pipe.pids):
        if pipe.poss[i] < OP.BONUS_MIN_POSS:
            out.append(None)
            continue
        k = net.get(pipe.name_by_pid[p])
        out.append(max(1, int(k)) if k is not None else None)
    return out
# ==== E-111 027 END ====


# ------------------------------------------------------------------ 環境設定
def setup():
    PA.install()
    if M26_MODE:      # E-107：只在 026 模式換掉（其他模式不碰）
        m26_load_pool(POOL026)
        SA.zone_of = m26_zone_of
        IC.window_cards = m26_window_cards
        C.clip = m26_clip
    if M27_MODE:      # E-111：有 area 欄的季 area 缺值的 2pt 跳過；OVR 層防守加成換 UL 公式（只在 027 模式）
        m27_install_zone_filter()
        m27_install_ul({str(RAPM_STAR.resolve()): DEF_L_PRIMARY})
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


def three_value_columns(prior_ids, extra_ids=()):
    """回傳 ({pid: dict}, info)。vol＝合併 3PA/MIN×36；acc＝k 收縮（上季 abilityC 當 k 個出手的先驗＋本季原始 3PM/3PA；
    本季沒有出手難度資料，用原始命中）；rep＝合併聯盟 3P%−0.03；value＝vol×(acc−rep)；池內（合併 MIN>=500 且有先驗卡）百分位→attr()。"""
    s25 = _gamelog_sums(IC.TARGET_BOX)          # 2025-26
    s26 = _gamelog_sums(DATA26 / 'player-games.json')
    m_all = sum(v[1] for d in (s25, s26) for v in d.values())
    a_all = sum(v[2] for d in (s25, s26) for v in d.values())
    mu = m_all / a_all
    rep = mu - THREE_REP_GAP
    # E-128 errata-4：027b 的 threeValue 照 027 現行算法（兩季即時池、abilityC 先驗；頂端尾巴見下方，2026-10-30 起不封 99）
    prior = {int(k): v['abilityC'] for k, v in load_json(THREE_PRIOR).items()}

    def pct(x, arr):
        return 100 * (sum(v < x for v in arr) + .5 * sum(v == x for v in arr)) / (len(arr) or 1)

    def attr(p):
        return max(40, min(99, 40 + (p - 1) * 30 / 49 if p < 50 else 70 + (p - 50) * 29 / 49))

    cols = {}
    for pid in [*prior_ids, *extra_ids]:
        mn25, m25, a25 = s25.get(pid, (0.0, 0.0, 0.0))
        mn26, m26, a26 = s26.get(pid, (0.0, 0.0, 0.0))
        mn, a = mn25 + mn26, a25 + a26
        c = {'min26': mn26, 'fg3m26': m26, 'fg3a26': a26, 'minAll': mn, 'ok': pid in prior and mn > 0}
        if c['ok']:
            acc = (THREE_K * prior[pid] + m26) / (THREE_K + a26)
            vol = a / mn * 36
            c.update(acc=acc, vol=vol, value=vol * (acc - rep))
        cols[pid] = c
    # extra_ids（名單上還沒出賽的人）只給值、不進池，已出賽者的百分位不受影響
    pool = [c['value'] for pid, c in cols.items() if pid in prior_ids and c['ok'] and c['minAll'] >= THREE_POOL_MIN]
    # 2026-10-30 使用者「3PT 不要封 99」：027b 頂端改走 E-101 百分位尾巴（同卡片 threeValue：top 開、bot 關），
    # 錨點取本季即時池（m26_anchors），不用 pool-027b 的凍結錨點（那是 E-123 難度調整值，量尺不同）
    an = m26_anchors(pool) if M27B_MODE and pool else None

    def attr_open(x):
        p = pct(x, pool)
        if an is not None and p >= 99:
            return m26_top_tail(x - an['r99'], an['S'])
        return attr(p)

    for c in cols.values():
        c['threeValue'] = attr_open(c['value']) if c['ok'] else None
    return cols, {'mu': mu, 'rep': rep, 'k': THREE_K, 'poolMin': THREE_POOL_MIN, 'poolSize': len(pool),
                  'leagueFG3M': m_all, 'leagueFG3A': a_all, 'topTail': an}


# ------------------------------------------------------------------ foulDraw（E-070 公式，CARD_MODE=022）
_FD = {}


def foul_draw_y(rec):
    """視窗觀測值：percentile_pool(0.75·z(FTA/36)+0.25·z(FTA/FGA))→attr()。常數取自 prior JSON 的 foulDrawFreeze
    （2025-26 池；card 0.2.2 建 foulDraw 時的 z 平均／標準差與池內合成值），不用 2026-27 資料重估。"""
    if not _FD:
        fz = load_json(PRIOR_CARD)['foulDrawFreeze']
        _FD.update(fz)
        _FD['ref'] = sorted(fz['poolComposite'])
    fz, smp = _FD, rec['sample']
    fta, fga, mn = float(smp['fta']), float(smp['fga']), float(smp['min'])
    z_vol = (fta / mn * 36.0 - fz['vol']['mean']) / fz['vol']['std']
    z_rate = (fta / fga - fz['rate']['mean']) / fz['rate']['std']
    comp = fz['wVol'] * z_vol + fz['wRate'] * z_rate
    ref = fz['ref']
    p = 100 * (sum(v < comp for v in ref) + .5 * sum(v == comp for v in ref)) / len(ref)
    return max(40.0, min(99.0, 40 + (p - 1) * 30 / 49 if p < 50 else 70 + (p - 50) * 29 / 49))


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
        # foulDraw（card 0.1.2 新欄）：020：y 用舊 drive 的同一個原始量（FTA/FGA 百分位，視窗 rec['drive']）；
        # 022／024（E-074，card 0.2.2 / E-070）：y＝百分位(0.75·z(FTA/36)+0.25·z(FTA/FGA))，常數凍結自 2025-26 池（foul_draw_y）。
        # 樣本／最小樣本／δ²／rel 沿用 drive 的；不重估。drive 本身（0.1.2 改 PBP 版）凍結。
        a = 'foulDraw'
        vals[a] = x0[a]
        if not (pc is None or 'drive' in undefined or a in frozen or rec is None
                or IC.sample_of(rec, 'drive') < SA.SEASON_MIN_SAMPLE['drive']):
            if M26_MODE:     # E-107：觀測值已由 m26_window_cards 用 pool-026 合併池＋尾巴算好
                y = C.usage_adjust({a: x0[a]}, rec, a, usg.get(pid, 0.0))
            elif NEW_PRIOR:
                y = C.usage_adjust({a: x0[a]}, {**rec, a: foul_draw_y(rec)}, a, usg.get(pid, 0.0))
            else:
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
    if M27_MODE:     # E-111：usage-2025-26-card027.json 的 anchors／rRepl（load_usage 已對 phase2.json UL6 核對）
        a = d['anchors']
        return [a['PR1'], a['PR50'], a['PR99']], d['rRepl']
    if CARD_MODE == '025':     # E-095：card 0.2.5（E-089 results.json 的 report_only.card.new）
        a = d['report_only']['card']['new']['anchors']
        return [a['PR1'], a['PR50'], a['PR99']], d['report_only']['card']['new']['r_repl']
    if CARD_MODE in ('024', '026'):     # E-091：card 0.2.4（E-084 results.json 的 card 段）；E-107：E-101 的 cards/e101/e084/results.json card 段
        a = d['card']['anchors']
        return [a['PR1'], a['PR50'], a['PR99']], d['card']['r_repl']
    a = d['anchors']['repl' if E064_MODE == 'G1' else 'main']
    return [a['PR1'], a['PR50'], a['PR99']], (d['rRepl_PR10_of_pred'] if E064_MODE == 'G1' else 0.0)


def e064_map(g, anc):
    p1, p50, p99 = anc
    return 40 + 30 * (g - p1) / (p50 - p1) if g <= p50 else 70 + 29 * (g - p50) / (p99 - p50)


def load_usage():
    """E-091：讀 usage-2025-26-card024.json，核對 payload sha256、card 0.2.4 ranking.csv sha256、r_repl／錨點。回傳 (usage {pid: 特徵}, coef, payloadSha256)。"""
    import hashlib
    doc = load_json(USAGE_FILE)
    body = json.dumps({'coef': doc['coef'], 'rRepl': doc['rRepl'], 'anchors': doc['anchors'], 'players': doc['players']},
                      ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    if hashlib.sha256(body.encode('utf-8')).hexdigest() != doc['payloadSha256']:
        raise SystemExit('usage-2025-26-card024.json payload sha256 不符')
    summ = load_json(CARD024_SUMMARY)
    if hashlib.sha256(FORMAL_RANKING.read_bytes()).hexdigest() != summ['ranking_csv_sha256']:
        raise SystemExit(f'{CARD_VERSION} ranking.csv sha256 與 summary.json 不符')
    if M27_MODE:     # E-111：錨點對 phase2.json reportOnly.anchors.UL6（差 ≤ 1e-9）；r_repl／錨點是 build_usage_027 重跑 UL6 pipeline 的值
        p2 = (load_json(E128_RB / 'work/cards-result.json')['anchors'] if M27B_MODE
              else load_json(UL_PHASE2)['reportOnly']['anchors']['UL6'])
        if max(abs(doc['anchors'][k] - p2[k]) for k in ('PR1', 'PR50', 'PR99')) > 1e-9:
            raise SystemExit('usage-2025-26-card027.json 的錨點與 phase2.json UL6 不一致')
        return {int(k): v for k, v in doc['players'].items()}, doc['coef'], doc['payloadSha256']
    res = load_json(E084_RESULTS)   # usage JSON 是 card 0.2.4 時建的；025 的 r_repl 不變，錨點另由 e064_anchors 讀
    if doc['rRepl'] != res['card']['r_repl'] or doc['anchors'] != res['card']['anchors']:
        raise SystemExit('usage JSON 的 r_repl／錨點與 e084 results.json 不一致')
    if CARD_MODE == '025' and doc['rRepl'] != load_json(E089_RESULTS)['report_only']['card']['new']['r_repl']:
        raise SystemExit('usage JSON 的 r_repl 與 E-089 results.json 不一致')
    return {int(k): v for k, v in doc['players'].items()}, doc['coef'], doc['payloadSha256']


def apply_usage(entries, usage, coef):
    """E-091：predNew = b0 + b1·p + b2·L + b3·a + b4·y + b5·v + b6·y·L + b7·v·L + b8·y·d·L（用人特徵凍結 2025-26，p＝賽中 C4 的 pred）；
    沒有凍結特徵（has=False 或不在 card 0.2.4）→ predNew = p。原 p 留在 predP，pred 換成 predNew 給 e064_convert。"""
    out = {}
    for pid, e in entries.items():
        if not isinstance(e, dict):      # ref 帶 '_capIterations'
            out[pid] = e
            continue
        u = usage.get(pid)
        if u is None or not u['has']:
            pn = e['pred']
        else:
            L, a, y, v, d = u['L'], u['a'], u['y'], u['v'], u['d']
            pn = (coef['b0'] + coef['b1_p'] * e['pred'] + coef['b2_L'] * L + coef['b3_a'] * a + coef['b4_y'] * y
                  + coef['b5_v'] * v + coef['b6_yL'] * y * L + coef['b7_vL'] * v * L + coef['b8_ydL'] * y * d * L)
        out[pid] = {**e, 'predP': e['pred'], 'pred': pn}
    return out


def team_badness(team_rows):
    """爛隊程度 d（R-097／R-098，同 run_c4_live_rookie.py:team_badness、卡 E-147）。{TEAM_ID: d}。
    nr＝累計得失分差／(GP+10)、wp＝(W+5)／(GP+10)、s＝0.7·(0.5+0.033·nr)+0.3·wp、d＝clip((0.40−s)/0.10, 0, 1)。"""
    acc = {}
    for r in team_rows:
        a = acc.setdefault(r['TEAM_ID'], [0, 0, 0.0])
        a[0] += 1
        a[1] += r['WL'] == 'W'
        a[2] += float(r['PLUS_MINUS'])
    out = {}
    for t, (gp, w, pm) in acc.items():
        s = 0.7 * (0.5 + 0.033 * pm / (gp + 10)) + 0.3 * (w + 5) / (gp + 10)
        out[t] = min(1.0, max(0.0, (0.40 - s) / 0.10))
    return out


def live_usage(usage, sd26):
    """R-098（2026-10-31 使用者「AB先上線」）：本季出賽過的人 d 換成最近一場所屬球隊的 team_badness；沒出賽的人照卡（N=0 → OVR＝先驗）。"""
    bad = team_badness(sd26['teamRows'])
    out = dict(usage)
    for pid, b in sd26['box'].items():
        u = usage.get(pid)
        if u is None or not b['rows']:
            continue
        t = max(b['rows'], key=lambda r: r['GAME_DATE'])['TEAM_ID']
        if t in bad:
            out[pid] = {**u, 'd': bad[t], 'dCard': u['d']}
    return out


def e064_convert(entries, mpg_by_pid, anc, r_repl=0.0, sat=False):
    """entries＝{pid: pw.predict 輸出}；回傳同結構但 ovr 改為每場 OVR（ovrPer36 保留原值）。
    g = (pred − r_repl)·MPG/36（G0：r_repl＝0 即 pred·MPG/36）；sat（CARD_MODE=025）：MPG/36 換成 W(MPG)。"""
    out = {}
    for pid, e in entries.items():
        if not isinstance(e, dict):      # ref 帶 '_capIterations'
            out[pid] = e
            continue
        if sat:
            g = (e['pred'] - r_repl) * sat_w(mpg_by_pid.get(pid, 0.0))
        else:
            g = (e['pred'] - r_repl) * mpg_by_pid.get(pid, 0.0) / 36.0
        out[pid] = {**e, 'ovrPer36': e['ovr'], 'g': g, 'ovr': e064_map(g, anc)}
    return out


def load_roster():
    """data/.../roster.json（commonallplayers 本季現役）→ {pid: 隊}；檔案不在就回空（退回只列已出賽）。"""
    path = DATA26 / 'roster.json'
    if not path.exists():
        print('沒有 roster.json：還沒出賽的球員不列入', file=sys.stderr)
        return {}
    return {int(r['PERSON_ID']): r['TEAM_ABBREVIATION'] for r in SA.result_set(path) if r['TEAM_ABBREVIATION']}


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
    usage, ucoef, usage_sha, mpg_card = {}, None, None, {}
    mpg_hat, mpg_win, w_mpg, mpg_nodata = {}, {}, {}, []
    if E064_MODE != 'off':
        # MPG0＝先驗卡那一季的 MIN／GP；ref（lastOVR 基準）一律用 MPG0 換成每場
        mpg0 = {pid: (float(c['observed']['MIN']) / float(c['observed']['GP']) if float(c['observed']['GP']) > 0 else 0.0)
                for pid, c in prior_cards.items()}
        anc064, r_repl064 = e064_anchors()
        if USAGE_MODE:
            # E-091：MPG0＝card 0.2.4 ranking.csv 的 mpg 欄（mpgAvail，依名字配對）；卡裡沒有的人維持上面的舊規則（MIN／GP）
            usage, ucoef, usage_sha = load_usage()
            for r_ in C.load_csv(FORMAL_RANKING):
                mpg_card.setdefault(r_['name'], float(r_['mpg']))
            if SAT:     # E-095：card 0.2.5 的 mpg 欄必須與 card 0.2.4 相同（預註冊 §2）
                m24 = {}
                for r_ in C.load_csv(CARD024_RANKING):
                    m24.setdefault(r_['name'], float(r_['mpg']))
                if m24 != mpg_card:
                    raise SystemExit(f'{CARD_VERSION} ranking 的 mpg 欄與 card 0.2.4 不同')
            for pid, c in prior_cards.items():
                if c['name'] in mpg_card:
                    mpg0[pid] = mpg_card[c['name']]
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
        if USAGE_MODE:
            res = apply_usage(res, live_usage(usage, sd26), ucoef)   # R-098：d 用當下球隊；ref／o1 仍用卡的 d
            ref = apply_usage(ref, usage, ucoef)
        res = e064_convert(res, mpg_hat, anc064, r_repl064, SAT)
        ref = e064_convert(ref, mpg0, anc064, r_repl064, SAT)

    # ---- 檢查 (a)：f=0、k 取上界 → 與上季卡逐球員 OVR 差 <0.5（c4_v5 T1）
    a1 = live_predict(delta2, rel_, undefined, frozen, f_force=0.0, k_max=True)
    o1 = pw.predict(a1)
    if E064_MODE != 'off':
        if USAGE_MODE:
            o1 = apply_usage(o1, usage, ucoef)
        o1 = e064_convert(o1, mpg0, anc064, r_repl064, SAT)
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
    roster = load_roster()
    team.update(roster)     # 現役名單優先（交易後還沒出賽也對）
    formal_rows = C.load_csv(FORMAL_RANKING)
    formal = {}
    for r in formal_rows:
        formal.setdefault(r['name'], float(r['ovr']))
    # 有先驗卡、在現役名單上但還沒出賽（傷兵等）：N=0，OVR＝先驗（f=0、無視窗資料）
    unplayed = [pid for pid in prior_cards if pid not in sd26['box'] and pid in roster and pid in res]
    tv_cols, tv_info = three_value_columns([pid for pid in sd26['box'] if prior_cards.get(pid) is not None], unplayed)
    rows, nopr = [], []
    boxes = list(sd26['box'].items()) + [(pid, {'name': prior_cards[pid]['name'], 'rows': []}) for pid in unplayed]
    for pid, b in boxes:
        pc = prior_cards.get(pid)
        gp = len(b['rows'])
        mins = sum(r['MIN'] for r in b['rows'])
        if pc is None:
            nopr.append({'playerId': pid, 'name': b['name'], 'team': team.get(pid, ''), 'N': gp,
                         'MIN26': round(mins, 1)})
            continue
        p = res[pid]
        row = {'ovr': r1(p['ovr']), 'name': pc['name'], 'pos': pc['pos'],
               'MIN': round(float(pc['observed']['MIN'])), 'predictedPer36': round(p.get('predP', p['pred']), 3),
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
        if USAGE_MODE:      # E-091：用人回歸後的每 36 預測（predictedPer36 仍是屬性迴歸 p）
            row['predNew'] = round(p['pred'], 4)
        if NEW_PRIOR:      # 顯示用（2025-26 先驗卡的值，賽中不更新；不進 OVR）
            row.update({'presDisplay': pc.get('presDisplay', ''), 'foulDisc': pc.get('foulDisc', '')})
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
    if NEW_PRIOR:
        head = head + ['presDisplay', 'foulDisc']
    if USAGE_MODE:
        head = head + ['predNew']
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
    not_played = [p for p in prior_cards if p not in prior_game_pids]   # 不在現役名單上（離隊、退休等）
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

    m26_info = None
    if M26_MODE:      # E-107：(L1) 卡內每人 ref OVR 對 card 0.2.6 ovr；026 範圍檢查（照開關）
        l1 = {prior_cards[p]['name']: ref[p]['ovr'] - formal[prior_cards[p]['name']] for p in attrs0
              if prior_cards[p]['name'] in formal}
        upd = [a for a in M26['attrs'] if a in C.UPD or a == 'foulDraw']
        out_of_range = [(prior_cards[p]['name'], a, attrs[p][a]) for p in attrs for a in upd
                        if not (m26_range(a)[0] - 1e-9 <= attrs[p][a] <= m26_range(a)[1] + 1e-9)]
        m26_info = {('pool027b' if M27B_MODE else 'pool027' if M27_MODE else 'pool026'): {'file': rel(POOL026), 'payloadSha256': M26['payloadSha256']},
                    ('L1_refVsCard027b' if M27B_MODE else 'L1_refVsCard027' if M27_MODE else 'L1_refVsCard026'): {
                        'n': len(l1), 'maxAbs': max(abs(v) for v in l1.values()),
                        'worst': sorted(l1.items(), key=lambda kv: -abs(kv[1]))[:5]},
                    'rangeCheck': {'attrs': upd, 'outOfRange': out_of_range[:20], 'nOutOfRange': len(out_of_range)},
                    'above99': sorted([(prior_cards[p]['name'], a, round(attrs[p][a], 2)) for p in attrs for a in upd
                                       if attrs[p][a] > 99 and p in w26], key=lambda t: -t[2])}
        if M27_MODE:      # E-111：UL 防守加成（凍結）對 card 0.2.7 defenseBonus；分區跳過數；stamina 不換尺
            pipe = pw.pipe
            ub = dict(zip(pipe.pids, m27_bonus_of(pipe)))
            fb = {r_['name']: float(r_['defenseBonus']) for r_ in formal_rows}
            dbon = [abs(round(ub[p], 3) - fb[prior_cards[p]['name']]) for p in pipe.pids if prior_cards[p]['name'] in fb]
            m26_info['ulBonus'] = {'defL': rel(DEF_L_PRIMARY), 'posMeanD': {k: float(v) for k, v in pipe._m27_posMeanD.items()},
                                   'vsCard027DefenseBonus3dp': {'n': len(dbon), 'maxAbs': float(max(dbon)),
                                                                'nMismatch': int(sum(bool(d > 1e-9) for d in dbon))},
                                   'refBonusEqualsUl': float(max(abs(ref[p]['bonus'] - ub[p]) for p in pipe.pids))}
            m26_info['zoneSkippedAreaMissing2pt'] = dict(M27_ZONE_DROPPED)
            m26_info['stamina'] = 'IC 單季映射（E-111 §1.3，不進合併池、不加尾巴）'

    # ---- meta.json
    inputs = {
        '2026-27 player-games': DATA26 / 'player-games.json', '2026-27 team-games': DATA26 / 'team-games.json',
        '2026-27 bio': DATA26 / 'bio.json', 'prior card': PRIOR_CARD, 'S* RAPM': RAPM_STAR,
        '2025-26 player-games': IC.TARGET_BOX, '2025-26 team-games': IC.TARGET_TEAM,
        '2025-26 bio': BIO25, 'threeValue prior (abilityC)': THREE_PRIOR, 'dependence-audit': IC.DEPENDENCE, 'formal ranking (cross-check)': FORMAL_RANKING,
        **({'usage features (E-091)': USAGE_FILE, 'e084 results (coef/r_repl/anchors)': E084_RESULTS, (CARD_VERSION + ' summary' if SAT else 'card 0.2.4 summary'): CARD024_SUMMARY,
           **({'e089 results (card 0.2.5 anchors)': E089_RESULTS} if CARD_MODE == '025' else {})}
           if USAGE_MODE else {}),
        **({('pool-027b (E-128)' if M27B_MODE else 'pool-027 (E-111)' if M27_MODE else 'pool-026 (E-107)'): POOL026} if M26_MODE else {}),
        **({'card 0.2.7 OVR summary (UL6 primary)': CARD_SUMMARY, 'def-L primary (UL bonus)': DEF_L_PRIMARY,
            'phase2.json (UL6 anchors)': UL_PHASE2} if M27_MODE and not M27B_MODE else {}),
        **({'card 0.2.7b OVR summary (rebase-027a e123a primary)': CARD_SUMMARY, 'def-L primary (UL bonus)': DEF_L_PRIMARY,
            'rebase-027a cards-result.json (anchors)': E128_RB / 'work/cards-result.json'} if M27B_MODE else {}),
        'reliability': V2.RELIABILITY if hasattr(V2, 'RELIABILITY') else None,
    }
    sha = {k: {'path': rel(v), 'sha256': C.sha256_file(v)} for k, v in inputs.items() if v}
    pbp_files = sorted(p.stem for p in (DATA26 / 'pbp').glob('*.json'))
    games = sorted({r['GAME_ID'] for r in sd26['teamRows']})
    meta = {
        'version': VERSION, 'cardMode': CARD_MODE, 'e064Mode': E064_MODE, 'e064Anchors': anc064, 'e064RRepl': r_repl064 if E064_MODE == 'G1' else None,
        'e064MpgNoDataPlayers': len(mpg_nodata) if E064_MODE == 'G1' else None, 'priorCard': CARD_VERSION, 'dataCutoff': cutoff,
        'dataFirstDate': min(r['GAME_DATE'] for b in sd26['box'].values() for r in b['rows']),
        'games': len(games), 'pbpGames': len(pbp_files), 'missingPbp': sorted(set(games) - set(pbp_files)),
        'gitHead': git_head(), 'start': 'S*', 'prior': PRIOR, 'target': TARGET, 'c': C_PARAM, 'G': G_GAMES,
        'frozenAttrs': frozen + list(IC.FROZEN_ATTRS), 'updatableAttrs': list(C.UPD) + ['foulDraw'],
        'delta2Undefined': undefined, 'delta2': delta2,
        'players': {'ranked': len(rows), 'noPrior': len(nopr), 'priorCardNotPlayed': len(not_played),
                    'rosterUnplayed': len(unplayed), 'rosterFile': bool(roster)},
        'foulDrawFreeze': ({k: v for k, v in load_json(PRIOR_CARD)['foulDrawFreeze'].items() if k != 'poolComposite'}
                           if NEW_PRIOR else None),
        **({'usage': {'file': rel(USAGE_FILE), 'payloadSha256': usage_sha, 'frozenAt': PRIOR, 'coef': ucoef,
                      'mpg0': 'card 0.2.4 ranking.csv mpg 欄（依名字配對；卡裡沒有的人退回 MIN／GP）',
                      'mpg0FromCard': sum(1 for pid, c in prior_cards.items() if c['name'] in mpg_card),
                      'mpg0Fallback': sum(1 for pid, c in prior_cards.items() if c['name'] not in mpg_card)}}
           if USAGE_MODE else {}),
        **({('e128' if M27B_MODE else 'e111' if M27_MODE else 'e107'): m26_info} if M26_MODE else {}),
        'inputs': sha, 'mapping2025_26': {'priors': mp['priors'], 'poolSize': mp['poolSize'],
                                          'boxPlayersDroppedNoBio': mp['boxPlayersDroppedNoBio'],
                                          'priorShotSampleFilled': [mp['priorShotSampleFilled'], mp['priorCards']]},
        'sanity': sanity,
        'threeValue': {**tv_info, 'formula': 'vol*(acc-rep); vol=合併(2025-26+2026-27)3PA/MIN*36; acc=(k*abilityC_2025-26+FG3M_2026-27)/(k+FG3A_2026-27)'
                       '（本季無出手難度資料，用原始命中）; rep=合併聯盟3P%-0.03; 池=合併MIN>=500且有先驗卡; 百分位→attr() 40-99，027b 下 PR≥99 走頂端尾巴（錨點＝即時池 r99、S）',
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
               f"兩段映射錨點 PR1/PR50/PR99＝{anc064[0]:.4f}/{anc064[1]:.4f}/{anc064[2]:.4f}（{CARD_VERSION} {'E-089 results.json 的 report_only.card.new（card 0.2.5）' if CARD_MODE == '025' else 'E-084 results.json 的 card 段' if CARD_MODE == '024' else ('P1 primary 的 pergame-summary.json' if CARD_MODE == '022' else 'summary.json')} 同組）。"
               f"MPG_hat = MPG0 + w·(本季場均分鐘 − MPG0)，w＝stamina 的 C4 w（stamina 最小樣本 1 場）；"
               f"沒有本季視窗紀錄的 {len(mpg_nodata)} 人（含沒出賽者，不在排名內）退回 MPG0。`ovrPer36` 是同一預測的每 36 分鐘 OVR。"),
        'G0': '- OVR 為每場（E-064 G0 試跑）：g = pred·MPG0/36，MPG_hat＝MPG0 不更新，錨點為平均基準。',
        'off': '- OVR 為每 36 分鐘（inseason 0.1.x 做法）。'}[E064_MODE]
    if NEW_PRIOR:
        fz = meta['foulDrawFreeze']
        ATTR_NOTE = (f"- card {('0.2.5' if SAT else '0.2.4') + '（能力值欄與 0.2.2 逐欄相同）' if USAGE_MODE else '0.2.2'} 的屬性處理（E-074，換版不重擬合）：先驗屬性 x0、屬性迴歸係數（card-0.2.2/cards/P1/primary/summary.json）{'取自 card 0.2.2' if USAGE_MODE else '、每場錨點與 r_repl 全部取自 card 0.2.2'}；"
                     f"pressure＝逼失誤 force（E-071 P1），賽中凍結；foulDraw 用 E-070 公式做 C4 更新：y＝百分位(0.75·z(FTA/36)＋0.25·z(FTA/FGA))，"
                     f"z 的平均／標準差與百分位對照母體凍結自 2025-26 池（GP≥30、MPG≥20，{fz['poolSize']} 人；FTA/36 mean {fz['vol']['mean']:.4f} std {fz['vol']['std']:.4f}、"
                     f"FTA/FGA mean {fz['rate']['mean']:.4f} std {fz['rate']['std']:.4f}），不用 2026-27 資料重估，收縮 k／δ²／rel 沿用 drive 的；"
                     f"drive（PBP 版）、onBall（E-060）、pressure、help、physique、heightInches 凍結。PRES 欄顯示 presDisplay、tooltip 列逼失誤與犯規紀律（2025-26，不進 OVR）。")
    else:
        ATTR_NOTE = '- card 0.1.2 的屬性處理：foulDraw 用舊 drive 的同一個原始量（FTA/FGA 百分位）做 C4 更新；drive（改 PBP 版）、onBall（E-060 重定義）、pressure、help、physique、heightInches 凍結。'
    if M26_MODE:
        ATTR_NOTE = ("- E-107（CARD_MODE=026，實驗中）：先驗 x0＝card 0.2.6 能力值（尾巴原樣、不夾 99）；屬性迴歸＝E-101 P1 primary 的 summary.json；"
                     "賽中觀測值改對 live/pool-026.json 的 2022-23～2025-26 四季合併池映射（百分位型 GP≥30 且 MPG≥20；命中率型 MIN≥500），"
                     "99 以上與 40 以下照 E-101 尾巴（開關照 E-090＋E-101 h1）；分區加 E-101 規則（Mid-Range 且 shotDistance<8 → short）；"
                     "foulDraw 合成值的 z 常數仍凍結自 2025-26，百分位改對合併池；drive、onBall、pressure、help、physique、heightInches 凍結。")
    if M27_MODE:
        ATTR_NOTE = ("- E-111（CARD_MODE=027，實驗中）：先驗 x0＝card 0.2.7 產生器的未四捨五入能力值（尾巴原樣、不夾 99）；屬性迴歸＝UL6 primary 的 summary.json；"
                     "賽中觀測值對 live/pool-027.json 的 2022-23～2025-26 四季合併池映射（百分位型 GP≥30 且 MPG≥20；命中率型 MIN≥500），"
                     "99 以上與 40 以下照 E-101 尾巴；分區照 E-101（有 area 欄的季 area 缺值的出手跳過、Mid-Range 且 shotDistance<8 → short）；"
                     "foulDraw 合併池用各季自己的 z、賽中視窗仍用 2025-26 凍結的 z；stamina 照單季映射（不換尺）；"
                     "drive、onBall、pressure、help、physique、heightInches 凍結；防守加成＝card 0.2.7 的 UL 值（凍結）。")
    if M27B_MODE:
        ATTR_NOTE = ("- E-128（CARD_MODE=027b，預設）：先驗 x0＝card 0.2.7b 產生器的未四捨五入能力值（尾巴原樣、不夾 99）；屬性迴歸＝rebase-027a e123a primary 的 summary.json；"
                     "賽中觀測值對 live/pool-027b.json 的合併池映射（pass 換 E-125 量×率合成值＋合併池，視窗不收縮、z 常數凍結自 2025-26 卡片端；其餘 8 欄同 pool-027），"
                     "99 以上與 40 以下照 E-101 尾巴；help 照 E-123 D1 尾巴（不夾 99）；drive、onBall、pressure、presDisplay、physique、heightInches 凍結；防守加成＝UL 值（同 027）。")
    if USAGE_MODE:
        OVR_NOTE += (f"\n- card 0.2.4 用人層（E-091，R-044 = 用人回歸＋當季 RAPM 目標）：p＝上面屬性迴歸的每 36 預測（`predictedPer36`，C4 照常更新），"
                     f"predNew＝b0 + b1·p + b2·L + b3·a + b4·y + b5·v + b6·y·L + b7·v·L + b8·y·d·L（`predNew` 欄）；"
                     f"L、a、y、v、d 與 has 旗標凍結在 2025-26 全季（`{USAGE_FILE.name}`，payload sha256 {usage_sha[:12]}…，年齡不加一歲），has=False 或不在卡內者 predNew＝p；"
                     f"係數 b0={ucoef['b0']:.4f}、b1={ucoef['b1_p']:.4f}（E-084 results.json）。MPG0＝card 0.2.4 ranking.csv 的 mpg 欄（mpgAvail，依名字配對），卡裡沒有的人退回 MIN／GP。"
                     + ("\n- E-095（CARD_MODE=025）：分鐘權重 mpg/36 改為飽和 W(mpg)=(1−e^(−mpg/15))/(1−e^(−36/15))（card 0.2.5，R-047），錨點／r_repl 取 E-089 results.json report_only.card.new。" if SAT else ''))
    if M27B_MODE:
        OVR_NOTE += f"\n- E-128：用人層係數、r_repl、錨點取 {rel(USAGE_FILE)}（rebase-027a e123a pipeline 重跑，錨點對 rebase-027a/work/cards-result.json 核對）；分鐘權重 W 同 card 0.2.5。"
    elif M27_MODE:
        OVR_NOTE += f"\n- E-111：用人層係數、r_repl、錨點取 {rel(USAGE_FILE)}（UL6 pipeline 重跑，錨點對 phase2.json UL6 核對）；分鐘權重 W 同 card 0.2.5。"
    elif M26_MODE:
        OVR_NOTE += f"\n- E-107：用人層係數、r_repl、錨點取 {rel(E084_RESULTS)} 的 card 段；分鐘權重 W 同 card 0.2.5。"
    md = f"""# {VERSION} 2026-27 即時結果（資料截至 {cutoff}）

- OVR：賽中 C4（{VERSION}），先驗 {CARD_VERSION}（live/{PRIOR_CARD.name}）；N = 該球員 2026-27 已打場數。
- 資料：{meta['dataFirstDate']}..{cutoff}、{len(games)} 場、{len(pbp_files)} 份 PBP；缺 PBP：{', '.join(meta['missingPbp']) or '無'}。
- git HEAD：`{meta['gitHead'][:12]}`；c={C_PARAM}（凍結）、G={G_GAMES}、f = min(N/{G_GAMES}, 1)。
- 排名 {len(rows)} 人（有先驗卡且已出賽，加上在現役名單上但還沒出賽的 {len(unplayed)} 人，N=0、OVR＝先驗）；沒有先驗卡 {len(nopr)} 人（`no-prior.csv`，不給 OVR）；有先驗卡、沒出賽也不在現役名單 {len(not_played)} 人（不列入）。
- N 分布：{', '.join(f'N={n}: {c} 人' for n, c in sorted(n_dist.items()))}。
- 3PT 欄 = threeValue（R-024，顯示用、不進 OVR）：vol＝合併（2025-26＋2026-27）3PA/MIN×36；acc＝(k·上季 abilityC＋本季 3PM)/(k＋本季 3PA)，k={THREE_K}（本季沒有出手難度資料，用原始命中）；rep＝合併聯盟 3P%（{tv_info['mu']:.4f}）−0.03；value＝vol×(acc−rep)，在合併 MIN≥500 且有先驗卡的 {tv_info['poolSize']} 人池內取百分位並套 attr()。`long` 欄仍在 ranking.csv 並進 OVR 計算，只是表格不顯示。
{ATTR_NOTE}
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

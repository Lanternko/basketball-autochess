"""Review snapshot: personal accuracy, team accuracy, card OVR top 20 (2025-26).

  python reports/status/status_snapshot.py

Writes status.json (everything), personal.json, team.json, top20.json, v55fix.json, trend.json, team_card.json (dashboard datasets) and status.md
next to this file, and the same four datasets (+ kpi.json) into dashboard_payload/ for direct upload.
Re-run after any model, board or card change; it only reads existing outputs.
Holdout ρ: E2/F2/G3/H1 come from reports/ovr-v58-holdout-2025-26/holdout.json; every other layer (sim boards, legacy, v53, blend,
B12/C1/D1) and the rho2k column come from reports/ovr-metrics-backfill-2025-26/backfill.json (run backfill.py first). If a file
is missing the cell shows 「未量測」. Also writes trend.json and team_card.json (+ team_card_teams.json) next to the other datasets.
"""
import csv, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
PAYLOAD = OUT / 'dashboard_payload'
HOLDOUT = 'reports/ovr-v58-holdout-2025-26/holdout.json'
BACKFILL = 'reports/ovr-metrics-backfill-2025-26/backfill.json'
NA = '未量測'  # 缺值一律顯示這個，不留空白
CIRC = 'ρRAPM 樣本內（align/封頂用 RAPM）'
BLEND_NOTE = 'RAPM 混合目標（α=0.5）→ ρRAPM 部分樣本內'
TEAM_NOTE = '卡片版本（v55–v58）只改顯示用 OVR，不影響模擬 winsMAE；卡片的球隊指標另列於 team_card.json'
EVAL_POSS = 5000
LOW_MIN, RAPM_FAR, BIGS = 1000, 100, {'C', 'PF'}
LATEST_SIM = 'v54'  # latest sim board measured
OFFICIAL_CARD = 'reports/card-0.1.1+E060-onball-targeting/primary/ranking.csv'  # 2026-10-28 起正式卡片 = card 0.1.2（= 0.1.1 + E-060 onBall）
C011_CARD = 'reports/ovr-v61-shrink-history-2025-26/ranking.csv'  # card 0.1.1（E-054+E-055），未曾正式發版
V58_CARD = 'reports/ovr-v58-card-2025-26/card-H1-m0/ranking.csv'  # 2026-10-21 ~ 10-28 正式卡片 = v58 H1-m0
THREE_VALUE = 'reports/card-0.1.1+E057-three-value/three-value.csv'  # E-057 threeValue（R-024：card 0.1.2 的 3PT 顯示欄；OVR 與模擬仍用 long）
CARD_EVAL = 'reports/card-0.1.1+E060-onball-targeting/evaluation.json'  # 0.1.1（label v61-shrink）與 0.1.2（label E060）的對 2K27 ρ
E2_CARD = 'reports/ovr-v55-card-E-2025-26/card-E2-lam0.4/ranking.csv'  # 2026-10-20 ~ 10-21 正式卡片
V53_CARD = 'reports/ovr-calibrated-2025-26/ranking.csv'
F2_CARD = 'reports/ovr-v56-card-defense-2025-26/card-F2-gamma0.5/ranking.csv'  # v56
G3_CARD = 'reports/ovr-v57-card-2025-26/card-G3-delta0.25/ranking.csv'  # v57
V55_CARDS = {'B12': 'reports/ovr-v55-finisher-fix-2025-26/card/B12/ranking.csv',
             'C1': 'reports/ovr-v55-card-origin-attr-2025-26/card-C1/ranking.csv',
             'D1': 'reports/ovr-v55-attr-deflate-2025-26/card/D1/ranking.csv',
             'E2': 'reports/ovr-v55-card-E-2025-26/card-E2-lam0.4/ranking.csv',
             'v58': V58_CARD}
V55_DESC = {'B12': '方向 B：吃餅長人禁區出手來源修正（模擬層）後重校卡片',
            'C1': '方向 1：自創禁區比例 s̃ 映成第 16 屬性 originShare 加進卡片回歸',
            'D1': '方向 2：屬性建構層 long 去膨脹（--attr-deflate）後重校卡片',
            'E2': '方向 E2：吃餅折扣 λ=0.4（禁區出手按非自創比例打折，PF/C 自創 ≥65 吸引包夾者豁免）'}
# 驗收：下修類看方向；不誤傷類只要卡片名次不低於 2K27 或 RAPM 其中一個的名次（兩者擇一准即可）
V55_CHECKS = [('Karlo Matković', '下修 ≥ 10 名', lambda a, b, ref: b - a >= 10),
              ('John Collins', '下修', lambda a, b, ref: b > a),
              ('Isaiah Stewart', '下修', lambda a, b, ref: b > a),
              ('Luka Garza', '下修', lambda a, b, ref: b > a),
              ('Neemias Queta', '名次 ≤ 2K27 或 RAPM 名次', lambda a, b, ref: b <= ref),
              ('Rudy Gobert', '名次 ≤ 2K27 或 RAPM 名次', lambda a, b, ref: b <= ref),
              ('Jalen Smith', '名次 ≤ 2K27 或 RAPM 名次', lambda a, b, ref: b <= ref)]


def spearman(a, b):
    return float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])


def rows(path):
    return list(csv.DictReader(open(ROOT / path, encoding='utf-8-sig')))


def load_holdout():
    try:
        return json.loads((ROOT / HOLDOUT).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def load_backfill():
    try:
        return json.loads((ROOT / BACKFILL).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def holdout_cell(holdout, key):
    """樣本外 ρ（淨值 / 防守）顯示文字；E2/F2/G3/H1 沿用 holdout.json；讀不到 = 未量測。"""
    try:
        a = holdout['cards'][key]['holdout_scale0.5']['avg']
        return f"{a['net']:.3f} / {a['def']:.3f}"
    except (KeyError, TypeError):
        return NA


def backfill_layer(backfill, key):
    return backfill.get('layers', {}).get(key)


def card_eval_2k(label):
    """card 0.1.1 / 0.1.2 的對 2K27 ρ（evaluation.json 候選表，label v61-shrink / E060）；讀不到 = None。"""
    try:
        d = json.loads((ROOT / CARD_EVAL).read_text(encoding='utf-8'))
        return next(c['rho2k'] for c in d['candidates'] if c['label'] == label)
    except (OSError, ValueError, StopIteration, KeyError):
        return None


def personal(rapm_by_id, rapm_by_name, holdout, backfill):
    out = []

    def add(layer, desc, scores, note='', src='', hold=None, bk=None, k2=None):
        b = backfill_layer(backfill, bk or hold)
        keep = [(s, r) for s, r in scores if r and float(r['pooledPoss']) >= EVAL_POSS]
        s = [k[0] for k in keep]
        out.append({'layer': layer, 'description': desc, 'players': len(keep),
                    'rhoNet': round(spearman(s, [float(r['pooledNet']) for _, r in keep]), 3),
                    'rhoDefense': round(spearman(s, [float(r['pooledD']) for _, r in keep]), 3),
                    'holdoutRho': holdout_cell(holdout, hold) if hold and holdout_cell(holdout, hold) != NA else (b['holdoutRho'] if b else NA),
                    'rho2k': round(k2, 3) if k2 is not None else (round(b['rho2k'], 3) if b else NA),
                    'note': note or f'無額外備註；來源 {src}，對全量 RAPM 計算'})
    sim = rows('reports/ovr-v53-shrinkage-2025-26/ranking-v2.csv')
    src = 'reports/ovr-v53-shrinkage-2025-26/ranking-v2.csv'
    add('模擬板 v53（原始）', '8 種子期望分差，位置置中每 36 分鐘', [(float(r['rawPer36']), rapm_by_id.get(r['playerId'])) for r in sim],
        '不讀 RAPM，樣本內即樣本外：同一份分數直接對 A 半、B 半 RAPM 各算一次 ρ 再平均（reports/ovr-metrics-backfill-2025-26）', src=src, bk='sim_v53_raw')
    add('模擬板 v53（收縮修正版）', '先發不收縮、替補收縮（已採用）', [(float(r['v2Per36']), rapm_by_id.get(r['playerId'])) for r in sim],
        '不讀 RAPM，樣本內即樣本外：同一份分數直接對 A 半、B 半 RAPM 各算一次 ρ 再平均（reports/ovr-metrics-backfill-2025-26）', src=src, bk='sim_v53_v2')
    sim = rows('reports/ovr-v54-shrinkage-2025-26/ranking-v2.csv')
    src = 'reports/ovr-v54-shrinkage-2025-26/ranking-v2.csv'
    add('模擬板 v54（原始）', '三分／禁區命中率改用可靠度加權收縮', [(float(r['rawPer36']), rapm_by_id.get(r['playerId'])) for r in sim],
        '不讀 RAPM，樣本內即樣本外：同一份分數直接對 A 半、B 半 RAPM 各算一次 ρ 再平均（reports/ovr-metrics-backfill-2025-26）', src=src, bk='sim_v54_raw')
    add('模擬板 v54（收縮修正版）', '同 v53 收縮規則', [(float(r['v2Per36']), rapm_by_id.get(r['playerId'])) for r in sim],
        '已收束；球隊層 2025-26 勝場 MAE 變差，未切換對局資料，卡片板仍為 v53 校準；不讀 RAPM，樣本內即樣本外：同一份分數直接對 A 半、B 半 RAPM 各算一次 ρ 再平均（reports/ovr-metrics-backfill-2025-26）', src=src, bk='sim_v54_v2')
    add('卡片 OVR（正式卡片板，card 0.1.2）', 'card 0.1.1（v61 收縮歷史，E-054+E-055）+ E-060 onBall 對位目標（2026-10-28 使用者裁定發版）（遊戲本體不讀取任何 OVR）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(OFFICIAL_CARD)],
        f'{CIRC}；樣本外 ρ（A/B 半 RAPM）尚未量測，不以 v58 數字代替；對 2K27 ρ 取 evaluation.json 的 E060 值；來源 card-0.1.1+E060-onball-targeting/primary', src=OFFICIAL_CARD, k2=card_eval_2k('E060'))
    add('卡片 OVR card 0.1.1（v61 收縮歷史）', 'v58 H1-m0 之後的 E-054+E-055（收縮歷史）卡片；未曾正式發版，直接併入 0.1.2',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(C011_CARD)],
        f'{CIRC}；未曾正式發版（2026-10-28 與 E-060 一併發為 card 0.1.2）；樣本外 ρ 未量測；對 2K27 ρ 取 evaluation.json 的 v61-shrink 值', src=C011_CARD, k2=card_eval_2k('v61-shrink'))
    add('卡片 OVR v58 H1-m0（前正式版）', 'v57 G3（γ=1.0、δ=0.25：防守加分 + 往 RAPM align）再加上限：單人總 lift 不得超過其 RAPM 名次（margin=0）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(V58_CARD)],
        f'2026-10-28 由 card 0.1.2 取代；{CIRC}；樣本外 ρ 為 A/B 半場對調平均（ovr-v58-holdout-2025-26/report.md）；19/19 硬門檻全過；對 2K27 ρ .537；前十長人僅 Wemby/Giannis/Jokić/Chet（皆為 v58 當時數字）', src=V58_CARD, hold='H1')
    add('卡片 OVR v57 G3（γ=1.0、δ=0.25）', 'E2 之上加防守加分（γ=1.0，全位置、PR 90–96 漸減）+ 往 RAPM align δ=0.25，無封頂（v58 的前身）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(G3_CARD)], f'{CIRC}；v58 加封頂後樣本外 ρ 幾乎不變；v58 已於 2026-10-28 由 card 0.1.2 取代', src=G3_CARD, hold='G3')
    add('卡片 OVR v56 F2（PF/C 防守加分 γ=0.5）', 'E2 之上只對 PF/C 加防守加分，無 align、無封頂',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(F2_CARD)], 'ρRAPM 部分樣本內（防守加分用 RAPM pooledD，另有 RAPM 混合目標）', src=F2_CARD, hold='F2')
    add('卡片 OVR v55 E2（前正式版）', '吃餅折扣 λ=0.4（PF/C 自創 ≥65 豁免）後重校，目標同 v53：模擬與 RAPM 混合 α=0.5',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(E2_CARD)], f'2026-10-21 由 v58 H1-m0 取代（v58 於 10-28 由 card 0.1.2 取代）；{BLEND_NOTE}', src=E2_CARD, hold='E2')
    add('卡片 OVR v53（前正式版）', '能力值公式校準到模擬與 RAPM 混合目標，α=0.5，見 ovr-blended-2025-26/dataflow.md',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(V53_CARD)],
        f'2026-10-20 由 E2 取代（E2 再於 10-21 由 v58 H1-m0 取代，v58 於 10-28 由 card 0.1.2 取代）；{BLEND_NOTE}；樣本外為 backfill 以 A/B 半 RAPM 重擬合（calibrate.py 複本加 --rapm，全量重現 OVR 最大差 0.0）', src=V53_CARD, hold='v53')
    legacy = rows('reports/ovr-calibrated-2025-26/legacy-sim-only/ranking.csv')
    add('卡片 OVR（舊版，sim-only）', '能力值公式校準到 v53 模擬，α=0（已被正式卡片板取代）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in legacy], f'目標不含 RAPM，ρRAPM 為純樣本外（全量 RAPM）；不讀 RAPM，樣本內即樣本外：同一份分數直接對 A 半、B 半 RAPM 各算一次 ρ 再平均（reports/ovr-metrics-backfill-2025-26）',
        src='reports/ovr-calibrated-2025-26/legacy-sim-only/ranking.csv', bk='legacy')
    blend = rows('reports/ovr-blended-2025-26/ranking.csv')
    add('卡片 OVR（混合 α=0.5）', '校準目標 = 模擬與 RAPM 各半（與正式卡片板同一組數字，來源腳本不同）', [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in blend],
        '目標含 RAPM，樣本內 ρ 偏高；blend.py 與 calibrate.py --alpha 0.5 輸出逐名相同，樣本外沿用 v53 的 A/B 半重擬合（backfill）', src='reports/ovr-blended-2025-26/ranking.csv', bk='blend')
    for key, desc in V55_DESC.items():
        if key in ('E2', 'v58'):
            continue
        add(f'卡片 OVR 實驗 {key}（未採用）', desc, [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(V55_CARDS[key])],
            f'Karlo 未過，不採用；{BLEND_NOTE}；樣本外為 backfill 以 A/B 半 RAPM 重擬合', src=V55_CARDS[key], bk=key)
    return out


def v55fix(rapm_by_name):
    """7-player acceptance table for the v55 card experiments vs the official v53 card."""
    ranks = {k: {r['name']: int(r['rank']) for r in rows(p)} for k, p in {'v53': V53_CARD, **V55_CARDS}.items()}
    rank2k = {r['name']: float(r['rank2k']) for r in rows('reports/ovr-v55-2k27-compare/merged.csv') if r['rank2k']}
    pool = sorted((r for r in rapm_by_name.values() if float(r['pooledPoss']) >= EVAL_POSS), key=lambda r: -float(r['pooledNet']))
    rapm_rank = {r['name']: i + 1 for i, r in enumerate(pool)}
    out = []
    for name, cond, ok in V55_CHECKS:
        base = ranks['v53'][name]; ref = max(rank2k[name], rapm_rank.get(name, 0))
        row = {'name': name, 'condition': cond, 'v53': base, 'rank2k': rank2k[name], 'rapmRank': rapm_rank.get(name, '—')}
        for k in V55_CARDS:
            row[k] = ranks[k][name]; row[k + 'Pass'] = ok(base, ranks[k][name], ref)
        out.append(row)
    return out


def team():
    chart = json.loads((ROOT / 'reports/model-evolution-20261016/chart-data.json').read_text(encoding='utf-8'))
    out = [{'version': f'v{v}', 'order': int(v), 'winsMAE': round(m['winsMAE'], 2), 'netRMSE': round(m['netRMSE'], 3),
            'ptsMAE': round(m['pts'], 2), 'source': 'model-evolution-20261016', 'measured': True}
           for v, m in chart['team'].items() if v != 'control']
    seen = {r['version'] for r in out}
    for v in (46, 47, 48, 49):
        d = json.loads((ROOT / f'reports/player-impact-v{v}/2025-26-scores.json').read_text(encoding='utf-8'))
        for c in d['cells']:
            if c['variant'] not in seen:
                m = c['teamMetrics']; seen.add(c['variant'])
                out.append({'version': c['variant'], 'order': int(c['variant'][1:]), 'winsMAE': round(m['winsMAE'], 2),
                            'netRMSE': round(m['netRMSE'], 3), 'ptsMAE': NA, 'source': f'player-impact-v{v}', 'measured': True})
    v53 = json.loads((ROOT / 'reports/player-impact-v53-team/scores.json').read_text(encoding='utf-8'))
    m = next(c['teamMetrics'] for c in v53['cells'] if c['season'] == '2025-26' and c['variant'] == 'v53')
    out.append({'version': 'v53', 'order': 53, 'winsMAE': round(m['winsMAE'], 2), 'netRMSE': round(m['netRMSE'], 3), 'ptsMAE': NA,
                'source': 'player-impact-v53-team（壓迫係數為樣本內）', 'measured': True})
    v54 = json.loads((ROOT / 'reports/player-impact-v54-team/scores.json').read_text(encoding='utf-8'))
    m = next(c['teamMetrics'] for c in v54['cells'] if c['season'] == '2025-26' and c['variant'] == 'v54')
    out.append({'version': 'v54', 'order': 54, 'winsMAE': round(m['winsMAE'], 2), 'netRMSE': round(m['netRMSE'], 3), 'ptsMAE': NA,
                'source': 'player-impact-v54-team（未採用）', 'measured': True})
    return sorted(out, key=lambda r: r['order'])


TREND = [('舊版 sim-only', 'legacy', 1, True), ('v53', 'v53', 2, True), ('E2 (v55)', 'E2', 3, True), ('F2 (v56)', 'F2', 4, True),
         ('G3 (v57)', 'G3', 5, True), ('H1 (v58)', 'H1', 6, True), ('card 0.1.1', 'c011', 7, False), ('card 0.1.2', 'c012', 8, True),
         ('B12', 'B12', 9, False), ('C1', 'C1', 10, False), ('D1', 'D1', 11, False)]
TREND_LAYER = {'legacy': '卡片 OVR（舊版，sim-only）', 'v53': '卡片 OVR v53（前正式版）', 'E2': '卡片 OVR v55 E2（前正式版）',
               'F2': '卡片 OVR v56 F2（PF/C 防守加分 γ=0.5）', 'G3': '卡片 OVR v57 G3（γ=1.0、δ=0.25）', 'H1': '卡片 OVR v58 H1-m0（前正式版）', 'c011': '卡片 OVR card 0.1.1（v61 收縮歷史）', 'c012': '卡片 OVR（正式卡片板，card 0.1.2）',
               'B12': '卡片 OVR 實驗 B12（未採用）', 'C1': '卡片 OVR 實驗 C1（未採用）', 'D1': '卡片 OVR 實驗 D1（未採用）'}


def trend(personal_rows, backfill, holdout):
    """卡片版本趨勢：樣本內／樣本外／2K27 ρ。B12/C1/D1 是 v55 期間未採用的分支實驗，order 排在主線之後（adopted=false）。"""
    by_layer = {r['layer']: r for r in personal_rows}
    out = []
    for version, key, order, adopted in TREND:
        row = by_layer.get(TREND_LAYER[key]) or next((r for r in personal_rows if r['layer'].startswith(TREND_LAYER[key])), None)
        b = backfill_layer(backfill, key)
        try:
            h = holdout['cards'][key]['holdout_scale0.5']['avg']; net, df = h['net'], h['def']
        except (KeyError, TypeError):
            net, df = (b['out']['net'], b['out']['def']) if b else (None, None)
        out.append({'version': version, 'order': order, 'adopted': adopted, 'rhoNetIn': row['rhoNet'] if row else None,
                    'rhoNetOut': None if net is None else round(net, 3), 'rhoDefOut': None if df is None else round(df, 3),
                    'rho2k': round(b['rho2k'], 3) if b else (row['rho2k'] if row and row['rho2k'] != NA else None)})
    return out


def team_card(backfill):
    """卡片球隊指標：球隊名單依 2025-26 上場分鐘加權的平均卡片 OVR vs 實際每場分差（30 隊）。與模擬 winsMAE 分開。"""
    tc = backfill.get('teamCard')
    if not tc:
        return [], []
    names = {k: next((t for v, kk, o, a in TREND if kk == k for t in [v]), k) for k in {c['card'] for c in tc['cards']}}
    order = {kk: (o, a) for v, kk, o, a in TREND}
    rows_ = [{'version': names[c['card']], 'order': order[c['card']][0], 'adopted': order[c['card']][1], 'teams': c['teams'],
              'pearsonR': round(c['pearsonR'], 3), 'spearmanRho': round(c['spearmanRho'], 3), 'source': tc['source']} for c in tc['cards']]
    return sorted(rows_, key=lambda r: r['order']), tc['teams']


def three_value_by_name():
    # three-value.csv 以 playerId 為鍵；正式卡 ranking.csv 沒有 playerId，改用姓名對（兩邊 582 人姓名皆唯一且完全對上）。對不上的給 None。
    return {r['name']: float(r['tv_main']) for r in rows(THREE_VALUE)}


def top20(rapm_by_name):
    card = rows(OFFICIAL_CARD)
    tv = three_value_by_name()
    sim = {r['name']: int(r['rank']) for r in rows('reports/ovr-v54-shrinkage-2025-26/ranking-v2.csv')}
    pool = sorted((r for r in rapm_by_name.values() if float(r['pooledPoss']) >= EVAL_POSS), key=lambda r: -float(r['pooledNet']))
    rapm_rank = {r['name']: i + 1 for i, r in enumerate(pool)}
    out = []
    for r in card[:20]:
        rr = rapm_rank.get(r['name']); flags = []
        if int(r['MIN']) < LOW_MIN: flags.append('低分鐘')
        if rr is None: flags.append('RAPM 樣本不足')
        elif rr > RAPM_FAR: flags.append('RAPM 差距大')
        if r['pos'] in BIGS: flags.append('長人')
        out.append({'rank': int(r['rank']), 'name': r['name'], 'pos': r['pos'], 'ovr': float(r['ovr']), 'minutes': int(r['MIN']),
                    'threeValue': round(tv[r['name']], 1) if r['name'] in tv else None,
                    'simRank': sim.get(r['name'], '—'), 'rapmRank': rr if rr is not None else '—', 'flags': '、'.join(flags) or '—'})
    return out, len(pool)


def kpi(holdout, personal_rows):
    """頂部 KPI；正式卡片 = card 0.1.2。樣本外 ρ 尚未量測（顯示未量測，不拿 v58 代替）。遊戲本體不讀 OVR，所以標籤是「正式卡片」而非「遊戲現用」。"""
    def cell(key, field):
        try:
            return holdout['cards'][key]['holdout_scale0.5']['avg'][field]
        except (KeyError, TypeError):
            return None
    fmt = lambda v: NA if v is None else f'{v:.3f}'
    row = lambda name: next((r for r in personal_rows if name in r['layer']), {})
    inS = f"{row('card 0.1.2')['rhoNet']:.3f}" if row('card 0.1.2') else NA
    k2 = row('card 0.1.2').get('rho2k', NA)
    k2 = fmt(k2) if not isinstance(k2, str) else k2
    k2old = row('v58 H1-m0（前').get('rho2k', NA)
    return [{'label': '正式卡片 card 0.1.2 樣本外 ρ（淨值）', 'value': NA,
             'sub': f'A/B 半 RAPM 樣本外尚未量測；樣本內 {inS}（循環）；前正式版 v58 H1-m0 為 {fmt(cell("H1", "net"))}（不同卡片，僅供參考）'},
            {'label': '正式卡片 card 0.1.2 樣本外 ρ（防守）', 'value': NA, 'sub': f'尚未量測；v58 H1-m0 為 {fmt(cell("H1", "def"))}（僅供參考）'},
            {'label': '正式卡片 card 0.1.2 對 2K27 ρ（外部基準）', 'value': k2,
             'sub': f"v58 H1-m0 {k2old if isinstance(k2old, str) else fmt(k2old)}；來源 {CARD_EVAL}（E060）；2K27 不參與擬合"}]


def md(snap):
    L = [f"# 審查表（{snap['generatedAt'][:10]}）", '', f"模擬版本 {LATEST_SIM}。由 `reports/status/status_snapshot.py` 產生。", '',
         '## 重點（KPI）', '', '| ' + ' | '.join(k['label'] for k in snap['kpi']) + ' |', '|' + '---:|' * len(snap['kpi']),
         '| ' + ' | '.join(f"**{k['value']}**" for k in snap['kpi']) + ' |', '', *[f"- {k['label']}：{k['sub']}" for k in snap['kpi']], '',
         f"## 個人準確度（RAPM，pooledPoss ≥ {EVAL_POSS}）", '',
         '樣本外 ρ = 只用 A 半（gameId 偶數）RAPM 擬合的卡片對 B 半 RAPM 的 ρ，再對調取平均（`reports/ovr-v58-holdout-2025-26/report.md`）；不讀 RAPM 的層（模擬板、舊版 sim-only）直接對 A／B 半 RAPM 各算一次再平均；讀 RAPM 的卡片層（v53／混合／B12／C1／D1）以 A／B 半重擬合（`reports/ovr-metrics-backfill-2025-26/`）；人群 = 評估半 pooledPoss ≥ 2500 的共同球員（約 408 人，各層共用）。對 2K27 ρ 的人群 = 所有層共有且有 2K 值的 575 人。', '',
         '| 層 | 人數 | 淨值 ρ（全量 RAPM） | 防守 ρ（全量 RAPM） | 樣本外 ρ（淨值 / 防守） | 對 2K27 ρ | 備註 |', '|---|---:|---:|---:|---:|---:|---|']
    L += [f"| {r['layer']} | {r['players']} | {r['rhoNet']:.3f} | {r['rhoDefense']:.3f} | {r['holdoutRho']} | {r['rho2k'] if isinstance(r['rho2k'], str) else format(r['rho2k'], '.3f')} | {r['note']} |" for r in snap['personal']]
    L += ['', '## 球隊準確度（30 隊、全季）', '', f"說明：{TEAM_NOTE}。球隊 winsMAE 只來自模擬模型版本（v53/v54 等）。", '',
          '| 版本 | 勝場 MAE | 淨分 RMSE | 得分 MAE | 來源 |', '|---|---:|---:|---:|---|']
    f = lambda v, p: v if isinstance(v, str) else f'{v:.{p}f}'
    L += [f"| {r['version']} | {f(r['winsMAE'], 2)} | {f(r['netRMSE'], 3)} | {f(r['ptsMAE'], 2)} | {r['source']} |" for r in snap['team']]
    L += ['', '## 卡片球隊指標（30 隊、2025-26）', '',
          '各隊名單依 2025-26 上場分鐘加權的平均卡片 OVR，對實際每場分差（`data/season-league.json` 的 PLUS_MINUS / GP）。與上表模擬 winsMAE 不同口徑；全量卡片、樣本內（卡片的 RAPM 目標含本季比賽），不可與模擬 winsMAE 比較。', '',
          '| 卡片 | 隊數 | Pearson r | Spearman ρ | 採用 |', '|---|---:|---:|---:|---|']
    L += [f"| {r['version']} | {r['teams']} | {r['pearsonR']:.3f} | {r['spearmanRho']:.3f} | {'是' if r['adopted'] else '否'} |" for r in snap['teamCard']]
    L += ['', '## 卡片版本趨勢', '', '| 版本 | 序 | 採用 | 樣本內 ρ 淨值 | 樣本外 ρ 淨值 | 樣本外 ρ 防守 | 對 2K27 ρ |', '|---|---:|---|---:|---:|---:|---:|']
    g = lambda v: '—' if v is None else f'{v:.3f}'
    L += [f"| {r['version']} | {r['order']} | {'是' if r['adopted'] else '否'} | {g(r['rhoNetIn'])} | {g(r['rhoNetOut'])} | {g(r['rhoDefOut'])} | {g(r['rho2k'])} |" for r in snap['trend']]
    L += ['', f"## 卡片 OVR 前 20（RAPM 名次在 {snap['rapmPool']} 人中）", '', '| # | 球員 | 位置 | OVR | 3PT | 分鐘 | 模擬名次 | RAPM 名次 | 旗標 |',
          '|---:|---|---|---:|---:|---:|---:|---:|---|']
    L += [f"| {r['rank']} | {r['name']} | {r['pos']} | {r['ovr']:.1f} | {'' if r['threeValue'] is None else format(r['threeValue'], '.1f')} | {r['minutes']} | {r['simRank']} | {r['rapmRank']} | {r['flags']} |" for r in snap['top20']]
    mark = lambda r, k: f"{r[k]}{'' if r[k + 'Pass'] else ' ✗'}"
    L += ['', '## v55 卡片修正各方向（7 人驗收，v53 名次 → 實驗名次，✗ = 未過；E2 曾為正式卡片，10-21 ~ 10-28 正式卡片為 v58 H1-m0，10-28 起為 card 0.1.2）', '',
          '| 球員 | 條件 | 2K27 | RAPM | v53 | ' + ' | '.join(V55_CARDS) + ' |', '|---|---|---:|---:|---:|' + '---:|' * len(V55_CARDS)]
    L += [f"| {r['name']} | {r['condition']} | {r['rank2k']:g} | {r['rapmRank']} | {r['v53']} | " + ' | '.join(mark(r, k) for k in V55_CARDS) + ' |' for r in snap['v55fix']]
    return '\n'.join(L) + '\n'


def main():
    rapm = rows('reports/impact-rapm/rapm.csv')
    by_id = {r['playerId']: r for r in rapm}; by_name = {r['name']: r for r in rapm}
    t20, pool = top20(by_name)
    holdout = load_holdout()
    backfill = load_backfill()
    personal_rows = personal(by_id, by_name, holdout, backfill)
    tcard, tcard_teams = team_card(backfill)
    snap = {'generatedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'simVersion': LATEST_SIM, 'evalPoss': EVAL_POSS,
            'rapmPool': pool, 'kpi': kpi(holdout, personal_rows), 'teamNote': TEAM_NOTE, 'personal': personal_rows, 'team': team(),
            'top20': t20, 'v55fix': v55fix(by_name), 'trend': trend(personal_rows, backfill, holdout), 'teamCard': tcard, 'teamCardTeams': tcard_teams}
    PAYLOAD.mkdir(exist_ok=True)
    for k in ('personal', 'team', 'top20', 'v55fix', 'trend'):
        for d in (OUT, PAYLOAD):
            (d / f'{k}.json').write_text(json.dumps(snap[k], ensure_ascii=False, indent=1), encoding='utf-8')
    for d in (OUT, PAYLOAD):
        (d / 'team_card.json').write_text(json.dumps(snap['teamCard'], ensure_ascii=False, indent=1), encoding='utf-8')
        (d / 'team_card_teams.json').write_text(json.dumps(snap['teamCardTeams'], ensure_ascii=False, indent=1), encoding='utf-8')
    (PAYLOAD / 'kpi.json').write_text(json.dumps(snap['kpi'], ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.json').write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.md').write_text(md(snap), encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    print(md(snap))


if __name__ == '__main__':
    main()

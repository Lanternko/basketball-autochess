"""Review snapshot: personal accuracy, team accuracy, card OVR top 20 (2025-26).

  python reports/status/status_snapshot.py

Writes status.json (everything), personal.json, team.json, top20.json, v55fix.json (dashboard datasets) and status.md
next to this file, and the same four datasets (+ kpi.json) into dashboard_payload/ for direct upload.
Re-run after any model, board or card change; it only reads existing outputs.
Holdout ρ comes from reports/ovr-v58-holdout-2025-26/holdout.json; if it is missing the column shows 「未量測」.
"""
import csv, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
PAYLOAD = OUT / 'dashboard_payload'
HOLDOUT = 'reports/ovr-v58-holdout-2025-26/holdout.json'
NA = '未量測'  # 缺值一律顯示這個，不留空白
CIRC = 'ρRAPM 樣本內（align/封頂用 RAPM）'
BLEND_NOTE = 'RAPM 混合目標（α=0.5）→ ρRAPM 部分樣本內'
TEAM_NOTE = '卡片版本（v55–v58）只改顯示用 OVR，不影響模擬 winsMAE'
EVAL_POSS = 5000
LOW_MIN, RAPM_FAR, BIGS = 1000, 100, {'C', 'PF'}
LATEST_SIM = 'v54'  # latest sim board measured
OFFICIAL_CARD = 'reports/ovr-v58-card-2025-26/card-H1-m0/ranking.csv'  # 2026-10-21 起正式卡片 = v58 H1-m0
E2_CARD = 'reports/ovr-v55-card-E-2025-26/card-E2-lam0.4/ranking.csv'  # 2026-10-20 ~ 10-21 正式卡片
V53_CARD = 'reports/ovr-calibrated-2025-26/ranking.csv'
F2_CARD = 'reports/ovr-v56-card-defense-2025-26/card-F2-gamma0.5/ranking.csv'  # v56
G3_CARD = 'reports/ovr-v57-card-2025-26/card-G3-delta0.25/ranking.csv'  # v57
V55_CARDS = {'B12': 'reports/ovr-v55-finisher-fix-2025-26/card/B12/ranking.csv',
             'C1': 'reports/ovr-v55-card-origin-attr-2025-26/card-C1/ranking.csv',
             'D1': 'reports/ovr-v55-attr-deflate-2025-26/card/D1/ranking.csv',
             'E2': 'reports/ovr-v55-card-E-2025-26/card-E2-lam0.4/ranking.csv',
             'v58': 'reports/ovr-v58-card-2025-26/card-H1-m0/ranking.csv'}
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


def holdout_cell(holdout, key):
    """樣本外 ρ（淨值 / 防守）顯示文字；讀不到或該卡無半份重擬合版 = 未量測。"""
    try:
        a = holdout['cards'][key]['holdout_scale0.5']['avg']
        return f"{a['net']:.3f} / {a['def']:.3f}"
    except (KeyError, TypeError):
        return NA


def personal(rapm_by_id, rapm_by_name, holdout):
    out = []

    def add(layer, desc, scores, note='', src='', hold=None):
        keep = [(s, r) for s, r in scores if r and float(r['pooledPoss']) >= EVAL_POSS]
        s = [k[0] for k in keep]
        out.append({'layer': layer, 'description': desc, 'players': len(keep),
                    'rhoNet': round(spearman(s, [float(r['pooledNet']) for _, r in keep]), 3),
                    'rhoDefense': round(spearman(s, [float(r['pooledD']) for _, r in keep]), 3),
                    'holdoutRho': holdout_cell(holdout, hold) if hold else NA,
                    'note': note or f'無額外備註；來源 {src}，對全量 RAPM 計算（樣本外欄僅卡片有）'})
    sim = rows('reports/ovr-v53-shrinkage-2025-26/ranking-v2.csv')
    src = 'reports/ovr-v53-shrinkage-2025-26/ranking-v2.csv'
    add('模擬板 v53（原始）', '8 種子期望分差，位置置中每 36 分鐘', [(float(r['rawPer36']), rapm_by_id.get(r['playerId'])) for r in sim], src=src)
    add('模擬板 v53（收縮修正版）', '先發不收縮、替補收縮（已採用）', [(float(r['v2Per36']), rapm_by_id.get(r['playerId'])) for r in sim], src=src)
    sim = rows('reports/ovr-v54-shrinkage-2025-26/ranking-v2.csv')
    src = 'reports/ovr-v54-shrinkage-2025-26/ranking-v2.csv'
    add('模擬板 v54（原始）', '三分／禁區命中率改用可靠度加權收縮', [(float(r['rawPer36']), rapm_by_id.get(r['playerId'])) for r in sim], src=src)
    add('模擬板 v54（收縮修正版）', '同 v53 收縮規則', [(float(r['v2Per36']), rapm_by_id.get(r['playerId'])) for r in sim],
        '已收束；球隊層 2025-26 勝場 MAE 變差，未切換對局資料，卡片板仍為 v53 校準', src=src)
    add('卡片 OVR（正式卡片板，v58 H1-m0）', 'v57 G3（γ=1.0、δ=0.25：防守加分 + 往 RAPM align）再加上限：單人總 lift 不得超過其 RAPM 名次（margin=0）（遊戲本體不讀取任何 OVR）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(OFFICIAL_CARD)],
        f'{CIRC}；樣本外 ρ 為 A/B 半場對調平均（ovr-v58-holdout-2025-26/report.md）；19/19 硬門檻全過；對 2K27 ρ .537；前十長人僅 Wemby/Giannis/Jokić/Chet', src=OFFICIAL_CARD, hold='H1')
    add('卡片 OVR v57 G3（γ=1.0、δ=0.25）', 'E2 之上加防守加分（γ=1.0，全位置、PR 90–96 漸減）+ 往 RAPM align δ=0.25，無封頂（v58 的前身）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(G3_CARD)], f'{CIRC}；v58 加封頂後樣本外 ρ 幾乎不變', src=G3_CARD, hold='G3')
    add('卡片 OVR v56 F2（PF/C 防守加分 γ=0.5）', 'E2 之上只對 PF/C 加防守加分，無 align、無封頂',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(F2_CARD)], 'ρRAPM 部分樣本內（防守加分用 RAPM pooledD，另有 RAPM 混合目標）', src=F2_CARD, hold='F2')
    add('卡片 OVR v55 E2（前正式版）', '吃餅折扣 λ=0.4（PF/C 自創 ≥65 豁免）後重校，目標同 v53：模擬與 RAPM 混合 α=0.5',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(E2_CARD)], f'2026-10-21 由 v58 H1-m0 取代；{BLEND_NOTE}', src=E2_CARD, hold='E2')
    add('卡片 OVR v53（前正式版）', '能力值公式校準到模擬與 RAPM 混合目標，α=0.5，見 ovr-blended-2025-26/dataflow.md',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(V53_CARD)],
        f'2026-10-20 由 E2 取代（E2 再於 10-21 由 v58 H1-m0 取代）；{BLEND_NOTE}；校準腳本無法半份重擬合故樣本外未量測', src=V53_CARD, hold='v53')
    legacy = rows('reports/ovr-calibrated-2025-26/legacy-sim-only/ranking.csv')
    add('卡片 OVR（舊版，sim-only）', '能力值公式校準到 v53 模擬，α=0（已被正式卡片板取代）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in legacy], '目標不含 RAPM，ρRAPM 為純樣本外（全量 RAPM）',
        src='reports/ovr-calibrated-2025-26/legacy-sim-only/ranking.csv')
    blend = rows('reports/ovr-blended-2025-26/ranking.csv')
    add('卡片 OVR（混合 α=0.5）', '校準目標 = 模擬與 RAPM 各半（與正式卡片板同一組數字，來源腳本不同）', [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in blend],
        '目標含 RAPM，樣本內 ρ 偏高；留出 ρ 見 ovr-blended-2025-26/summary.json', src='reports/ovr-blended-2025-26/ranking.csv')
    for key, desc in V55_DESC.items():
        if key in ('E2', 'v58'):
            continue
        add(f'卡片 OVR 實驗 {key}（未採用）', desc, [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(V55_CARDS[key])],
            f'Karlo 未過，不採用；{BLEND_NOTE}', src=V55_CARDS[key])
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
    out = sorted(out, key=lambda r: r['order'])
    out.append({'version': 'v55–v58 卡片', 'order': 99, 'winsMAE': '不適用', 'netRMSE': '不適用', 'ptsMAE': '不適用',
                'source': TEAM_NOTE, 'measured': False})
    return out


def top20(rapm_by_name):
    card = rows(OFFICIAL_CARD)
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
                    'simRank': sim.get(r['name'], '—'), 'rapmRank': rr if rr is not None else '—', 'flags': '、'.join(flags) or '—'})
    return out, len(pool)


def kpi(holdout, personal_rows):
    """頂部 KPI；第一格 = v58 樣本外 ρ（淨值）。遊戲本體不讀 OVR，所以標籤是「正式卡片」而非「遊戲現用」。"""
    def cell(key, field):
        try:
            return holdout['cards'][key]['holdout_scale0.5']['avg'][field]
        except (KeyError, TypeError):
            return None
    v58, e2 = cell('H1', 'net'), cell('E2', 'net')
    fmt = lambda v: NA if v is None else f'{v:.3f}'
    inS = next((f"{r['rhoNet']:.3f}" for r in personal_rows if 'v58 H1-m0' in r['layer']), NA)
    k2 = lambda key: fmt(holdout['cards'][key]['rho2k']) if key in holdout.get('cards', {}) else NA
    return [{'label': '正式卡片 v58 H1-m0 樣本外 ρ（淨值）', 'value': fmt(v58),
             'sub': f'E2 同法 {fmt(e2)}；樣本內 {inS}（align/封頂讀 RAPM，循環）；RAPM 分半 A→B／B→A 平均'},
            {'label': '正式卡片 v58 H1-m0 樣本外 ρ（防守）', 'value': fmt(cell('H1', 'def')), 'sub': f"E2 同法 {fmt(cell('E2', 'def'))}"},
            {'label': '正式卡片 v58 H1-m0 對 2K27 ρ（外部基準）', 'value': k2('H1'), 'sub': f"E2 {k2('E2')}；2K27 不參與擬合（H1 的封頂只讀 RAPM）"}]


def md(snap):
    L = [f"# 審查表（{snap['generatedAt'][:10]}）", '', f"模擬版本 {LATEST_SIM}。由 `reports/status/status_snapshot.py` 產生。", '',
         '## 重點（KPI）', '', '| ' + ' | '.join(k['label'] for k in snap['kpi']) + ' |', '|' + '---:|' * len(snap['kpi']),
         '| ' + ' | '.join(f"**{k['value']}**" for k in snap['kpi']) + ' |', '', *[f"- {k['label']}：{k['sub']}" for k in snap['kpi']], '',
         f"## 個人準確度（RAPM，pooledPoss ≥ {EVAL_POSS}）", '',
         '樣本外 ρ = 只用 A 半（gameId 偶數）RAPM 擬合的卡片對 B 半 RAPM 的 ρ，再對調取平均（`reports/ovr-v58-holdout-2025-26/report.md`）；「未量測」= 無半份重擬合版或該層不讀 RAPM。', '',
         '| 層 | 人數 | 淨值 ρ（全量 RAPM） | 防守 ρ（全量 RAPM） | 樣本外 ρ（淨值 / 防守） | 備註 |', '|---|---:|---:|---:|---:|---|']
    L += [f"| {r['layer']} | {r['players']} | {r['rhoNet']:.3f} | {r['rhoDefense']:.3f} | {r['holdoutRho']} | {r['note']} |" for r in snap['personal']]
    L += ['', '## 球隊準確度（30 隊、全季）', '', f"說明：{TEAM_NOTE}。球隊 winsMAE 只來自模擬模型版本（v53/v54 等）。", '',
          '| 版本 | 勝場 MAE | 淨分 RMSE | 得分 MAE | 來源 |', '|---|---:|---:|---:|---|']
    f = lambda v, p: v if isinstance(v, str) else f'{v:.{p}f}'
    L += [f"| {r['version']} | {f(r['winsMAE'], 2)} | {f(r['netRMSE'], 3)} | {f(r['ptsMAE'], 2)} | {r['source']} |" for r in snap['team']]
    L += ['', f"## 卡片 OVR 前 20（RAPM 名次在 {snap['rapmPool']} 人中）", '', '| # | 球員 | 位置 | OVR | 分鐘 | 模擬名次 | RAPM 名次 | 旗標 |',
          '|---:|---|---|---:|---:|---:|---:|---|']
    L += [f"| {r['rank']} | {r['name']} | {r['pos']} | {r['ovr']:.1f} | {r['minutes']} | {r['simRank']} | {r['rapmRank']} | {r['flags']} |" for r in snap['top20']]
    mark = lambda r, k: f"{r[k]}{'' if r[k + 'Pass'] else ' ✗'}"
    L += ['', '## v55 卡片修正各方向（7 人驗收，v53 名次 → 實驗名次，✗ = 未過；E2 曾為正式卡片，10-21 起正式卡片為 v58 H1-m0）', '',
          '| 球員 | 條件 | 2K27 | RAPM | v53 | ' + ' | '.join(V55_CARDS) + ' |', '|---|---|---:|---:|---:|' + '---:|' * len(V55_CARDS)]
    L += [f"| {r['name']} | {r['condition']} | {r['rank2k']:g} | {r['rapmRank']} | {r['v53']} | " + ' | '.join(mark(r, k) for k in V55_CARDS) + ' |' for r in snap['v55fix']]
    return '\n'.join(L) + '\n'


def main():
    rapm = rows('reports/impact-rapm/rapm.csv')
    by_id = {r['playerId']: r for r in rapm}; by_name = {r['name']: r for r in rapm}
    t20, pool = top20(by_name)
    holdout = load_holdout()
    personal_rows = personal(by_id, by_name, holdout)
    snap = {'generatedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'simVersion': LATEST_SIM, 'evalPoss': EVAL_POSS,
            'rapmPool': pool, 'kpi': kpi(holdout, personal_rows), 'teamNote': TEAM_NOTE, 'personal': personal_rows, 'team': team(),
            'top20': t20, 'v55fix': v55fix(by_name)}
    PAYLOAD.mkdir(exist_ok=True)
    for k in ('personal', 'team', 'top20', 'v55fix'):
        for d in (OUT, PAYLOAD):
            (d / f'{k}.json').write_text(json.dumps(snap[k], ensure_ascii=False, indent=1), encoding='utf-8')
    (PAYLOAD / 'kpi.json').write_text(json.dumps(snap['kpi'], ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.json').write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.md').write_text(md(snap), encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    print(md(snap))


if __name__ == '__main__':
    main()

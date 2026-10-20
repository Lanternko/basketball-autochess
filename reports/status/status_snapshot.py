"""Review snapshot: personal accuracy, team accuracy, card OVR top 20 (2025-26).

  python reports/status/status_snapshot.py

Writes status.json (everything), personal.json, team.json, top20.json, v55fix.json (dashboard datasets) and status.md
next to this file. Re-run after any model, board or card change; it only reads existing outputs.
"""
import csv, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
EVAL_POSS = 5000
LOW_MIN, RAPM_FAR, BIGS = 1000, 100, {'C', 'PF'}
LATEST_SIM = 'v54'  # latest sim board measured (official card board is still calibrated to v53)
OFFICIAL_CARD = 'reports/ovr-calibrated-2025-26/ranking.csv'
V55_CARDS = {'B12': 'reports/ovr-v55-finisher-fix-2025-26/card/B12/ranking.csv',
             'C1': 'reports/ovr-v55-card-origin-attr-2025-26/card-C1/ranking.csv',
             'D1': 'reports/ovr-v55-attr-deflate-2025-26/card/D1/ranking.csv'}
V55_DESC = {'B12': '方向 B：吃餅長人禁區出手來源修正（模擬層）後重校卡片',
            'C1': '方向 1：自創禁區比例 s̃ 映成第 16 屬性 originShare 加進卡片回歸',
            'D1': '方向 2：屬性建構層 long 去膨脹（--attr-deflate）後重校卡片'}
V55_CHECKS = [('Karlo Matković', '下修 ≥ 10 名', lambda a, b: b - a >= 10),
              ('John Collins', '下修', lambda a, b: b > a),
              ('Isaiah Stewart', '下修', lambda a, b: b > a),
              ('Luka Garza', '下修', lambda a, b: b > a),
              ('Neemias Queta', '下滑 ≤ 15 名', lambda a, b: b - a <= 15),
              ('Rudy Gobert', '下滑 ≤ 15 名', lambda a, b: b - a <= 15),
              ('Jalen Smith', '下滑 ≤ 15 名', lambda a, b: b - a <= 15)]


def spearman(a, b):
    return float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])


def rows(path):
    return list(csv.DictReader(open(ROOT / path, encoding='utf-8-sig')))


def personal(rapm_by_id, rapm_by_name):
    out = []

    def add(layer, desc, scores, note=''):
        keep = [(s, r) for s, r in scores if r and float(r['pooledPoss']) >= EVAL_POSS]
        s = [k[0] for k in keep]
        out.append({'layer': layer, 'description': desc, 'players': len(keep),
                    'rhoNet': round(spearman(s, [float(r['pooledNet']) for _, r in keep]), 3),
                    'rhoDefense': round(spearman(s, [float(r['pooledD']) for _, r in keep]), 3), 'note': note})
    sim = rows('reports/ovr-v53-shrinkage-2025-26/ranking-v2.csv')
    add('模擬板 v53（原始）', '8 種子期望分差，位置置中每 36 分鐘', [(float(r['rawPer36']), rapm_by_id.get(r['playerId'])) for r in sim])
    add('模擬板 v53（收縮修正版）', '先發不收縮、替補收縮（已採用）', [(float(r['v2Per36']), rapm_by_id.get(r['playerId'])) for r in sim])
    sim = rows('reports/ovr-v54-shrinkage-2025-26/ranking-v2.csv')
    add('模擬板 v54（原始）', '三分／禁區命中率改用可靠度加權收縮', [(float(r['rawPer36']), rapm_by_id.get(r['playerId'])) for r in sim])
    add('模擬板 v54（收縮修正版）', '同 v53 收縮規則', [(float(r['v2Per36']), rapm_by_id.get(r['playerId'])) for r in sim],
        '已收束；球隊層 2025-26 勝場 MAE 變差，未切換對局資料，卡片板仍為 v53 校準')
    card = rows(OFFICIAL_CARD)
    add('卡片 OVR（正式卡片板）', '能力值公式校準到模擬與 RAPM 混合目標，α=0.5（遊戲本體不讀取任何 OVR，見 ovr-blended-2025-26/dataflow.md）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in card],
        '替補可靠度收縮已依預註冊跑完但不採用（G1、G2 未過，見 ovr-blended-bench-shrinkage/report.md），本板維持不變')
    legacy = rows('reports/ovr-calibrated-2025-26/legacy-sim-only/ranking.csv')
    add('卡片 OVR（舊版，sim-only）', '能力值公式校準到 v53 模擬，α=0（已被正式卡片板取代）',
        [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in legacy])
    blend = rows('reports/ovr-blended-2025-26/ranking.csv')
    add('卡片 OVR（混合 α=0.5）', '校準目標 = 模擬與 RAPM 各半（與正式卡片板同一組數字，來源腳本不同）', [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in blend],
        '目標含 RAPM，樣本內 ρ 偏高；留出 ρ 見 ovr-blended-2025-26/summary.json')
    for key, desc in V55_DESC.items():
        add(f'卡片 OVR 實驗 {key}（未採用）', desc, [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in rows(V55_CARDS[key])],
            'Karlo、Jalen Smith 兩條未過，正式卡片板維持 v53')
    return out


def v55fix():
    """7-player acceptance table for the three v55 card experiments vs the official v53 card."""
    ranks = {k: {r['name']: int(r['rank']) for r in rows(p)} for k, p in {'v53': OFFICIAL_CARD, **V55_CARDS}.items()}
    out = []
    for name, cond, ok in V55_CHECKS:
        base = ranks['v53'][name]; row = {'name': name, 'condition': cond, 'v53': base}
        for k in V55_CARDS:
            row[k] = ranks[k][name]; row[k + 'Pass'] = ok(base, ranks[k][name])
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
                            'netRMSE': round(m['netRMSE'], 3), 'ptsMAE': None, 'source': f'player-impact-v{v}', 'measured': True})
    v53 = json.loads((ROOT / 'reports/player-impact-v53-team/scores.json').read_text(encoding='utf-8'))
    m = next(c['teamMetrics'] for c in v53['cells'] if c['season'] == '2025-26' and c['variant'] == 'v53')
    out.append({'version': 'v53', 'order': 53, 'winsMAE': round(m['winsMAE'], 2), 'netRMSE': round(m['netRMSE'], 3), 'ptsMAE': None,
                'source': 'player-impact-v53-team（壓迫係數為樣本內）', 'measured': True})
    v54 = json.loads((ROOT / 'reports/player-impact-v54-team/scores.json').read_text(encoding='utf-8'))
    m = next(c['teamMetrics'] for c in v54['cells'] if c['season'] == '2025-26' and c['variant'] == 'v54')
    out.append({'version': 'v54', 'order': 54, 'winsMAE': round(m['winsMAE'], 2), 'netRMSE': round(m['netRMSE'], 3), 'ptsMAE': None,
                'source': 'player-impact-v54-team（未採用）', 'measured': True})
    return sorted(out, key=lambda r: r['order'])


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
                    'simRank': sim.get(r['name']), 'rapmRank': rr, 'flags': '、'.join(flags)})
    return out, len(pool)


def md(snap):
    L = [f"# 審查表（{snap['generatedAt'][:10]}）", '', f"模擬版本 {LATEST_SIM}。由 `reports/status/status_snapshot.py` 產生。", '',
         f"## 個人準確度（RAPM，pooledPoss ≥ {EVAL_POSS}）", '', '| 層 | 人數 | 淨值 ρ | 防守 ρ | 備註 |', '|---|---:|---:|---:|---|']
    L += [f"| {r['layer']} | {r['players']} | {r['rhoNet']:.3f} | {r['rhoDefense']:.3f} | {r['note']} |" for r in snap['personal']]
    L += ['', '## 球隊準確度（30 隊、全季）', '', '| 版本 | 勝場 MAE | 淨分 RMSE | 得分 MAE | 來源 |', '|---|---:|---:|---:|---|']
    f = lambda v, p: '—' if v is None else f'{v:.{p}f}'
    L += [f"| {r['version']} | {f(r['winsMAE'], 2)} | {f(r['netRMSE'], 3)} | {f(r['ptsMAE'], 2)} | {r['source']} |" for r in snap['team']]
    L += ['', f"## 卡片 OVR 前 20（RAPM 名次在 {snap['rapmPool']} 人中）", '', '| # | 球員 | 位置 | OVR | 分鐘 | 模擬名次 | RAPM 名次 | 旗標 |',
          '|---:|---|---|---:|---:|---:|---:|---|']
    L += [f"| {r['rank']} | {r['name']} | {r['pos']} | {r['ovr']:.1f} | {r['minutes']} | {r['simRank'] or '—'} | {r['rapmRank'] or '—'} | {r['flags']} |" for r in snap['top20']]
    mark = lambda r, k: f"{r[k]}{'' if r[k + 'Pass'] else ' ✗'}"
    L += ['', '## v55 卡片修正三方向（7 人驗收，正式卡片名次 → 實驗名次，✗ = 未過）', '', '| 球員 | 條件 | v53 | B12 | C1 | D1 |', '|---|---|---:|---:|---:|---:|']
    L += [f"| {r['name']} | {r['condition']} | {r['v53']} | {mark(r, 'B12')} | {mark(r, 'C1')} | {mark(r, 'D1')} |" for r in snap['v55fix']]
    return '\n'.join(L) + '\n'


def main():
    rapm = rows('reports/impact-rapm/rapm.csv')
    by_id = {r['playerId']: r for r in rapm}; by_name = {r['name']: r for r in rapm}
    t20, pool = top20(by_name)
    snap = {'generatedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'simVersion': LATEST_SIM, 'evalPoss': EVAL_POSS,
            'rapmPool': pool, 'personal': personal(by_id, by_name), 'team': team(), 'top20': t20, 'v55fix': v55fix()}
    for k in ('personal', 'team', 'top20', 'v55fix'):
        (OUT / f'{k}.json').write_text(json.dumps(snap[k], ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.json').write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.md').write_text(md(snap), encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    print(md(snap))


if __name__ == '__main__':
    main()

"""Review snapshot: personal accuracy, team accuracy, card OVR top 20 (2025-26).

  python reports/status/status_snapshot.py

Writes status.json (everything), personal.json, team.json, top20.json (dashboard datasets) and status.md
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
LATEST_SIM = 'v53'  # board version the cards and sim rows describe


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
    card = rows('reports/ovr-calibrated-2025-26/ranking.csv')
    add('卡片 OVR（遊戲現用）', '能力值公式校準到 v53 模擬', [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in card])
    blend = rows('reports/ovr-blended-2025-26/ranking.csv')
    add('卡片 OVR（混合 α=0.5）', '校準目標 = 模擬與 RAPM 各半（未接進遊戲）', [(float(r['ovr']), rapm_by_name.get(r['name'])) for r in blend],
        '目標含 RAPM，樣本內 ρ 偏高；留出 ρ 見 ovr-blended-2025-26/summary.json')
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
    out.append({'version': LATEST_SIM, 'order': int(LATEST_SIM[1:]), 'winsMAE': None, 'netRMSE': None, 'ptsMAE': None,
                'source': '未跑全季球隊驗證', 'measured': False})
    return sorted(out, key=lambda r: r['order'])


def top20(rapm_by_name):
    card = rows('reports/ovr-calibrated-2025-26/ranking.csv')
    sim = {r['name']: int(r['rank']) for r in rows('reports/ovr-v53-shrinkage-2025-26/ranking-v2.csv')}
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
    return '\n'.join(L) + '\n'


def main():
    rapm = rows('reports/impact-rapm/rapm.csv')
    by_id = {r['playerId']: r for r in rapm}; by_name = {r['name']: r for r in rapm}
    t20, pool = top20(by_name)
    snap = {'generatedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'simVersion': LATEST_SIM, 'evalPoss': EVAL_POSS,
            'rapmPool': pool, 'personal': personal(by_id, by_name), 'team': team(), 'top20': t20}
    for k in ('personal', 'team', 'top20'):
        (OUT / f'{k}.json').write_text(json.dumps(snap[k], ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.json').write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'status.md').write_text(md(snap), encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    print(md(snap))


if __name__ == '__main__':
    main()

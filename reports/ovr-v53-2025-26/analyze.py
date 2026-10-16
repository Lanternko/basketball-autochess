"""Compare the v53 OVR board with v47 against real impact (pooled four-season RAPM).

  python3 reports/ovr-v53-2025-26/analyze.py [--variant both]

Per player: mean paired margin delta -> position-centered per-36 contribution, with the same
rule as reports/ovr-v47-2025-26/position-centering.py (confident pool = starts >= 5,
source-minute weighted per-minute bias) re-estimated on the v53 board itself.

Gates, fixed before the run (players with >= 5000 pooled RAPM possessions):
  parity    the control smoke test, if run, reproduces the saved v47 strata exactly
  defense   Spearman(v53, RAPM defense) > Spearman(v47, RAPM defense)
  net       Spearman(v53, RAPM net) >= Spearman(v47, RAPM net)
Adopt v53 only if all pass.
"""
import csv, json, statistics as st, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
FOCUS = ['Alex Caruso', 'Marcus Smart', 'Herbert Jones', 'Dyson Daniels', 'Derrick White', 'Victor Wembanyama', 'Rudy Gobert',
         'Jalen Brunson', 'Trae Young', 'Stephen Curry', 'Shai Gilgeous-Alexander', 'Nikola Jokić', 'Luka Dončić']


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def load(variant):
    rows = {}
    for line in open(OUT / f'checkpoint-{variant}.jsonl', encoding='utf-8'):
        r = json.loads(line); rows[r['playerId']] = r
    return rows


def parity():
    f, saved = OUT / 'checkpoint-control.jsonl', ROOT / 'reports/ovr-v47-2025-26/healthy-checkpoint.jsonl'
    if not f.exists() or not saved.exists():
        return None
    mine = load('control'); worst = 0.0; checked = 0
    for line in open(saved, encoding='utf-8'):
        row = json.loads(line); r = mine.get(row['playerId'])
        if not r:
            continue
        d = {(o, i): v for o, i, v, *_ in r['draws']}
        for s in row['healthy']['strata']:
            for i, v in enumerate(s['values']):
                worst = max(worst, abs(v - d[(s['opponent'], i)])); checked += 1
    return {'valuesChecked': checked, 'maxAbsDifference': worst, 'passed': checked > 0 and worst < 1e-9}


def centered(board):
    comp = {r['name']: r for r in csv.DictReader(open(ROOT / 'reports/ovr-v47-2025-26/comparison.csv', encoding='utf-8-sig'))}
    ids = {int(r['playerId']): r for r in csv.DictReader(open(ROOT / 'reports/ovr-v47-2025-26/ranking.csv', encoding='utf-8-sig'))}
    work = {int(r['playerId']): r for r in csv.DictReader(open(ROOT / 'reports/player-impact-v29/2025-26-all-player-workload.csv', encoding='utf-8-sig'))}
    rows = []
    for pid, r in board.items():
        info = ids[pid]; c = comp[info['name']]
        rows.append({'playerId': pid, 'name': info['name'], 'pos': info['position'], 'm': r['minutes'],
                     'c': st.mean(d[2] for d in r['draws']), 'W': float(c['source_games_played']) * float(c['source_minutes_per_played_game']),
                     'confident': int(work[pid]['starts']) >= 5,
                     'oppTov': st.mean(d[4] for d in r['draws']), 'oppFga': st.mean(d[3] for d in r['draws'])})
    for pos in {r['pos'] for r in rows}:
        pool = [r for r in rows if r['pos'] == pos and r['confident']]
        b = sum(r['W'] * r['c'] / r['m'] for r in pool) / sum(r['W'] for r in pool)
        for r in rows:
            if r['pos'] == pos:
                r['per36'] = (r['c'] - b * r['m']) / r['m'] * 36
    return {r['playerId']: r for r in rows}


def main():
    variant = sys.argv[sys.argv.index('--variant') + 1] if '--variant' in sys.argv else 'both'
    v53 = centered(load(variant))
    v47 = {r['name']: float(r['centered_contribution']) / float(r['healthy_minutes']) * 36
           for r in csv.DictReader(open(ROOT / 'reports/ovr-v47-2025-26/centered-ranking.csv', encoding='utf-8'))}
    rapm = {int(r['playerId']): r for r in csv.DictReader(open(ROOT / 'reports/impact-rapm/rapm.csv', encoding='utf-8'))}
    ff = {int(r['playerId']): float(r['tovNonSteal_defense']) for r in csv.DictReader(open(ROOT / 'reports/impact-rapm/four-factors.csv', encoding='utf-8'))}
    keep = [p for p in v53 if p in rapm and float(rapm[p]['pooledPoss']) >= 5000 and v53[p]['name'] in v47]
    D = [float(rapm[p]['pooledD']) for p in keep]; N = [float(rapm[p]['pooledNet']) for p in keep]
    new = [v53[p]['per36'] for p in keep]; old = [v47[v53[p]['name']] for p in keep]
    result = {
        'variant': variant, 'players': len(v53), 'comparedPlayers': len(keep), 'parity': parity(),
        'spearmanWithRAPMDefense': {'v47': spearman(old, D), 'v53': spearman(new, D)},
        'spearmanWithRAPMNet': {'v47': spearman(old, N), 'v53': spearman(new, N)},
        'mechanism': {'spearmanChangeVsTovNonStealCoefficient': spearman([a - b for a, b in zip(new, old)], [ff.get(p, 0.0) for p in keep]),
                      'spearmanOpponentTovVsTovNonStealCoefficient': spearman([v53[p]['oppTov'] for p in keep], [ff.get(p, 0.0) for p in keep])},
    }
    par = result['parity']
    result['gates'] = {'parity': par['passed'] if par else 'not run',
                       'defense': result['spearmanWithRAPMDefense']['v53'] > result['spearmanWithRAPMDefense']['v47'],
                       'net': result['spearmanWithRAPMNet']['v53'] >= result['spearmanWithRAPMNet']['v47']}
    result['gates']['adopt'] = result['gates']['defense'] and result['gates']['net'] and result['gates']['parity'] is not False
    rank_new = {p: k + 1 for k, p in enumerate(sorted(v53, key=lambda p: -v53[p]['per36']))}
    rank_old = {n: k + 1 for k, n in enumerate(sorted(v47, key=lambda n: -v47[n]))}
    result['focus'] = {v53[p]['name']: {'v47Rank': rank_old.get(v53[p]['name']), 'v53Rank': rank_new[p], 'v47Per36': round(v47.get(v53[p]['name'], float('nan')), 2),
                                         'v53Per36': round(v53[p]['per36'], 2)} for p in v53 if v53[p]['name'] in FOCUS}
    (OUT / f'result-{variant}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    with open(OUT / f'ranking-{variant}.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh); w.writerow(['rank', 'playerId', 'name', 'position', 'minutes', 'per36Centered', 'v47Per36Centered', 'opponentTovPerGame', 'opponentFgaPerGame'])
        for p in sorted(v53, key=lambda p: rank_new[p]):
            r = v53[p]
            w.writerow([rank_new[p], p, r['name'], r['pos'], round(r['m'], 2), round(r['per36'], 3), round(v47.get(r['name'], float('nan')), 3), round(r['oppTov'], 3), round(r['oppFga'], 3)])
    print(json.dumps(result, ensure_ascii=False, indent=1))


main()

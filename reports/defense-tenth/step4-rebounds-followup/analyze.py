"""Post-hoc descriptive ORB check; reads frozen runs, never reruns or changes models."""
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'reports/defense-tenth/step4-rebounds'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
old = read(BASE / 'seed-arrays.json')
protocol = read(BASE / 'protocol.json')
seasons = list(old)
versions = ['T0', 'pooled', 'dreb']
arrays = {}
for season in seasons:
    source = (ROOT / 'data/season-source' if season == '2025-26'
              else ROOT / 'data/defense-seventh' / season)
    table = read(source / 'team-games.json')['data']['resultSets'][0]
    rows = [dict(zip(table['headers'], r)) for r in table['rowSet']]
    games = defaultdict(list)
    for r in rows:
        games[r['GAME_ID']].append(r)
    totals = defaultdict(lambda: np.zeros(2))
    for game, pair in games.items():
        assert len(pair) == 2, (season, game, len(pair))
        for own, opp in [pair, pair[::-1]]:
            totals[own['TEAM_ID']] += [own['OREB'], opp['DREB']]
    ids = old[season]['ids']
    truth = np.array([100 * totals[i][0] / totals[i].sum() for i in ids])
    predictions = {}
    for version in versions:
        values = []
        for seed in range(20261012, 20261032):
            p = (ROOT / f'reports/defense-tenth/step4-t0/runs/{season}-pure-{seed}.json'
                 if version == 'T0' else BASE / f'runs/{season}-{version}-{seed}.json')
            teams = {t['id']: t for t in read(p)['teams']}
            values.append([100 * teams[i]['stats']['oreb'] /
                           (teams[i]['stats']['oreb'] + teams[i]['opponent']['dreb']) for i in ids])
        predictions[version] = np.array(values)
    arrays[season] = {'truth': truth, 'predictions': predictions}

B = protocol['uncertainty']['bootstrap']
rng = np.random.default_rng(protocol['uncertainty']['seed'])
fr = rng.integers(0, 30, (B, 30))
se = rng.integers(0, 20, (B, 20))
counts = np.stack([(se == i).sum(1) for i in range(20)], axis=1) / 20
center = lambda x: x - x.mean(-1, keepdims=True)
rms = lambda x: np.sqrt((x * x).mean((-1, -2)))

def metrics(x, y):
    x, y = center(x), center(y)
    return {'OREB_RMSE_pp': rms(x - y),
            'OREB_MAE_pp': np.abs(x - y).mean((-1, -2)),
            'OREB_correlation': (x * y).mean((-1, -2)) / (rms(x) * rms(y))}

out = {}
for selected in [[s] for s in seasons] + [seasons]:
    label = selected[0] if len(selected) == 1 else 'four-seasons-equal'
    points, boots = {}, {}
    for v in versions:
        x = np.stack([arrays[s]['predictions'][v].mean(0) for s in selected])
        y = np.stack([arrays[s]['truth'] for s in selected])
        bx = np.stack([np.take_along_axis(counts @ arrays[s]['predictions'][v], fr, axis=1)
                       for s in selected], axis=1)
        by = np.stack([arrays[s]['truth'][fr] for s in selected], axis=1)
        points[v], boots[v] = metrics(x, y), metrics(bx, by)
    out[label] = {
        'versions': {v: {k: float(val) for k, val in points[v].items()} for v in versions},
        'drebMinuspooled': {k: {'point': float(points['dreb'][k] - points['pooled'][k]),
                              'joint95': np.quantile(boots['dreb'][k] - boots['pooled'][k], [.025, .975]).tolist()}
                            for k in points['dreb']}}
result = {'status': 'post-hoc descriptive; four seasons already seen; no new simulations',
          'definition': 'own credited OREB / (own credited OREB + opponent credited DREB); centered within season',
          'bootstrap': protocol['uncertainty'], 'results': out}
(HERE / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(out['four-seasons-equal'], indent=2))

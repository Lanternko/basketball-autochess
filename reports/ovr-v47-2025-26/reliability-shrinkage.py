"""Step 2a: empirical-Bayes reliability shrinkage on the position-centered v47 board.

Works per 36 simulated minutes (x = centered contribution / minutes * 36) so starters and
bench players share one scale. Two noise sources are separated:
  * Monte Carlo noise: known per player, (conditional SE / minutes * 36)^2
  * source small-sample noise: unknown, modelled as kappa / W (W = source total minutes)
Variance model fitted on all players by weighted least squares:
  (x - mu(W))^2 - mc = tau^2 + kappa / W
Prior mean mu = a + b * log(minutes per played game): role-based, so missed games never
lower the prior (availability is not deducted). Games played only enter through kappa / W.
Posterior: x_hat = mu + B * (x - mu), B = tau^2 / (tau^2 + mc + kappa / W).
Final contribution = x_hat * minutes / 36, so the board stays in points per game.

Requires position-centering.py output. No new simulation; v41 uses the same fitted
form with v47 Monte Carlo SE as a stand-in (same design and sample count).
"""
import csv, json, math, statistics as st, unicodedata
from pathlib import Path

root = Path(__file__).parent
reports = root.parent
comp = {r['name']: r for r in csv.DictReader(open(root / 'comparison.csv', encoding='utf-8-sig'))}
cent = list(csv.DictReader(open(root / 'centered-ranking.csv', encoding='utf-8')))
media = json.loads((reports / 'model-evolution-20261016/media-ranks.json').read_text(encoding='utf-8'))
center = json.loads((root / 'position-centering.json').read_text(encoding='utf-8'))
f = float

rows = []
for r in cent:
    c = comp[r['name']]
    m = f(r['healthy_minutes'])
    old_bias = center['bias']['v41'][r['position']]['perMinuteBias']
    rows.append({'name': r['name'], 'position': r['position'], 'm': m, 'games': int(c['source_games_played']),
                 'W': f(c['source_games_played']) * f(c['source_minutes_per_played_game']), 'mpg': f(c['source_minutes_per_played_game']),
                 'x47': f(r['centered_contribution']) / m * 36,
                 'x41': (f(c['old_contribution']) - old_bias * m) / m * 36,
                 'mc': (f(r['conditional_se']) / m * 36) ** 2,
                 'rawRank': int(r['raw_v47_rank']), 'centeredRank': int(r['rank'])})


def wls(xs, ys, ws):
    sw = sum(ws); mx = sum(w * x for x, w in zip(xs, ws)) / sw; my = sum(w * y for y, w in zip(ys, ws)) / sw
    b = sum(w * (x - mx) * (y - my) for x, y, w in zip(xs, ys, ws)) / sum(w * (x - mx) ** 2 for x, w in zip(xs, ws))
    return my - b * mx, b


def fit(key):
    # Role prior on log minutes per played game, weighted by inverse Monte Carlo variance.
    a, b = wls([math.log(r['mpg']) for r in rows], [r[key] for r in rows], [1 / r['mc'] for r in rows])
    mu = {r['name']: a + b * math.log(r['mpg']) for r in rows}
    # Excess variance on 1/W; two passes so the weights use the fitted variance.
    weights = [1 / r['mc'] ** 2 for r in rows]
    for _ in range(2):
        tau2, kappa = wls([1 / r['W'] for r in rows], [(r[key] - mu[r['name']]) ** 2 - r['mc'] for r in rows], weights)
        tau2, kappa = max(tau2, 1e-6), max(kappa, 0.0)
        weights = [1 / (tau2 + r['mc'] + kappa / r['W']) ** 2 for r in rows]
    for r in rows:
        B = tau2 / (tau2 + r['mc'] + kappa / r['W'])
        r[key + 'B'] = B
        r[key + 's'] = (mu[r['name']] + B * (r[key] - mu[r['name']])) * r['m'] / 36
    return {'priorIntercept': a, 'priorLogMinutesPerGameSlope': b, 'tau2Per36': tau2, 'kappa': kappa,
            'sourceNoiseEqualsSignalAtMinutes': kappa / tau2 if tau2 else None}


fits = {'v47': fit('x47'), 'v41': fit('x41')}


def ranks(key):
    return {r['name']: i + 1 for i, r in enumerate(sorted(rows, key=lambda r: (-r[key], r['name'])))}


R47, R41 = ranks('x47s'), ranks('x41s')
names = [r['name'] for r in rows]


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().replace('.', '').replace(' iii', '').replace(' jr', '')


byfold = {fold(n): n for n in names}
mrank = {}
for p in media['players']:
    n = byfold.get(fold(p['name']))
    if n:
        mrank[n] = st.mean(p['ranks'].get(k, 101) for k in media['selectedMedia'])
mn = sorted(mrank)
centeredRank = {r['name']: r['centeredRank'] for r in rows}


def topcount(rank, n, cond):
    return sum(1 for r in rows if rank[r['name']] <= n and cond(r))


small = lambda r: r['games'] < 20
summary = {
    'method': 'empirical-Bayes per-36 shrinkage after position centering; role prior on log minutes per played game; noise = Monte Carlo + kappa/W',
    'fits': fits,
    'spearmanV41V47': {'centered': center['spearmanV41V47']['centered'], 'shrunk': st.correlation([R41[n] for n in names], [R47[n] for n in names])},
    'spearmanWithMedia': {'centered': center['spearmanWithMedia']['v47Centered'],
                          'shrunk': st.correlation([-R47[n] for n in mn], [-mrank[n] for n in mn]), 'matched': len(mn)},
    'smallSampleUnder20GamesInTop50': {'raw': topcount({r['name']: r['rawRank'] for r in rows}, 50, small),
                                       'centered': topcount(centeredRank, 50, small), 'shrunk': topcount(R47, 50, small)},
    'medianShrinkFactor': {'under20Games': st.median(r['x47B'] for r in rows if small(r)), '20PlusGames': st.median(r['x47B'] for r in rows if not small(r))},
    'unchanged': 'Ranking still single-replicate Monte Carlo; split-half stability needs the local resample run',
}
(root / 'reliability-shrinkage.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
with open(root / 'shrunk-ranking.csv', 'w', encoding='utf-8', newline='') as fh:
    out = csv.writer(fh)
    out.writerow(['rank', 'centered_rank', 'raw_v47_rank', 'name', 'position', 'healthy_minutes', 'source_games_played', 'shrunk_contribution', 'centered_contribution', 'shrink_factor'])
    for r in sorted(rows, key=lambda r: R47[r['name']]):
        out.writerow([R47[r['name']], r['centeredRank'], r['rawRank'], r['name'], r['position'], round(r['m'], 2), r['games'],
                      round(r['x47s'], 3), round(r['x47'] * r['m'] / 36, 3), round(r['x47B'], 3)])
print(json.dumps(summary, ensure_ascii=False, indent=1))

"""Step 1: post-hoc positional baseline centering for the v47 contribution board.

The synthetic baseline for each slot is meant to equal the confident natural-position
pool's source-minute-weighted average player. In v47 the per-slot means drift by up to
+-1.15 points, so the same synthetic "average 70" is stronger at some slots than others.

Correction (per position, estimated on the same confident pool the synthetic used):
  per-minute bias b = sum_i W_i * (c_i / m_i) / sum_i W_i
  centered c'_i = c_i - b * m_i
W_i = source total minutes, m_i = simulated healthy minutes, c_i = raw contribution.
The bias scales with simulated minutes because the baseline only replaces the minutes
the candidate actually plays.

Confident pool proxy: starts >= 5 in the workload source (original rule: role starts < 5
is low confidence). No new simulation; Monte Carlo noise and mechanism gaps are unchanged.
"""
import csv, json, random, statistics as st, unicodedata
from pathlib import Path

root = Path(__file__).parent
reports = root.parent
rows = list(csv.DictReader(open(root / 'comparison.csv', encoding='utf-8-sig')))
ids = {r['name']: r['playerId'] for r in csv.DictReader(open(root / 'ranking.csv', encoding='utf-8-sig'))}
work = {r['playerId']: r for r in csv.DictReader(open(reports / 'player-impact-v29/2025-26-all-player-workload.csv', encoding='utf-8-sig'))}
media = json.loads((reports / 'model-evolution-20261016/media-ranks.json').read_text(encoding='utf-8'))
POS = ['PG', 'SG', 'SF', 'PF', 'C']
f = float

for r in rows:
    w = work.get(ids[r['name']])
    assert w, 'Missing workload row ' + r['name']
    r['W'] = f(r['source_games_played']) * f(r['source_minutes_per_played_game'])
    r['m'] = f(r['healthy_minutes'])
    r['confident'] = int(w['starts']) >= 5
    r['c47'] = f(r['margin_contribution'])
    r['c41'] = f(r['old_contribution'])
    r['se'] = (f(r['conditional_ci95_high']) - f(r['conditional_ci95_low'])) / 3.92


def bias(pool, key):
    return sum(r['W'] * r[key] / r['m'] for r in pool) / sum(r['W'] for r in pool)


def center(key):
    out = {}
    for pos in POS:
        pool = [r for r in rows if r['position'] == pos and r['confident']]
        b = bias(pool, key)
        rng = random.Random(20261017 + POS.index(pos))
        boot = [bias([rng.choice(pool) for _ in pool], key) for _ in range(2000)]
        out[pos] = {'confidentPlayers': len(pool), 'perMinuteBias': b, 'per32MinuteBias': b * 32,
                    'bootstrapSE32': st.stdev(boot) * 32}
        for r in rows:
            if r['position'] == pos:
                r[key + 'c'] = r[key] - b * r['m']
    return out


def ranks(key):
    order = sorted(rows, key=lambda r: (-r[key], r['name']))
    return {r['name']: i + 1 for i, r in enumerate(order)}


def spearman(a, b, names):
    return st.correlation([a[n] for n in names], [b[n] for n in names])


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().replace('.', '').replace(' iii', '').replace(' jr', '')


bias47, bias41 = center('c47'), center('c41')
R = {k: ranks(k) for k in ['c47', 'c47c', 'c41', 'c41c']}
names = [r['name'] for r in rows]


def top_positions(key, n):
    top = [r for r in rows if R[key][r['name']] <= n]
    return {p: sum(r['position'] == p for r in top) for p in POS}


def pos_means(key):
    return {p: st.mean(r[key] for r in rows if r['position'] == p) for p in POS}


# External sanity reference only: preseason media consensus, not ability truth.
sel = media['selectedMedia']
byfold = {fold(r['name']): r['name'] for r in rows}
mrank = {}
for p in media['players']:
    n = byfold.get(fold(p['name']))
    if n:
        mrank[n] = st.mean(p['ranks'].get(m, 101) for m in sel)
mnames = sorted(mrank)
mediaRank = {n: -mrank[n] for n in mnames}

# Noise-adjusted signal share: 1 - mean(se^2) / var(contribution).
mse = st.mean(r['se'] ** 2 for r in rows)
reliability = {k: 1 - mse / st.pvariance([r[k] for r in rows]) for k in ['c47', 'c47c']}

summary = {
    'method': 'post-hoc per-position per-minute centering on confident source-minute-weighted pool; no new simulation',
    'confidentPoolProxy': 'workload starts >= 5',
    'bias': {'v47': bias47, 'v41': bias41},
    'positionMeans': {'v47Raw': pos_means('c47'), 'v47Centered': pos_means('c47c'), 'v41Raw': pos_means('c41'), 'v41Centered': pos_means('c41c')},
    'top20Positions': {'v47Raw': top_positions('c47', 20), 'v47Centered': top_positions('c47c', 20), 'v41Centered': top_positions('c41c', 20)},
    'top50Positions': {'v47Raw': top_positions('c47', 50), 'v47Centered': top_positions('c47c', 50), 'v41Centered': top_positions('c41c', 50)},
    'spearmanV41V47': {'raw': spearman(R['c41'], R['c47'], names), 'centered': spearman(R['c41c'], R['c47c'], names)},
    'mediaMatched': len(mnames),
    'spearmanWithMedia': {'v47Raw': spearman({n: -R['c47'][n] for n in mnames}, mediaRank, mnames),
                          'v47Centered': spearman({n: -R['c47c'][n] for n in mnames}, mediaRank, mnames)},
    'signalShare': reliability,
    'unchanged': 'Monte Carlo noise, missing small-sample shrinkage and mechanism gaps (off-ball, spacing, rim deterrence) are not addressed here',
}
(root / 'position-centering.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

order = sorted(rows, key=lambda r: (-r['c47c'], r['name']))
with open(root / 'centered-ranking.csv', 'w', encoding='utf-8', newline='') as fh:
    out = csv.writer(fh)
    out.writerow(['rank', 'raw_v47_rank', 'name', 'position', 'healthy_minutes', 'centered_contribution', 'raw_contribution', 'position_adjustment', 'conditional_se', 'source_games_played'])
    for i, r in enumerate(order):
        out.writerow([i + 1, R['c47'][r['name']], r['name'], r['position'], round(r['m'], 2), round(r['c47c'], 3), round(r['c47'], 3), round(r['c47c'] - r['c47'], 3), round(r['se'], 3), r['source_games_played']])
print(json.dumps({k: summary[k] for k in ['spearmanV41V47', 'spearmanWithMedia', 'signalShare', 'mediaMatched']}, indent=1))
print(json.dumps({p: round(v['per32MinuteBias'], 2) for p, v in bias47.items()}), json.dumps({p: round(v['bootstrapSE32'], 2) for p, v in bias47.items()}))
print(summary['top20Positions'], summary['top50Positions'], sep='\n')

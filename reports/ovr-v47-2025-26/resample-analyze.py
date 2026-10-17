"""Step 2c: validate centering + shrinkage on independent halves of the seed draws.

  python3 reports/ovr-v47-2025-26/resample-analyze.py              # needs local checkpoints
  python3 reports/ovr-v47-2025-26/resample-analyze.py --self-check # snapshot-only consistency check

Halves split by seed pairs (i // 2 even vs odd) so each half keeps both rotation phases,
all 30 opponents and both seats, matching the original stability.py split (0,1 vs 2,3).

Adoption gates (fixed before the local run):
  1. full-sample split-half Spearman of centered contributions >= 0.80
  2. shrunk half A predicts half B with lower per-36 MSE than unshrunk half A
The formulas mirror position-centering.py and reliability-shrinkage.py; --self-check
proves they reproduce shrunk-ranking.csv from the saved 4-seed results.
"""
import csv, json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path

root = Path(__file__).parent
reports = root.parent
POS = ['PG', 'SG', 'SF', 'PF', 'C']
f = float


def source_info():
    comp = {r['name']: r for r in csv.DictReader(open(root / 'comparison.csv', encoding='utf-8-sig'))}
    ids = {r['name']: r['playerId'] for r in csv.DictReader(open(root / 'ranking.csv', encoding='utf-8-sig'))}
    work = {r['playerId']: r for r in csv.DictReader(open(reports / 'player-impact-v29/2025-26-all-player-workload.csv', encoding='utf-8-sig'))}
    out = {}
    for name, c in comp.items():
        g, mpg = f(c['source_games_played']), f(c['source_minutes_per_played_game'])
        out[int(ids[name])] = {'name': name, 'position': c['position'], 'W': g * mpg, 'mpg': mpg, 'games': int(g),
                               'confident': int(work[ids[name]]['starts']) >= 5}
    return out


def estimate(strata):
    """strata: {opponent: [delta, ...]} -> (contribution, standard error), as in run.mjs."""
    vals = list(strata.values())
    contribution = st.mean(st.mean(v) for v in vals)
    var = sum(st.variance(v) / len(v) for v in vals) / len(vals) ** 2
    return contribution, math.sqrt(var)


def center(rows):
    for pos in POS:
        pool = [r for r in rows if r['position'] == pos and r['confident']]
        b = sum(r['W'] * r['c'] / r['m'] for r in pool) / sum(r['W'] for r in pool)
        for r in rows:
            if r['position'] == pos:
                r['cc'] = r['c'] - b * r['m']
                r['x'] = r['cc'] / r['m'] * 36
                r['mc'] = (r['se'] / r['m'] * 36) ** 2


def wls(xs, ys, ws):
    sw = sum(ws); mx = sum(w * x for x, w in zip(xs, ws)) / sw; my = sum(w * y for y, w in zip(ys, ws)) / sw
    b = sum(w * (x - mx) * (y - my) for x, y, w in zip(xs, ys, ws)) / sum(w * (x - mx) ** 2 for x, w in zip(xs, ws))
    return my - b * mx, b


def shrink(rows):
    a, b = wls([math.log(r['mpg']) for r in rows], [r['x'] for r in rows], [1 / r['mc'] for r in rows])
    for r in rows:
        r['mu'] = a + b * math.log(r['mpg'])
    weights = [1 / r['mc'] ** 2 for r in rows]
    for _ in range(2):
        tau2, kappa = wls([1 / r['W'] for r in rows], [(r['x'] - r['mu']) ** 2 - r['mc'] for r in rows], weights)
        tau2, kappa = max(tau2, 1e-6), max(kappa, 0.0)
        weights = [1 / (tau2 + r['mc'] + kappa / r['W']) ** 2 for r in rows]
    for r in rows:
        B = tau2 / (tau2 + r['mc'] + kappa / r['W'])
        r['xs'] = r['mu'] + B * (r['x'] - r['mu'])
        r['cs'] = r['xs'] * r['m'] / 36
    return {'tau2Per36': tau2, 'kappa': kappa}


def board(info, per_player):
    """per_player: {pid: (minutes, contribution, se)} -> adjusted rows."""
    rows = [{**info[pid], 'pid': pid, 'm': m, 'c': c, 'se': se} for pid, (m, c, se) in per_player.items()]
    center(rows)
    fit = shrink(rows)
    return {r['pid']: r for r in rows}, fit


def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0] * len(v)
        for k, i in enumerate(order):
            out[i] = k
        return out
    return st.correlation(rank(a), rank(b))


def self_check(info):
    comp = {r['name']: r for r in csv.DictReader(open(root / 'comparison.csv', encoding='utf-8-sig'))}
    per = {pid: (f(comp[v['name']]['healthy_minutes']), f(comp[v['name']]['margin_contribution']),
                 (f(comp[v['name']]['conditional_ci95_high']) - f(comp[v['name']]['conditional_ci95_low'])) / 3.92) for pid, v in info.items()}
    rows, _ = board(info, per)
    saved = {r['name']: f(r['shrunk_contribution']) for r in csv.DictReader(open(root / 'shrunk-ranking.csv', encoding='utf-8'))}
    worst = max(abs(round(r['cs'], 3) - saved[r['name']]) for r in rows.values())
    print(json.dumps({'selfCheckMaxAbsDiff': worst, 'passed': worst <= 0.0011}))
    if worst > 0.0011:
        sys.exit(1)


def load_draws():
    draws = defaultdict(dict)
    minutes = {}
    for line in open(root / 'healthy-checkpoint.jsonl', encoding='utf-8'):
        row = json.loads(line)
        minutes[row['playerId']] = row['healthy']['minutes']
        for s in row['healthy']['strata']:
            for i, v in enumerate(s['values']):
                draws[row['playerId']][(s['opponent'], i)] = v
    for line in open(root / 'resample-checkpoint.jsonl', encoding='utf-8'):
        row = json.loads(line)
        assert abs(row['minutes'] - minutes[row['playerId']]) < 0.01, row['name']
        for opponent, i, margin, base in row['draws']:
            assert (opponent, i) not in draws[row['playerId']], 'duplicate seed index'
            draws[row['playerId']][(opponent, i)] = margin - base
    return draws, minutes


def main():
    info = source_info()
    if '--self-check' in sys.argv:
        return self_check(info)
    draws, minutes = load_draws()
    complete = [pid for pid in info if len({i for _, i in draws[pid]}) == max(len({i for _, i in d}) for d in draws.values())]
    if len(complete) < len(info):
        print(json.dumps({'warning': 'players without the full seed set are excluded', 'excluded': len(info) - len(complete)}))
    info = {pid: info[pid] for pid in complete}

    def half(pid, keep):
        strata = defaultdict(list)
        for (opponent, i), v in sorted(draws[pid].items()):
            if keep(i):
                strata[opponent].append(v)
        return (minutes[pid], *estimate(strata))

    A, fitA = board(info, {pid: half(pid, lambda i: (i // 2) % 2 == 0) for pid in info})
    B, fitB = board(info, {pid: half(pid, lambda i: (i // 2) % 2 == 1) for pid in info})
    full, fitFull = board(info, {pid: half(pid, lambda i: True) for pid in info})
    pids = sorted(info)
    mse = lambda key: st.mean((A[p][key] - B[p]['x']) ** 2 for p in pids)
    split = spearman([A[p]['cc'] for p in pids], [B[p]['cc'] for p in pids])
    # Spearman-Brown: reliability of the full board from the half-board correlation.
    fullReliability = 2 * split / (1 + split)
    top20 = lambda rows, key: {p for p in sorted(pids, key=lambda p: -rows[p][key])[:20]}
    result = {
        'players': len(pids), 'seedIndices': sorted({i for d in draws.values() for _, i in d}),
        'splitHalfSpearmanCentered': split, 'splitHalfSpearmanRaw': spearman([A[p]['c'] for p in pids], [B[p]['c'] for p in pids]),
        'splitHalfSpearmanShrunk': spearman([A[p]['cs'] for p in pids], [B[p]['cs'] for p in pids]),
        'top20OverlapCentered': len(top20(A, 'cc') & top20(B, 'cc')), 'top20OverlapShrunk': len(top20(A, 'cs') & top20(B, 'cs')),
        'fullBoardReliabilitySpearmanBrown': fullReliability,
        'predictHalfBPer36MSE': {'unshrunkA': mse('x'), 'shrunkA': mse('xs')},
        'fits': {'halfA': fitA, 'halfB': fitB, 'full': fitFull},
        'gates': {'fullReliabilityAtLeast080': fullReliability >= 0.80, 'shrinkageImprovesPrediction': mse('xs') < mse('x')},
    }
    (root / 'resample-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    with open(root / 'resample-ranking.csv', 'w', encoding='utf-8', newline='') as fh:
        out = csv.writer(fh)
        out.writerow(['rank', 'playerId', 'name', 'position', 'healthy_minutes', 'source_games_played', 'shrunk_contribution', 'centered_contribution', 'standard_error'])
        for k, p in enumerate(sorted(pids, key=lambda p: -full[p]['cs'])):
            r = full[p]
            out.writerow([k + 1, p, r['name'], r['position'], round(r['m'], 2), r['games'], round(r['cs'], 3), round(r['cc'], 3), round(r['se'], 3)])
    print(json.dumps(result, ensure_ascii=False, indent=1))


main()

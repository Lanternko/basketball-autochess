"""Card OVR formula: card attributes -> the final real-player OVR scale (2025-26).

Real players get their OVR from box-prior RAPM (reports/ovr-final-2025-26). Fictional cards
have no games, so this fits a formula from card attributes to the same target, so every
card is measured with one ruler: points per 100 possessions its team gains with it on court.

  target   2025-26 box-prior RAPM net, offense and defense (reports/impact-rapm/rapm-prior.csv)
  inputs   the 14 card attributes of reports/ovr-calibrated-2025-26 (13 season-league card
           fields + derived 'creation'), standardized
  fit      weighted ridge, weight = min(minutes, 2000) / 2000; model form (linear or
           position-specific slopes) and ridge strength chosen by repeated 5-fold CV on net;
           offense and defense refitted with the same form and strength, so net = O + D
  output   formula.json (everything needed to score any card), ranking.csv, summary.json

  python3 reports/ovr-card-2025-26/fit.py

Linear in attributes: a card far outside the real attribute range is extrapolated.
"""
import csv, importlib.util, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('cal', ROOT / 'reports/ovr-calibrated-2025-26/calibrate.py')
cal = importlib.util.module_from_spec(spec); spec.loader.exec_module(cal)
LAMBDAS = [0.3, 1, 3, 10, 30, 100]
FORMS = ['linear', 'position-interactions']


def rows():
    league = json.loads((ROOT / 'data/season-league.json').read_text(encoding='utf-8'))
    cards = {}
    for t in league['teams']:
        for p in t['roster']:
            c = cards.setdefault(p['name'], {'card': p, 'MIN': 0.0})
            c['MIN'] += p['observed']['MIN']
    cal.attach_creation(cards)
    final = {r['name']: r for r in csv.DictReader(open(ROOT / 'reports/ovr-final-2025-26/ranking.csv', encoding='utf-8'))}
    prior = {int(r['playerId']): r for r in csv.DictReader(open(ROOT / 'reports/impact-rapm/rapm-prior.csv', encoding='utf-8'))}
    out = []
    for name, c in cards.items():
        f = final[name]; r = prior[int(f['playerId'])]
        out.append({'name': name, 'playerId': int(f['playerId']), 'pos': f['pos'], 'card': c['card'], 'MIN': c['MIN'],
                    'finalOvr': float(f['ovr']), 'net': float(r['lastSeasonNet']), 'O': float(r['lastSeasonO']), 'D': float(r['lastSeasonD'])})
    return out


def fit(X, y, w, lam):
    A = np.c_[np.ones(len(X)), X]
    pen = lam * np.eye(A.shape[1]); pen[0, 0] = 0
    return np.linalg.solve(A.T @ (w[:, None] * A) + pen, A.T @ (w * y))


def cv(X, y, w, lam, reps=10):
    tot = np.sum(w * (y - np.average(y, weights=w)) ** 2); scores = []
    for rep in range(reps):
        idx = np.random.default_rng(rep).permutation(len(y)); sse = 0.0
        for k in range(5):
            te = idx[k::5]; tr = np.setdiff1d(idx, te)
            b = fit(X[tr], y[tr], w[tr], lam)
            sse += np.sum(w[te] * (y[te] - np.c_[np.ones(len(te)), X[te]] @ b) ** 2)
        scores.append(1 - sse / tot)
    return float(np.mean(scores))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    data = rows()
    w = np.array([min(r['MIN'], 2000) / 2000 for r in data])
    y = {k: np.array([r[k] for r in data]) for k in ('net', 'O', 'D')}
    grid = {}
    for form in FORMS:
        X, _, _ = cal.design(data, form)
        for lam in LAMBDAS:
            grid[f'{form}|{lam}'] = cv(X, y['net'], w, lam)
    best = max(grid, key=grid.get)
    form, lam = best.split('|')[0], float(best.split('|')[1])
    X, mean, sd = cal.design(data, form)
    coef = {k: fit(X, y[k], w, lam) for k in ('net', 'O', 'D')}
    pred = {k: np.c_[np.ones(len(X)), X] @ coef[k] for k in coef}
    # Same display scale as the final real-player board (reports/ovr-final-2025-26/summary.json).
    anchors = json.loads((ROOT / 'reports/ovr-final-2025-26/summary.json').read_text(encoding='utf-8'))['scaleAnchorsNetPer100']
    p1, p50, p99 = anchors['PR1'], anchors['PR50'], anchors['PR99']
    to_ovr = lambda x: 40 + 30 * (x - p1) / (p50 - p1) if x <= p50 else 70 + 29 * (x - p50) / (p99 - p50)
    ovr = np.array([to_ovr(x) for x in pred['net']])
    regular = np.array([r['MIN'] >= 500 for r in data])
    nA = len(cal.ATTRS)
    per10 = {a: {k: float(coef[k][1 + i] / sd[i] * 10) for k in ('net', 'O', 'D')} for i, a in enumerate(cal.ATTRS)}
    summary = {'chosen': {'form': form, 'ridge': lam}, 'cvR2Net': grid,
               'spearmanWithFinalOVR': {'all': spearman(ovr, [r['finalOvr'] for r in data]),
                                        'atLeast500Minutes': spearman(ovr[regular], np.array([r['finalOvr'] for r in data])[regular])},
               'meanAbsOvrGapAtLeast500Minutes': float(np.mean(np.abs(ovr[regular] - np.array([r['finalOvr'] for r in data])[regular]))),
               'valuePer10AttributePointsNetPer100': per10,
               'positionSlopeAttributes': cal.INTERACT if form == 'position-interactions' else []}
    formula = {'description': 'netPer100 = intercept + sum(coef_j * z_j); z = (attribute - mean) / sd; position-interaction columns multiply the z of INTERACT attributes by a 0/1 dummy for PG, SG, SF, PF (C is the reference). OVR from netPer100 with the PR anchors.',
               'attributes': cal.ATTRS, 'mean': dict(zip(cal.ATTRS, map(float, mean[:nA]))), 'sd': dict(zip(cal.ATTRS, map(float, sd[:nA]))),
               'form': form, 'interactAttributes': cal.INTERACT, 'dummyPositions': cal.POS[:-1],
               'intercept': {k: float(coef[k][0]) for k in coef}, 'coefficients': {k: list(map(float, coef[k][1:])) for k in coef},
               'ovrAnchorsNetPer100': anchors, 'creationDefinition': 'self-created FGA per 36 = (1 - receivedShare) * FGA/36, percentile-mapped to 40-99 as in scripts/build_season_league.js'}
    (OUT / 'formula.json').write_text(json.dumps(formula, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    order = np.argsort(-pred['net'])
    with open(OUT / 'ranking.csv', 'w', encoding='utf-8', newline='') as fh:
        wr = csv.writer(fh)
        wr.writerow(['rank', 'cardOvr', 'finalOvr', 'name', 'pos', 'MIN', 'cardNet', 'cardO', 'cardD', 'finalNet'] + cal.ATTRS)
        for k, i in enumerate(order):
            r = data[i]
            wr.writerow([k + 1, round(ovr[i]), round(r['finalOvr']), r['name'], r['pos'], round(r['MIN']), round(pred['net'][i], 2), round(pred['O'][i], 2), round(pred['D'][i], 2), round(r['net'], 2)]
                        + [round(r['card'][a], 1) for a in cal.ATTRS])
    print(json.dumps({k: summary[k] for k in ['chosen', 'spearmanWithFinalOVR', 'meanAbsOvrGapAtLeast500Minutes']}, indent=1))
    print('cv', {k: round(v, 3) for k, v in grid.items()})
    print('per10', {a: (round(v['net'], 2), round(v['O'], 2), round(v['D'], 2)) for a, v in per10.items()})


if __name__ == '__main__':
    main()

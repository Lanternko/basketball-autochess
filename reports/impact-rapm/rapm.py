"""Real player impact from play-by-play stints: on/off ratings and RAPM (local data required).

  python3 reports/impact-rapm/rapm.py                 # 2022-23 .. 2025-26
  python3 reports/impact-rapm/rapm.py --self-test     # synthetic stints with known effects

Input: the local stint files written by scripts/prepare_defense_b1.js
  2025-26  reports/defense-b1/stints.jsonl
  others   reports/defense-seventh/<season>/stints/stints.jsonl
Each stint has teams[i] = {teamId, players[5], opponent{points,...}, defensivePossessions};
teams[i].opponent holds what the OTHER team scored while team i defended.

Outputs (reports/impact-rapm/):
  onoff.csv          per player-season: on/off offensive, defensive and net rating per 100
  rapm.csv           per player: ridge-regularised offensive / defensive / net impact per 100
  rapm-summary.json  chosen ridge strength, cross-validated error, comparison with the
                     simulated board and both OVR prototypes (2025-26 players)

Model: for every stint and side, y = 100 * points / possessions, weight = possessions,
y = mu + sum(offense players' O) - sum(defense players' D); a player's net impact = O + D,
positive D means fewer points allowed. Ridge strength is chosen by 5-fold cross-validation
grouped by game, so a game never sits in both train and test. Pooled RAPM uses all seasons
with one coefficient per player; the 2025-26 RAPM uses that season only.
"""
import csv, json, sys, unicodedata, zlib
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']
LAMBDAS = [100, 300, 1000, 3000, 10000, 30000]
FOCUS = ['Jalen Brunson', 'Cade Cunningham', 'Stephen Curry', 'Victor Wembanyama', 'Nikola Jokić', 'Luka Dončić',
         'Anthony Edwards', 'Cormac Ryan', 'Charles Bassey', 'Robert Williams III', 'John Konchar']


def stint_path(season):
    return ROOT / ('reports/defense-b1/stints.jsonl' if season == '2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')


def observations(seasons, reader=None):
    """Yield (season, gameId, offensePlayers, defensePlayers, points, possessions, offenseTeam, defenseTeam)."""
    for season in seasons:
        lines = reader(season) if reader else open(stint_path(season), encoding='utf-8')
        for line in lines:
            s = json.loads(line) if isinstance(line, str) else line
            if s['seconds'] <= 0 or len(s['teams']) != 2:
                continue
            for d in (0, 1):
                defense, offense = s['teams'][d], s['teams'][1 - d]
                poss = defense['defensivePossessions']
                if poss <= 0:
                    continue
                yield season, s['id'], offense['players'], defense['players'], defense['opponent']['points'], poss, offense['teamId'], defense['teamId']


def onoff(obs):
    """On/off ratings per player-season-team; off = same team's possessions without the player."""
    team = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])  # offPts, offPoss, defPts, defPoss
    on = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for season, _, op, dp, pts, poss, ot, dt in obs:
        t = team[(season, ot)]; t[0] += pts; t[1] += poss
        t = team[(season, dt)]; t[2] += pts; t[3] += poss
        for p in op:
            o = on[(season, ot, p)]; o[0] += pts; o[1] += poss
        for p in dp:
            o = on[(season, dt, p)]; o[2] += pts; o[3] += poss
    rows = []
    for (season, tid, pid), o in on.items():
        t = team[(season, tid)]
        off = [t[i] - o[i] for i in range(4)]
        r = lambda a, b: 100 * a / b if b > 0 else None
        rows.append({'season': season, 'teamId': tid, 'playerId': pid, 'onPoss': o[1] + o[3], 'offPoss': off[1] + off[3],
                     'onORtg': r(o[0], o[1]), 'onDRtg': r(o[2], o[3]), 'offORtg': r(off[0], off[1]), 'offDRtg': r(off[2], off[3])})
    for x in rows:
        if None not in (x['onORtg'], x['onDRtg'], x['offORtg'], x['offDRtg']):
            x['onNet'] = x['onORtg'] - x['onDRtg']; x['offNet'] = x['offORtg'] - x['offDRtg']; x['onOffNet'] = x['onNet'] - x['offNet']
    return rows


def normal_equations(obs, index, n_folds=5):
    """Accumulate X'WX and X'Wy per game fold; columns [O_0..O_P-1, D_0..D_P-1]."""
    P = len(index); K = 2 * P
    XtX = np.zeros((n_folds, K + 1, K + 1)); Xty = np.zeros((n_folds, K + 1)); yy = np.zeros(n_folds); wsum = np.zeros(n_folds)
    fold_of = {}
    for _, gid, op, dp, pts, poss, _, _ in obs:
        f = fold_of.setdefault(gid, zlib.crc32(str(gid).encode()) % n_folds)  # stable across runs
        cols = [K] + [index[p] for p in op] + [P + index[p] for p in dp]
        sign = np.array([1.0] + [1.0] * len(op) + [-1.0] * len(dp))
        y = 100 * pts / poss
        XtX[f][np.ix_(cols, cols)] += poss * np.outer(sign, sign)
        Xty[f][cols] += poss * y * sign
        yy[f] += poss * y * y; wsum[f] += poss
    return XtX, Xty, yy, wsum


def solve(A, b, lam, K):
    pen = lam * np.eye(A.shape[0]); pen[K, K] = 0  # intercept unpenalised
    return np.linalg.solve(A + pen, b)


def fit_rapm(obs, players):
    index = {p: i for i, p in enumerate(players)}
    K = 2 * len(players)
    XtX, Xty, yy, wsum = normal_equations(obs, index)
    cv = {}
    for lam in LAMBDAS:
        sse = 0.0
        for f in range(XtX.shape[0]):
            tr = [g for g in range(XtX.shape[0]) if g != f]
            b = solve(XtX[tr].sum(0), Xty[tr].sum(0), lam, K)
            sse += yy[f] - 2 * b @ Xty[f] + b @ XtX[f] @ b  # weighted SSE on the held-out fold
        cv[lam] = float(sse / wsum.sum())
    lam = min(cv, key=cv.get)
    b = solve(XtX.sum(0), Xty.sum(0), lam, K)
    poss = np.diag(XtX.sum(0))[:K]
    out = {p: {'O': float(b[i]), 'D': float(b[len(players) + i]), 'poss': float(poss[i] + poss[len(players) + i])} for p, i in index.items()}
    for v in out.values():
        v['net'] = v['O'] + v['D']
    return out, {'lambda': lam, 'cvWeightedMSE': cv, 'intercept': float(b[K])}


def spearman(a, b):
    def rank(v):
        o = np.argsort(v); r = np.empty(len(v)); r[o] = np.arange(len(v)); return r
    return float(np.corrcoef(rank(np.array(a)), rank(np.array(b)))[0, 1])


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().replace('.', '').replace(' iii', '').replace(' jr', '')


def compare(rapm, names):
    """2025-26 players: RAPM vs simulated board and both OVR prototypes (rank correlations)."""
    boards = {
        'simulatedCentered': ('reports/ovr-v47-2025-26/centered-ranking.csv', 'rank'),
        'simulatedShrunk': ('reports/ovr-v47-2025-26/shrunk-ranking.csv', 'rank'),
        'calibratedOVR': ('reports/ovr-calibrated-2025-26/ranking.csv', 'rank'),
        'expectedProductionOVR': ('reports/ovr-expected-2025-26/ranking.csv', 'rank'),
    }
    by_name = {fold(names[p]): v for p, v in rapm.items() if p in names}
    result = {}
    for label, (path, key) in boards.items():
        f = ROOT / path
        if not f.exists():
            continue
        rows = [r for r in csv.DictReader(open(f, encoding='utf-8')) if fold(r['name']) in by_name and by_name[fold(r['name'])]['poss'] >= 2000]
        result[label] = {'players': len(rows), 'spearmanWithNetRAPM': spearman([-int(r[key]) for r in rows], [by_name[fold(r['name'])]['net'] for r in rows])}
        # Rank of each board for the top-25 RAPM players and the players discussed so far.
        ranks = {fold(r['name']): int(r[key]) for r in csv.DictReader(open(f, encoding='utf-8'))}
        for n in sorted(by_name, key=lambda n: -by_name[n]['net'])[:25] + [fold(x) for x in FOCUS]:
            if n in by_name:
                result.setdefault('players', {}).setdefault(n, {'netRAPM': round(by_name[n]['net'], 2), 'possessions': round(by_name[n]['poss'])})[label] = ranks.get(n)
    return result


def run(seasons, reader=None, write=True):
    obs = list(observations(seasons, reader))
    players = sorted({p for o in obs for p in o[2] + o[3]})
    league = json.loads((ROOT / 'data/season-league.json').read_text(encoding='utf-8')) if write else {'teams': []}
    names = {p['playerId']: p['name'] for t in league['teams'] for p in t['roster']}
    pooled, pooled_fit = fit_rapm(obs, players)
    last = [o for o in obs if o[0] == seasons[-1]]
    single, single_fit = fit_rapm(last, sorted({p for o in last for p in o[2] + o[3]}))
    if not write:
        return pooled, pooled_fit
    with open(OUT / 'onoff.csv', 'w', encoding='utf-8', newline='') as fh:
        rows = onoff(obs)
        w = csv.DictWriter(fh, fieldnames=['season', 'teamId', 'playerId', 'name', 'onPoss', 'offPoss', 'onORtg', 'onDRtg', 'onNet', 'offORtg', 'offDRtg', 'offNet', 'onOffNet'])
        w.writeheader()
        for r in rows:
            w.writerow({**r, 'name': names.get(r['playerId'], '')})
    with open(OUT / 'rapm.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['playerId', 'name', 'pooledNet', 'pooledO', 'pooledD', 'pooledPoss', 'lastSeasonNet', 'lastSeasonO', 'lastSeasonD', 'lastSeasonPoss'])
        for p in sorted(pooled, key=lambda p: -pooled[p]['net']):
            a, s = pooled[p], single.get(p, {})
            w.writerow([p, names.get(p, ''), round(a['net'], 3), round(a['O'], 3), round(a['D'], 3), round(a['poss']),
                        round(s.get('net', 0), 3), round(s.get('O', 0), 3), round(s.get('D', 0), 3), round(s.get('poss', 0))])
    summary = {'seasons': seasons, 'observations': len(obs), 'players': len(players),
               'pooled': pooled_fit, 'lastSeason': single_fit,
               'comparison2025_26': {'pooledRAPM': compare(pooled, names), 'lastSeasonRAPM': compare(single, names)}}
    (OUT / 'rapm-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=1))


def self_test():
    """Synthetic league with known O/D effects: RAPM must recover them better than chance."""
    rng = np.random.default_rng(7)
    P = 150; trueO = rng.normal(0, 2.5, P); trueD = rng.normal(0, 2.0, P)
    teams = [list(range(i * 15, i * 15 + 15)) for i in range(10)]
    stints = []
    for g in range(1200):
        a, b = rng.choice(10, 2, replace=False)
        for k in range(20):
            la, lb = list(rng.choice(teams[a], 5, replace=False)), list(rng.choice(teams[b], 5, replace=False))
            sides = []
            for off, de in ((la, lb), (lb, la)):
                poss = float(rng.integers(3, 9))
                rate = 1.12 + (trueO[off].sum() - trueD[de].sum()) / 100
                sides.append({'teamId': 0, 'players': [int(x) for x in de], 'opponent': {'points': float(rng.poisson(rate * poss))}, 'defensivePossessions': poss})
            stints.append({'id': f'g{g}', 'seconds': 100, 'teams': sides})
    fit, info = run(['synthetic'], reader=lambda s: stints, write=False)
    estO = np.array([fit[p]['O'] for p in range(P)]); estD = np.array([fit[p]['D'] for p in range(P)])
    r = {'corrO': float(np.corrcoef(estO, trueO)[0, 1]), 'corrD': float(np.corrcoef(estD, trueD)[0, 1]),
         'corrNet': float(np.corrcoef(estO + estD, trueO + trueD)[0, 1]), 'lambda': info['lambda']}
    print(json.dumps(r))
    assert r['corrNet'] > 0.5, 'RAPM failed to recover synthetic effects'


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        self_test()
    else:
        run(SEASONS)

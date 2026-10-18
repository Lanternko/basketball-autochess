"""Expected-production OVR (2025-26): a transparent, instant rating that does not run games.

Basketball analogue of a wOBA-style rating: each counted event gets a fixed point value
expressed through league points per possession (PPP), every player's net value is computed
per 100 on-court possessions, noisy small samples are shrunk, then mapped to the
PR1=40 / PR50=70 / PR99=99 display scale used by the baseball calculator.

  python3 reports/ovr-expected-2025-26/expected-ovr.py

Components (points per 100 possessions, before centering):
  scoring   PTS - REPL * lgPTS/TSA * TSA          volume above replacement efficiency
  assists   (AST - receivedShare * FGM) * W_AST * lgPTS/FGM
            the assister's share of an assisted basket moves from scorer to passer, so assist
            credit is zero-sum; receivedShare = source share of a player's shots that came
            from a teammate's pass (v41 validation export, creationDependence_sourceRole)
  turnovers -TOV * PPP
  rebounds  OREB * W_OREB * PPP + DREB * W_DREB * PPP
  defense   STL * PPP - PF * W_PF
  rim/shot  W_ONOFF * opponent points per FGA saved on court vs off court (v45 actual
            on/off shooting, 2025-26); relative to the player's own team, not causal
Inputs are observed facts only; no simulation output feeds the rating.
"""
import csv, json, math, statistics as st, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
WEIGHTS = {'REPL': 0.92, 'W_AST': 0.25, 'W_OREB': 0.5, 'W_DREB': 0.2, 'W_PF': 0.35, 'W_ONOFF': 0.5}
SCALE_MIN_MINUTES = 500
LEAGUE_3P = 0.36


def load(weights):
    league = json.loads((ROOT / 'data/season-league.json').read_text(encoding='utf-8'))
    onoff = {int(r['playerId']): r for r in csv.DictReader(open(ROOT / 'reports/player-impact-v45/2025-26-defense-players.csv', encoding='utf-8-sig')) if r['variant'] == 'v41'}
    received = {int(r['playerId']): float(r['creationDependence_sourceRole']) for r in csv.DictReader(open(ROOT / 'reports/player-impact-v41/2025-26-player-validation.csv', encoding='utf-8-sig'))}
    L = defaultdict(float)
    teams = []
    for t in league['teams']:
        tot = defaultdict(float)
        for p in t['roster']:
            for k, v in p['observed'].items():
                tot[k] += v
        poss = tot['FGA'] - tot['OREB'] + tot['TOV'] + 0.44 * tot['FTA']
        teams.append({'id': t['id'], 'name': t['name'], 'roster': t['roster'], 'poss': poss, 'min': tot['MIN'],
                      'net100': t['observed']['PLUS_MINUS'] / poss * 100})
        for k, v in tot.items():
            L[k] += v
        L['POSS'] += poss
    lg = {'PPP': L['PTS'] / L['POSS'], 'PTS_TSA': L['PTS'] / (L['FGA'] + 0.44 * L['FTA']), 'PTS_FGM': (L['PTS'] - L['FTM']) / L['FGM']}
    return league, onoff, received, teams, lg


def stint_values(teams, received, lg, w):
    """Per player-team stint: raw component totals and their Poisson-style sampling variance."""
    rows = []
    for t in teams:
        for p in t['roster']:
            o = p['observed']
            if o['MIN'] <= 0:
                continue
            poss = o['MIN'] * t['poss'] / (t['min'] / 5)
            tsa = o['FGA'] + 0.44 * o['FTA']
            off = {
                'scoring': o['PTS'] - w['REPL'] * lg['PTS_TSA'] * tsa,
                'assists': (o['AST'] - received[p['playerId']] * o['FGM']) * w['W_AST'] * lg['PTS_FGM'],
                'turnovers': -o['TOV'] * lg['PPP'],
                'rebounds': o['OREB'] * w['W_OREB'] * lg['PPP'] + o['DREB'] * w['W_DREB'] * lg['PPP'],
                'defenseBox': o['STL'] * lg['PPP'] - o['PF'] * w['W_PF'],
            }
            # Per-attempt scoring variance ~1.3 points^2; counted events treated as Poisson.
            var = (1.3 * tsa + (w['W_AST'] * lg['PTS_FGM']) ** 2 * o['AST'] + lg['PPP'] ** 2 * (o['TOV'] + o['STL'])
                   + (w['W_OREB'] * lg['PPP']) ** 2 * o['OREB'] + (w['W_DREB'] * lg['PPP']) ** 2 * o['DREB'] + w['W_PF'] ** 2 * o['PF'])
            rows.append({'playerId': p['playerId'], 'name': p['name'], 'team': t['name'], 'pos': p['pos'], 'MIN': o['MIN'], 'GP': o['GP'],
                         'poss': poss, 'off': off, 'offVar': var})
    return rows


def onoff_value(r, w):
    """Opponent points per 100 possessions saved while on court, plus its sampling variance."""
    if r is None or any(r[f'{side}{k}_actual'] == '' for side in ('on', 'off') for k in ('FGpct', 'longShare', 'FGA48')):
        return 0.0, None  # no usable on/off shooting sample
    f = lambda k: float(r[k])
    # Points per FGA = 2*FG% + 3PA share * 3P%. Zone FG% columns are blank when that side had too few
    # attempts in the zone; overall FG% is always present and a blank 3P% falls back to the league rate.
    three = lambda side: f(f'{side}longFGpct_actual') / 100 if r[f'{side}longFGpct_actual'] != '' else LEAGUE_3P
    pps = lambda side: 2 * f(f'{side}FGpct_actual') / 100 + f(f'{side}longShare_actual') / 100 * three(side)
    on_fga = f('onFGA48_actual') * f('minutes') / 48
    off_min = max(f('minutes'), 82 * 48 - f('minutes'))
    off_fga = f('offFGA48_actual') * off_min / 48
    saved_per_fga = pps('off') - pps('on')
    fga_per100 = f('onFGA48_actual') / 48 * 48 * 100 / 99.0  # ~99 possessions per 48 minutes
    value = w['W_ONOFF'] * saved_per_fga * fga_per100
    se_pps = math.sqrt(1.25 / max(on_fga, 1) + 1.25 / max(off_fga, 1))
    return value, (w['W_ONOFF'] * se_pps * fga_per100) ** 2


def wls(xs, ys, ws):
    sw = sum(ws); mx = sum(a * c for a, c in zip(xs, ws)) / sw; my = sum(b * c for b, c in zip(ys, ws)) / sw
    b = sum(c * (a - mx) * (y - my) for a, y, c in zip(xs, ys, ws)) / sum(c * (a - mx) ** 2 for a, c in zip(xs, ws))
    return my - b * mx, b


def shrink(players, key, var_key):
    """Empirical Bayes toward a role prior on log minutes per game; tau^2 by method of moments."""
    xs = [math.log(p['mpg']) for p in players]
    a, b = wls(xs, [p[key] for p in players], [1 / p[var_key] for p in players])
    tau2 = 1.0
    for _ in range(50):
        ws = [1 / (tau2 + p[var_key]) for p in players]
        resid = [(p[key] - a - b * x) ** 2 - p[var_key] for p, x in zip(players, xs)]
        tau2 = max(1e-6, sum(r * c for r, c in zip(resid, ws)) / sum(ws))
    for p, x in zip(players, xs):
        B = tau2 / (tau2 + p[var_key])
        p[key + 'Shrunk'] = a + b * x + B * (p[key] - a - b * x)
        p[key + 'B'] = B
    return {'priorIntercept': a, 'priorLogMpgSlope': b, 'tau2': tau2}


def build(weights=WEIGHTS):
    league, onoff, received, teams, lg = load(weights)
    stints = stint_values(teams, received, lg, weights)
    by = defaultdict(list)
    for s in stints:
        by[s['playerId']].append(s)
    players = []
    for pid, ss in by.items():
        poss = sum(s['poss'] for s in ss)
        mins = sum(s['MIN'] for s in ss)
        comp = {k: sum(s['off'][k] for s in ss) / poss * 100 for k in ss[0]['off']}
        d, dv = onoff_value(onoff.get(pid), weights)
        players.append({'playerId': pid, 'name': ss[0]['name'], 'pos': ss[-1]['pos'], 'teams': ' / '.join(s['team'] for s in ss),
                        'MIN': mins, 'GP': sum(s['GP'] for s in ss), 'mpg': mins / sum(s['GP'] for s in ss), 'poss': poss,
                        'components': comp, 'offense': sum(comp.values()), 'offenseVar': sum(s['offVar'] for s in ss) / poss ** 2 * 1e4,
                        'onoff': d, 'onoffVar': dv if dv is not None else 1e6})
    # Center so the minute-weighted league player is 0 per 100 possessions.
    for key in ['offense', 'onoff']:
        m = sum(p[key] * p['MIN'] for p in players) / sum(p['MIN'] for p in players)
        for p in players:
            p[key] -= m
    fits = {'offense': shrink(players, 'offense', 'offenseVar'), 'onoff': shrink(players, 'onoff', 'onoffVar')}
    for p in players:
        p['net'] = p['offenseShrunk'] + p['onoffShrunk']
        p['netRaw'] = p['offense'] + p['onoff']
    # Display scale: PR1=40, PR50=70, PR99=99 among players with enough minutes.
    ref = sorted(p['net'] for p in players if p['MIN'] >= SCALE_MIN_MINUTES)
    q = lambda pr: ref[min(len(ref) - 1, max(0, round(pr / 100 * (len(ref) - 1))))]
    p1, p50, p99 = q(1), q(50), q(99)
    for p in players:
        x = p['net']
        p['ovr'] = 40 + 30 * (x - p1) / (p50 - p1) if x <= p50 else 70 + 29 * (x - p50) / (p99 - p50)
    players.sort(key=lambda p: -p['net'])
    for i, p in enumerate(players):
        p['rank'] = i + 1
    return players, teams, lg, fits, (p1, p50, p99)


def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); out = [0] * len(v)
        for k, i in enumerate(order):
            out[i] = k
        return out
    return st.correlation(rank(a), rank(b))


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().replace('.', '').replace(' iii', '').replace(' jr', '')


def main():
    players, teams, lg, fits, anchors = build()
    byid = {p['playerId']: p for p in players}
    # Team check: minute-weighted raw player values vs actual net per 100. On/off sums to ~0 within a team,
    # so this only tests the box part; it is not a test of individual defense.
    pred, act = [], []
    for t in teams:
        pred.append(sum(byid[p['playerId']]['offense'] * p['observed']['MIN'] for p in t['roster'] if p['playerId'] in byid) * 5 / t['min'])
        act.append(t['net100'])
    team_r = st.correlation(pred, act)
    # External references (not truth): simulated v47 board after centering + shrinkage, preseason media.
    sim = {r['name']: float(r['shrunk_contribution']) for r in csv.DictReader(open(ROOT / 'reports/ovr-v47-2025-26/shrunk-ranking.csv', encoding='utf-8'))}
    names = [p['name'] for p in players if p['name'] in sim]
    media = json.loads((ROOT / 'reports/model-evolution-20261016/media-ranks.json').read_text(encoding='utf-8'))
    byfold = {fold(p['name']): p for p in players}
    mm = [(byfold[fold(m['name'])]['net'], -st.mean(m['ranks'].get(k, 101) for k in media['selectedMedia'])) for m in media['players'] if fold(m['name']) in byfold]
    # Sensitivity: every judgement weight at x0.5 and x1.5 (REPL moves its gap to 1).
    base = {p['playerId']: p['net'] for p in players}
    top20 = {p['playerId'] for p in players[:20]}
    sens = {}
    for k, v in WEIGHTS.items():
        for mult in (0.5, 1.5):
            alt = dict(WEIGHTS)
            alt[k] = 1 - (1 - v) * mult if k == 'REPL' else v * mult
            ps = build(alt)[0]
            ids = [p['playerId'] for p in ps]
            sens[f'{k}x{mult}'] = {'spearman': spearman([base[i] for i in ids], [p['net'] for p in ps]),
                                  'top20Overlap': len(top20 & {p['playerId'] for p in ps[:20]})}
    summary = {
        'weights': WEIGHTS, 'league': lg, 'scaleAnchorsNetPer100': {'PR1': anchors[0], 'PR50': anchors[1], 'PR99': anchors[2]},
        'shrinkage': fits, 'players': len(players),
        'teamBoxCorrelation': team_r,
        'spearmanWithSimulatedBoard': spearman([byfold[fold(n)]['net'] for n in names], [sim[n] for n in names]),
        'spearmanWithMedia': {'r': spearman([a for a, _ in mm], [b for _, b in mm]), 'matched': len(mm)},
        'sensitivity': sens,
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    with open(OUT / 'ranking.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        keys = list(players[0]['components'])
        w.writerow(['rank', 'ovr', 'name', 'pos', 'teams', 'GP', 'MIN', 'netPer100', 'netRawPer100', 'offenseShrunk', 'onoffShrunk', 'offenseShrinkFactor', 'onoffShrinkFactor'] + keys)
        for p in players:
            w.writerow([p['rank'], round(p['ovr'], 1), p['name'], p['pos'], p['teams'], p['GP'], round(p['MIN']), round(p['net'], 2), round(p['netRaw'], 2),
                        round(p['offenseShrunk'], 2), round(p['onoffShrunk'], 2), round(p['offenseB'], 3), round(p['onoffB'], 3)] + [round(p['components'][k], 2) for k in keys])
    print(json.dumps({k: v for k, v in summary.items() if k != 'sensitivity'}, ensure_ascii=False, indent=1))
    print(json.dumps(sens))


if __name__ == '__main__':
    main()

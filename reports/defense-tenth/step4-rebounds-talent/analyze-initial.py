"""Registered, individual-only signal analysis. Never imports the game engine."""
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
from scipy.stats import rankdata

from register import ROOT, HERE, sha, dump

read = lambda path: json.loads(path.read_text(encoding='utf-8'))
STATIC = ['height', 'mass', 'wingspan', 'reach']
ATHLETIC = ['standingJump', 'runningJump', 'bench', 'agility', 'shuttle', 'sprint', 'testAge']
BEHAVIOR = ['speedOff', 'speedDef', 'chances36', 'contestedShare']
TESTS = {'wingspan': 'WINGSPAN', 'reach': 'STANDING_REACH', 'standingJump': 'STANDING_VERTICAL_LEAP',
         'runningJump': 'MAX_VERTICAL_LEAP', 'bench': 'BENCH_PRESS', 'agility': 'LANE_AGILITY_TIME',
         'shuttle': 'MODIFIED_LANE_AGILITY_TIME', 'sprint': 'THREE_QUARTER_SPRINT'}


def table(doc):
    sets = doc['data'].get('resultSets', doc['data'].get('resultSet'))
    s = sets[0] if isinstance(sets, list) else sets
    return [dict(zip(s['headers'], r)) for r in s['rowSet']]


def number(value, zero=False):
    if value is None or isinstance(value, bool):
        return None
    try:
        x = float(value)
        return x if math.isfinite(x) and (x >= 0 if zero else x > 0) else None
    except (ValueError, TypeError):
        return None


def correlation(x, y):
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def prepare(p):
    manifest = read(HERE / 'fetch-manifest.json')
    assert manifest['done'] == manifest['jobs'], 'Acquisition incomplete'
    for source in manifest['sources']:
        assert sha(ROOT / source['file']) == source['sha256']
    tests = defaultdict(list)
    unmatched = 0
    for source in manifest['sources']:
        if source['kind'] not in p['acquisition']['endpoints']:
            continue
        for row in table(read(ROOT / source['file'])):
            pid = number(row.get('PLAYER_ID'))
            if pid is None:
                unmatched += 1
                continue
            tests[int(pid)].append((source['year'], row, source['file']))
    seasons, coverage, associations, join_issues = {}, [], [], []
    for season in p['seasons']:
        folder = ROOT / f'data/defense-seventh/{season}'
        logs = table(read(ROOT / 'data/season-source/player-games.json' if season == '2025-26' else folder / 'player-games.json'))
        bio = {r['PLAYER_ID']: r for r in table(read(ROOT / 'data/benchmark-source/bio.json' if season == '2025-26' else folder / 'bio.json'))}
        advanced_rows = table(read(ROOT / f'reports/defense-tenth/step4-t2/raw/{season}/0-advanced.json'))
        assert len({r['PLAYER_ID'] for r in advanced_rows}) == len(advanced_rows)
        advanced = {r['PLAYER_ID']: r for r in advanced_rows}
        groups = defaultdict(list)
        for r in logs:
            if (r.get('MIN') or 0) > 0:
                groups[r['PLAYER_ID']].append(r)
        tracks = {}
        for kind in p['acquisition']['tracking']:
            path = HERE / f'raw/tracking/{season}-{kind}.json'
            rows = table(read(path)) if path.exists() else []
            if len({r['PLAYER_ID'] for r in rows}) != len(rows):
                join_issues.append({'season': season, 'kind': kind, 'issue': 'Duplicate player tracking rows; excluded ambiguous IDs'})
            by = defaultdict(list)
            for r in rows:
                by[r['PLAYER_ID']].append(r)
            tracks[kind] = {pid: rs[0] for pid, rs in by.items() if len(rs) == 1}
        cohort = []
        for pid, games in sorted(groups.items()):
            games.sort(key=lambda r: (r['GAME_DATE'], r['GAME_ID']))
            total_min = sum(r['MIN'] for r in games)
            oreb = sum(r.get('OREB') or 0 for r in games)
            team_min = defaultdict(float)
            for g in games:
                team_min[g['TEAM_ID']] += g['MIN']
            main_team = max(team_min, key=lambda k: (team_min[k], -k))
            b = bio.get(pid, {})
            row = {'id': pid, 'name': games[0]['PLAYER_NAME'], 'season': season, 'minutes': total_min,
                   'oreb': oreb, 'rate': oreb / total_min * 36,
                   'pct': (advanced[pid]['OREB_PCT'] * 100 if pid in advanced and advanced[pid].get('OREB_PCT') is not None else None),
                   'team': main_team, 'height': number(b.get('PLAYER_HEIGHT_INCHES')),
                   'mass': number(b.get('PLAYER_WEIGHT')), 'games': games,
                   'measurementSources': {}, 'measurementYears': {}}
            eligible = [t for t in tests.get(pid, []) if t[0] <= int(season[:4])]
            for key, field in TESTS.items():
                obs = [(year, number(r.get(field), zero=key == 'bench'), source)
                       for year, r, source in eligible]
                obs = [r for r in obs if r[1] is not None]
                selected = max(obs, key=lambda r: r[0]) if obs else None
                row[key] = selected[1] if selected else None
                if selected:
                    row['measurementSources'][key] = selected[2]
                    row['measurementYears'][key] = selected[0]
            years = list(row['measurementYears'].values())
            row['testAge'] = int(season[:4]) - max(years) if years else None
            reb = tracks['Rebounding'].get(pid, {})
            speed = tracks['SpeedDistance'].get(pid, {})
            row['speedOff'], row['speedDef'] = number(speed.get('AVG_SPEED_OFF')), number(speed.get('AVG_SPEED_DEF'))
            row['chances36'] = reb.get('OREB_CHANCES', 0) / reb['MIN'] * 36 if (reb.get('MIN') or 0) > 0 else None
            row['contestedShare'] = number(reb.get('OREB_CONTEST_PCT'), zero=True)
            row['trackingRebMinutes'], row['trackingSpeedMinutes'] = reb.get('MIN') or 0, speed.get('MIN') or 0
            row['trackingRebGP'], row['trackingSpeedGP'] = reb.get('GP') or 0, speed.get('GP') or 0
            cohort.append(row)
        seasons[season] = cohort
        all_min = sum(r['minutes'] for r in cohort)
        cov = {}
        for f in STATIC + ATHLETIC + BEHAVIOR:
            observed = [r for r in cohort if r[f] is not None]
            cov[f] = {'n': len(observed), 'players': len(cohort),
                      'minuteCoverage': sum(r['minutes'] for r in observed) / all_min}
        coverage.append({'season': season, 'players': len(cohort), 'fields': cov,
                         'trackedReboundMinuteFraction': sum(min(r['minutes'], r['trackingRebMinutes']) for r in cohort) / all_min,
                         'trackedSpeedMinuteFraction': sum(min(r['minutes'], r['trackingSpeedMinutes']) for r in cohort) / all_min,
                         'testAgeMedian': float(np.median([r['testAge'] for r in cohort if r['testAge'] is not None])),
                         'testAgeMax': max((r['testAge'] for r in cohort if r['testAge'] is not None), default=None)})
        for f in STATIC + ATHLETIC + BEHAVIOR:
            for target in ['rate', 'pct']:
                valid = [r for r in cohort if r['minutes'] >= 500 and r[f] is not None and r[target] is not None]
                x, y = [r[f] for r in valid], [r[target] for r in valid]
                associations.append({'season': season, 'feature': f, 'target': target, 'n': len(valid),
                                     'Pearson': correlation(x, y), 'Spearman': correlation(rankdata(x), rankdata(y))})
    dump(HERE / 'coverage.json', {'seasons': coverage, 'unmatchedCombineRows': unmatched,
                                 'joinIssues': join_issues, 'requestFailures': manifest['failures']})
    dump(HERE / 'associations.json', {'label': 'Descriptive, same-season and observed-only; not causal/incremental', 'rows': associations})
    # Persist only personal features/exposure; raw official game logs remain unchanged.
    dump(HERE / 'features.json', {s: [{k: v for k, v in r.items() if k != 'games'} for r in rows] for s, rows in seasons.items()})
    return seasons


def cross_rows(seasons, source, target, outcome):
    before = {r['id']: r for r in seasons[source]}
    result = []
    for r in seasons[target]:
        q = before.get(r['id'])
        if q is None or min(q['minutes'], r['minutes']) < 100 or q[outcome] is None or r[outcome] is None:
            continue
        if q['pct'] is None:
            continue
        result.append({'id': r['id'], 'name': r['name'], 'season': target, 'sourceSeason': source,
                       'team': r['team'], 'y': r[outcome], 'prior': q[outcome],
                       'sourceMinutes': q['minutes'], 'targetMinutes': r['minutes'], 'priorPct': q['pct'],
                       'logMinutes': math.log1p(q['minutes']), 'mover': q['team'] != r['team'],
                       **{f: q[f] for f in STATIC + ATHLETIC + BEHAVIOR}})
    return result


def within_rows(seasons, season, k):
    result = []
    for r in seasons[season]:
        early, late = r['games'][:k], r['games'][k:]
        em, lm = sum(g['MIN'] for g in early), sum(g['MIN'] for g in late)
        if min(em, lm) < 100:
            continue
        team_min = defaultdict(float)
        for g in late:
            team_min[g['TEAM_ID']] += g['MIN']
        team = max(team_min, key=lambda x: (team_min[x], -x))
        result.append({'id': r['id'], 'name': r['name'], 'season': season, 'team': team,
                       'y': 36 * sum(g.get('OREB') or 0 for g in late) / lm,
                       'prior': 36 * sum(g.get('OREB') or 0 for g in early) / em,
                       'sourceMinutes': em, 'targetMinutes': lm, 'logMinutes': math.log1p(em),
                       **{f: r[f] for f in STATIC + ATHLETIC}})
    return result


def columns(model, task, outcome):
    base = ['prior', 'logMinutes']
    if task == 'cross' and outcome == 'rate':
        base += ['priorPct']
    if model == 'orebPctOnly':
        return ['priorPct', 'logMinutes'] if task == 'cross' else ['prior', 'logMinutes']
    if model == 'history':
        return base
    if model == 'static':
        return base + STATIC
    if model == 'talent':
        return base + STATIC + ATHLETIC
    if model == 'talentOnly':
        return ['logMinutes'] + STATIC + ATHLETIC
    if model == 'missingOnly':
        return base + ['missing_' + f for f in STATIC + ATHLETIC if f != 'testAge'] + ['testAge']
    if model == 'behavior':
        return base + STATIC + ATHLETIC + BEHAVIOR
    raise ValueError(model)


def matrix(rows, cols):
    return np.array([[float(r[f.removeprefix('missing_')] is None) if f.startswith('missing_')
                      else (r.get(f) if r.get(f) is not None else np.nan) for f in cols] for r in rows], dtype=float)


def transform(train, test):
    med = np.array([np.median(v[np.isfinite(v)]) if np.isfinite(v).any() else 0 for v in train.T])
    def impute(a):
        missing = ~np.isfinite(a)
        return np.concatenate([np.where(missing, med, a), missing.astype(float)], axis=1)
    a, b = impute(train), impute(test)
    mu, sd = a.mean(0), a.std(0)
    sd[sd < 1e-12] = 1
    return (a - mu) / sd, (b - mu) / sd


def fit(train, test, model, task, outcome, p):
    if model == 'persistence':
        return np.array([r['prior'] for r in test]), {'lambda': None, 'columns': []}
    cols = columns(model, task, outcome)
    a, b = matrix(train, cols), matrix(test, cols)
    y = np.array([r['y'] for r in train])
    w = np.array([min(r['targetMinutes'], 1000) for r in train])
    w /= w.mean()
    folds = np.array([int(hashlib.sha256(str(r['id']).encode()).hexdigest(), 16) % 5 for r in train])
    scores = []
    for ridge in p['prediction']['ridge']['grid']:
        errors = np.zeros(len(y))
        for fold in range(5):
            it, iv = folds != fold, folds == fold
            aa, bb = transform(a[it], a[iv])
            sw = np.sqrt(w[it])
            aa, bb = np.column_stack([np.ones(len(aa)), aa]), np.column_stack([np.ones(len(bb)), bb])
            penalty = np.diag([0] + [ridge] * (aa.shape[1] - 1))
            coef = np.linalg.solve((aa * sw[:, None]).T @ (aa * sw[:, None]) + penalty,
                                   (aa * sw[:, None]).T @ (y[it] * sw))
            errors[iv] = (bb @ coef - y[iv]) ** 2
        scores.append((float(np.average(errors, weights=w)), ridge))
    loss, ridge = min(scores, key=lambda x: (x[0], -x[1]))
    aa, bb = transform(a, b)
    aa, bb = np.column_stack([np.ones(len(aa)), aa]), np.column_stack([np.ones(len(bb)), bb])
    sw = np.sqrt(w)
    penalty = np.diag([0] + [ridge] * (aa.shape[1] - 1))
    coef = np.linalg.solve((aa * sw[:, None]).T @ (aa * sw[:, None]) + penalty,
                           (aa * sw[:, None]).T @ (y * sw))
    pred = bb @ coef
    pred = np.maximum(pred, 0)
    if outcome == 'pct':
        pred = np.minimum(pred, 100)
    return pred, {'lambda': ridge, 'CV_MSE': loss, 'columns': cols,
                  'standardizedCoefficients': coef.tolist(), 'trainRows': len(train), 'testRows': len(test),
                  'allCV': [{'MSE': loss, 'lambda': lam} for loss, lam in scores]}


def metrics(rows, pred):
    y = np.array([r['y'] for r in rows])
    minutes = np.array([r['targetMinutes'] for r in rows])
    error = pred - y
    return {'n': len(rows), 'MAE': float(np.average(abs(error), weights=minutes)),
            'RMSE': float(np.sqrt(np.average(error ** 2, weights=minutes))),
            'Pearson': correlation(pred, y),
            'conditionalCountMAE': float(np.mean(abs(error) * minutes / 36))}


def intervals(rows, predictions, p, outcome):
    rng = np.random.default_rng(p['prediction']['uncertainty']['seed'])
    B = p['prediction']['uncertainty']['replicates']
    ids = sorted({r['id'] for r in rows})
    teams = sorted({r['team'] for r in rows})
    id_index, team_index = {x: i for i, x in enumerate(ids)}, {x: i for i, x in enumerate(teams)}
    draws = rng.integers(0, len(teams), (B, len(teams)))
    fc = np.stack([(draws == i).sum(1) for i in range(len(teams))], axis=1)
    pc = rng.poisson(1, (B, len(ids)))
    weights = (fc[:, [team_index[r['team']] for r in rows]] * pc[:, [id_index[r['id']] for r in rows]]).astype(float)
    minutes = np.array([r['targetMinutes'] for r in rows])
    y = np.array([r['y'] for r in rows])
    wm = weights * minutes
    den = wm.sum(1)
    good = den > 0
    wm, den, weights = wm[good], den[good], weights[good]
    point, boots = {}, {}
    for model, pred in predictions.items():
        error = pred - y
        point[model] = metrics(rows, pred)
        if outcome == 'pct':
            point[model].pop('conditionalCountMAE')
        boots[model] = {'MAE': wm @ abs(error) / den,
                        'RMSE': np.sqrt(wm @ (error ** 2) / den)}
        if outcome == 'rate':
            boots[model]['conditionalCountMAE'] = weights @ (abs(error) * minutes / 36) / weights.sum(1)
    pairs = {}
    for model in predictions:
        if model == 'history':
            continue
        pairs[model + 'MinusHistory'] = {
            k: {'point': point[model][k] - point['history'][k],
                'joint95': np.quantile(boots[model][k] - boots['history'][k], [.025, .975]).tolist()}
            for k in boots[model]}
    if 'talent' in predictions and 'static' in predictions:
        pairs['talentMinusStatic'] = {k: {'point': point['talent'][k] - point['static'][k],
                                             'joint95': np.quantile(boots['talent'][k] - boots['static'][k], [.025, .975]).tolist()}
                                     for k in boots['talent']}
    return {'versions': point, 'paired': pairs, 'bootstrapValid': int(good.sum()), 'franchises': len(teams)}


def run():
    p = read(HERE / 'protocol.json')
    digest = (HERE / 'protocol.sha256').read_text(encoding='utf-8').split()[0]
    assert sha(HERE / 'protocol.json') == digest
    for file, expected in p['inputHashes'].items():
        assert sha(ROOT / file) == expected, file
    lock = read(HERE / 'analysis-code-registration.json')
    assert sha(HERE / 'analyze.py') == lock['sha256'], 'Analysis code changed'
    seasons = prepare(p)
    results, fits, predictions_out = {}, {}, {}
    for outcome in ['rate', 'pct']:
        train = cross_rows(seasons, '2022-23', '2023-24', outcome) + cross_rows(seasons, '2023-24', '2024-25', outcome)
        test = cross_rows(seasons, '2024-25', '2025-26', outcome)
        label = 'cross2025-' + outcome
        preds = {}
        fits[label] = {}
        for model in p['prediction']['models']:
            preds[model], fits[label][model] = fit(train, test, model, 'cross', outcome, p)
        groups = {'all': np.ones(len(test), dtype=bool),
                  'movers': np.array([r['mover'] for r in test]),
                  'stayers': np.array([not r['mover'] for r in test]),
                  'lowSourceMinutes': np.array([r['sourceMinutes'] < 500 for r in test]),
                  'both500': np.array([min(r['sourceMinutes'], r['targetMinutes']) >= 500 for r in test])}
        results[label] = {}
        for group, mask in groups.items():
            if mask.sum() >= 10:
                rows = [r for r, keep in zip(test, mask) if keep]
                results[label][group] = intervals(rows, {m: v[mask] for m, v in preds.items()}, p, outcome)
            else:
                results[label][group] = {'n': int(mask.sum()), 'status': 'Insufficient group (<10); not estimated'}
        predictions_out[label] = [{'id': r['id'], 'name': r['name'], 'team': r['team'], 'season': r['season'],
                                  'y': r['y'], 'sourceMinutes': r['sourceMinutes'], 'targetMinutes': r['targetMinutes'],
                                  'mover': r['mover'], 'predictions': {m: float(v[i]) for m, v in preds.items()}}
                                 for i, r in enumerate(test)]
        print(label, json.dumps({m: r['MAE'] for m, r in results[label]['all']['versions'].items()}), flush=True)
    for k in [20, 41]:
        pooled_rows, pooled_preds = [], defaultdict(list)
        for i, season in enumerate(p['seasons'][1:], start=1):
            train = [r for s in p['seasons'][:i] for r in within_rows(seasons, s, k)]
            test = within_rows(seasons, season, k)
            label = f'within{k}-{season}'
            fits[label], preds = {}, {}
            for model in p['prediction']['models']:
                if model == 'behavior':
                    continue
                preds[model], fits[label][model] = fit(train, test, model, 'within', 'rate', p)
                pooled_preds[model].extend(preds[model].tolist())
            results[label] = intervals(test, preds, p, 'rate')
            predictions_out[label] = [{'id': r['id'], 'team': r['team'], 'season': r['season'],
                                      'y': r['y'], 'sourceMinutes': r['sourceMinutes'], 'targetMinutes': r['targetMinutes'],
                                      'predictions': {m: float(v[j]) for m, v in preds.items()}}
                                     for j, r in enumerate(test)]
            pooled_rows.extend(test)
            print(label, 'done', len(test), flush=True)
        results[f'within{k}-pooled'] = intervals(pooled_rows, {m: np.array(v) for m, v in pooled_preds.items()}, p, 'rate')
    dump(HERE / 'predictions.json', predictions_out)
    dump(HERE / 'fits.json', fits)
    dump(HERE / 'results.json', {'at': datetime.now(timezone.utc).isoformat(), 'protocolSHA256': digest,
                                'label': p['label'], 'uncertainty': p['prediction']['uncertainty'], 'results': results})
    print('Complete', flush=True)


if __name__ == '__main__':
    run()

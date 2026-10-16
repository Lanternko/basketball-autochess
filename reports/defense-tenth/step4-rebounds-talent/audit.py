"""Integrity and estimate reconstruction checks; no model changes."""
from datetime import datetime, timezone
import numpy as np
from register import ROOT, HERE, sha, dump
from analyze import read, table, metrics, columns, STATIC, ATHLETIC

def main():
    p = read(HERE / 'protocol.json')
    checks = {}
    digest = (HERE / 'protocol.sha256').read_text(encoding='utf-8').split()[0]
    checks['protocolSHA256'] = sha(HERE / 'protocol.json') == digest
    checks['registrationCode'] = sha(HERE / 'register.py') == p['registrationCodeSHA256']
    checks['protectedManifest'] = sha(HERE / 'protected-before.json') == p['protectedManifestSHA256']
    before = read(HERE / 'protected-before.json')
    changed = [f for f, expected in before.items() if not (ROOT / f).is_file() or sha(ROOT / f) != expected]
    checks['protectedFilesUnchanged'] = not changed
    expected_files = set(before)
    new_protected = [f.relative_to(ROOT).as_posix() for scope in ['src', 'scripts', 'reports/defense-tenth']
                     for f in (ROOT / scope).rglob('*') if f.is_file() and HERE not in f.parents
                     and f.relative_to(ROOT).as_posix() not in expected_files]
    checks['noNewFilesInProtectedScopes'] = not new_protected
    checks['inputHashes'] = all(sha(ROOT / f) == h for f, h in p['inputHashes'].items())
    manifest = read(HERE / 'fetch-manifest.json')
    checks['all60Sources'] = manifest['jobs'] == manifest['done'] == len(manifest['sources']) == 60 and not manifest['failures']
    checks['rawSourceHashes'] = all(sha(ROOT / s['file']) == s['sha256'] for s in manifest['sources'])
    checks['noEmptySourceTables'] = all(s['rows'] > 0 for s in manifest['sources'])
    checks['registeredBeforeAcquisition'] = all(p['registeredAt'] < s['fetchedAt'] for s in manifest['sources'])
    checks['fetchCodeLock'] = sha(HERE / 'fetch.mjs') == read(HERE / 'fetch-code-registration.json')['sha256']
    lock = read(HERE / 'analysis-code-registration.json')
    repair = read(HERE / 'analysis-code-repair-1.json')
    checks['analysisCodeRecordedRepair'] = (sha(HERE / 'analyze-initial.py') == lock['sha256'] == repair['beforeSHA256']
                                           and sha(HERE / 'analyze.py') == repair['afterSHA256']
                                           and repair['predictionOutputExisted'] is False)
    features = read(HERE / 'features.json')
    checks['combineYearBeforeOrigin'] = all(year <= int(season[:4]) for season, rs in features.items()
                                          for r in rs for year in r['measurementYears'].values())
    pred = read(HERE / 'predictions.json')
    results = read(HERE / 'results.json')
    checks['resultRegistration'] = results['protocolSHA256'] == digest and results['at'] > repair['registeredAt']
    checks['finiteNonnegativePredictions'] = all(np.isfinite(v) and v >= 0 for rs in pred.values()
                                               for r in rs for v in r['predictions'].values())
    checks['noDuplicatePlayerSeasonTargets'] = all(len({(r['id'],r['season']) for r in rs}) == len(rs) for rs in pred.values())
    max_metric_error = 0.0
    for label, rs in pred.items():
        report = results['results'][label]['all'] if label.startswith('cross') else results['results'][label]
        for model in rs[0]['predictions']:
            actual = metrics(rs, np.array([r['predictions'][model] for r in rs]))
            for metric in ['MAE', 'RMSE', 'Pearson']:
                max_metric_error = max(max_metric_error, abs(actual[metric] - report['versions'][model][metric]))
    checks['metricsRecomputedFromPredictions'] = max_metric_error < 1e-10
    forbidden = {'id', 'PLAYER_ID', 'team', 'TEAM_ID', 'net', 'wins', 'rank', 'onOff', 'stint', 'y'}
    all_columns = {c for label, fs in read(HERE / 'fits.json').items() for fit in fs.values() for c in fit['columns']}
    checks['noForbiddenModelColumns'] = not (forbidden & all_columns)
    source = (HERE / 'analyze.py').read_text(encoding='utf-8')
    checks['noEngineDependency'] = 'src/' not in source and 'simulate' not in source
    checks['withinSeasonExcludesTrackingAndFullSeasonPct'] = all(
        set(columns(m, 'within', 'rate')) <= set(['prior', 'logMinutes'] + STATIC + ATHLETIC +
             ['missing_' + f for f in STATIC + ATHLETIC])
        for m in p['prediction']['models'] if m not in ['behavior', 'persistence'])
    # Reconstruct both exact cross-season benchmark inputs from earlier personal records.
    origin = {r['id']: r for r in features['2024-25']}
    checks['crossBaselineUsesPriorSeasonOnly'] = all(
        abs(r['predictions']['persistence'] - origin[r['id']][outcome]) < 1e-12
        for outcome in ['rate', 'pct'] for r in pred['cross2025-' + outcome])
    checks['reportExists'] = (HERE / 'report.md').is_file()
    evidence = [f for f in HERE.iterdir() if f.is_file() and f.name != 'completion-audit.json']
    out = {'at': datetime.now(timezone.utc).isoformat(), 'protocolSHA256': digest,
           'pass': all(checks.values()), 'checks': checks, 'protectedFiles': len(before),
           'changedProtectedFiles': changed, 'newProtectedFiles': new_protected,
           'registeredInputs': len(p['inputHashes']), 'officialSources': len(manifest['sources']),
           'maxMetricReconstructionError': max_metric_error,
           'artifactHashes': {f.name: sha(f) for f in evidence},
           'limits': ['Column audit verifies implemented feature lists, not historical publication availability.',
                      'No simulation/engine adoption audit claimed; offline franchise+player uncertainty only.']}
    dump(HERE / 'completion-audit.json', out)
    print({'pass': out['pass'], 'checks': len(checks), 'protectedFiles': len(before),
           'changed': len(changed), 'newProtected': len(new_protected), 'maxMetricError': max_metric_error})
    assert out['pass'], {k:v for k,v in checks.items() if not v}

if __name__ == '__main__':
    main()

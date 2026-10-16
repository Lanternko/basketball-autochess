"""Verify the substantive invariants of this read-only audit."""
import json
from datetime import datetime, timezone
from register import ROOT, HERE, sha, dump

read = lambda name: json.loads((HERE / name).read_text(encoding='utf-8'))
p, a, records = read('protocol.json'), read('analysis.json'), read('body-records.json')
protected = read('protected-before.json')
issues = []
for path, digest in protected.items():
    if not (ROOT / path).exists() or sha(ROOT / path) != digest:
        issues.append('Protected file changed: ' + path)
for path, digest in p['inputHashes'].items():
    if sha(ROOT / path) != digest:
        issues.append('Registered input changed: ' + path)
for path, digest in read('analysis-code-registration.json')['hashes'].items():
    if sha(ROOT / path) != digest:
        issues.append('Registered analysis code/spec changed: ' + path)
if sha(HERE / 'protocol.json') != (HERE / 'protocol.sha256').read_text(encoding='utf-8').split()[0]:
    issues.append('Protocol hash changed')
for s in a['seasons']:
    rows = records[s['season']]
    if len({r['playerId'] for r in rows}) != len(rows) or len(rows) != s['players']:
        issues.append('Duplicate/missing individuals: ' + s['season'])
    if abs(sum(r['minutes'] for r in rows) - s['minutes']) > 1e-8:
        issues.append('Minute sum mismatch: ' + s['season'])
    for field, summary in s['coverage'].items():
        present = [r for r in rows if r[field] is not None and r[field] > 0]
        if len(present) != summary['observedPlayers']:
            issues.append('Coverage count mismatch: ' + s['season'] + '/' + field)
        if abs(sum(r['minutes'] for r in present) / s['minutes'] - summary['minuteCoverage']) > 1e-12:
            issues.append('Minute-weighted coverage mismatch: ' + s['season'] + '/' + field)
    if s['rankReconstructionMismatches'] or s['duplicateCardConflicts'] or s['duplicateBioConflicts']:
        issues.append('Legacy reconstruction/source conflicts: ' + s['season'])
    for r in rows:
        if any(r[k] is not None for k in ['wingspanInches', 'standingReachInches',
                                         'strengthMeasurement', 'standingVerticalInches', 'maxVerticalInches']):
            issues.append('Unexpected physical measurement: ' + s['season'] + '/' + str(r['playerId']))
        if r['rawWeightLb'] is None and r['rawSizeIndex'] is not None:
            issues.append('Raw missing weight imputed: ' + s['season'] + '/' + str(r['playerId']))
result = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'protocolSHA256': sha(HERE / 'protocol.json'),
          'protectedFilesChecked': len(protected), 'registeredInputsChecked': len(p['inputHashes']),
          'positiveMinutePlayerSeasons': sum(s['players'] for s in a['seasons']),
          'legacyRankMismatches': sum(len(s['rankReconstructionMismatches']) for s in a['seasons']),
          'issues': issues, 'noSimulation': True,
          'outputHashes': {p.name: sha(p) for p in HERE.iterdir()
                           if p.is_file() and p.name not in ['completion-audit.json', 'protected-before.json']}}
dump(HERE / 'completion-audit.json', result)
print(json.dumps({k: v for k, v in result.items() if k != 'outputHashes'}))
if issues:
    raise SystemExit(1)

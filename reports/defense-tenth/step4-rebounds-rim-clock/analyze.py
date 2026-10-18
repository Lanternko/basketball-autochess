import collections
import datetime
import hashlib
import json
from pathlib import Path

R = Path(__file__).parent
load = lambda f: json.loads(Path(f).read_text(encoding='utf8'))
p = load(R / 'protocol.json')
out = {'label': 'mechanism tests only; allNoRim is unrealistic stress, no accuracy inference', 'seasons': {}}
for season in ['2022-23', '2023-24', '2024-25', '2025-26']:
    d = {m: load(R / f'runs/{season}-{m}.json') for m in ['baseline', 'off', 'allRim', 'noRim']}
    for mode in ['off', 'allRim']:
        for key in ['matches', 'teams', 'allocationTrace', 'gameplayHash']:
            assert d[mode][key] == d['baseline'][key], (season, mode, key)
    frozen = load(R.parent / f'step4-rebounds-turnover-time/runs/{season}-split-20261012.json')
    assert d['baseline']['matches'] == frozen['matches'][:12]
    for mode in ['allRim', 'noRim']:
        for e in d[mode]['rimTrace']:
            if e['type'] == 'REBOUND_CLOCK':
                assert (e['clockAfter'] == 14 and e['reset']) if e['freeThrow'] or e['rimContact'] else (e['clockAfter'] == e['clockBefore'] and not e['reset'])
            if e['type'] == 'SHOT_CLOCK':
                assert e['independent'] is False and e['naturalNoRim']
    t = d['noRim']['rimTrace']
    clocks = [e for e in t if e['type'] == 'REBOUND_CLOCK']
    carries = [e for e in clocks if not e['freeThrow']]
    out['seasons'][season] = {
        'gamesPerMode': len(d['baseline']['matches']),
        'offExactParity': True,
        'allRimGameplayExactParity': True,
        'frozenMatchParity': True,
        'allNoRimStress': {
            'missedFGContactDecisions': sum(e['type'] == 'RIM_CONTACT_STATE' for e in t),
            'retainedClockTransitions': len(carries),
            'retainedClockAbove14': sum(e['clockBefore'] > 14 for e in carries),
            'liveFinalFTReset14': sum(e['freeThrow'] for e in clocks),
            'naturalExpiry': sum(e['type'] == 'SHOT_CLOCK' for e in t),
            'expiryLocations': dict(collections.Counter(e['where'] for e in t if e['type'] == 'SHOT_CLOCK')),
        },
    }
assert sum(s['allNoRimStress']['naturalExpiry'] for s in out['seasons'].values()) > 0
assert sum(s['allNoRimStress']['retainedClockAbove14'] for s in out['seasons'].values()) > 0
assert sum(s['allNoRimStress']['liveFinalFTReset14'] for s in out['seasons'].values()) > 0
(R / 'analysis.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf8')
protected = load(R / 'protected-before.json')
bad = [f for f, h in protected.items() if not Path(f).exists() or hashlib.sha256(Path(f).read_bytes()).hexdigest() != h]
assert not bad, bad
sha = hashlib.sha256((R / 'protocol.json').read_bytes()).hexdigest()
assert sha == (R / 'protocol.sha256').read_text().strip()
audit = {'finishedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protectedFiles': len(protected), 'changed': bad, 'protocolSHA': sha, 'fullSeasonRuns': 0, 'integrationGames': 192, 'baselinePromoted': False, 'unitTests': load(R / 'unit-tests.json')}
(R / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf8')
print(json.dumps(out, indent=2))

"""Independent accounting and artifact checks; no accuracy/rank acceptance test."""
import collections
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT=Path('reports/player-impact-v29')
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8'))
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=read('workload-source.json');protocol=read('protocol.json');state=read('checkpoint.json');manifest=read('manifest.json')
opp=read('opponent-role-exposure.json');summary=read('pilot-summary.json');policy=read('reliability-policy.json')
hashes={**source['hashes'],**protocol['hashes'],**opp['hashes']}
for f,h in hashes.items():assert digest(f)==h, f
assert manifest['checkpointSHA256']==digest(ROOT/'checkpoint.json')
assert state['fingerprint']==protocol['fingerprint']==manifest['fingerprint']
assert len({r['job']['id'] for r in state['rows']})==len(state['rows'])==10
assert set(r['job']['id'] for r in state['rows'])==set(protocol['ids'])

counts=collections.defaultdict(collections.Counter)
mins=collections.defaultdict(list)
row_seen=set()
statuses=collections.defaultdict(collections.Counter)
with (ROOT/'workload-game-rows.jsonl').open(encoding='utf-8') as f:
    for line in f:
        r=json.loads(line);key=(r['season'],r['gameId'],r['playerId']);assert key not in row_seen;row_seen.add(key)
        k=(r['season'],r['playerId']);counts[k]['listedGames']+=1;statuses[r['season']][r['status']]+=1
        if r['minutes']>0:
            assert r['status']=='played';mins[k].append(r['minutes']);counts[k]['playedGames']+=1;counts[k]['starts']+=r['starter']
        elif r['status']=='documented_injury_illness':
            assert r['reason'] in ['INACTIVE_INJURY','DNP_INJURY'] or 'injury/illness' in r['comment'].lower()
            counts[k]['documentedInjuryIllnessGames']+=1
        elif r['status']=='other_documented_absence':
            assert r['reason'] or r['comment'];counts[k]['otherDocumentedAbsences']+=1
        else:
            assert r['status']=='unknown_zero_minutes' and not r['reason'] and not r['comment'];counts[k]['unknownZeroMinuteGames']+=1
for a in source['seasons']:
    assert sum(statuses[a['season']].values())==a['listedPlayerGames']
    assert dict(statuses[a['season']])==a['absenceCategories']
assert len(row_seen)==170647
assert len(source['capTrainingLeaders'])==90
assert set(r['season'] for r in source['capTrainingLeaders'])=={'2022-23','2023-24','2024-25'}
assert source['capMinutes']==statistics.median(r['minutesPerPlayedGame'] for r in source['capTrainingLeaders'])
cap=source['capMinutes']
for pid,p in source['players'].items():
    assert int(pid)==p['playerId']
    for season,h in p['history'].items():
        c=counts[season,int(pid)]
        for key in ['listedGames','playedGames','starts','documentedInjuryIllnessGames','otherDocumentedAbsences','unknownZeroMinuteGames']:
            assert c[key]==h[key],(pid,season,key)
        assert mins[season,int(pid)]==h['playedMinutes']
    target=mins['2025-26',int(pid)]
    supported=statistics.mean(min(m,cap) for m in target)
    assert abs(supported-p['supportedMinutes'])<1e-10
    rates=sorted([h['documentedInjuryIllnessGames']/h['listedGames'] for h in p['history'].values() if h['historyCoverageAdequate']],reverse=True)
    persistent=rates[1] if len(rates)>1 else 0
    assert persistent==p['persistentDocumentedInjuryIllnessRate']
    assert abs(p['primaryBenchmarkMinutes']-supported*(1-.1*persistent))<1e-10

def close(a,b):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)
def estimate(games,func):
    groups=collections.defaultdict(list)
    for g in games:groups[g['opponent']].append(statistics.mean(func(p) for p in g['pair']))
    mean=statistics.mean(statistics.mean(v) for v in groups.values())
    se=math.sqrt(sum(statistics.variance(v)/len(v) for v in groups.values())/len(groups)**2)
    return mean,se

summaries={p['playerId']:p for p in summary['players']}
policies={p['playerId']:p for p in policy['players']}
actual_games=0;checked_seats=0
for item in state['rows']:
    r=item['result'];e=source['players'][str(r['playerId'])];arms={a['arm']:a for a in r['arms']}
    assert set(arms)=={'fullCapCounterfactual','supportedHealthy','recurrent05','recurrent10'}
    targets={'fullCapCounterfactual':cap,'supportedHealthy':e['supportedMinutes'],
        'recurrent05':e['supportedMinutes']*(1-.05*e['persistentDocumentedInjuryIllnessRate']),
        'recurrent10':e['primaryBenchmarkMinutes']}
    unique_ticks=set()
    for arm,a in arms.items():
        expected_tick=math.floor(targets[arm]*600+.5);close(a['minutes'],expected_tick/600)
        assert len(a['games'])==120
        assert {(g['opponent'],g['i']) for g in a['games']}=={(j,i) for j in range(30) for i in range(4)}
        assert collections.Counter(g['phase'] for g in a['games'])=={0:60,1:60}
        for g in a['games']:
            assert g['phase']==g['i']%2
            assert g['seed']==(20261016+(g['opponent']*5+r['slot'])*1000003+g['i']*7919)&0xffffffff
            assert [p['side'] for p in g['pair']]==[0,1]
            for p in g['pair']:
                close(p['playerMinutes'],expected_tick/600)
                for key,value in p['playerStats'].items():assert value>=0 and value==int(value)
                s=p['playerStats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm']
                assert s['fgm']<=s['fga'] and s['fg3m']<=s['fg3a'] and s['ftm']<=s['fta']
                assert p['win']==(1 if p['margin']>0 else 0 if p['margin']<0 else .5)
                assert p['baselineWin']==(1 if p['baselineMargin']>0 else 0 if p['baselineMargin']<0 else .5)
                checked_seats+=1
        for key,fn in [('pairedMargin',lambda p:p['margin']-p['baselineMargin']),('pairedWins',lambda p:p['win']-p['baselineWin'])]:
            mean,se=estimate(a['games'],fn)
            out=next(b for b in summaries[r['playerId']]['arms'] if b['arm']==arm)[key]
            close(mean,out['mean']);close(se,out['standardError']);close(mean-1.96*se,out['ci95'][0]);close(mean+1.96*se,out['ci95'][1])
        unique_ticks.add(expected_tick)
    assert r['simulatedGames']==len(unique_ticks)*480
    actual_games+=r['simulatedGames']
    healthy=next(b for b in summaries[r['playerId']]['arms'] if b['arm']=='supportedHealthy')['pairedMargin']['mean']
    for out in policies[r['playerId']]['reliabilitySensitivity']:
        factor=1-out['coefficient']*e['persistentDocumentedInjuryIllnessRate']
        close(out['healthyContribution'],healthy);close(out['reliabilityScale'],factor)
        close(out['deduction'],max(healthy,0)*(1-factor));close(out['adjustedContribution'],healthy-out['deduction'])
        assert out['adjustedContribution']<=healthy
assert actual_games==manifest['simulatedGames']==summary['simulatedGames']==19200
with (ROOT/'2025-26-all-player-workload.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==len({r['playerId'] for r in rows})==len(source['players'])==582
opps={p['playerId']:p for p in opp['seasons'][-1]['players']}
for r in rows:
    e=source['players'][r['playerId']];h=e['history']['2025-26']
    close(float(r['supportedMinutes']),e['supportedMinutes']);close(float(r['minutesPerPlayedGame']),h['minutesPerPlayedGame'])
    close(float(r['reliabilityScalePrototype']),e['reliabilityScale'])
    o=opps.get(int(r['playerId']))
    if o:close(float(r['opposingStarterFraction']),o['opposingStarterFraction'])
    else:assert r['opposingStarterFraction']==''
    assert 'no new OVR' in r['ratingScope']
status=read('status.json');assert not status['adopted'] and not status['fullOvr']
artifact_hashes={p.as_posix():digest(p) for p in ROOT.iterdir() if p.is_file() and p.name!='verification.json'}
artifact_hashes.update({f:digest(f) for f in ['src/player_workload.js','src/player_reliability.js','test/player_workload.js','test/player_workload_benchmark.js','test/player_reliability.js']})
out=dict(passed=True,sourceFilesHashed=len(hashes),boxGames=4920,listedPlayerGames=len(row_seen),allPlayers=582,
    diagnosticPlayers=10,simulatedGames=actual_games,checkedSeatRecords=checked_seats,
    scope='Source accounting, frozen runtime/input hashes, independent paired statistics, all-player CSV and selected reliability formula. Not a causal, medical, ranking or general team-season accuracy validation.',artifactHashes=artifact_hashes)
(ROOT/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='artifactHashes'}),flush=True)

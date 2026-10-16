"""Rejoin every conditional count to original PBP, independent of the model probability code."""
import hashlib
import json
import math
import re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path('reports/player-impact-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sec(s):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',s);return int(m[1] or 0)*60+float(m[2])
def putbacks(actions):
 last=None;result=set()
 for i,e in enumerate(actions):
  k=e.get('actionType')
  if e.get('isFieldGoal') and k in ['2pt','3pt']:
   if last is not None:
    a=actions[last]
    if e.get('personId')==a.get('personId') and e.get('teamId')==a.get('teamId') and e['period']==a['period'] and k=='2pt' and e.get('area')!='Mid-Range' and 0<=sec(a['clock'])-sec(e['clock'])<=3:result.add(i)
   last=None
  elif k=='rebound' and e.get('subType')=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):last=i
  elif k in ['turnover','freethrow','foul','period','jumpball'] or k=='rebound' and e.get('subType')=='defensive':last=None
 return result

baseline=read('reports/player-impact-v30/validation-protocol.json')
for p,h in baseline['hashes'].items():assert sha(p)==h,p
seasons=[];allHashes={}
for season in ['2022-23','2023-24','2024-25','2025-26']:
 f=ROOT/f'{season}-conditional-data.json';d=read(f);ix={k:i for i,k in enumerate(d['columns'])}
 for p,h in d['hashes'].items():assert sha(p)==h,p
 allHashes.update(d['hashes']);allHashes[str(f).replace('\\','/')]=sha(f)
 truth=read(f'reports/player-impact-v1/{season}-on-court-truth.json');valid=set(truth['gameIds'])
 source=read(f'reports/player-impact-v17/{season}-shot-exposures.json')
 rows={};totals=Counter();allOwn=defaultdict(Counter)
 for row in d['rows']:
  gid,team=row[ix['gameId']],row[ix['teamId']];key=(gid,row[ix['startIndex']],row[ix['endIndex']],team)
  assert gid in valid and key not in rows;rows[key]=row
  assert row[ix['gameFold']]==int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5
  ids=row[ix['playerIds']];assert len(ids)==len(set(ids))==5 and ids==sorted(ids)
  for field in ['attempts','selfMakes','assistedMakes','attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected']:assert len(row[ix[field]])==5
  for i,pid in enumerate(ids):
   a,m,n=[row[ix[k]][i] for k in ['attempts','selfMakes','assistedMakes']]
   assert 0<=m+n<=a and all(int(v)==v for v in [a,m,n])
   v=[row[ix[k]][i] for k in ['attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected']]
   assert all(math.isfinite(x) and x>=0 for x in v) and v[0]>0
   assert v[2]+v[4]<=v[0]+1e-9 and v[3]<=v[1]+1e-9
   expected=sum(source['games'][gid][str(key[1])+':'+str(key[2])].get(str(pid),{}).values())
   assert a==expected
   totals.update(freshAttempts=a,selfMakes=m,assistedMakes=n)
 counts=defaultdict(lambda:defaultdict(Counter));frameCounts=Counter()
 base=Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')
 sf=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
 frames=defaultdict(list)
 for line in sf.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:frames[s['id']].append(s)
 for spec in read(base/'manifest.json')['sources']:
  gid=spec['id']
  if gid not in valid:continue
  actions=read(spec['file'])['data']['game']['actions'];pb=putbacks(actions)
  for frame in frames[gid]:
   byTeam={t['teamId']:set(t['players']) for t in frame['teams']}
   local={tid:defaultdict(Counter) for tid in byTeam}
   for i in range(frame['startIndex'],frame['endIndex']):
    e=actions[i]
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt']:continue
    pid,tid=e['personId'],e['teamId'];assert pid in byTeam[tid]
    allOwn[pid].update(fga=1,fgm=int(e.get('shotResult')=='Made'),fg3a=int(e['actionType']=='3pt'),fg3m=int(e['actionType']=='3pt' and e.get('shotResult')=='Made'))
    if i in pb:continue
    local[tid][pid]['attempts']+=1
    if e.get('shotResult')=='Made':local[tid][pid]['assistedMakes' if e.get('assistPersonId') else 'selfMakes']+=1
   for tid,own in local.items():
    frameCounts['states']+=1;key=(gid,frame['startIndex'],frame['endIndex'],tid)
    if not any(v['attempts'] for v in own.values()):
     assert key not in rows;frameCounts['zeroShotStates']+=1;continue
    row=rows[key];assert set(row[ix['playerIds']])==byTeam[tid]
    for j,pid in enumerate(row[ix['playerIds']]):
     for k in ['attempts','selfMakes','assistedMakes']:assert row[ix[k]][j]==own[pid][k],(season,key,pid,k)
    frameCounts['shotStates']+=1
 for p in truth['players']:
  for k in ['fga','fgm','fg3a','fg3m']:assert allOwn[p['playerId']][k]==p['own'].get(k,0),(season,p['playerId'],k)
 for k,v in totals.items():assert v==d['coverage'][k]
 for k,v in frameCounts.items():assert v==d['coverage'][k]
 assert len(frames)==d['coverage']['games']==len(valid)
 seasons.append(dict(season=season,**d['coverage']));print(json.dumps(seasons[-1]),flush=True)
pv=read(ROOT/'probability-verification.json');assert pv['passed'] and pv['allProbabilitiesExactlyGameClosure'] and pv['missingPressureRejected']
allHashes.update(pv['hashes']);allHashes[str(Path(__file__)).replace('\\','/')]=sha(__file__)
out=dict(passed=True,seasons=seasons,games=sum(s['games'] for s in seasons),sourceStates=sum(s['states'] for s in seasons),freshAttempts=sum(s['freshAttempts'] for s in seasons),
 allCountsRejoinedToOriginalPbp=True,strictOwnTotalsExactlyReproduced=True,probabilityClosureComparisons=pv['probabilityComparisons'],
 scope='Count/source and probability-call consistency only. Complete same-season descriptors, not a blind or causal evaluation.',hashes=allHashes)
(ROOT/'data-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['hashes','seasons']},indent=2),flush=True)

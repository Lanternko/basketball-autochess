"""Rejoin PBP to source stints without the preparation JS or fit library."""
import json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();results=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 d=read(R/(season+'-miss-data.json'))
 for p,h in d['hashes'].items():assert sha(p)==h,p
 truth=read(f'reports/player-impact-v1/{season}-on-court-truth.json');valid=set(truth['gameIds']);mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json';specs={s['id']:s for s in read(mf)['sources']}
 sf='reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl';frames=defaultdict(list)
 for line in Path(sf).read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:frames[s['id']].append(s)
 assert set(frames)==valid;grouped={};minutes={};count=Counter()
 for gid,stints in frames.items():
  events=read(specs[gid]['file'])['data']['game']['actions'];fold=int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5;exposure=defaultdict(float)
  for s in stints:
   lineups=[tuple(sorted(t['players'])) for t in s['teams']];attempts=[0,0]
   for ls in lineups:
    assert len(ls)==5 and len(set(ls))==5
    for pid in ls:exposure[pid]+=s['seconds']/60
   for e in events[s['startIndex']:s['endIndex']]:
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt']:continue
    off=[t['teamId'] for t in s['teams']].index(e['teamId']);defense=1-off;attempts[defense]+=1;count['fga']+=1
    if e['shotResult']=='Made':assert not e.get('blockPersonId');continue
    assert e['shotResult']=='Missed';z=0 if e['actionType']=='3pt' else 1 if e.get('area')=='Mid-Range' else 2;key=(gid,fold,s['teams'][defense]['teamId'],z,lineups[defense]);g=grouped.setdefault(key,[0,[0]*5]);g[0]+=1;count['misses']+=1
    if e.get('blockPersonId'):
     g[1][lineups[defense].index(e['blockPersonId'])]+=1;count['blocks']+=1
   for i in [0,1]:assert attempts[i]==s['teams'][i]['opponent']['fga']
  minutes[gid]=(fold,dict(exposure))
 assert len(grouped)==len(d['rows'])
 for gid,fold,team,z,ids,n,b in d['rows']:assert grouped[(gid,fold,team,z,tuple(ids))]==[n,b]
 assert len(minutes)==len(d['minutes'])
 for gid,fold,ps in d['minutes']:
  fold0,expected=minutes[gid];assert fold==fold0 and set(expected)=={pid for pid,_ in ps}
  for pid,n in ps:assert math.isclose(expected[pid],n,abs_tol=1e-8,rel_tol=1e-12)
 assert set(p for _,_,_,_,ids,_,_ in d['rows'] for p in ids)<=set(p['playerId'] for p in d['players'])
 coverage={'games':len(frames),'fga':count['fga'],'misses':count['misses'],'blocks':count['blocks'],'rows':len(grouped)};assert coverage==d['coverage'];results.append({'season':season,**coverage});print(results[-1],flush=True)
out={'passed':True,'seasons':results,'sourceGames':sum(r['games'] for r in results),'sourceFga':sum(r['fga'] for r in results),'sourceMisses':sum(r['misses'] for r in results),'sourceBlocks':sum(r['blocks'] for r in results),'scope':'Every grouped miss, blocked-player mark, source-five and minute exposure independently rejoined from source PBP/stints; full-source fitting includes outcomes.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'verify-data.py']+[R/(s+'-miss-data.json') for s in ['2022-23','2023-24','2024-25','2025-26']]}}
(R/'data-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

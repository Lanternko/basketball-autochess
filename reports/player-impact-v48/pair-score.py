import json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
R=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
verification=read(R/'pair-verification.json');assert verification['passed']
for f,h in {**verification['sourceHashes'],**verification['outputHashes']}.items():assert sha(f)==h
valid=set(read('reports/player-impact-v1/2025-26-on-court-truth.json')['gameIds']);stints=[];curryGames=set();sides={}
file=Path('reports/defense-b1/stints.jsonl')
with file.open(encoding='utf-8') as stream:
 for line in stream:
  x=json.loads(line)
  if x['id'] not in valid:continue
  stints.append(x)
  for t in x['teams']:
   if 201939 in t['players']:curryGames.add(x['id']);sides[x['id']]=t['teamId']
actual=defaultdict(Counter);pred=defaultdict(Counter);sources={file.as_posix():sha(file)}
for x in stints:
 if x['id'] not in curryGames:continue
 for t in x['teams']:
  if t['teamId']!=sides[x['id']]:continue
  arm='on' if 201939 in t['players'] else 'off'
  for pid in t['players']:actual[pid][arm]+=x['seconds']
for seed in [20261012,20261013,20261014]:
 file=R/f'pair-{seed}.json';r=read(file);assert r['baselineParityPassed'];sources[file.as_posix()]=sha(file)
 for pid,c in r['pairs'].items():
  for arm,s in c.items():pred[int(pid)][arm]+=s/3
base=next(c for c in read(R/'baseline-offense-scores.json')['cells'] if c['season']=='2025-26');cats=base['curryDecomposition'];rows=[]
names={p['playerId']:p.get('name',p.get('playerName',str(p['playerId']))) for p in base['players']}
for pid in sorted(set(actual)|set(pred)):
 row={'playerId':pid,'name':names.get(pid,str(pid)),'arms':{}}
 for arm in ['on','off']:
  catsFor=[x for x in cats[arm]['contributions'] if x['playerId']==pid];a=sum(x['actualAttempts'] for x in catsFor);pa=sum(x['predictedAttempts'] for x in catsFor);ra=next((x for x in catsFor if x['zone']=='ra'),None);sec=actual[pid][arm];ps=pred[pid][arm]
  row['arms'][arm]={'actualMinutes':sec/60,'predictedMinutes':ps/60,'actualTwoAttempts':a,'predictedTwoAttempts':pa,'actualRAattempts':ra['actualAttempts'] if ra else 0,'predictedRAattempts':ra['predictedAttempts'] if ra else 0,'actualRAper36':2160*ra['actualAttempts']/sec if ra and sec else None,'predictedRAper36':2160*ra['predictedAttempts']/ps if ra and ps else None}
 rows.append(row)
out={'scope':'2025-26 strict games with Curry active. All3 baseline seeds exact gameplay parity. Real stint seconds vs exact simulated player-second intervals. Conditional rates are descriptive; neither a causal rotation experiment nor a gameplay change.','curryGames':len(curryGames),'rows':rows,'sourceSHA256':sources}
(R/'pair-scores.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps([x for x in rows if x['playerId'] in [201939,1627780,202710]]))

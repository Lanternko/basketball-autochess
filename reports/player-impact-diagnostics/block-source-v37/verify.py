"""Reconstruct block rates and recipient conditionals independently from PBP."""
import json,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
R=Path('reports/player-impact-diagnostics/block-source-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(R/'audit.json');cards=read(R/'source-cards.json');protocol=read('reports/player-impact-v30/validation-protocol.json')
for obj in [d,cards,protocol]:
 for p,h in obj['hashes'].items():assert sha(p)==h,p
inside={'PG':.15,'SG':.20,'SF':.35,'PF':.65,'C':.85,'G':.18,'F':.50};base={'long':.006,'mid':.022,'short':.095};direct={'long':.90,'mid':.60,'short':.25}
close=lambda a,b:math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10)
results=[]
for season in d['seasons']:
 name=season['season'];cs=next(s for s in cards['seasons'] if s['season']==name);teams={t['teamId']:{p['playerId']:p for p in t['cards']} for t in cs['teams']}
 stint='reports/defense-b1/stints.jsonl' if name=='2025-26' else f'reports/defense-seventh/{name}/stints/stints.jsonl';valid=set(read(f'reports/player-impact-v1/{name}-on-court-truth.json')['gameIds'])
 manifest=('data/defense-a-source' if name=='2025-26' else f'data/defense-seventh/{name}')+'/manifest.json';specs={s['id']:s for s in read(manifest)['sources']};games=defaultdict(list);out=defaultdict(Counter);n=Counter()
 for line in Path(stint).read_text(encoding='utf-8').splitlines():
  f=json.loads(line)
  if f['id'] in valid and f['seconds']>=0:games[f['id']].append(f)
 for gid,frames in games.items():
  actions=read(specs[gid]['file'])['data']['game']['actions']
  for f in frames:
   lineups=[[teams[t['teamId']][pid] for pid in t['players']] for t in f['teams']];weights=[];duty=[];actual=[0,0]
   for ls in lineups:
    rate=[(p['box']['blk']+240*p['box']['priorRates']['blk'])/(p['box']['minutes']+240) for p in ls];weights.append([r/sum(rate) for r in rate]);near=[inside.get(p['pos'],.5) for p in ls];duty.append([v/sum(near) for v in near])
    for p in ls:out[p['playerId']]['seconds']+=f['seconds']
   for e in actions[f['startIndex']:f['endIndex']]:
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt']:continue
    off=next(i for i,t in enumerate(f['teams']) if t['teamId']==e['teamId']);ds=1-off;index=f['teams'][off]['players'].index(e['personId']);zone='long' if e['actionType']=='3pt' else 'mid' if e.get('area')=='Mid-Range' else 'short';total=0
    for i,p in enumerate(lineups[ds]):
     attr=lambda k:max(0,min(150,p[k]));skill=.7*attr('onBall')+.3*attr('physique') if zone=='long' else .8*attr('help')+.2*attr('physique');exposure=(1-direct[zone])*duty[ds][i]+(direct[zone] if i==index else 0);total+=exposure*(1+.65*math.tanh((skill-70)/45))
    prob=min(base[zone]*total,.65);n['fga']+=1;n['upper']+=prob
    for i,p in enumerate(lineups[ds]):out[p['playerId']]['upper']+=prob*weights[ds][i]
    if e.get('blockPersonId'):actual[ds]+=1;n['blocks']+=1;out[e['blockPersonId']]['blocks']+=1
   for side,ls in enumerate(lineups):
    for i,p in enumerate(ls):out[p['playerId']]['conditional']+=actual[side]*weights[side][i]
 assert n['fga']==season['sourceFga'] and n['blocks']==season['actualBlocks'] and close(n['upper'],season['expectedUpperBound'])
 for p in season['players']:
  q=out[p['playerId']]
  for a,b in [('seconds','seconds'),('actualBlocks','blocks'),('expectedUpperBound','upper'),('expectedGivenActualTeamBlocks','conditional')]:assert close(p[a],q[b]),(name,p['playerId'],a)
  for field,key in [('actual36','blocks'),('upperBound36','upper'),('conditionalAllocation36','conditional')]:assert close(p[field],2160*q[key]/q['seconds'])
 results.append({'season':name,'sourceGames':len(games),'players':len(season['players']),'fga':n['fga'],'blocks':n['blocks']});print(json.dumps(results[-1]),flush=True)
out={'passed':True,'seasons':results,'allSourceCountsAndExpectationsIndependentlyRecomputed':True,'runtimeChanged':False,'scope':'Source-only descriptive diagnosis, not OVR or a fitted improvement.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'audit.json',R/'source-cards.json',R/'verify.py']}}
(R/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

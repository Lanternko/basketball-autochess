import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
R=Path('reports/player-impact-v49');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));p=read(R/'tuning-protocol.json');v=read(R/'tuning-verification.json');assert v['passed']
for file,h in v['outputHashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
cells=[]
for season in p['seasons']:
 meta=read(R/f'{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};sample=read(R/f'tuning-{season}-weight0.25.json');valid={m['id'] for m in sample['matches']};truth={gid:{t['teamId']:{'players':{str(q['playerId']):np.zeros(24) for q in t['players'] if q['seconds']>0},'pairs':Counter()} for t in ex[gid]['teams']} for gid in valid}
 with Path(f'reports/defense-seventh/{season}/stints/stints.jsonl').open(encoding='utf-8') as stream:
  for line in stream:
   s=json.loads(line)
   if s['id'] not in valid or s['period']>4 or s['seconds']<=0:continue
   start=(s['period']-1)*720+720-s['startClock'];end=start+s['seconds'];w=np.maximum(0,np.minimum(np.arange(1,25)*120,end)-np.maximum(np.arange(24)*120,start))
   for t in s['teams']:
    q=truth[s['id']][t['teamId']];ids=sorted(t['players'])
    for pid in ids:q['players'][str(pid)]+=w
    for i,a in enumerate(ids):
     for b in ids[i+1:]:q['pairs'][f'{a}/{b}']+=s['seconds']
 for weight in p['pairWeights']:
  r=read(R/f'tuning-{season}-weight{weight}.json');assert {m['id'] for m in r['matches']}==valid;phase=[];pairs=[];minutes=[]
  for g in r['rotation']['games']:
   for tid,t in g['teams'].items():
    tr=truth[g['id']][int(tid)];ids=sorted(map(int,tr['players']));official=next(x for x in ex[g['id']]['teams'] if x['teamId']==int(tid))
    for pid,ap in tr['players'].items():
     pp=t['players'].get(pid,{});phase.append(np.abs(np.array(pp.get('phase',[0]*24))/10-ap).sum()/60);actual=next(q['seconds'] for q in official['players'] if q['playerId']==int(pid));minutes.append(abs(pp.get('seconds',0)/10-actual)/60)
    for i,a in enumerate(ids):
     for b in ids[i+1:]:key=f'{a}/{b}';pairs.append(abs(t['pairs'].get(key,0)/10-tr['pairs'][key])/60)
  cells.append({'season':season,'weight':weight,'phaseMAE':float(np.mean(phase)),'pairMAE':float(np.mean(pairs)),'minuteMAE':float(np.mean(minutes))})
table=[]
for weight in p['pairWeights']:
 cs=[c for c in cells if c['weight']==weight];base={c['season']:c for c in cells if c['weight']==.25};eligible=all(c['minuteMAE']<=base[c['season']]['minuteMAE']+.05 for c in cs);score=float(np.mean([c['phaseMAE']/base[c['season']]['phaseMAE']+c['pairMAE']/base[c['season']]['pairMAE'] for c in cs]));table.append({'weight':weight,'eligible':eligible,'score':score,'cells':cs})
best=min((r for r in table if r['eligible']),key=lambda x:(x['score'],x['weight']));selected=best['weight'] if best['score']<1.98 else .25
out={'selectedPairWeight':selected,'targetExcluded':True,'games':720,'table':table};(R/'tuning-selection.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))

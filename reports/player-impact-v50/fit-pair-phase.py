import json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path('reports/player-impact-v50');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));p=read(R/'pair-protocol.json');hashes={}
for season in p['seasons']:
 meta=read(f'reports/player-impact-v49/{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};fold=read(f'reports/player-impact-v49/{season}-profiles.json')['foldByGame'];counts=defaultdict(lambda:np.zeros((5,24)));games=defaultdict(lambda:np.zeros(5))
 for gid in fold:
  for t in ex[gid]['teams']:
   ids=sorted(x['playerId'] for x in t['players'] if x['seconds']>0)
   for i,a in enumerate(ids):
    for b in ids[i+1:]:games[f"{t['teamId']}/{a}/{b}"][fold[gid]]+=1
 src=Path(f'reports/defense-seventh/{season}/stints/stints.jsonl');hashes[src.as_posix()]=hashlib.sha256(src.read_bytes()).hexdigest()
 with src.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in fold or st['period']>4 or st['seconds']<=0:continue
   f=fold[st['id']];start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds'];w=np.maximum(0,np.minimum(np.arange(1,25)*120,end)-np.maximum(np.arange(24)*120,start))
   for t in st['teams']:
    ids=sorted(t['players'])
    for i,a in enumerate(ids):
     for b in ids[i+1:]:counts[f"{t['teamId']}/{a}/{b}"][f]+=w
 def fit(f):
  keep=[i for i in range(5) if i!=f];out={}
  for k,v in counts.items():
   c=v[keep].sum(0);total=c.sum();n=games[k][keep].sum()
   if total<=0:continue
   prior=total/max(1,n)*p['priorGames'];q=(c+prior/24)/(total+prior);out[k]=[0]+np.cumsum(q).tolist();out[k][-1]=1
  return out
 out={'folds':[fit(f) for f in range(5)],'fallbackPrior':fit(-1),'foldByGame':fold}
 (R/f'{season}-pair-phase.json').write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,flush=True)
(R/'pair-fit-sources.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')

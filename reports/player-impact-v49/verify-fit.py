"""Independently reconstruct held-out-fold phase and pair sufficient counts."""
import json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path('reports/player-impact-v49');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));p=read(R/'protocol.json');sel=read(R/'selection.json');checks=[]
for key,metric in [('phasePriorGames','phaseNLL'),('pairPriorGames','pairNLL')]:assert sel[key]==min(sel['table'],key=lambda r:(r[metric],r['priorGames']))['priorGames']
assert sel['targetExcluded'] and all(c['season']!='2025-26' for r in sel['table'] for c in r['cells'])
for s in p['seasons']:
 fit=read(R/f'{s}-profiles.json');folds=fit['foldByGame'];meta=read(R/f'{s}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};truth=defaultdict(list)
 source=Path('reports/defense-b1/stints.jsonl' if s=='2025-26' else f'reports/defense-seventh/{s}/stints/stints.jsonl')
 with source.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] in folds and st['period']<=4:truth[st['id']].append(st)
 entries=0;pairChecks=0;maxError=0.
 for excluded in range(5):
  counts=defaultdict(lambda:np.zeros((24,2)));globalCounts=np.zeros((2,24,2));pairs=defaultdict(lambda:np.zeros(4))
  for gid,stints in truth.items():
   if folds[gid]==excluded:continue
   for team in ex[gid]['teams']:
    tid=team['teamId'];active={q['playerId']:int(bool(q.get('starter'))) for q in team['players'] if q['seconds']>0};ids=sorted(active)
    for st in stints:
     on=set(next(t['players'] for t in st['teams'] if t['teamId']==tid));start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds'];weights=np.maximum(0,np.minimum(np.arange(1,25)*120,end)-np.maximum(np.arange(24)*120,start))
     for pid,starter in active.items():
      key=f'{tid}/{pid}/{starter}';counts[key][:,0]+=weights*(pid in on);counts[key][:,1]+=weights;globalCounts[starter,:,0]+=weights*(pid in on);globalCounts[starter,:,1]+=weights
     for i,a in enumerate(ids):
      for b in ids[i+1:]:pairs[f'{tid}/{a}/{b}'][0 if a in on and b in on else 1 if a in on else 2 if b in on else 3]+=st['seconds']
  prior=(globalCounts[:,:,0]+1)/(globalCounts[:,:,1]+2)
  for key,values in fit['folds'][excluded]['players'].items():
   starter=int(key.rsplit('/',1)[1]);c=counts[key];expected=(c[:,0]+120*sel['phasePriorGames']*prior[starter])/(c[:,1]+120*sel['phasePriorGames']);err=float(np.max(np.abs(expected-values)));maxError=max(maxError,err);assert err<1e-10;entries+=1
  for key,value in fit['folds'][excluded]['pairs'].items():
   c=pairs[key];n=c.sum();a=(c[0]+.5)/(n+1);b=(c[0]+c[2]+.5)/(n+1);a=(c[0]+c[1]+.5)/(n+1);q=(c+2880*sel['pairPriorGames']*np.array([a*b,a*(1-b),(1-a)*b,(1-a)*(1-b)]))/(n+2880*sel['pairPriorGames']);expected=np.log(q[0]*q[3]/(q[1]*q[2]));assert abs(expected-value)<1e-10;pairChecks+=1
 checks.append({'season':s,'playerFoldProfiles':entries,'pairFoldProfiles':pairChecks,'maxProbabilityError':maxError});print(json.dumps(checks[-1]),flush=True)
result={'passed':True,'wholeGameFoldExclusionRebuilt':True,'olderThreePriorSelectionVerified':True,'checks':checks,'profileSHA256':{(R/f'{s}-profiles.json').as_posix():hashlib.sha256((R/f'{s}-profiles.json').read_bytes()).hexdigest() for s in p['seasons']}}
(R/'fit-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

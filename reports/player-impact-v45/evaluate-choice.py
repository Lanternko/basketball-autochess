import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));branches=['three','paintGivenTwo','raGivenPaint','cornerGivenThree'];zones=['ra','paint','mid','corner','arc'];selected=read(ROOT/'choice-extended-selection.json')['selected'];output=[]
for season in read(ROOT/'protocol.json')['seasons']:
 d=read(ROOT/f'{season}-fga-data.json');ids=[p['playerId'] for p in d['players']];idx={p:i for i,p in enumerate(ids)};models={};groups={}
 for r in d['rows']:groups.setdefault((r[0],r[1],r[3],tuple(r[5])),np.zeros(5))[r[2]]+=r[6]
 for f in range(5):
  for name,c in selected.items():
   for variant,sigma,feature in [('selected',c['sigma'],c['feature']),('identityOnly',.05,False)]:
    fit=read(ROOT/'fits'/f'choice-{season}-sigma{sigma:g}-feature{int(feature)}-fold{f}.json');assert fit['playerIds']==ids
    models[f,name,variant]=next(m for m in fit['models'] if m['name']==name)
 valid={gid for gid,f,ps in d['minutes']};active={gid:{pid for pid,m in ps if m>0} for gid,f,ps in d['minutes']};sides=defaultdict(dict)
 source=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
 for line in source.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid:
   for t in s['teams']:
    for pid in t['players']:sides[s['id']][pid]=t['teamId']
 total=defaultdict(lambda:np.zeros((3,5)));on=defaultdict(lambda:np.zeros((3,5)));sums=defaultdict(lambda:{'on':np.zeros((3,5)),'off':np.zeros((3,5))});loss={v:0. for v in ['selected','identityOnly']}
 for (gid,f,shooter,ds),counts in groups.items():
  n=counts.sum();a=[counts];trials=[n,counts[:3].sum(),counts[:2].sum(),counts[3:].sum()];yes=[counts[3:].sum(),counts[:2].sum(),counts[0],counts[3]]
  for variant in ['identityOnly','selected']:
   probs=[]
   for j,name in enumerate(branches):
    m=models[f,name,variant];eta=m['intercept']+m['shooterLogits'][idx[shooter]]+sum(m['defenderLogits'][idx[p]] for p in ds);probs.append(float(expit(eta)));loss[variant]+=trials[j]*np.logaddexp(0,eta)-yes[j]*eta
   three,paint,ra,corner=probs;a.append(n*np.array([(1-three)*paint*ra,(1-three)*paint*(1-ra),(1-three)*(1-paint),three*corner,three*(1-corner)]))
  a=np.array(a);total[gid,sides[gid][ds[0]]]+=a
  for pid in ds:sums[pid]['on']+=a;on[gid,pid]+=a
 for gid,players in active.items():
  for pid in players:sums[pid]['off']+=total[gid,sides[gid][pid]]-on[gid,pid]
 minutes=defaultdict(float)
 for gid,f,ps in d['minutes']:
  for pid,m in ps:minutes[pid]+=m
 rows=[]
 for p in d['players']:
  arms=sums[p['playerId']];metrics={}
  if min(x[0].sum() for x in arms.values())>=100:
   for z,zz in [(z,[i]) for i,z in enumerate(zones)]+[('short',[0,1]),('long',[3,4])]:
    vals={arm:dict(zip(['actual','identityOnly','selected'],(100*a[:,zz].sum(axis=1)/a[0].sum()).tolist())) for arm,a in arms.items()};vals['delta']={v:vals['on'][v]-vals['off'][v] for v in ['actual','identityOnly','selected']};metrics[z]=vals
  rows.append({**p,'minutes':minutes[p['playerId']],'metrics':metrics})
 summary={}
 for z in zones+['short','long']:
  for arm in ['on','delta']:
   ps=[p for p in rows if p['minutes']>=500 and z in p['metrics']];den=sum(p['minutes'] for p in ps);summary[z+':'+arm]={v:sum(p['minutes']*abs(p['metrics'][z][arm][v]-p['metrics'][z][arm]['actual']) for p in ps)/den for v in ['identityOnly','selected']}
 output.append({'season':season,'heldoutNLL':loss,'summary':summary,'players':rows});print(json.dumps({'season':season,'nll':loss,'wemby':next((p['metrics'] for p in rows if p['playerId']==1641705),None)}),flush=True)
(ROOT/'choice-evaluation.json').write_text(json.dumps({'scope':'Whole-game cross-fitted shot-choice expectation on fixed real fresh-FGA shooters and lineups. No attempt-rate hazard, simulated choices or source on/off residual fitting. Target excluded from hyperparameter selection, still same-season reconstruction.','seasons':output}),encoding='utf-8')

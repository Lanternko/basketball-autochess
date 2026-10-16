import json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));zones=['ra','paint','mid','corner','arc'];coarse=['short','short','mid','long','long'];selected=read(ROOT/'make-extended-selection.json')['selected'];out=[]
for season in read(ROOT/'protocol.json')['seasons']:
 data=read(ROOT/f'{season}-fga-data.json');ids=[p['playerId'] for p in data['players']];idx={p:i for i,p in enumerate(ids)};modelcache={}
 for fold in range(5):
  for name,c in selected.items():
   f=read(ROOT/'fits'/f"make-{season}-sigma{c['sigma']:g}-feature{int(c['feature'])}-fold{fold}.json");assert f['playerIds']==ids;modelcache[(fold,name,'selected')]=next(m for m in f['models'] if m['name']==name)
   f=read(ROOT/'fits'/f'make-{season}-sigma0-feature0-fold{fold}.json');modelcache[(fold,name,'fineZero')]=next(m for m in f['models'] if m['name']==name)
  for name,sigma in [('long',0),('mid',.025),('short',.05)]:
   paths=[Path(f'reports/player-impact-v43/fits/{season}-sigma{sigma:g}-tail0-fold{fold}.json'),Path(f'reports/player-impact-v41/fits/{season}-sigma{sigma:g}-fold{fold}.json'),Path(f'reports/player-impact-v40/fits/{season}-sigma{sigma:g}-fold{fold}.json')]
   f=read(next(p for p in paths if p.exists()));assert f['playerIds']==ids;modelcache[(fold,name,'coarse')]=next(m for m in f['zones'] if m['zone']==name)
 source=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');valid={r[0] for r in data['minutes']};sides=defaultdict(dict);active={gid:{pid for pid,m in ps if m>0} for gid,fold,ps in data['minutes']}
 for line in source.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid:
   for t in s['teams']:
    for pid in t['players']:sides[s['id']][pid]=t['teamId']
 sums=defaultdict(lambda:{'on':np.zeros((5,5)),'off':np.zeros((5,5))});gameTotal=defaultdict(lambda:np.zeros((5,5)));gameOn=defaultdict(lambda:np.zeros((5,5)));losses={v:np.zeros(5) for v in ['coarse','fineZero','selected']};trials=np.zeros(5)
 for gid,fold,zi,shooter,own,ds,n,m,blocks in data['rows']:
  values=[n,m];trials[zi]+=n
  for v in ['coarse','fineZero','selected']:
   f=modelcache[(fold,coarse[zi] if v=='coarse' else zones[zi],v)];eta=f['intercept']+f['shooterLogits'][idx[shooter]]+sum(f['defenderLogits'][idx[p]] for p in ds);values.append(n*float(expit(eta)));losses[v][zi]+=n*np.logaddexp(0,eta)-m*eta
  team=sides[gid][ds[0]];gameTotal[(gid,team)][zi]+=values
  for pid in ds:sums[pid]['on'][zi]+=values;gameOn[(gid,pid)][zi]+=values
 for gid,players in active.items():
  for pid in players:sums[pid]['off']+=gameTotal[(gid,sides[gid][pid])]-gameOn[(gid,pid)]
 minutes=defaultdict(float)
 for gid,f,ps in data['minutes']:
  for pid,m in ps:minutes[pid]+=m
 players=[]
 for p in data['players']:
  metrics={}
  for name,zz in [(z,[i]) for i,z in enumerate(zones)]+[('short',[0,1]),('long',[3,4])]:
   arms={arm:sums[p['playerId']][arm][zz].sum(axis=0) for arm in ['on','off']}
   if min(a[0] for a in arms.values())<100:continue
   values={arm:{'attempts':int(a[0]),**{k:100*a[i]/a[0] for i,k in enumerate(['actual','coarse','fineZero','selected'],1)}} for arm,a in arms.items()}
   values['delta']={k:values['on'][k]-values['off'][k] for k in ['actual','coarse','fineZero','selected']};metrics[name]=values
  players.append({**p,'minutes':minutes[p['playerId']],'metrics':metrics})
 summary={}
 for name in zones+['short','long']:
  for arm in ['on','delta']:
   ps=[p for p in players if p['minutes']>=500 and name in p['metrics']];den=sum(p['minutes'] for p in ps)
   summary[name+':'+arm]={v:sum(p['minutes']*abs(p['metrics'][name][arm][v]-p['metrics'][name][arm]['actual']) for p in ps)/den for v in ['coarse','fineZero','selected']}
 cell={'season':season,'heldoutNLL':{v:{'total':float(a.sum()),'byZone':dict(zip(zones,a.tolist()))} for v,a in losses.items()},'trials':dict(zip(zones,trials.tolist())),'summary':summary,'players':players};out.append(cell)
 print(json.dumps({'season':season,'nll':{v:float(a.sum()) for v,a in losses.items()},'wemby':next((p['metrics'] for p in players if p['playerId']==1641705),None)}),flush=True)
result={'scope':'Whole-game cross-fitted expected makes on fixed real fresh-FGA zones and lineups. No simulated outcomes or source on/off residual fitting. Earlier seasons used in hyperparameter selection; target excluded from selection but still an already-seen-season reconstruction check, not future prediction. MAE uses >=500 source minutes and >=100 attempts both on and off.','seasons':out}
(ROOT/'make-evaluation.json').write_text(json.dumps(result),encoding='utf-8')

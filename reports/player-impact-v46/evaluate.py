import json,importlib.util
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit
ROOT=Path('reports/player-impact-v46');SOURCE=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));spec=importlib.util.spec_from_file_location('joint46','reports/player-impact-v46/fit.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib);selected=read(ROOT/'selection.json')['selected'];prior=read(SOURCE/'make-fit.json')['selected'];out=[]
for season in read(ROOT/'protocol.json')['seasons']:
 d=lib.data(season);pred={v:np.zeros(len(d['n'])) for v in ['v45','v46']};nll={v:0. for v in pred}
 for fold in range(5):
  joint=read(lib.path((season,selected['commonSigma'],selected['contrastSigma'],fold)))
  for z,name in enumerate(['ra','paint']):
   c=prior[name];old=read(SOURCE/'fits'/f"make-{season}-sigma{c['sigma']:g}-feature{int(c['feature'])}-fold{fold}.json");mask=(d['fold']==fold)&(d['zone']==z)
   for v,models in [('v45',old['models']),('v46',joint['models'])]:
    m=next(m for m in models if m['name']==name);eta=m['intercept']+np.array(m['shooterLogits'])[d['own'][mask]]+np.array(m['defenderLogits'])[d['ds'][mask]].sum(axis=1);pred[v][mask]=d['n'][mask]*expit(eta);nll[v]+=float(np.sum(d['n'][mask]*np.logaddexp(0,eta)-d['b'][mask]*eta))
 source=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');valid={r[0] for r in d['doc']['minutes']};sides=defaultdict(dict);active={gid:{pid for pid,m in ps if m>0} for gid,f,ps in d['doc']['minutes']}
 for line in source.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid:
   for t in s['teams']:
    for pid in t['players']:sides[s['id']][pid]=t['teamId']
 sums=defaultdict(lambda:{'on':np.zeros((2,4)),'off':np.zeros((2,4))});total=defaultdict(lambda:np.zeros((2,4)));on=defaultdict(lambda:np.zeros((2,4)))
 for i,r in enumerate(d['rows']):
  gid,f,z,shooter,own,ds,n,m,blocks=r;values=np.array([n,m,pred['v45'][i],pred['v46'][i]]);total[gid,sides[gid][ds[0]]][z]+=values
  for pid in ds:sums[pid]['on'][z]+=values;on[gid,pid][z]+=values
 for gid,ps in active.items():
  for pid in ps:sums[pid]['off']+=total[gid,sides[gid][pid]]-on[gid,pid]
 players=[]
 for i,p in enumerate(d['doc']['players']):
  metrics={}
  for name,zz in [('ra',[0]),('paint',[1]),('short',[0,1])]:
   arms={arm:sums[p['playerId']][arm][zz].sum(axis=0) for arm in ['on','off']}
   if min(a[0] for a in arms.values())<100:continue
   values={arm:{'attempts':int(a[0]),**dict(zip(['actual','v45','v46'],(100*a[1:]/a[0]).tolist()))} for arm,a in arms.items()};values['delta']={k:values['on'][k]-values['off'][k] for k in ['actual','v45','v46']};metrics[name]=values
  players.append({**p,'minutes':d['minutes'][i],'metrics':metrics})
 summary={}
 for z in ['ra','paint','short']:
  for arm in ['on','delta']:
   ps=[p for p in players if p['minutes']>=500 and z in p['metrics']];den=sum(p['minutes'] for p in ps);summary[z+':'+arm]={v:sum(p['minutes']*abs(p['metrics'][z][arm][v]-p['metrics'][z][arm]['actual']) for p in ps)/den for v in pred}
 out.append({'season':season,'heldoutNLL':nll,'summary':summary,'players':players});print(json.dumps({'season':season,'nll':nll,'paintMAE':summary['short:on'],'wemby':next((p['metrics'] for p in players if p['playerId']==1641705),None)}),flush=True)
(ROOT/'source-evaluation.json').write_text(json.dumps({'scope':'Whole-game cross-fit on fixed actual fresh paint FGA, shooters, zones and lineups. Both arms >=100 actual zone attempts; source-minute weighted >=500 minute cohort. Target excluded from hyperparameter selection; same-season reconstruction, not future prediction.','seasons':out}),encoding='utf-8')

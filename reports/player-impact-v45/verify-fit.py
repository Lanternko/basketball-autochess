import json,hashlib,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit,logit
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={};checks=[]
for file in sorted((ROOT/'fits').glob('*.json')):
 f=read(file)
 if sys.argv[1:] and f['kind']!=sys.argv[1]:continue
 season=f['season'];fold=f['fold'];sigma=f['sigma'];feature=int(f['feature'])
 if season not in cache:cache[season]=read(ROOT/f'{season}-fga-data.json')
 data=cache[season];ids=[p['playerId'] for p in data['players']];assert ids==f['playerIds'];idx={p:i for i,p in enumerate(ids)};k=len(ids)
 for m in f['models']:
  name=m['name']
  if f['kind']=='make':
   zi=data['zones'].index(name);rows=[r for r in data['rows'] if r[2]==zi];groups=None
   own=np.array([idx[r[3]] for r in rows]);ds=np.array([[idx[p] for p in r[5]] for r in rows]);n=np.array([r[6] for r in rows],float);made=np.array([r[7] for r in rows],float);folds=np.array([r[1] for r in rows]);nuMinutes=sum(v for _,foldid,ps in data['minutes'] if fold is None or foldid!=fold for _,v in ps)
  else:
   groups={}
   for r in data['rows']:groups.setdefault((r[0],r[1],r[3],tuple(r[5])),np.zeros(5))[r[2]]+=r[6]
   keys=list(groups);v=np.array(list(groups.values()));own=np.array([idx[r[2]] for r in keys]);ds=np.array([[idx[p] for p in r[3]] for r in keys]);folds=np.array([r[1] for r in keys])
   n=v.sum(axis=1) if name=='three' else v[:,:3].sum(axis=1) if name=='paintGivenTwo' else v[:,:2].sum(axis=1) if name=='raGivenPaint' else v[:,3:].sum(axis=1)
   made=v[:,3:].sum(axis=1) if name=='three' else v[:,:2].sum(axis=1) if name=='paintGivenTwo' else v[:,0] if name=='raGivenPaint' else v[:,3]
  train=(n>0)&(np.ones(len(n),bool) if fold is None else folds!=fold);test=(n>0)&(np.ones(len(n),bool) if fold is None else folds==fold)
  features=np.zeros(k)
  if feature==1:
   opportunities=np.bincount(ds[train].ravel(),weights=np.repeat(n[train],5),minlength=k);blocks=np.zeros(k)
   if f['kind']=='make':
    for included,r in zip(train,rows):
     if included:
      for p,b in r[8]:blocks[idx[p]]+=b
   else:
    groupIndex={key:i for i,key in enumerate(keys)};allowed={'three':{0,1,2,3,4},'paintGivenTwo':{0,1,2},'raGivenPaint':{0,1},'cornerGivenThree':{3,4}}[name]
    for r in data['rows']:
     if r[2] in allowed and train[groupIndex[(r[0],r[1],r[3],tuple(r[5]))]]:
      for p,b in r[8]:blocks[idx[p]]+=b
   muBlock=blocks.sum()/opportunities.sum();features=10*((blocks+200*muBlock)/(opportunities+200)-muBlock)
  elif feature==2:
   previous=f'{int(season[:4])-1}-{int(season[:4])%100:02d}';p=Path(f'reports/player-impact-v20/{previous}-defense-exposure.json')
   if p.exists() and name!='mid':
    prior=read(p);z='short' if name in ['ra','paint'] else 'long'
    for i,pid in enumerate(ids):
     c=prior['cards'].get(str(pid),{}).get(z)
     if c and not c['sourceMissing'] and c['rawDifference'] is not None:features[i]=10*c['rate']/prior['leagueAttemptsPerTeamMinute'][z]*c['rawDifference']*c['attempts']/(c['attempts']+200)
  assert np.max(abs(features-np.array(m['blockFeatures'])))<1e-12
  a=np.array(m['shooterLogits']);d=np.array(m['defenderLogits']);residualDefense=np.array(m['defenderResiduals']);slope=m['blockSlope'];assert np.max(abs(d-residualDefense-slope*features))<1e-12
  eta=m['intercept']+a[own]+d[ds].sum(axis=1);nll=float(np.sum(n[test]*np.logaddexp(0,eta[test])-made[test]*eta[test]));assert abs(nll-m['nll'])<1e-6
  mu=made[train].sum()/n[train].sum();nu=.5 if f['kind']=='choice' else 60*n[train].sum()/nuMinutes;res=n[train]*expit(eta[train])-made[train]
  ga=np.bincount(own[train],weights=res,minlength=k)+nu*(expit(logit(mu)+a)-mu);gd=np.bincount(ds[train].ravel(),weights=np.repeat(res,5),minlength=k)
  if sigma:gd+=residualDefense/(sigma*sigma)
  else:gd=np.zeros(k);assert np.max(abs(residualDefense))==0
  gb=float(res@features[ds[train]].sum(axis=1)+slope) if feature else 0.;maximum=max(abs(ga).max(),abs(gd).max(),abs(gb),abs(res.sum()));assert maximum<.001,(file,name,maximum)
  checks.append({'file':str(file),'name':name,'nll':nll,'maxGradient':float(maximum)})
for data in cache.values():
 assert data['coarseLedgerParityPassed']
 for gid,fold,z,pid,own,ds,n,m,blocks in data['rows']:
  assert fold==int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5;assert sum(b for p,b in blocks)<=n-m and all(p in ds for p,b in blocks)
result={'passed':True,'models':len(checks),'trainingOnlyBlockFeaturesIndependentlyRebuilt':True,'priorSeasonTrackingFeaturesIndependentlyRebuilt':True,'wholeGameFoldsPassed':True,'checks':checks}
(ROOT/((sys.argv[1]+'-' if sys.argv[1:] else '')+'fit-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))

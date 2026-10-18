import json,hashlib
from pathlib import Path
import numpy as np
from scipy.special import expit,logit
R=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={};checks=[]
for file in sorted((R/'choice-fits').glob('*.json')):
 f=read(file);s=f['season'];fold=f['fold'];sigma=f['sigma'];source=Path(f'reports/player-impact-v45/{s}-fga-data.json');assert hashlib.sha256(source.read_bytes()).hexdigest()==f['sourceDataSHA256']
 if s not in cache:
  doc=read(source);ids=[p['playerId'] for p in doc['players']];idx={pid:i for i,pid in enumerate(ids)};g={}
  for row in doc['rows']:
   if row[2]<3:g.setdefault((row[0],row[1],row[3],tuple(row[4]),tuple(row[5])),np.zeros(3))[row[2]]+=row[6]
  keys=list(g);cache[s]=(ids,np.array(list(g.values())),np.array([idx[r[2]] for r in keys]),np.array([[idx[p] for p in r[3] if p!=r[2]] for r in keys]),np.array([[idx[p] for p in r[4]] for r in keys]),np.array([r[1] for r in keys]))
 ids,c,own,mate,ds,folds=cache[s];assert ids==f['playerIds'];k=len(ids)
 for bi,m in enumerate(f['models']):
  n=c.sum(axis=1) if bi==0 else c[:,:2].sum(axis=1);b=c[:,:2].sum(axis=1) if bi==0 else c[:,0];train=(n>0)&(np.ones(len(n),bool) if fold is None else folds!=fold);test=(n>0)&(np.ones(len(n),bool) if fold is None else folds==fold);path=Path(m['baseModelPath']);assert path.name==f'choice-{s}-sigma0.05-feature1-fold{fold}.json';assert hashlib.sha256(path.read_bytes()).hexdigest()==m['baseModelSHA256'];base=read(path);assert base['playerIds']==ids;old=next(v for v in base['models'] if v['name']==m['name']);assert old['defenderLogits']==m['baseDefenderLogits'];a=np.array(m['shooterLogits']);t=np.array(m['teammateLogits']);d=np.array(m['baseDefenderLogits']);eta=m['intercept']+a[own]+t[mate].sum(axis=1)+d[ds].sum(axis=1);mu=b[train].sum()/n[train].sum();res=n[train]*expit(eta[train])-b[train];ga=np.bincount(own[train],weights=res,minlength=k)+.5*(expit(logit(mu)+a)-mu);grads=[abs(ga).max(),abs(res.sum())]
  if sigma:grads.append(abs(np.bincount(mate[train].ravel(),weights=np.repeat(res,4),minlength=k)+t/sigma**2).max())
  else:assert np.all(t==0);assert np.max(abs(a-np.array(old['shooterLogits'])))<.0001;assert abs(m['intercept']-old['intercept'])<.0001
  nll=float(np.sum(n[test]*np.logaddexp(0,eta[test])-b[test]*eta[test]));assert abs(nll-m['nll'])<1e-7 and max(grads)<.001;assert int(n[test].sum())==m['testAttempts'];checks.append({'file':file.as_posix(),'branch':m['name'],'maxGradient':float(max(grads))})
proto=read(R/'choice-protocol.json');selection=read(R/'choice-selection.json');assert selection['selectedSigma']==min(selection['table'],key=lambda c:(c['meanNllPerTwoAttempt'],c['sigma']))['sigma']
for row in selection['table']:
 for c in row['cells']:
  assert c['season'] in proto['seasons'][:3];fs=[read(R/'choice-fits'/f"{c['season']}-sigma{row['sigma']:g}-fold{f}.json") for f in range(5)];assert abs(sum(m['nll'] for f in fs for m in f['models'])-c['nll'])<1e-7;assert sum(f['testTwoAttempts'] for f in fs)==c['twoAttempts']
 assert abs(np.mean([c['nll']/c['twoAttempts'] for c in row['cells']])-row['meanNllPerTwoAttempt'])<1e-12
full=read(R/'choice-fit.json');assert full['selectedSigma']==selection['selectedSigma']
for s in full['seasons']:assert s==read(R/'choice-fits'/f"{s['season']}-sigma{full['selectedSigma']:g}-foldNone.json")
result={'passed':True,'models':len(checks),'maxGradient':max(c['maxGradient'] for c in checks),'independentRawChoiceGroupsRebuilt':True,'frozenTrainingOnlyDefenderOffsetsVerified':True,'zeroSigmaReproducesFrozenBaseline':True,'targetExcludedFromSelection':True,'fullCoefficientsMatchSelectedFits':True,'checks':checks};(R/'choice-fit-verification.json').write_text(json.dumps(result),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))

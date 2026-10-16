"""Rebuild scores and stationarity from raw rows, not the fitting matrices."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.special import expit,logit
R=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={};checks=[]
for file in sorted((R/'fits').glob('*.json')):
 f=read(file);season=f['season'];fold=f['fold'];sigma=f['sigma'];source=Path(f'reports/player-impact-v45/{season}-fga-data.json');assert hashlib.sha256(source.read_bytes()).hexdigest()==f['sourceDataSHA256']
 if season not in cache:cache[season]=read(source)
 d=cache[season];ids=[p['playerId'] for p in d['players']];assert f['playerIds']==ids;idx={pid:i for i,pid in enumerate(ids)};k=len(ids)
 for zi,m in enumerate(f['models']):
  raw=[r for r in d['rows'] if r[2]==zi];n=np.array([r[6] for r in raw],float);b=np.array([r[7] for r in raw],float);own=np.array([idx[r[3]] for r in raw]);mate=np.array([[idx[p] for p in r[4] if p!=r[3]] for r in raw]);ds=np.array([[idx[p] for p in r[5]] for r in raw]);tr=np.array([fold is None or r[1]!=fold for r in raw]);te=np.ones(len(raw),bool) if fold is None else ~tr;assert str(m['baseModelPath']).endswith(f'fold{fold}.json');base=read(m['baseModelPath']);assert base['playerIds']==ids and hashlib.sha256(Path(m['baseModelPath']).read_bytes()).hexdigest()==m['baseModelSHA256'];original=next(v for v in base['models'] if v['name']==m['name']);assert m['baseDefenderLogits']==original['defenderLogits'];a=np.array(m['shooterLogits']);t=np.array(m['teammateLogits']);defense=np.array(m['baseDefenderLogits']);eta=m['intercept']+a[own]+t[mate].sum(axis=1)+defense[ds].sum(axis=1);q=expit(eta);res=n[tr]*q[tr]-b[tr];mu=b[tr].sum()/n[tr].sum();mins=sum(v for gid,fld,ps in d['minutes'] if fold is None or fld!=fold for pid,v in ps);nu=60*n[tr].sum()/mins;ga=np.bincount(own[tr],weights=res,minlength=k)+nu*(expit(logit(mu)+a)-mu);g=[abs(ga).max(),abs(res.sum())]
  if sigma:g.append(abs(np.bincount(mate[tr].ravel(),weights=np.repeat(res,4),minlength=k)+t/sigma**2).max())
  else:assert np.all(t==0);assert max(abs(a-np.array(original['shooterLogits'])))<.0001;assert abs(m['intercept']-original['intercept'])<.0001
  nll=float(np.sum(n[te]*np.logaddexp(0,eta[te])-b[te]*eta[te]));assert abs(nll-m['nll'])<1e-7 and max(g)<.001,(file,max(g));assert int(n[te].sum())==m['testAttempts']
  for key,val in [('actualAttempts',n[te]),('actualMakes',b[te]),('predictedMakes',n[te]*q[te])]:
   ctr=m['counters'][key];on=np.bincount(np.column_stack([own[te],mate[te]]).ravel(),weights=np.repeat(val,5),minlength=k);mates=np.bincount(mate[te].ravel(),weights=np.repeat(val,4),minlength=k);assert np.max(abs(on-np.array(ctr['on'])))<1e-7 and np.max(abs(mates-np.array(ctr['teammates'])))<1e-7;assert min(ctr['off'])>=-1e-7
  checks.append({'file':file.as_posix(),'zone':m['name'],'maxGradient':float(max(g)),'heldoutNLL':nll})
p=read(R/'protocol.json');selection=read(R/'selection.json');assert selection['selectedSigma']==min(selection['table'],key=lambda c:(c['meanNllPerAttempt'],c['sigma']))['sigma']
for row in selection['table']:
 for c in row['cells']:
  assert c['season'] in p['seasons'][:3];models=[m for check in [(R/'fits'/f"{c['season']}-sigma{row['sigma']:g}-fold{f}.json") for f in range(5)] for m in read(check)['models']];assert abs(sum(m['nll'] for m in models)-c['nll'])<1e-7
 assert abs(np.mean([c['nll']/c['attempts'] for c in row['cells']])-row['meanNllPerAttempt'])<1e-12
full=read(R/'make-fit.json')
for s in full['seasons']:
 original=read(R/'fits'/f"{s['season']}-sigma{full['selectedSigma']:g}-foldNone.json");assert s['playerIds']==original['playerIds'];assert s['models']==[{k:v for k,v in m.items() if k!='counters'} for m in original['models']]
result={'passed':True,'models':len(checks),'maxGradient':max(c['maxGradient'] for c in checks),'allTrainingOnlyDefenderOffsetsVerified':True,'allZeroSigmaShooterParametersMatchFrozenBaseline':True,'sourceOnAndTeammateLedgersRebuiltFromRawRows':True,'targetExcludedFromSelection':True,'checks':checks};(R/'fit-verification.json').write_text(json.dumps(result),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))

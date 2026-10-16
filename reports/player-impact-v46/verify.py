import json,hashlib
from pathlib import Path
import numpy as np
from scipy.special import expit,logit
ROOT=Path('reports/player-impact-v46');SOURCE=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={};featuresCache={};checks=[]
for file in sorted((ROOT/'fits').glob('*.json')):
 f=read(file);season=f['season'];fold=f['fold'];a=f['commonSigma'];b=f['contrastSigma']
 if season not in cache:
  d=read(SOURCE/f'{season}-fga-data.json');ids=[p['playerId'] for p in d['players']];idx={p:i for i,p in enumerate(ids)};rows=[r for r in d['rows'] if r[2]<2];cache[season]=(d,ids,rows,np.array([idx[r[3]] for r in rows]),np.array([[idx[p] for p in r[5]] for r in rows]),np.array([r[2] for r in rows]),np.array([r[6] for r in rows],float),np.array([r[7] for r in rows],float),np.array([r[1] for r in rows]))
 d,ids,rows,own,ds,zone,n,m,folds=cache[season];idx={p:i for i,p in enumerate(ids)};k=len(ids);assert f['playerIds']==ids;assert f['sourceDataSHA256']==hashlib.sha256((SOURCE/f'{season}-fga-data.json').read_bytes()).hexdigest();train=np.ones(len(n),bool) if fold is None else folds!=fold;test=np.ones(len(n),bool) if fold is None else folds==fold
 common=np.array(f['models'][0]['commonDefender']);contrast=np.array(f['models'][0]['contrastDefender']);gc=common/a**2;gr=contrast/b**2 if b else np.zeros(k);expected=np.zeros(len(n));maximum=0.
 assert all(np.array_equal(common,z['commonDefender']) and np.array_equal(contrast,z['contrastDefender']) for z in f['models'])
 if not b:assert abs(contrast).max()==0
 totalMinutes=sum(v for gid,ff,ps in d['minutes'] if fold is None or ff!=fold for pid,v in ps)
 for z,model in enumerate(f['models']):
  trainZ=train&(zone==z);testZ=test&(zone==z);key=(season,fold,z)
  if key not in featuresCache:
   opportunities=np.bincount(ds[trainZ].ravel(),weights=np.repeat(n[trainZ],5),minlength=k);blocks=np.zeros(k)
   for include,r in zip(trainZ,rows):
    if include:
     for pid,count in r[8]:blocks[idx[pid]]+=count
   league=blocks.sum()/opportunities.sum();featuresCache[key]=10*((blocks+200*league)/(opportunities+200)-league)
  feature=featuresCache[key];assert np.max(abs(feature-np.array(model['blockFeatures'])))<1e-12;alpha=np.array(model['shooterLogits']);slope=model['blockSlope'];delta=common+(1 if z==0 else -1)*contrast+slope*feature;assert np.max(abs(delta-np.array(model['defenderLogits'])))<1e-12
  eta=model['intercept']+alpha[own]+delta[ds].sum(axis=1);res=n[trainZ]*expit(eta[trainZ])-m[trainZ];expected[zone==z]=n[zone==z]*expit(eta[zone==z]);nll=float(np.sum(n[testZ]*np.logaddexp(0,eta[testZ])-m[testZ]*eta[testZ]));assert abs(nll-model['nll'])<1e-6
  mu=m[trainZ].sum()/n[trainZ].sum();nu=60*n[trainZ].sum()/totalMinutes;ga=np.bincount(own[trainZ],weights=res,minlength=k)+nu*(expit(logit(mu)+alpha)-mu);gd=np.bincount(ds[trainZ].ravel(),weights=np.repeat(res,5),minlength=k);gc+=gd;gr+=(1 if z==0 else -1)*gd;gb=float(res@feature[ds[trainZ]].sum(axis=1)+slope);maximum=max(maximum,abs(ga).max(),abs(gb),abs(res.sum()))
 counts=np.column_stack([np.bincount(ds[test].ravel(),weights=np.repeat(v[test],5),minlength=k) for v in [n,m,expected]]);assert np.max(abs(counts-np.array(f['onCounts'])))<1e-8;maximum=max(maximum,abs(gc).max(),abs(gr).max() if b else 0);assert maximum<.001,(file,maximum)
 checks.append({'file':str(file),'maxGradient':float(maximum),'onCountAndNllPassed':True})
result={'passed':True,'jointFits':len(checks),'rawFeatureAndGradientIndependentlyRebuilt':True,'sourceHashesPassed':True,'checks':checks};(ROOT/'fit-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))

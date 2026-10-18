"""One conditional mark calibration, older seasons only, no probability floor."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
protocol=read(R/'marked-protocol.json');seasons=[*protocol['trainingSeasons'],protocol['checkSeason']]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in protocol['hashes'].items():assert sha(p)==h,p
data={};coverage=[]
for season in seasons:
 d=read(R/f'{season}-marked-data.json');samples=[];unsupported=[];rows=d['rows']
 for r in rows:
  for i,pid in enumerate(r[6]):
   n,s=r[7][i],r[8][i];assists=r[9][i];miss=n-s-sum(assists);assert miss>=0 and assists[i]==0
   if not n:continue
   f=r[10][i];a,b,c,e,z,w,g=f
   assert abs(a-c-z)<1e-9 and abs(b-e-w-sum(g))<1e-9 and g[i]==0
   for j,count in enumerate(assists):
    if count and g[j]<=0:unsupported.append({'gameId':r[0],'startIndex':r[3],'playerId':pid,'passerId':r[6][j],'count':count})
   const=-sum(count*math.log(g[j]) for j,count in enumerate(assists) if count and g[j]>0)
   samples.append([n,s,miss,a,b,c,e,z,w,const,r[1]])
 coverage.append({'season':season,**d['coverage'],'positiveFgaPlayerStints':len(samples),'unsupportedAssistedMarks':unsupported})
 if unsupported:
  (R/'unsupported-marks.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8');raise ValueError(f'{season}: zero support for {len(unsupported)} source assisted marks')
 x=np.array(samples,dtype=float);data[season]=x
 print(json.dumps({k:v for k,v in coverage[-1].items() if k!='unsupportedAssistedMarks'}),flush=True)
 del d,rows,samples

def terms(x,logscale):
 k=math.exp(float(logscale));n,s,m,a,b,c,d,e,f,constant=x[:,:10].T
 den=k*a+b;own=k*c+d;miss=k*e+f
 assert np.all(den>0) and np.all(own>0) and np.all(miss>0)
 return n*np.log(den)-s*np.log(own)-m*np.log(miss)+constant

def objective(logscale,fold=None,exclude=False):
 vals=[]
 for season in protocol['trainingSeasons']:
  x=data[season]
  if fold is not None:x=x[(x[:,10]!=fold) if exclude else (x[:,10]==fold)]
  vals.append(float(terms(x,logscale).sum()/x[:,0].sum()))
 return sum(vals)/len(vals)

def fit(fold=None):
 result=minimize_scalar(lambda k:objective(k,fold,fold is not None),bracket=(-1.,1.),method='brent',options={'xtol':1e-10,'maxiter':200})
 assert result.success and np.isfinite(result.x) and np.isfinite(result.fun)
 # Numerical score/curvature checks reject boundary/nonstationary selection.
 h=1e-4;f=lambda z:objective(z,fold,fold is not None)
 derivative=(f(result.x+h)-f(result.x-h))/(2*h);curvature=(f(result.x+h)-2*f(result.x)+f(result.x-h))/h**2
 assert abs(derivative)<1e-6 and curvature>0,(derivative,curvature)
 return {'logSelfScale':float(result.x),'selfScale':math.exp(float(result.x)),'trainingNllPerAttempt':float(result.fun),'numericalDerivative':derivative,'numericalCurvature':curvature}

out=fit();out['design']=protocol['criterion'];out['folds']=[];out['seasons']=[];out['sourceCoverage']=coverage
for fold in range(5):
 f=fit(fold);f['fold']=fold;f['heldoutNllPerAttempt']=objective(f['logSelfScale'],fold);f['priorOneHeldoutNllPerAttempt']=objective(0.,fold);out['folds'].append(f)
for season,x in data.items():
 a,b=terms(x,0.),terms(x,out['logSelfScale']);out['seasons'].append({'season':season,'freshAttempts':int(x[:,0].sum()),'priorOneNll':float(a.sum()),'fittedNll':float(b.sum()),'gainPerAttempt':float((a-b).sum()/x[:,0].sum()),'sourceSelfMakes':int(x[:,1].sum()),'sourceAssistedMakes':int((x[:,0]-x[:,1]-x[:,2]).sum())})
out['trainingSeasons']=protocol['trainingSeasons'];out['checkSeason']=protocol['checkSeason']
out['limits']=protocol['limits'];out['hashes']={str(p).replace('\\','/'):sha(p) for p in [R/'marked-protocol.json',R/'fit-marked.py',*[R/f'{s}-marked-data.json' for s in seasons]]}
p=R/'marked-fit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['hashes','sourceCoverage']},indent=2))

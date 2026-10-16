"""MAP branch-selection inference with a varying known recorded-FGA survival."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
root=Path('reports/player-impact-v23');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));seasons=['2022-23','2023-24','2024-25','2025-26']
sources={s:read(root/f'{s}-choice-survival.json') for s in seasons};datasets={};folds=[]
for season,src in sources.items():
 ids=np.array(sorted(map(int,src['cards'])),dtype=np.int64);rows=np.array([[*r,g['fold']] for g in src['games'] for r in g['rows']],dtype=float);ix=np.searchsorted(ids,rows[:,0].astype(np.int64));assert np.all(ids[ix]==rows[:,0]);datasets[season]=(src,ids,rows,ix)
 if season in seasons[:3]:
  for f in range(5):
   mask=rows[:,3]==f;folds.append((season,f,len(ids),rows[~mask],ix[~mask],rows[mask],ix[mask]))
def fit_theta(k,rows,ix,size):
 y=rows[:,1];s=rows[:,2];mu=float(y.sum()/s.sum());assert 0<mu<1
 success=np.bincount(ix,y,minlength=size);lo=np.full(size,1e-10);hi=np.full(size,1-1e-10)
 for _ in range(36):
  theta=(lo+hi)/2
  failure=np.bincount(ix,(1-y)*s/(1-theta[ix]*s),minlength=size)
  gradient=(success+k*mu)/theta-k*(1-mu)/(1-theta)-failure
  lo=np.where(gradient>0,theta,lo);hi=np.where(gradient>0,hi,theta)
 return (lo+hi)/2,mu
def score(k,detail=False):
 out=[]
 for season,f,size,train,tix,test,vix in folds:
  theta,mu=fit_theta(k,train,tix,size);p=theta[vix]*test[:,2];y=test[:,1]
  assert np.all((p>0)&(p<1));nll=-float(np.sum(y*np.log(p)+(1-y)*np.log1p(-p)))
  out.append({'season':season,'fold':f,'events':len(test),'nll':nll})
 return out if detail else sum(r['nll'] for r in out)
fit=minimize_scalar(lambda x:score(math.exp(x)),bounds=(math.log(.001),math.log(100000)),method='bounded');assert fit.success;k=math.exp(fit.x)
output={'kappaRebounds':k,'fitSeasons':seasons[:3],'checkSeason':'2025-26','design':'Observed fast recorded-FGA probability = theta_player * source_model_survival_event. MAP theta has Beta(1+kappa*mu,1+kappa*(1-mu)) prior, mu=total successes/sum survival, solved by monotone derivative bisection. Common kappa minimizes five whole-game fold Bernoulli NLL. Counts and contextual survival only; no simulated residual, name, rank, ON/OFF or wins fit. Survival uses full-season v22 shooting/turnover covariates and coarse engine foul/endgame assumptions, so descriptive conditional reconstruction, not blind or causal skill estimation. Runtime unchanged; source choice physics centering and residual policy mismatches must be audited before integration.','nll':{'fitted':score(k),'nearUnshrunk':score(.001),'pooledApprox':score(100000)},'foldScores':score(k,True),'sourceHashes':{str(root/f'{s}-choice-survival.json'):hashlib.sha256((root/f'{s}-choice-survival.json').read_bytes()).hexdigest() for s in seasons},'codeHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
for s,(src,ids,rows,ix) in datasets.items():
 theta,mu=fit_theta(k,rows,ix,len(ids));cards={str(pid):{**src['cards'][str(pid)],'selectionProbabilityMAP':float(theta[i])} for i,pid in enumerate(ids)}
 path=root/f'{s}-choice-rates.json'
 if path.exists():raise RuntimeError('Preserve source posterior')
 path.write_text(json.dumps({'season':s,'kappaRebounds':k,'leagueSelectionReference':mu,'cards':cards,'sourceHash':output['sourceHashes'][str(root/f'{s}-choice-survival.json')],'fitCodeHash':output['codeHash'],'runtimeApplied':False},indent=2),encoding='utf-8');print(s,'leagueSelection',mu,flush=True)
path=root/'choice-prior.json'
if path.exists():raise RuntimeError('Preserve source fit')
path.write_text(json.dumps(output,indent=2),encoding='utf-8');print('FIT',k,output['nll'],flush=True)

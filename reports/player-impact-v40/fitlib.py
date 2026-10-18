import json,math
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.special import expit,logit
from scipy.optimize import minimize
from scipy.sparse.linalg import spsolve
R=Path('reports/player-impact-v40');_cache={}
def data(season):
 if season in _cache:return _cache[season]
 d=json.loads((R/(season+'-fga-data.json')).read_text(encoding='utf-8'));ids=[p['playerId'] for p in d['players']];lookup={pid:i for i,pid in enumerate(ids)};games=sorted(r[0] for r in d['minutes']);gi={gid:i for i,gid in enumerate(games)};k=len(ids);zones=[]
 for zone in range(3):
  rows=[r for r in d['rows'] if r[2]==zone];n=len(rows);own=np.array([lookup[r[3]] for r in rows]);ds=np.array([[lookup[pid] for pid in r[5]] for r in rows]);ri=np.repeat(np.arange(n),7);ci=np.column_stack([own,k+ds,np.full(n,2*k)]).ravel();x=sparse.csr_matrix((np.ones(n*7),(ri,ci)),shape=(n,2*k+1));x0=x[:,list(range(k))+[2*k]]
  zones.append({'x':x,'x0':x0,'own':own,'n':np.array([r[6] for r in rows],float),'b':np.array([r[7] for r in rows],float),'fold':np.array([r[1] for r in rows]),'g':np.array([gi[r[0]] for r in rows])})
 out={'doc':d,'ids':ids,'k':k,'games':games,'zones':zones};_cache[season]=out;return out
def prepare(x,z,fold,sigma):
 raw=x['zones'][z];mask=np.ones(len(raw['n']),bool) if fold is None else raw['fold']!=fold;minutes=sum(v for _,f,ps in x['doc']['minutes'] if fold is None or f!=fold for _,v in ps);n=raw['n'][mask];b=raw['b'][mask];mu=b.sum()/n.sum();nu=60*n.sum()/minutes
 return {'x':raw['x'][mask] if sigma else raw['x0'][mask],'n':n,'b':b,'mu':mu,'nu':nu,'base':float(logit(mu)),'k':x['k'],'sigma':sigma,'mask':mask,'minutes':minutes}
def loss_gradient(params,t):
 eta=t['x']@params;p=expit(eta);res=t['n']*p-t['b'];a=params[:t['k']];priorEta=t['base']+a;priorProb=expit(priorEta);loss=float(np.sum(t['n']*np.logaddexp(0,eta)-t['b']*eta)+t['nu']*np.sum(np.logaddexp(0,priorEta)-t['mu']*priorEta));grad=np.asarray(t['x'].T@res);grad[:t['k']]+=t['nu']*(priorProb-t['mu'])
 if t['sigma']:
  d=params[t['k']:2*t['k']];loss+=float(np.dot(d,d)/(2*t['sigma']**2));grad[t['k']:2*t['k']]+=d/t['sigma']**2
 return loss,grad
def hessian(params,t):
 p=expit(t['x']@params);w=t['n']*p*(1-p);diag=np.zeros(len(params));q=expit(t['base']+params[:t['k']]);diag[:t['k']]=t['nu']*q*(1-q)
 if t['sigma']:diag[t['k']:2*t['k']]=1/t['sigma']**2
 return (t['x'].T@t['x'].multiply(w[:,None])+sparse.diags(diag)).tocsc()
def fit(t):
 k=t['k'];own=t['x'][:,:k];counts=np.asarray(own.T@t['n']);made=np.asarray(own.T@t['b']);initialOwn=logit((made+t['nu']*t['mu'])/(counts+t['nu']))-t['base'];initial=np.r_[initialOwn,np.zeros(k),t['base']] if t['sigma'] else np.r_[initialOwn,t['base']];total=t['n'].sum()
 def objective(params):l,g=loss_gradient(params,t);return l/total,g/total
 result=minimize(objective,initial,jac=True,method='L-BFGS-B',options={'maxiter':1500,'ftol':1e-15,'gtol':2e-11,'maxcor':25,'maxls':50});params=result.x.copy();steps=0
 for _ in range(8):
  loss,gradient=loss_gradient(params,t)
  if np.max(abs(gradient))<=1e-5:break
  delta=spsolve(hessian(params,t),-gradient);scale=1.
  while scale>2**-20:
   trial=params+scale*delta;newloss,_=loss_gradient(trial,t)
   if newloss<=loss+1e-9:break
   scale/=2
  assert scale>2**-20;params=trial;steps+=1
 loss,gradient=loss_gradient(params,t);maximum=float(np.max(abs(gradient)));assert maximum<=.001,maximum
 return params,{'success':True,'lbfgsSuccess':bool(result.success),'lbfgsMessage':str(result.message),'iterations':result.nit,'newtonSteps':steps,'maxAbsoluteGradient':maximum,'penalizedNll':loss}
def task(job):
 season,sigma,fold=job;x=data(season);zones=[];nll=0.;gameLoss=np.zeros(len(x['games']));gameN=np.zeros(len(x['games']));trainingN=0
 for z in range(3):
  t=prepare(x,z,fold,sigma);params,diagnostic=fit(t);raw=x['zones'][z];test=~t['mask'] if fold is not None else t['mask'];matrix=raw['x'][test] if sigma else raw['x0'][test];eta=matrix@params;loss=raw['n'][test]*np.logaddexp(0,eta)-raw['b'][test]*eta;nll+=float(loss.sum());gameLoss+=np.bincount(raw['g'][test],weights=loss,minlength=len(gameLoss));gameN+=np.bincount(raw['g'][test],weights=raw['n'][test],minlength=len(gameN));trainingN+=int(t['n'].sum())
  zones.append({'zone':['long','mid','short'][z],'intercept':float(params[-1]),'shooterLogits':params[:x['k']].tolist(),'defenderLogits':params[x['k']:2*x['k']].tolist() if sigma else [0.]*x['k'],'trainingFga':int(t['n'].sum()),'trainingPlayerMinutes':t['minutes'],'priorEquivalentFga':float(t['nu']),'trainingLeagueMake':float(t['mu']),'fit':diagnostic})
 return {'season':season,'sigma':sigma,'heldoutFold':fold,'playerIds':x['ids'],'zones':zones,'nll':nll,'trainingFga':trainingN,'evaluatedFga':int(gameN.sum()),'games':[[gid,float(gameLoss[i]),int(gameN[i])] for i,gid in enumerate(x['games']) if gameN[i]>0]}

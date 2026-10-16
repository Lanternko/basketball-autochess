import json,math
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from scipy.optimize import minimize
R=Path('reports/player-impact-v39')
_cache={}
def data(season):
 if season in _cache:return _cache[season]
 d=json.loads((R/(season+'-miss-data.json')).read_text(encoding='utf-8'));ids=[p['playerId'] for p in d['players']];lookup={pid:i for i,pid in enumerate(ids)};rows=d['rows'];games=sorted({r[0] for r in rows});gi={gid:i for i,gid in enumerate(games)}
 x={'doc':d,'ids':ids,'idx':np.array([[lookup[pid] for pid in r[4]] for r in rows]),'n':np.array([r[5] for r in rows],float),'b':np.array([r[6] for r in rows],float),'z':np.array([r[3] for r in rows]),'fold':np.array([r[1] for r in rows]),'g':np.array([gi[r[0]] for r in rows]),'games':games}
 x['k']=len(ids);_cache[season]=x;return x
def loss_gradient(params,x,mask,sigma):
 idx=x['idx'][mask];n=x['n'][mask];b=x['b'][mask];z=x['z'][mask];theta=params[:x['k']];logs=theta[idx]+params[x['k']:][z,None];ld=logsumexp(np.column_stack([np.zeros(len(n)),logs]),axis=1);p=np.exp(logs-ld[:,None]);residual=n[:,None]*p-b
 loss=np.dot(n,ld)-np.sum(b*logs)+np.dot(theta,theta)/(2*sigma*sigma)
 grad=np.r_[np.bincount(idx.ravel(),weights=residual.ravel(),minlength=x['k'])+theta/(sigma*sigma),np.bincount(z,weights=residual.sum(axis=1),minlength=3)]
 return loss,grad
def fit(x,mask,sigma):
 n=x['n'][mask];z=x['z'][mask];b=x['b'][mask];nz=np.bincount(z,weights=n,minlength=3);bz=np.bincount(z,weights=b.sum(axis=1),minlength=3)
 assert np.all(bz>0) and np.all(nz>bz);initial=np.r_[np.zeros(x['k']),np.log(bz/(5*(nz-bz)))];total=n.sum()
 if sigma==0:return initial,{'success':True,'iterations':0,'maxAbsoluteGradient':0.0,'nll':float(np.sum(n*np.logaddexp(0,math.log(5)+initial[x['k']:][z]))-np.dot(b.sum(axis=1),initial[x['k']:][z]))}
 def objective(t):l,g=loss_gradient(t,x,mask,sigma);return l/total,g/total
 result=minimize(objective,initial,jac=True,method='L-BFGS-B',options={'maxiter':1500,'ftol':1e-15,'gtol':2e-11,'maxls':50,'maxcor':25})
 loss,grad=loss_gradient(result.x,x,mask,sigma);maximum=float(np.max(np.abs(grad)))
 if not result.success or maximum>1e-3:raise RuntimeError((result.message,maximum))
 return result.x,{'success':True,'iterations':result.nit,'maxAbsoluteGradient':maximum,'nll':float(loss),'message':str(result.message)}
def score(x,params,mask):
 logs=params[:x['k']][x['idx'][mask]]+params[x['k']:][x['z'][mask],None];ld=logsumexp(np.column_stack([np.zeros(len(logs)),logs]),axis=1);loss=x['n'][mask]*ld-(x['b'][mask]*logs).sum(axis=1)
 games=np.bincount(x['g'][mask],weights=loss,minlength=len(x['games']));n=np.bincount(x['g'][mask],weights=x['n'][mask],minlength=len(x['games']));return float(loss.sum()),[[gid,float(games[i]),int(n[i])] for i,gid in enumerate(x['games']) if n[i]>0]
def recipient_benchmark(x,train,test):
 idx=x['idx'][train];n=x['n'][train];b=x['b'][train];z=x['z'][train];exposure=np.bincount(idx.ravel(),weights=np.repeat(n,5),minlength=x['k']);counts=np.bincount(idx.ravel(),weights=b.ravel(),minlength=x['k']);folds=set(x['fold'][train].tolist());minutes=sum(v for _,fold,rows in x['doc']['minutes'] if fold in folds for _,v in rows)
 k=240*n.sum()/(minutes/5);rate=(counts+k*b.sum()/(5*n.sum()))/(exposure+k);nz=np.bincount(z,weights=n,minlength=3);bz=np.bincount(z,weights=b.sum(axis=1),minlength=3);prob=bz/nz
 r=rate[x['idx'][test]];weights=r/r.sum(axis=1)[:,None];n=x['n'][test];b=x['b'][test];p=prob[x['z'][test]];loss=-(n-b.sum(axis=1))*np.log1p(-p)-(b*(np.log(p)[:,None]+np.log(weights))).sum(axis=1)
 g=np.bincount(x['g'][test],weights=loss,minlength=len(x['games']));num=np.bincount(x['g'][test],weights=n,minlength=len(x['games']));return {'nll':float(loss.sum()),'kappaMissExposuresEquivalentTo240Minutes':float(k),'games':[[gid,float(g[i]),int(num[i])] for i,gid in enumerate(x['games']) if num[i]>0]}
def task(job):
 season,sigma,fold=job;x=data(season);mask=np.ones(len(x['n']),bool) if fold is None else x['fold']!=fold;params,diagnostic=fit(x,mask,sigma);test=~mask if fold is not None else mask;nll,games=score(x,params,test)
 return {'season':season,'sigma':sigma,'heldoutFold':fold,'playerIds':x['ids'],'playerLogHazards':params[:x['k']].tolist(),'zoneLogBase':params[x['k']:].tolist(),'trainingMisses':int(x['n'][mask].sum()),'evaluatedMisses':int(x['n'][test].sum()),'nll':nll,'games':games,'fit':diagnostic,'recipientBenchmark':recipient_benchmark(x,mask,test) if fold is not None else None}

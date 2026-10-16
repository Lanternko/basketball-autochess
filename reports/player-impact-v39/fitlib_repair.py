"""Numerical repair only: same convex objective, prior grid and acceptance gate.

The archived first run stopped at gradient .0016126 > .001; retain its files.
Refine L-BFGS with exact Newton steps, without relaxing stationarity tolerance.
"""
from fitlib import *
from scipy.linalg import solve

def hessian(params,x,mask,sigma):
 idx=x['idx'][mask];n=x['n'][mask];z=x['z'][mask];k=x['k'];logs=params[:k][idx]+params[k:][z,None]
 ld=logsumexp(np.column_stack([np.zeros(len(n)),logs]),axis=1);p=np.exp(logs-ld[:,None]);h=np.zeros((k+3,k+3))
 for i in range(5):
  np.add.at(h,(idx[:,i],idx[:,i]),n*p[:,i])
  for j in range(5):np.add.at(h,(idx[:,i],idx[:,j]),-n*p[:,i]*p[:,j])
  cross=n*p[:,i]*(1-p.sum(axis=1));np.add.at(h,(idx[:,i],k+z),cross);np.add.at(h,(k+z,idx[:,i]),cross)
 np.add.at(h,(k+z,k+z),n*p.sum(axis=1)*(1-p.sum(axis=1)))
 h[np.arange(k),np.arange(k)]+=1/(sigma*sigma)
 return h

def fit(x,mask,sigma):
 if sigma==0:
  import fitlib
  return fitlib.fit(x,mask,sigma)
 n=x['n'][mask];z=x['z'][mask];b=x['b'][mask];nz=np.bincount(z,weights=n,minlength=3);bz=np.bincount(z,weights=b.sum(axis=1),minlength=3)
 initial=np.r_[np.zeros(x['k']),np.log(bz/(5*(nz-bz)))];total=n.sum()
 def objective(t):l,g=loss_gradient(t,x,mask,sigma);return l/total,g/total
 result=minimize(objective,initial,jac=True,method='L-BFGS-B',options={'maxiter':1500,'ftol':1e-15,'gtol':2e-11,'maxls':50,'maxcor':25})
 params=result.x.copy();steps=0
 for _ in range(8):
  loss,grad=loss_gradient(params,x,mask,sigma)
  if np.max(np.abs(grad))<=1e-5:break
  delta=solve(hessian(params,x,mask,sigma),-grad,assume_a='pos');scale=1.
  while scale>2**-20:
   trial=params+scale*delta;newloss,_=loss_gradient(trial,x,mask,sigma)
   if newloss<=loss+1e-9:break
   scale/=2
  assert scale>2**-20
  params=trial;steps+=1
 loss,grad=loss_gradient(params,x,mask,sigma);maximum=float(np.max(np.abs(grad)))
 if maximum>1e-3:raise RuntimeError(('Newton refinement stationarity failure',maximum))
 return params,{'success':True,'iterations':int(result.nit),'newtonSteps':steps,'maxAbsoluteGradient':maximum,'nll':float(loss),'message':str(result.message),'solver':'same objective; exact Newton refinement after original L-BFGS'}

def task(job):
 season,sigma,fold=job;x=data(season);mask=np.ones(len(x['n']),bool) if fold is None else x['fold']!=fold;params,diagnostic=fit(x,mask,sigma);test=~mask if fold is not None else mask;nll,games=score(x,params,test)
 return {'season':season,'sigma':sigma,'heldoutFold':fold,'playerIds':x['ids'],'playerLogHazards':params[:x['k']].tolist(),'zoneLogBase':params[x['k']:].tolist(),'trainingMisses':int(x['n'][mask].sum()),'evaluatedMisses':int(x['n'][test].sum()),'nll':nll,'games':games,'fit':diagnostic,'recipientBenchmark':recipient_benchmark(x,mask,test) if fold is not None else None}

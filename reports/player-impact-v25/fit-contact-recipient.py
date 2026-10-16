"""Fit conditional ordinary-contact victim strengths, regularized with whole-game CV."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,minimize_scalar

root=Path('reports/player-impact-v25');seasons=['2022-23','2023-24','2024-25','2025-26']
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
datasets={};folds=[];fits={}
for season in seasons:
 src=read(root/f'{season}-contact-policy.json');ids=np.array(sorted(map(int,src['players'])),dtype=np.int64)
 rows=np.array([[*r['choice'],g['fold']] for g in src['games'] for r in g['rows'] if r['group']=='ordinary'],dtype=np.int64)
 ix=np.searchsorted(ids,rows[:,:6]);assert np.all(ids[ix]==rows[:,:6]);win=ix[:,0];risk=ix[:,1:];fold=rows[:,6]
 datasets[season]=(src,ids,win,risk)
 if season in seasons[:3]:
  for f in range(5):
   test=fold==f;folds.append((season,f,len(ids),win[~test],risk[~test],win[test],risk[test]))

def fit_weights(k,win,risk,size):
 observed=np.bincount(win,minlength=size);flat=risk.ravel()
 def objective(z):
  weights=np.exp(z[risk]);den=weights.sum(axis=1);prob=weights/den[:,None]
  loss=float(np.log(den).sum()-z[win].sum()+.5*k*np.dot(z,z))
  gradient=np.bincount(flat,prob.ravel(),minlength=size)-observed+k*z
  return loss,gradient
 fitted=minimize(objective,np.zeros(size),jac=True,method='L-BFGS-B',options={'gtol':1e-7,'ftol':1e-14,'maxiter':6000,'maxcor':30,'maxls':40})
 assert fitted.success,fitted.message
 assert np.max(np.abs(fitted.jac))<.005,np.max(np.abs(fitted.jac))
 return fitted.x

def score(logk,details=False):
 key=round(float(logk),12)
 if key not in fits:
  k=math.exp(logk);cells=[]
  for season,f,size,train,trisk,test,testrisk in folds:
   z=fit_weights(k,train,trisk,size);loss=float((np.log(np.exp(z[testrisk]).sum(axis=1))-z[test]).sum())
   cells.append({'season':season,'fold':f,'events':len(test),'nll':loss})
  fits[key]=cells
  print('CV',k,sum(c['nll'] for c in cells),flush=True)
 return fits[key] if details else sum(c['nll'] for c in fits[key])

target=root/'contact-recipient-prior.json'
if target.exists():raise RuntimeError('Preserve prior')
fit=minimize_scalar(score,bounds=(math.log(.001),math.log(10000)),method='bounded',options={'xatol':.005});assert fit.success
k=math.exp(fit.x)
prior={'l2Precision':k,'fitSeasons':seasons[:3],'excludedFitSeason':seasons[3],'folds':5,'design':'Conditional multinomial choice P(drawnPlayer=i|ordinary defensive nonshooting personal contact, actual own five)=exp(z_i)/sum(exp(z_j)). Log strengths have independent zero-centered Gaussian prior, L2 precision chosen by whole-game held-out NLL. Only source recipients/lineups are inputs; no same-game held-out counts, team wins, simulated residuals, OVR, names or ON/OFF. Conditional strengths have no identified cross-disconnected-team absolute scale; the zero-centered prior selects that gauge. They describe recipient allocation, not causal contact-drawing skill or team offensive effect or portable cross-team ability. Source contact frequency and every runtime mechanism are unchanged at this preparation stage.','nll':{'fitted':score(fit.x),'weakRegularizationPrecision0_1':score(math.log(.1)),'uniform':sum(len(f[5])*math.log(5) for f in folds)},'foldScores':score(fit.x,True),'sourceHashes':{str(root/f'{s}-contact-policy.json'):sha(root/f'{s}-contact-policy.json') for s in seasons},'codeHash':sha(Path(__file__))}
for season,(src,ids,win,risk) in datasets.items():
 z=fit_weights(k,win,risk,len(ids));weight=np.exp(z);prob=weight[risk]/weight[risk].sum(axis=1)[:,None]
 observed=np.bincount(win,minlength=len(ids));expected=np.bincount(risk.ravel(),prob.ravel(),minlength=len(ids));exposure=np.bincount(risk.ravel(),minlength=len(ids))
 assert abs(float(expected.sum())-len(win))<1e-8
 cards={str(int(pid)):{'sourceDrawnContacts':int(observed[i]),'sourceContactOpportunities':int(exposure[i]),'logStrength':float(z[i]),'strength':float(weight[i]),'sourceExpectedContacts':float(expected[i])} for i,pid in enumerate(ids)}
 output=root/f'{season}-contact-recipient.json'
 if output.exists():raise RuntimeError('Preserve posterior')
 output.write_text(json.dumps({'season':season,'l2Precision':k,'cards':cards,'sourceHash':prior['sourceHashes'][str(root/f'{season}-contact-policy.json')],'fitCodeHash':prior['codeHash']},indent=2),encoding='utf-8')
 print('FULL',season,len(win),float(np.mean(np.abs(expected-observed))),flush=True)
target.write_text(json.dumps(prior,indent=2),encoding='utf-8');print('FIT',k,prior['nll'],flush=True)

"""Independent direct-probability likelihood, score, gradient and prior selection."""
import json,math,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10),(a,b)
selection=read(R/'selection.json');final=read(R/'fit.json');protocol=read(R/'solver-repair-protocol.json')
for o in [selection,final,protocol]:
 for p,h in o['hashes'].items():assert sha(p)==h,p
for p,h in protocol['retainedCheckpoints'].items():assert sha(p)==h,p
datasets={};summaries=[];gradientMaximum=0;source=[]
for p in sorted((R/'fits').glob('*.json')):
 f=read(p);season=f['season'];datasets.setdefault(season,read(R/(season+'-miss-data.json')));d=datasets[season];ids=[q['playerId'] for q in d['players']];lookup={pid:i for i,pid in enumerate(ids)};assert ids==f['playerIds'];k=len(ids)
 rows=d['rows'];idx=np.array([[lookup[pid] for pid in r[4]] for r in rows]);n=np.array([r[5] for r in rows]);b=np.array([r[6] for r in rows]);z=np.array([r[3] for r in rows]);folds=np.array([r[1] for r in rows]);train=np.ones(len(rows),bool) if f['heldoutFold'] is None else folds!=f['heldoutFold'];test=train if f['heldoutFold'] is None else ~train
 assert f['trainingMisses']==int(n[train].sum()) and f['evaluatedMisses']==int(n[test].sum())
 theta=np.array(f['playerLogHazards']);intercept=np.array(f['zoneLogBase']);lam=np.exp(theta[idx]+intercept[z,None]);den=1+lam.sum(axis=1);prob=lam/den[:,None];pnone=1/den
 losses=-(n-b.sum(axis=1))*np.log(pnone)-(b*np.log(prob)).sum(axis=1);close(losses[test].sum(),f['nll']);games=defaultdict(lambda:np.zeros(2))
 for i,r in enumerate(rows):
  if test[i]:games[r[0]]+=np.array([losses[i],n[i]])
 assert set(games)=={g[0] for g in f['games']}
 for gid,l,count in f['games']:close(games[gid][0],l);assert games[gid][1]==count
 residual=n[train,None]*prob[train]-b[train];gradient=np.r_[np.bincount(idx[train].ravel(),weights=residual.ravel(),minlength=k),np.bincount(z[train],weights=residual.sum(axis=1),minlength=3)]
 sigma=f['sigma'];penalty=0
 if sigma:
  gradient[:k]+=theta/(sigma*sigma);penalty=np.dot(theta,theta)/(2*sigma*sigma);maximum=float(np.max(np.abs(gradient)));assert maximum<1e-3,(p,maximum);gradientMaximum=max(gradientMaximum,maximum)
 else:assert np.all(theta==0);assert max(abs(gradient[k:]))<1e-7
 close(losses[train].sum()+penalty,f['fit']['nll'])
 bench=None;null=None
 if f['heldoutFold'] is not None:
  assert not ({r[0] for i,r in enumerate(rows) if train[i]}&set(games))
  exp=np.bincount(idx[train].ravel(),weights=np.repeat(n[train],5),minlength=k);counts=np.bincount(idx[train].ravel(),weights=b[train].ravel(),minlength=k)
  minute=sum(v for _,fold,ps in d['minutes'] if fold!=f['heldoutFold'] for _,v in ps);prior=240*n[train].sum()/(minute/5);rate=(counts+prior*b[train].sum()/(5*n[train].sum()))/(exp+prior)
  nz=np.bincount(z[train],weights=n[train],minlength=3);bz=np.bincount(z[train],weights=b[train].sum(axis=1),minlength=3);q=bz/nz;w=rate[idx[test]];w/=w.sum(axis=1)[:,None]
  bl=-(n[test]-b[test].sum(axis=1))*np.log1p(-q[z[test]])-(b[test]*(np.log(q[z[test]])[:,None]+np.log(w))).sum(axis=1)
  nl=-(n[test]-b[test].sum(axis=1))*np.log1p(-q[z[test]])-(b[test]*np.log(q[z[test],None]/5)).sum(axis=1)
  close(prior,f['recipientBenchmark']['kappaMissExposuresEquivalentTo240Minutes']);close(bl.sum(),f['recipientBenchmark']['nll']);bench=float(bl.sum());null=float(nl.sum());bg=defaultdict(float);ng=defaultdict(float)
  for i,j in enumerate(np.flatnonzero(test)):bg[rows[j][0]]+=bl[i];ng[rows[j][0]]+=nl[i]
  for gid,l,count in f['recipientBenchmark']['games']:close(l,bg[gid]);assert count==games[gid][1]
  differences=np.array([games[g][0]-bg[g] for g in sorted(games)]);mean=float(differences.mean());se=float(differences.std(ddof=1)/math.sqrt(len(differences)))
  ci=[mean-1.96*se,mean+1.96*se]
  summaries.append({'season':season,'sigma':sigma,'fold':f['heldoutFold'],'misses':int(n[test].sum()),'nll':float(losses[test].sum()),'benchmarkNll':bench,'nullNll':null,'meanNllDifferencePerGameVsBenchmark':mean,'pointwiseNormal95':ci})
 else:
  expBlocks=np.bincount(idx.ravel(),weights=(n[:,None]*prob).ravel(),minlength=k);actual=np.bincount(idx.ravel(),weights=b.ravel(),minlength=k);minute=defaultdict(float)
  for _,_,ps in d['minutes']:
   for pid,v in ps:minute[pid]+=v
  source.append({'season':season,'actualBlocks':int(b.sum()),'expectedBlocks':float(expBlocks.sum()),'players':[{'playerId':pid,'name':d['players'][i]['name'],'sourceMinutes':minute[pid],'actualBlocks':int(actual[i]),'expectedBlocks':float(expBlocks[i]),'actual36':float(actual[i]*36/minute[pid]) if minute[pid] else None,'expected36':float(expBlocks[i]*36/minute[pid]) if minute[pid] else None} for i,pid in enumerate(ids)]})
 print(p.name,'verified',flush=True)
assert len(summaries)==80 and len(source)==4
scores=[]
for sigma in [0,.25,.5,1,2]:
 a=[r for r in summaries if r['season']!='2025-26' and r['sigma']==sigma];assert len(a)==15;scores.append({'sigma':sigma,'heldoutNll':sum(r['nll'] for r in a),'misses':sum(r['misses'] for r in a)})
for a,b0 in zip(scores,selection['olderOnlyScores']):
 assert a['sigma']==b0['sigma'] and a['misses']==b0['misses'];close(a['heldoutNll'],b0['heldoutNll'])
minimum=min(r['heldoutNll']/r['misses'] for r in scores);assert min(r['sigma'] for r in scores if r['heldoutNll']/r['misses']<=minimum+1e-10)==selection['selectedSigma']==final['selectedSigma']
# Check exact-Hessian implementation against differences of the analytic gradient.
from fitlib_repair import data,loss_gradient,hessian
x=data('2025-26');f=next(f for f in final['seasons'] if f['season']=='2025-26');params=np.r_[f['playerLogHazards'],f['zoneLogBase']];mask=np.ones(len(x['n']),bool);h=hessian(params,x,mask,.5);maxHessianError=0
for j in [0,100,300,580,582,584]:
 step=np.zeros(len(params));step[j]=1e-5;_,a=loss_gradient(params+step,x,mask,.5);_,b0=loss_gradient(params-step,x,mask,.5);err=float(np.max(np.abs((a-b0)/2e-5-h[:,j])));assert err<1e-5;maxHessianError=max(maxHessianError,err)
out={'passed':True,'fits':84,'retainedCheckpoints':len(protocol['retainedCheckpoints']),'selectedSigma':final['selectedSigma'],'maxGradient':gradientMaximum,'maxHessianFiniteDifferenceError':maxHessianError,'olderOnlyScores':scores,'heldout':summaries,'sourceFullFit':source,'scope':'Whole-game local source reconstruction; full-source fit includes its own outcomes. CIs are per-fold pointwise descriptive, not source/model uncertainty or multiplicity adjusted.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'verify-fit.py',R/'selection.json',R/'fit.json',R/'solver-repair-protocol.json']}}
(R/'fit-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('All84 fits verified; sigma',final['selectedSigma'],'gradientMax',gradientMaximum,flush=True)

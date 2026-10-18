"""Direct-array verification, independent of the sparse fitter's design matrix."""
import json,hashlib,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit,logit
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();close=lambda a,b:math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10)
selection=read(R/'selection.json');final=read(R/'fit.json');null=read(R/'target-null.json');sources=read(R/'data-verification.json');assert sources['passed'];cache={};checks=[];maximumGradient=0.;full=[]
for obj in [selection,final,null,read(R/'source-fit-protocol.json'),read(R/'target-null-protocol.json'),sources]:
 for p,h in obj['hashes'].items():assert sha(p)==h,p
for path in sorted((R/'fits').glob('*.json')):
 f=read(path);season=f['season'];sigma=f['sigma'];fold=f['heldoutFold']
 if season not in cache:
  d=read(R/(season+'-fga-data.json'));ids=[p['playerId'] for p in d['players']];lookup={pid:i for i,pid in enumerate(ids)};games=sorted(r[0] for r in d['minutes']);gi={g:i for i,g in enumerate(games)};zones=[]
  for z in range(3):
   rows=[r for r in d['rows'] if r[2]==z];zones.append({'own':np.array([lookup[r[3]] for r in rows]),'ds':np.array([[lookup[pid] for pid in r[5]] for r in rows]),'fold':np.array([r[1] for r in rows]),'n':np.array([r[6] for r in rows]),'m':np.array([r[7] for r in rows]),'g':np.array([gi[r[0]] for r in rows])})
  cache[season]={'doc':d,'ids':ids,'games':games,'zones':zones}
 x=cache[season];k=len(x['ids']);assert f['playerIds']==x['ids'];gameLoss=np.zeros(len(x['games']));gameN=np.zeros(len(x['games']));zoneChecks=[]
 trainingMinutes=sum(v for _,j,ps in x['doc']['minutes'] if fold is None or j!=fold for _,v in ps)
 for z,zone in enumerate(f['zones']):
  a=np.array(zone['shooterLogits']);d=np.array(zone['defenderLogits']);r=x['zones'][z];train=np.ones(len(r['n']),bool) if fold is None else r['fold']!=fold;test=train if fold is None else ~train;n=r['n'];m=r['m'];eta=zone['intercept']+a[r['own']]+d[r['ds']].sum(axis=1);p=expit(eta);loss=n*np.logaddexp(0,eta)-m*eta;gameLoss+=np.bincount(r['g'][test],weights=loss[test],minlength=len(gameLoss));gameN+=np.bincount(r['g'][test],weights=n[test],minlength=len(gameN));nu=60*n[train].sum()/trainingMinutes;mu=m[train].sum()/n[train].sum();priorEta=logit(mu)+a;priorProb=expit(priorEta);penalty=nu*np.sum(np.logaddexp(0,priorEta)-mu*priorEta)
  assert close(zone['trainingPlayerMinutes'],trainingMinutes) and close(zone['priorEquivalentFga'],nu) and close(zone['trainingLeagueMake'],mu);assert zone['trainingFga']==n[train].sum()
  residual=n[train]*p[train]-m[train];ga=np.bincount(r['own'][train],weights=residual,minlength=k)+nu*(priorProb-mu);gd=np.bincount(r['ds'][train].ravel(),weights=np.repeat(residual,5),minlength=k)
  if sigma:gd+=d/sigma**2;penalty+=np.dot(d,d)/(2*sigma**2);gradient=np.r_[ga,gd,residual.sum()]
  else:assert np.all(d==0);gradient=np.r_[ga,residual.sum()]
  maximum=float(np.max(abs(gradient)));maximumGradient=max(maximumGradient,maximum);assert maximum<=.001,(path,z,maximum);assert close(float(loss[train].sum()+penalty),zone['fit']['penalizedNll'])
  assert not ({x['games'][i] for i in set(r['g'][train])}&{x['games'][i] for i in set(r['g'][test])}) if fold is not None else True
  zoneChecks.append({'zone':zone['zone'],'fga':int(n[test].sum()),'makes':int(m[test].sum()),'expectedMakes':float(np.sum(n[test]*p[test])),'nll':float(loss[test].sum())})
 assert close(float(gameLoss.sum()),f['nll']);assert int(gameN.sum())==f['evaluatedFga'];expected={g:(gameLoss[i],gameN[i]) for i,g in enumerate(x['games']) if gameN[i]}
 assert set(expected)=={r[0] for r in f['games']}
 for gid,l,n in f['games']:assert close(expected[gid][0],l) and expected[gid][1]==n
 if fold is not None:checks.append({'season':season,'sigma':sigma,'fold':fold,'fga':int(gameN.sum()),'nll':float(gameLoss.sum()),'zones':zoneChecks})
 else:full.append({'season':season,'sigma':sigma,'fga':int(gameN.sum()),'nll':float(gameLoss.sum()),'zones':zoneChecks})
 print(path.name,'verified',flush=True)
scores=[]
for sigma in [0,.025,.05,.1,.2,.4]:
 rows=[r for r in checks if r['season']!='2025-26' and r['sigma']==sigma];assert len(rows)==15;scores.append({'sigma':sigma,'heldoutNll':sum(r['nll'] for r in rows),'fga':sum(r['fga'] for r in rows)})
for a,b in zip(scores,selection['olderOnlyScores']):assert a['sigma']==b['sigma'] and a['fga']==b['fga'] and close(a['heldoutNll'],b['heldoutNll'])
minimum=min(r['heldoutNll']/r['fga'] for r in scores);selected=min(r['sigma'] for r in scores if r['heldoutNll']/r['fga']<=minimum+1e-10);assert selected==selection['selectedSigma']==final['selectedSigma'];assert len(full)==4
seasonSummary=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 for sigma in sorted({0,selected}):
  docs=[read(p) for p in (R/'fits').glob('*.json') if read(p)['season']==season and read(p)['sigma']==sigma and read(p)['heldoutFold'] is not None];assert len(docs)==5
  allgames=[r for d in docs for r in d['games']];assert len(allgames)==len({r[0] for r in allgames})==cache[season]['doc']['coverage']['games'];seasonSummary.append({'season':season,'sigma':sigma,'fga':sum(r[2] for r in allgames),'nll':sum(r[1] for r in allgames),'zones':[{'zone':z,'fga':sum(rz['fga'] for r in checks if r['season']==season and r['sigma']==sigma for rz in r['zones'] if rz['zone']==z),'nll':sum(rz['nll'] for r in checks if r['season']==season and r['sigma']==sigma for rz in r['zones'] if rz['zone']==z)} for z in ['long','mid','short']]})
# Finite differences of both objective and gradient; sparse Hessian independent
# checks use direct-array gradients above for fitted stationarity.
from fitlib import data,prepare,loss_gradient,hessian
x=data('2025-26');f=next(f for f in final['seasons'] if f['season']=='2025-26');hessianError=0.;gradientDifferenceError=0.
for z in range(3):
 t=prepare(x,z,None,selected);q=f['zones'][z];params=np.r_[q['shooterLogits'],q['defenderLogits'],q['intercept']] if selected else np.r_[q['shooterLogits'],q['intercept']];h=hessian(params,t);_,g=loss_gradient(params,t)
 for j in [0,100,x['k']-1,len(params)//2,len(params)-1]:
  step=np.zeros(len(params));step[j]=1e-4;l1,g1=loss_gradient(params+step,t);l0,g0=loss_gradient(params-step,t);err=float(max(abs((g1-g0)/2e-4-h[:,j].toarray().ravel())));assert err<1e-4;hessianError=max(hessianError,err);ge=abs((l1-l0)/2e-4-g[j]);assert ge<1e-4;gradientDifferenceError=max(gradientDifferenceError,ge)
out={'passed':True,'fits':len(checks)+len(full),'selectedSigma':selected,'sourceGames':4421,'freshFga':754914,'olderOnlyScores':scores,'heldoutSeasonSummary':seasonSummary,'foldChecks':checks,'fullSourceChecks':full,'maxAbsoluteGradient':maximumGradient,'maxHessianDifferenceError':hessianError,'maxObjectiveGradientDifferenceError':gradientDifferenceError,'scope':'Whole-game source holdout includes each game exactly once at a fixed sigma. Target excludes selection and includes a preregistered no-defense null. Source logits describe adjusted associations; not causal defense, unknown offball/handle skills or an OVR rating.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'verify-fit.py',R/'selection.json',R/'fit.json',R/'target-null.json',R/'source-fit-protocol.json',R/'target-null-protocol.json',R/'data-verification.json']}}
(R/'fit-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('All fits verified',out['fits'],'sigma',selected,'maxGradient',maximumGradient,flush=True)

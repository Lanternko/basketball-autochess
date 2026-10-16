import json,hashlib,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit,logit
R=Path('reports/player-impact-v41');V=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();close=lambda a,b:math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10);selection=read(R/'selection.json');final=read(R/'fit.json');old=read(V/'fit-verification.json');assert old['passed'];cache={};summaries=[];maximum=0.
for obj in [old,read(V/'fit.json'),read(V/'selection.json'),read(V/'target-null.json'),selection,final,read(R/'fit-protocol.json'),read(R/'launcher-protocol.json')]:
 for p,h in obj['hashes'].items():assert sha(p)==h,p
for z in ['long','mid','short']:
 table=[]
 for sigma in [0,.025,.05,.1,.2,.4]:
  rows=[q for r in old['foldChecks'] if r['season']!='2025-26' and r['sigma']==sigma for q in r['zones'] if q['zone']==z];table.append({'sigma':sigma,'nll':sum(q['nll'] for q in rows),'fga':sum(q['fga'] for q in rows)})
 assert table==selection['olderOnlyScores'][z];minimum=min(r['nll']/r['fga'] for r in table);assert min(r['sigma'] for r in table if r['nll']/r['fga']<=minimum+1e-10)==selection['selectedSigmaByZone'][z]
for job in final['jobs']:
 path=job['file'];assert sha(path)==job['sha256'];f=read(path);season=f['season'];sigma=f['sigma'];fold=f['heldoutFold'];assert (season,sigma,fold)==(job['season'],job['sigma'],job['fold'])
 if season not in cache:
  d=read(V/(season+'-fga-data.json'));ids=[p['playerId'] for p in d['players']];lookup={pid:i for i,pid in enumerate(ids)};gs=sorted(r[0] for r in d['minutes']);gi={g:i for i,g in enumerate(gs)};zs=[]
  for z in range(3):
   rs=[r for r in d['rows'] if r[2]==z];zs.append({'own':np.array([lookup[r[3]] for r in rs]),'ds':np.array([[lookup[pid] for pid in r[5]] for r in rs]),'fold':np.array([r[1] for r in rs]),'n':np.array([r[6] for r in rs],float),'m':np.array([r[7] for r in rs],float),'g':np.array([gi[r[0]] for r in rs])})
  cache[season]={'doc':d,'ids':ids,'games':gs,'zones':zs}
 x=cache[season];assert x['ids']==f['playerIds'];k=len(x['ids']);minute=sum(v for _,j,ps in x['doc']['minutes'] if fold is None or j!=fold for _,v in ps);gl=np.zeros(len(x['games']));gn=np.zeros(len(x['games']));zoneNll=[]
 for z,q in enumerate(f['zones']):
  r=x['zones'][z];n=r['n'];m=r['m'];train=np.ones(len(n),bool) if fold is None else r['fold']!=fold;test=train if fold is None else ~train;a=np.array(q['shooterLogits']);d=np.array(q['defenderLogits']);eta=q['intercept']+a[r['own']]+d[r['ds']].sum(axis=1);p=expit(eta);loss=n*np.logaddexp(0,eta)-m*eta;nu=60*n[train].sum()/minute;mu=m[train].sum()/n[train].sum();pe=logit(mu)+a;penalty=nu*np.sum(np.logaddexp(0,pe)-mu*pe);res=n[train]*p[train]-m[train];ga=np.bincount(r['own'][train],weights=res,minlength=k)+nu*(expit(pe)-mu)
  assert close(nu,q['priorEquivalentFga']) and close(mu,q['trainingLeagueMake']) and close(minute,q['trainingPlayerMinutes'])
  if sigma:
   gd=np.bincount(r['ds'][train].ravel(),weights=np.repeat(res,5),minlength=k)+d/sigma**2;penalty+=np.dot(d,d)/(2*sigma**2);grad=np.r_[ga,gd,res.sum()]
  else:assert np.all(d==0);grad=np.r_[ga,res.sum()]
  err=float(max(abs(grad)));maximum=max(maximum,err);assert err<=.001;assert close(loss[train].sum()+penalty,q['fit']['penalizedNll']);gl+=np.bincount(r['g'][test],weights=loss[test],minlength=len(gl));gn+=np.bincount(r['g'][test],weights=n[test],minlength=len(gn));zoneNll.append({'zone':q['zone'],'nll':float(loss[test].sum()),'fga':int(n[test].sum())})
 assert close(gl.sum(),f['nll']) and gn.sum()==f['evaluatedFga'];by={gid:(gl[i],gn[i]) for i,gid in enumerate(x['games']) if gn[i]};assert set(by)=={g[0] for g in f['games']}
 for gid,nll,count in f['games']:assert close(by[gid][0],nll) and by[gid][1]==count
 summaries.append({'season':season,'sigma':sigma,'fold':fold,'zones':zoneNll});print(Path(path).name,'verified',flush=True)
for model in final['seasons']+final['targetHeldout']:
 for i,z in enumerate(['long','mid','short']):
  spec=model['sources'][i];assert spec['zone']==z and spec['sigma']==selection['selectedSigmaByZone'][z] and sha(spec['file'])==spec['sha256'];source=read(spec['file']);assert source['playerIds']==model['playerIds'];assert source['season']==model['season'] and source['heldoutFold']==model['heldoutFold'];assert source['zones'][i]==model['zones'][i]
seasonSummary=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 summary={'season':season,'zones':[]}
 for z in ['long','mid','short']:
  chosen=selection['selectedSigmaByZone'][z];collection=old['foldChecks'] if season!='2025-26' else summaries;records=[]
  for sigma in sorted({0,chosen}):
   rs=[q for r in collection if r['season']==season and r['sigma']==sigma and (r.get('fold') is not None) for q in r['zones'] if q['zone']==z];assert len(rs)==5;records.append({'sigma':sigma,'nll':sum(r['nll'] for r in rs),'fga':sum(r['fga'] for r in rs)})
  null=next(r for r in records if r['sigma']==0);candidate=next(r for r in records if r['sigma']==chosen);summary['zones'].append({'zone':z,'sigma':chosen,'nullNll':null['nll'],'candidateNll':candidate['nll'],'fga':candidate['fga']})
 summary['nullNll']=sum(z['nullNll'] for z in summary['zones']);summary['candidateNll']=sum(z['candidateNll'] for z in summary['zones']);seasonSummary.append(summary)
out={'passed':True,'sourceJobs':len(final['jobs']),'sourceZoneFits':3*len(final['jobs']),'priorV40FitsVerifiedAndUnchanged':104,'selectedSigmaByZone':selection['selectedSigmaByZone'],'maxAbsoluteGradient':maximum,'heldoutSummary':seasonSummary,'scope':'Zone-separable source-only refinement; every selected/reused fit probability, penalty, gradient, whole-game score and assembled zone independently recomputed. Target excluded from prior selection. Source associations, not causal skill or OVR.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'verify-fit.py',R/'selection.json',R/'fit.json',R/'fit-protocol.json',R/'launcher-protocol.json',V/'fit-verification.json']}}
(R/'fit-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('v41 assembled source fits verified',out['selectedSigmaByZone'],flush=True)

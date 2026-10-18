import json,pathlib,hashlib,datetime,numpy as np
R=pathlib.Path(__file__).parent; OLD=R.parent/'step4-rebounds-turnover-time'
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
p=load(R/'protocol.json'); assert hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest()==(R/'protocol.sha256').read_text().strip()
arrays=load(OLD/'seed-arrays.json');real=load(R/'real.json');rng=np.random.default_rng(p['bootstrapSeed']);B=p['bootstrapDraws']
ids=arrays[p['seasons'][0]]['ids']; draw=rng.integers(0,len(ids),(B,len(ids)));sd=rng.integers(0,len(p['seeds']),(B,len(p['seeds'])))
fields=['n','points','fgPoints','ftPoints','additionalOreb','zero','one','two','three','fourPlus']; modes=['first','all']
def counts(games,mode):
 out=np.zeros((len(ids),len(fields)))
 for g in games:
  for row in g['rows']:
   if mode=='first' and not row['first']:continue
   i=ids.index(g['ids'][row['off']]);pt=row['points'];out[i]+=np.array([1,pt,row['fgPoints'],row['ftPoints'],row['additionalOreb'],pt==0,pt==1,pt==2,pt==3,pt>=4],dtype=float)
 return out
def values(c):
 t=c.sum(axis=0);return {k:float(t[j]/t[0]) for j,k in enumerate(fields) if j>0}|{'n':int(t[0])}
oreb={};boot={m:[] for m in modes}
for s in p['seasons']:
 sim=[]
 for seed in p['seeds']:
  run=load(R/f'runs/{s}-{seed}.json');assert len(run['matches'])==len(run['fullOreb']['games'])
  allowed={g['id'] for g in real[s]['games']}
  sim.append([{'id':g['id'],'ids':[g['homeId'],g['awayId']],'rows':rows} for g,rows in zip(run['matches'],run['fullOreb']['games']) if g['id'] in allowed])
 oreb[s]={'games':len(real[s]['games']),'failures':real[s]['failures'],'modes':{}}
 for mode in modes:
  rc=counts(real[s]['games'],mode);sc=np.stack([counts(g,mode) for g in sim]); rm=values(rc);sm=[values(c) for c in sc];avg={k:float(np.mean([m[k] for m in sm])) for k in rm}
  delta={k:avg[k]-rm[k] for k in rm if k!='n'}
  oreb[s]['modes'][mode]={'real':rm,'sim':avg,'simBySeed':sm,'delta':delta}
  # Same franchises and seeds across seasons; each team's anchor frequency remains a weight.
  rr=rc[draw].sum(axis=1); ss=np.stack([sc[sd[:,j,None],draw].sum(axis=1) for j in range(len(p['seeds']))],axis=1)
  br=rr[:,1:]/rr[:,:1];bs=(ss[:,:,1:]/ss[:,:,:1]).mean(axis=1);boot[mode].append(bs-br)
pooled={}
for mode in modes:
 ks=[k for k in fields if k!='n'];d=np.mean(boot[mode],axis=0)
 pooled[mode]={k:{'real':float(np.mean([oreb[s]['modes'][mode]['real'][k] for s in p['seasons']])),'sim':float(np.mean([oreb[s]['modes'][mode]['sim'][k] for s in p['seasons']])),'delta':float(np.mean([oreb[s]['modes'][mode]['delta'][k] for s in p['seasons']])),'joint95':np.quantile(d[:,j],[.025,.975]).tolist()} for j,k in enumerate(ks)}
def components(ov,dv,ix=None):
 if ix is not None:ov=ov[ix];dv=dv[ix]
 ov=ov-ov.mean();dv=dv-dv.mean();mo=np.mean(ov**2);md=np.mean(dv**2);cov=np.mean(ov*dv);mn=np.mean((ov+dv)**2);assert abs(mn-(mo+md+2*cov))<1e-8
 return {'offenseRMSE':float(np.sqrt(mo)),'defenseRMSE':float(np.sqrt(md)),'netRMSE':float(np.sqrt(mn)),'offenseMSE':float(mo),'defenseMSE':float(md),'covariance':float(cov),'errorCorrelation':float(cov/np.sqrt(mo*md)),'cancellationFraction':float(-2*cov/(mo+md))}
comp={};worst={}
for s,a in arrays.items():
 b=load(R.parent/f'step4-t0/{s}/bundle.json');names={t['id']:t['name'] for t in b['league']['teams']}; comp[s]={};v=a['versions']['split'];t=a['truth']
 for unit,ok,dk in [('perGame','off','allowed'),('efficiencyProxy','ortg','drtg')]:
  o=np.mean(v[ok],axis=0)-t[ok];d=np.array(t[dk])-np.mean(v[dk],axis=0);comp[s][unit]=components(o,d)
  if unit=='perGame':
   oc=o-o.mean();dc=d-d.mean();worst[s]=sorted([{'team':names[i],'offenseError':float(oc[j]),'defenseError':float(dc[j]),'netError':float(oc[j]+dc[j]),'grossAbsoluteError':float(abs(oc[j])+abs(dc[j])),'cancelledAbsoluteError':float(abs(oc[j])+abs(dc[j])-abs(oc[j]+dc[j]))} for j,i in enumerate(a['ids'])],key=lambda r:r['cancelledAbsoluteError'],reverse=True)[:8]
 common=(np.mean(v['off'],axis=0)-t['off']+np.mean(v['allowed'],axis=0)-t['allowed'])/2
 pace=np.mean(np.asarray(v['off'])/np.asarray(v['ortg'])*100,axis=0)-np.asarray(t['off'])/np.asarray(t['ortg'])*100
 comp[s]['paceAssociation']={'derivedProxyDefinition':'off points/game divided by offense proxy * 100; simulation compute per seed then mean','correlationWithCommonScoringError':float(np.corrcoef(pace,common)[0,1]),'centeredProxyErrorRMSE':float(np.sqrt(np.mean((pace-pace.mean())**2))),'observationalNotCausal':True}
result={'oreb':oreb,'pooledOreb':pooled,'errorComponents':comp,'largestCancellations':worst,'limits':['three seeds for conditional possession diagnosis; not an adoption test','all four seasons already seen; individual OREB input own-season in-sample','ordinary FT and repeated rebounds included; special-FT possessions excluded','all-anchor values overlap; first-anchor values do not','attack/defense error decomposition describes cancellation, not causal attribution to an event mechanism']}
(R/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
issues=[]
for f,h in p['inputHashes'].items():
 if hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h:issues.append(f)
protected=load(OLD/'protected-before.json')
for f,h in protected.items():
 if not pathlib.Path(f).exists() or hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h:issues.append(f)
assert not issues,issues
(R/'audit.json').write_text(json.dumps({'registeredSHA':(R/'protocol.sha256').read_text().strip(),'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protectedFiles':len(protected),'issues':issues,'parity':load(R/'parity.json')},indent=2)+'\n',encoding='utf8')
print(json.dumps({'pooledOreb':pooled,'errorComponents':comp},ensure_ascii=True,indent=2))

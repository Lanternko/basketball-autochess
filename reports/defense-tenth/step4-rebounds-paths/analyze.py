import json,pathlib,numpy as np,hashlib,datetime
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');real=load(R/'real.json');base=load(R.parent/'step4-rebounds-turnover-time/seed-arrays.json');ids=base['2022-23']['ids'];routes=p['definitions']['routes'];rng=np.random.default_rng(p['bootstrapSeed']);B=p['bootstrapDraws'];draw=rng.integers(0,30,(B,30));weights=np.stack([(draw==i).sum(axis=1) for i in range(30)],axis=1);sd=rng.integers(0,3,(B,3))
fields=['n','points','fgPoints','ftPoints','firstFgN','firstFgMade','firstFgPoints','missN','recoverPlayer','recoverTeam','foulBeforeAttempt']
def tally(games):
 c=np.zeros((30,len(routes),len(fields)))
 for g in games:
  for x in g['rows']:
   if not x['first']:continue
   i=ids.index(g['ids'][x['off']]);j=routes.index(x['route']);c[i,j]+=np.array([1,x['points'],x['fgPoints'],x['ftPoints'],x['firstFgZone'] is not None,x['firstFgMade'] is True,x['firstFgPoints'],x['firstFgMiss'],x['recovery']=='player',x['recovery']=='team',x['foulBeforeAttempt']],float)
 return c
def ratios(c):
 n=c[...,0].sum(axis=-1,keepdims=True);pr=np.divide(c[...,0],n,out=np.zeros_like(c[...,0]),where=n>0);v=np.divide(c[...,1],c[...,0],out=np.zeros_like(c[...,0]),where=c[...,0]>0)
 return pr,v
def overall(c):
 z=c.sum(axis=-2);return {'points':z[...,1]/z[...,0],'firstFgPoints':z[...,6]/z[...,0],'postFirstFgPoints':(z[...,1]-z[...,6])/z[...,0],'firstFgMakeRate':z[...,5]/z[...,4],'firstFgReached':z[...,4]/z[...,0],'recoveryPlayerGivenMiss':z[...,8]/z[...,7],'recoveryTeamGivenMiss':z[...,9]/z[...,7],'foulBeforeAttempt':z[...,10]/z[...,0]}
result={};routeBoot=[];overallBoot=[];attemptBoot=[]
for season in p['seasons']:
 rc=tally(real[season]['games']);sc=[];allowed={g['id'] for g in real[season]['games']}
 for seed in p['seeds']:
  run=load(R/f'runs/{season}-{seed}.json');gs=[{'ids':[g['homeId'],g['awayId']],'rows':rows} for g,rows in zip(run['matches'],run['fullOreb']['games']) if g['id'] in allowed];sc.append(tally(gs))
 sc=np.array(sc);rt=rc.sum(axis=0);st=sc.sum(axis=1);pr,vr=ratios(rt);ps,vs=ratios(st);freq=(ps-pr)*(vs+vr)/2;value=(vs-vr)*(ps+pr)/2;contrib=ps*vs-pr*vr
 assert np.max(abs(contrib-freq-value))<1e-10
 rm=overall(rt);sm=overall(st)
 routeMakeReal=np.divide(rt[:,5],rt[:,4],out=np.zeros_like(rt[:,5]),where=rt[:,4]>0);routeMakeSim=np.divide(st[:,:,5],st[:,:,4],out=np.zeros_like(st[:,:,5]),where=st[:,:,4]>0)
 result[season]={'games':len(real[season]['games']),'firstAnchorsReal':int(rt[:,0].sum()),'real':{k:float(v) for k,v in rm.items()},'simulation':{k:float(v.mean()) for k,v in sm.items()},'routes':{k:{'realProbability':float(pr[j]),'simProbability':float(ps[:,j].mean()),'realValue':float(vr[j]),'simValue':float(vs[:,j].mean()),'realFirstFgMake':float(routeMakeReal[j]),'simFirstFgMake':float(routeMakeSim[:,j].mean()),'frequencyContribution':float(freq[:,j].mean()),'valueContribution':float(value[:,j].mean()),'totalContribution':float(contrib[:,j].mean())} for j,k in enumerate(routes)}}
 ar=pr[:4].sum();ass=ps[:,:4].sum(axis=1);qr=rm['points']/ar;qs=sm['points']/ass
 af=(ass-ar)*(qs+qr)/2;av=(qs-qr)*(ass+ar)/2
 result[season]['attemptDecomposition']={'realAttemptProbability':float(ar),'simAttemptProbability':float(ass.mean()),'realValueGivenAttempt':float(qr),'simValueGivenAttempt':float(qs.mean()),'frequencyContribution':float(af.mean()),'valueContribution':float(av.mean())}
 rr=np.einsum('bi,irk->brk',weights,rc);ss=np.stack([np.einsum('bi,irk->brk',weights,c) for c in sc],axis=1);ss=ss[np.arange(B)[:,None],sd];br,bv=ratios(rr);bs,bsv=ratios(ss)
 ff=((bs-br[:,None,:])*(bsv+bv[:,None,:])/2).mean(axis=1);vv=((bsv-bv[:,None,:])*(bs+br[:,None,:])/2).mean(axis=1)
 brm=np.divide(rr[:,:,5],rr[:,:,4],out=np.zeros_like(rr[:,:,5]),where=rr[:,:,4]>0);bsm=np.divide(ss[:,:,:,5],ss[:,:,:,4],out=np.zeros_like(ss[:,:,:,5]),where=ss[:,:,:,4]>0)
 routeBoot.append(np.stack([bs.mean(axis=1)-br,ff,vv,ff+vv,bsm.mean(axis=1)-brm],axis=-1));ro=overall(rr);so=overall(ss);overallBoot.append({k:so[k].mean(axis=1)-ro[k] for k in ro})
 bar=br[:,:4].sum(axis=1);bas=bs[:,:,:4].sum(axis=2);bqr=ro['points']/bar;bqs=so['points']/bas
 attemptBoot.append(np.stack([((bas-bar[:,None])*(bqs+bqr[:,None])/2).mean(axis=1),((bqs-bqr[:,None])*(bas+bar[:,None])/2).mean(axis=1)],axis=-1))
pool={};rb=np.mean(routeBoot,axis=0)
for j,k in enumerate(routes):
 x={key:float(np.mean([result[s]['routes'][k][key] for s in p['seasons']])) for key in result[p['seasons'][0]]['routes'][k]}
 for index,key in enumerate(['probabilityDelta','frequencyContribution','valueContribution','totalContribution','firstFgMakeDelta']):
  point=x['simProbability']-x['realProbability'] if index==0 else x['simFirstFgMake']-x['realFirstFgMake'] if index==4 else x[key];x[key+'Interval']={'delta':point,'joint95':np.quantile(rb[:,j,index],[.025,.975]).tolist()}
 pool[k]=x
op={}
for k in result[p['seasons'][0]]['real']:
 rv=np.mean([result[s]['real'][k] for s in p['seasons']]);sv=np.mean([result[s]['simulation'][k] for s in p['seasons']]);boot=np.mean([x[k] for x in overallBoot],axis=0);op[k]={'real':float(rv),'sim':float(sv),'delta':float(sv-rv),'joint95':np.quantile(boot,[.025,.975]).tolist()}
assert abs(sum(x['totalContribution'] for x in pool.values())-op['points']['delta'])<1e-10
old=load(R.parent/'step4-rebounds-possession-value/analysis.json')['pooledOreb']['first'];assert abs(op['points']['real']-old['points']['real'])<1e-10;assert abs(op['points']['sim']-old['points']['sim'])<1e-10
attempt={k:float(np.mean([result[s]['attemptDecomposition'][k] for s in p['seasons']])) for k in result[p['seasons'][0]]['attemptDecomposition']};ab=np.mean(attemptBoot,axis=0)
for j,k in enumerate(['frequencyContribution','valueContribution']):attempt[k+'Joint95']=np.quantile(ab[:,j],[.025,.975]).tolist()
assert abs(attempt['frequencyContribution']+attempt['valueContribution']-op['points']['delta'])<1e-10
out={'seasons':result,'pooledRoutes':pool,'pooledOverall':op,'attemptDecomposition':attempt,'accountingIdentityPassed':True,'interpretation':'Frequency/value decomposition is exact arithmetic, not causal or guaranteed benefit from fixing a probability. Conditional selection and opponent/card mix remain.'}
(R/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
protected=load(R/'protected-before.json');protected.update(load(R.parent/'step4-rebounds-turnover-time/protected-before.json'));issues=[f for f,h in protected.items() if not pathlib.Path(f).exists() or hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h];assert not issues
(R/'audit.json').write_text(json.dumps({'protectedFiles':len(protected),'issues':issues,'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocolSHA':hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf8')
print(json.dumps({'overall':op,'routes':pool},indent=2))

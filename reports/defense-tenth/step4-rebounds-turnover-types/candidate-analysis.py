import pathlib,json,numpy as np
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');real=load(R/'real.json');ids=load(R.parent/'step4-rebounds-turnover-time/seed-arrays.json')[p['seasons'][0]]['ids'];B=p['bootstrapDraws'];rng=np.random.default_rng(p['bootstrapSeed']);draw=rng.integers(0,30,(B,30));w=np.stack([(draw==i).sum(1) for i in range(30)],1);sd=rng.integers(0,3,(B,3))
cats=['passingLive','handlingLive','otherLive','passingDead','handlingDead','offensiveFoul','otherViolation','outUnclassified','unmappedDead','clock','ownershipOther'];mapping=dict(zip(['passSteal','touchSteal','passOutTov','handlingOutTov','offensiveFoulTov','otherViolationTov','unmappedDeadTov','SHOT_CLOCK','DREB','TEAM_DREB'],['passingLive','handlingLive','passingDead','handlingDead','offensiveFoul','otherViolation','unmappedDead','clock','ownershipOther','ownershipOther']))
keys=['n']+cats+['early_'+k for k in cats];ix={k:i for i,k in enumerate(keys)}
def tally(gs,first):
 a=np.zeros((30,len(keys)));raw={}
 for g in gs:
  for r in g['rows']:
   if (first and not r['first']) or not r['windowEligible']:continue
   i=ids.index(g['ids'][r['off']]);a[i,0]+=1
   if r['firstKind']!='loss':continue
   k=r.get('lossCategory') or mapping.get(r['lossKind'],'unmappedDead');a[i,ix[k]]+=1
   if r['earlyLoss']:a[i,ix['early_'+k]]+=1
   text=r.get('lossRaw') or r['lossKind'];raw[text]=raw.get(text,0)+1
 return a,raw
def metrics(a):
 def rate(names,den='n'):
  z=sum(a[...,ix[k]] for k in names);return np.divide(z,a[...,ix[den]],out=np.zeros_like(z),where=a[...,ix[den]]>0)
 o={k:rate([k]) for k in keys if k!='n'}
 o['totalTurnover']=sum(o[k] for k in cats if k!='ownershipOther');o['live']=sum(o[k] for k in ['passingLive','handlingLive','otherLive']);o['dead']=o['totalTurnover']-o['live'];o['matchedDead']=sum(o[k] for k in ['passingDead','handlingDead','offensiveFoul','otherViolation']);o['matchedGeneric']=o['handlingLive']+o['matchedDead'];o['unknown']=sum(o[k] for k in ['otherLive','outUnclassified','unmappedDead']);o['unknownShareOfTurnovers']=np.divide(o['unknown'],o['totalTurnover'],out=np.zeros_like(o['unknown']),where=o['totalTurnover']>0);o['earlyTurnover']=sum(o['early_'+k] for k in cats if k!='ownershipOther');o['lateTurnover']=o['totalTurnover']-o['earlyTurnover'];return o
results={};pools={}
for first,name in [(False,'allAnchors'),(True,'firstAnchors')]:
 seasonResults={};boot=[]
 for season in p['seasons']:
  rc,rr=tally(real[season]['games'],first);rm=metrics(rc.sum(0));rb=metrics(w@rc);cs=[];sr={};allowed={g['id'] for g in real[season]['games']}
  for seed in p['seeds']:
   run=load(R/f'runs/{season}-candidate-{seed}.json');gs=[{'ids':[m['homeId'],m['awayId']],'rows':rows} for m,rows in zip(run['matches'],run['fullOreb']['games']) if m['id'] in allowed];c,raw=tally(gs,first);cs.append(c)
   for k,v in raw.items():sr[k]=sr.get(k,0)+v/3
  cs=np.array(cs);sm={k:float(v.mean()) for k,v in metrics(cs.sum(1)).items()};bs=np.stack([w@c for c in cs],axis=1);bs=bs[np.arange(B)[:,None],sd];sb={k:v.mean(1) for k,v in metrics(bs).items()};boot.append({k:sb[k]-rb[k] for k in rb});seasonResults[season]={'real':{k:float(v) for k,v in rm.items()},'baseline':sm,'realN':int(rc[:,0].sum()),'baselineN':float(cs[:,:,0].sum(1).mean()),'realRaw':rr,'baselineRaw':sr}
 results[name]=seasonResults;pool={v:{k:float(np.mean([seasonResults[s][v][k] for s in p['seasons']])) for k in seasonResults[p['seasons'][0]][v]} for v in ['real','baseline']};pool['baselineMinusReal']={k:{'delta':pool['baseline'][k]-pool['real'][k],'joint95':np.quantile(np.mean([bb[k] for bb in boot],0),[.025,.975]).tolist()} for k in pool['real']};pools[name]=pool
x=pools['allAnchors'];guards={'handlingLiveExcess':x['baselineMinusReal']['handlingLive']['joint95'][0]>0,'matchedDeadExcess':x['baselineMinusReal']['matchedDead']['joint95'][0]>0,'unknownAtMost5pct':x['real']['unknownShareOfTurnovers']<=.05};mult=x['real']['matchedGeneric']/x['baseline']['matchedGeneric'];eligible=all(guards.values()) and 0<mult<1
out={'perSeason':results,'pooled':pools,'registeredGuards':guards,'candidateEligible':eligible,'registeredMultiplierIfEligible':mult if eligible else None,'simulationVersion':'candidate; baseline-labeled dictionary entries contain candidate for comparison with real only','interpretation':'engine touchSteal as handlingLive is a proxy; generic gate also produces passing dead/fouls/violations. One scalar cannot correct opposing category errors. Four seasons seen/in-sample; three seeds; joint20k95 intervals.'}
(R/'candidate-diagnosis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps({'guards':guards,'candidateEligible':eligible,'allAnchorPooled':x},indent=2))

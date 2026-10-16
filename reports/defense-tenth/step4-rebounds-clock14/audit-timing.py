import pathlib,json,numpy as np
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');d=load(R/'real.json');ids=load(R.parent/'step4-rebounds-turnover-time/seed-arrays.json')[p['seasons'][0]]['ids'];B=p['bootstrapDraws'];rng=np.random.default_rng(p['bootstrapSeed']);draw=rng.integers(0,30,(B,30));w=np.stack([(draw==i).sum(1) for i in range(30)],1);rows=[];out={};boots=[]
keys=['anchors','eligible','clock','eligibleClock','compatible','negative','under3','from3to13','from13to14','from14to15','over15','shortPeriodClock'];ix={k:i for i,k in enumerate(keys)}
for s in p['seasons']:
 a=np.zeros((30,len(keys)));events=[]
 for g in d[s]['games']:
  for r in g['rows']:
   i=ids.index(g['ids'][r['off']]);a[i,ix['anchors']]+=1;eligible=r['anchorSeconds']>14;a[i,ix['eligible']]+=eligible
   if r['firstKind']!='loss' or r['lossCategory']!='clock':continue
   dt=r['firstSeconds'];a[i,ix['clock']]+=1;a[i,ix['shortPeriodClock']]+=not eligible
   event={'season':s,'game':g['id'],'offense':g['ids'][r['off']],'firstAnchorInPossession':r['first'],'anchorSeconds':r['anchorSeconds'],'elapsedSeconds':dt,'eligible':eligible,'clockAction':r['firstLossAction'],**r['source']};events.append(event)
   if eligible:
    a[i,ix['eligibleClock']]+=1;a[i,ix['compatible']]+=dt>=13;a[i,ix['negative']]+=dt<0
    key='under3' if dt<3 else 'from3to13' if dt<13 else 'from13to14' if dt<14 else 'from14to15' if dt<=15 else 'over15';a[i,ix[key]]+=1
 z=a.sum(0);ratio=lambda v,n,de:np.divide(v[...,ix[n]],v[...,ix[de]],out=np.zeros_like(v[...,ix[n]]),where=v[...,ix[de]]>0)
 bs=w@a;compat=ratio(z,'compatible','eligibleClock');out[s]={'games':len(d[s]['games']),'counts':{k:int(z[ix[k]]) for k in keys},'eligibleClockRate':float(ratio(z,'eligibleClock','eligible')),'compatibleShare':float(compat),'compatible95Franchise':np.quantile(ratio(bs,'compatible','eligibleClock'),[.025,.975]).tolist(),'rawElapsedQuantiles':np.quantile([e['elapsedSeconds'] for e in events if e['eligible']],[0,.1,.25,.5,.75,.9,1]).tolist()};rows.extend(events);boots.append(ratio(bs,'compatible','eligibleClock'))
compatible=float(np.mean([x['compatibleShare'] for x in out.values()]));passed=compatible>=.95
result={'perSeason':out,'equalSeasonCompatibleShare':compatible,'equalSeasonCompatible95Franchise':np.quantile(np.mean(boots,0),[.025,.975]).tolist(),'registered95pctGuardPassed':passed,'candidateAllowed':passed,'note':'elapsed >=13sec is only a necessary plausibility check for fresh14 reset, not proof of rim contact or no intervening reset; all individual FG OREB anchors, no outcome-based exclusion from denominator. No new simulation or rate fitting before this gate.'}
(R/'timing-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');(R/'clock-events.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))

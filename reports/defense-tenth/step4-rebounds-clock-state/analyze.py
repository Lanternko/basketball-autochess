import json,pathlib,collections,hashlib,datetime
import numpy as np
R=pathlib.Path(__file__).parent
load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'))
p=load(R/'protocol.json');data=load(R/'states.json');seasons=list(data);allstats={};byfr={};validation=[]
for s,v in data.items():
 rows=[r for g in v['games'] for r in g['rows']];first=[r for r in rows if r['first']]
 exact=lambda r:r['before']['derived'] and abs(r['before']['hi']-r['before']['lo'])<1e-8 and 0<=r['before']['lo']<=24
 stats={'games':len(v['games']),'anchors':len(rows),'firstAnchors':len(first),'contactAll':dict(collections.Counter(r['contact']['classification'] for r in rows)),'contactFirst':dict(collections.Counter(r['contact']['classification'] for r in first)),'exactPreClock':sum(exact(r) for r in rows),'exactPreClockFirst':sum(exact(r) for r in first),'signedExpiredUpperBounds':sum(r['before']['derived'] and r['before']['hi']<0 for r in rows),'preClockReasons':dict(collections.Counter(r['before']['reason'] for r in rows)),'issues':dict(collections.Counter(i['reason'] for g in v['games'] for i in g['issues'])),'failures':v['failures']}
 byfr[s]={}
 for g in v['games']:
  for r in g['rows']:
   fid=str(g['ids'][r['off']]);t=byfr[s].setdefault(fid,np.zeros(5));t+=np.array([1,exact(r),r['contact']['classification']=='unknown',r['first'],exact(r) and r['first']])
   z=r['validation'];dt=z.get('firstSeconds')
   if z['lossCategory']=='clock' and z['firstKind']=='loss' and dt is not None:
    lo,hi=r['before']['lo'],r['before']['hi'];valid=exact(r) and not z.get('interveningAmbiguity',True) and r['seconds']>14
    validation.append({'season':s,'game':g['id'],'franchise':fid,'anchor':r['anchorAction'],'loss':z['lossAction'],'elapsed':dt,'preLo':lo,'preHi':hi,'preReason':r['before']['reason'],'contact':r['contact']['classification'],'eligibleExactNoIntervening':valid,'resetDeadlineAbsError':abs(dt-14),'retainDeadlineMinAbsError':max(lo-dt,dt-hi,0),'retainDeadlineMaxAbsError':max(abs(dt-lo),abs(dt-hi))})
 allstats[s]=stats
ids=sorted(set(k for s in byfr.values() for k in s));a=np.array([[byfr[s].get(k,np.zeros(5)) for k in ids] for s in seasons]);rng=np.random.default_rng(p['bootstrapSeed']);draw=rng.integers(0,len(ids),(p['bootstrapDraws'],len(ids)));agg=a[:,draw,:].sum(axis=2);boots=(agg[:,:,1]/agg[:,:,0]).mean(axis=0);bootsFirst=(agg[:,:,4]/agg[:,:,3]).mean(axis=0)
sel=[r for r in validation if r['eligibleExactNoIntervening']];vv={}
for s in seasons+['pooled']:
 rows=[r for r in sel if s=='pooled' or r['season']==s]
 vv[s]={'n':len(rows),'retainWithin1s':sum(r['retainDeadlineMinAbsError']<=1 for r in rows),'reset14Within1s':sum(r['resetDeadlineAbsError']<=1 for r in rows),'meanRetainDeadlineAbsError':float(np.mean([r['retainDeadlineMinAbsError'] for r in rows])) if rows else None,'meanReset14DeadlineAbsError':float(np.mean([r['resetDeadlineAbsError'] for r in rows])) if rows else None}
out={'label':'all four seasons seen/in-sample; observation only; signed negative bounds retained as invalid/expired evidence, not legal clock states','perSeason':allstats,'equalSeasonExactPreClockRate':float(np.mean([x['exactPreClock']/x['anchors'] for x in allstats.values()])),'exactPreClock95':np.quantile(boots,[.025,.975]).tolist(),'equalSeasonFirstExactRate':float(np.mean([x['exactPreClockFirst']/x['firstAnchors'] for x in allstats.values()])),'firstExact95':np.quantile(bootsFirst,[.025,.975]).tolist(),'clockEndpoints':len(validation),'exactEndpointValidation':vv,'validationCaveat':'Outcome-selected endpoint compatibility is not shot-clock MAE, rim classification, fresh14 hazard or unconditional event rate. Exact preclock means exact under registered event-start assumptions, not observed shot-clock truth.'}
(R/'analysis.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8');(R/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8')
protected=load(R/'protected-before.json');protected.update(load(R.parent/'step4-rebounds-turnover-time/protected-before.json'));bad=[f for f,h in protected.items() if not pathlib.Path(f).exists() or hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h];assert not bad;sha=hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest();assert sha==(R/'protocol.sha256').read_text().strip();(R/'audit.json').write_text(json.dumps({'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocolSHA':sha,'protectedFiles':len(protected),'changed':bad,'simulationRun':False,'engineChanged':False,'tests':load(R/'tests.json')},indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='perSeason'},indent=2))

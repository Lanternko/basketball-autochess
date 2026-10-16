import json,pathlib,numpy as np,hashlib,datetime
r=pathlib.Path('reports/defense-tenth/step4-rebounds-after');p=json.loads((r/'protocol.json').read_text(encoding='utf-8'));real=json.loads((r/'real.json').read_text(encoding='utf-8'));rng=np.random.default_rng(20261015)
def load(f):return json.loads(pathlib.Path(f).read_text(encoding='utf-8'))
def tally(rows):
 n=len(rows);shots=[x for x in rows if x['category'] in ['immediateProxy','otherShot']];times=[x['seconds'] for x in rows if x.get('seconds') is not None];return {'n':n,**{k:sum(x['category']==k for x in rows) for k in ['immediateProxy','otherShot','earlyLoss','laterLoss','foul','ft','periodEnd','unknown']},'official':sum(x.get('official',False) for x in shots),'sameShooter':sum(x.get('same',False) for x in shots),'shortShot':sum(x.get('zone')=='short' for x in shots),'longShot':sum(x.get('zone')=='long' for x in shots),'made':sum(x.get('made',False) for x in shots),'points':sum(x.get('points',0) for x in shots),'shots':len(shots),'timeSum':sum(times),'timeN':len(times),'interrupted':sum(x.get('interrupted',False) for x in rows)}
def merge(ts):return {k:sum(x[k] for x in ts) for k in ts[0]}
def metrics(t):return {**{k:100*t[k]/t['n'] for k in ['immediateProxy','otherShot','earlyLoss','laterLoss','foul','ft','periodEnd','unknown','official','interrupted']},'meanSeconds':t['timeSum']/t['timeN'],'shortShotPct':100*t['shortShot']/t['shots'],'longShotPct':100*t['longShot']/t['shots'],'fgPct':100*t['made']/t['shots'],'sameShooterPct':100*t['sameShooter']/t['shots'],'firstFgPointsPerOreb':t['points']/t['n']}
out={};influences={}; seedValues={}
for s in p['seasons']:
 ids=[g['id'] for g in real[s]['games']];rt=[tally(g['rows']) for g in real[s]['games']];seeds=[];simTs=[]
 for seed in p['seeds']:
  d=load(r/f'runs/{s}-allocation-{seed}.json');assert len(d['postOreb']['games'])==len(d['matches']);byid={m['id']:tally(rows) for m,rows in zip(d['matches'],d['postOreb']['games'])};ts=[byid[i] for i in ids];simTs.append(ts);seeds.append(metrics(merge(ts)))
 rm=metrics(merge(rt));sm={k:float(np.mean([z[k] for z in seeds])) for k in rm};out[s]={'games':len(ids),'missing':real[s]['missing'],'failures':real[s]['failures'],'excluded':real[s]['excluded'],'realCounts':merge(rt),'simulationCountsBySeed':[merge(ts) for ts in simTs],'real':rm,'simulation':sm,'simulationBySeed':seeds}
 influences[s]={};seedValues[s]={}
 for k in ['immediateProxy','otherShot','earlyLoss','laterLoss','foul']:
  rr=rm[k]/100;rc=np.array([x['n'] for x in rt]);ri=(np.array([x[k] for x in rt])-rr*rc)/np.mean(rc)*100
  si=[]
  for ts,z in zip(simTs,seeds):
   sc=np.array([x['n'] for x in ts]);si.append((np.array([x[k] for x in ts])-z[k]/100*sc)/np.mean(sc)*100)
  diff=np.mean(si,axis=0)-ri;influences[s][k]=float(np.var(diff,ddof=1)/len(diff));seedValues[s][k]=float(np.var([z[k] for z in seeds],ddof=1)/len(seeds))
keys=list(next(iter(out.values()))['real']);pooled={side:{k:float(np.mean([out[s][side][k] for s in p['seasons']])) for k in keys} for side in ['real','simulation']};intervals={}
for k in influences[p['seasons'][0]]:
 delta=pooled['simulation'][k]-pooled['real'][k];se=np.sqrt(sum(influences[s][k]+seedValues[s][k] for s in p['seasons'])/16);draw=rng.normal(delta,se,20000);intervals[k]={'deltaPp':delta,'approximate95':np.quantile(draw,[.025,.975]).tolist(),'method':'paired game ratio influence normal approximation + seed sampling; diagnostic only, not franchise joint adoption interval'}
summary={'seasons':out,'equalSeasonMeans':pooled,'descriptiveIntervals':intervals};(r/'analysis.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
protected=load(r/'protected-before.json');issues=[f for f,h in protected.items() if not pathlib.Path(f).exists() or hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h];(r/'completion-audit.json').write_text(json.dumps({'protectedFiles':len(protected),'issues':issues,'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2));assert not issues
print(json.dumps({'pooled':pooled,'intervals':intervals,'auditIssues':len(issues)},ensure_ascii=True,indent=2))

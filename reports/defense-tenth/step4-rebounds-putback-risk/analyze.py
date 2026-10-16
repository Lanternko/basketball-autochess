import json,pathlib,numpy as np,hashlib,datetime
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');real=load(R/'real.json');truth=load(R.parent/'step4-rebounds-turnover-time/seed-arrays.json');targets={c['season']:c['target'] for c in load(R.parent/'step4-rebounds-turnover-time/analysis.json')['cells']};ids=truth[p['seasons'][0]]['ids'];B=p['bootstrapDraws'];rng=np.random.default_rng(p['bootstrapSeed']);draw=rng.integers(0,30,(B,30));weights=np.stack([(draw==i).sum(axis=1) for i in range(30)],axis=1);sd=rng.integers(0,3,(B,3))
fields=['n','pts','ft','q','w','earlyLoss','lateLoss','earlyFg','earlyFt','earlyNonShootingFoul','loss','fgN','fgMade','qN','qMade','otherFgN','otherFgMade']+[f'{mode}_{k}' for mode in ['putback','restart','unknown'] for k in ['n','loss','q','earlyLoss','w']]
ix={k:i for i,k in enumerate(fields)}
def tally(games):
 a=np.zeros((30,len(fields)))
 for g in games:
  for r in g['rows']:
   if not r['first']:continue
   i=ids.index(g['ids'][r['off']]);w=r['windowEligible'];q=r['quickProxy'];fg=r['firstFgZone'] is not None;loss=r['firstKind']=='loss';mode=r['intent'] or 'unknown'
   vals={'n':1,'pts':r['points'],'ft':r['ftPoints'],'q':q,'w':w,'earlyLoss':w and r['earlyLoss'],'lateLoss':w and r['lateLoss'],'earlyFg':w and r['earlyFg'],'earlyFt':w and r['earlyFt'],'earlyNonShootingFoul':w and r['earlyNonShootingFoul'],'loss':loss,'fgN':fg,'fgMade':fg and r['firstFgMade'],'qN':q,'qMade':q and r['firstFgMade'],'otherFgN':fg and not q,'otherFgMade':fg and not q and r['firstFgMade'],f'{mode}_n':1,f'{mode}_loss':loss,f'{mode}_q':q,f'{mode}_earlyLoss':w and r['earlyLoss'],f'{mode}_w':w}
   for k,v in vals.items():a[i,ix[k]]+=v
 return a
def metrics(c):
 def ratio(n,d):return np.divide(c[...,ix[n]],c[...,ix[d]],out=np.zeros_like(c[...,ix[n]]),where=c[...,ix[d]]>0)
 o={k:ratio(n,de) for k,n,de in [('points','pts','n'),('ftPoints','ft','n'),('quickProxy','q','n'),('earlyLoss','earlyLoss','w'),('lateLoss','lateLoss','w'),('earlyFg','earlyFg','w'),('earlyFt','earlyFt','w'),('earlyNonShootingFoul','earlyNonShootingFoul','w'),('lossBeforeAttempt','loss','n'),('firstFgMake','fgMade','fgN'),('quickFgMake','qMade','qN'),('otherFgMake','otherFgMade','otherFgN')]}
 for mode in ['putback','restart','unknown']:
  o[mode+'Share']=ratio(mode+'_n','n');o[mode+'LossRate']=ratio(mode+'_loss',mode+'_n');o[mode+'EarlyLossRate']=ratio(mode+'_earlyLoss',mode+'_w');o[mode+'QuickConversion']=ratio(mode+'_q',mode+'_n')
 return o
result={};boots={v:[] for v in ['baseline-real','ablation-baseline','ablation-real']};score_arrays={};global_stats={}
for season in p['seasons']:
 rc=tally(real[season]['games']);rm=metrics(rc.sum(axis=0));rboot=metrics(weights@rc);versions={};vc={};simMetrics={};byids={};global_stats[season]={};allowed={g['id'] for g in real[season]['games']}
 for version in ['baseline','ablation']:
  cs=[];nets=[];wins=[];stats=[]
  for seed in p['seeds']:
   run=load(R/f'runs/{season}-{version}-{seed}.json');assert run['options']['skipGenericPutbackTouchRisk']==(version=='ablation')
   gs=[{'ids':[g['homeId'],g['awayId']],'rows':rows} for g,rows in zip(run['matches'],run['fullOreb']['games']) if g['id'] in allowed];cs.append(tally(gs));by={t['id']:t for t in run['teams']};nets.append([(by[i]['stats']['pts']-by[i]['opponent']['pts'])/by[i]['games'] for i in ids]);wins.append([by[i]['wins'] for i in ids]);tot={k:sum(t['stats'][k] for t in run['teams']) for k in ['pts','fga','fgm','fg3a','fg3m','fta','ftm','oreb','tov']};ng=sum(t['games'] for t in run['teams']);poss=tot['fga']-tot['oreb']+tot['tov']+.44*tot['fta'];stats.append({'efficiency':100*tot['pts']/poss,'possessions':poss/ng,'tov':tot['tov']/ng,'fg':100*tot['fgm']/tot['fga'],'three':100*tot['fg3m']/tot['fg3a'],'fta':tot['fta']/ng})
  cs=np.array(cs);vc[version]=cs;vm=metrics(cs.sum(axis=1));simMetrics[version]=vm;versions[version]={k:float(v.mean()) for k,v in vm.items()};versions[version]['counts']={k:float(cs[:,:,ix[k]].sum(axis=1).mean()) for k in ['n','w']};score_arrays.setdefault(season,{})[version]={'net':np.array(nets),'wins':np.array(wins)};global_stats[season][version]={k:float(np.mean([x[k] for x in stats])) for k in stats[0]}
  global_stats[season][version]['efficiencyBias']=global_stats[season][version]['efficiency']-targets[season]['offensiveRatingProxy'];global_stats[season][version]['possessionBias']=global_stats[season][version]['possessions']-targets[season]['possessionsProxy'];global_stats[season][version]['tovBias']=global_stats[season][version]['tov']-targets[season]['turnovers']
  # Same franchise draw and seed draw in both arms and all seasons.
  bs=np.stack([weights@c for c in cs],axis=1);bs=bs[np.arange(B)[:,None],sd];byids[version]={k:v.mean(axis=1) for k,v in metrics(bs).items()}
 result[season]={'games':len(real[season]['games']),'real':{k:float(v) for k,v in rm.items()},**versions}
 for comp,left,right in [('baseline-real','baseline','real'),('ablation-baseline','ablation','baseline'),('ablation-real','ablation','real')]:
  l=byids[left];rr=rboot if right=='real' else byids[right];boots[comp].append({k:l[k]-rr[k] for k in l})
pool={side:{k:float(np.mean([result[s][side][k] for s in p['seasons']])) for k in result[p['seasons'][0]]['real']} for side in ['real','baseline','ablation']};intervals={}
for comp,left,right in [('baseline-real','baseline','real'),('ablation-baseline','ablation','baseline'),('ablation-real','ablation','real')]:
 intervals[comp]={k:{'delta':pool[left][k]-pool[right][k],'joint95':np.quantile(np.mean([b[k] for b in boots[comp]],axis=0),[.025,.975]).tolist()} for k in pool[left]}
accuracy={}
for version in ['baseline','ablation']:
 ne=np.concatenate([score_arrays[s][version]['net'].mean(axis=0)-np.array(truth[s]['truth']['net']) for s in p['seasons']]);we=np.concatenate([score_arrays[s][version]['wins'].mean(axis=0)-np.array(truth[s]['truth']['wins']) for s in p['seasons']]);accuracy[version]={'netRMSE':float(np.sqrt(np.mean(ne**2))),'winsMAE':float(np.mean(abs(we))),'winsRMSE':float(np.sqrt(np.mean(we**2))),'note':'3seed descriptive only; not promotion evidence'}
latent=[k for k in pool['real'] if any(k.startswith(m) for m in ['putback','restart','unknown'])]
for k in latent:
 pool['real'][k]=None
 for season in result:result[season]['real'][k]=None
 for comp in ['baseline-real','ablation-real']:intervals[comp][k]={'status':'not identifiable: real intention unobserved'}
out={'seasons':result,'pooled':pool,'intervals':intervals,'leagueStats':global_stats,'descriptiveAccuracy':accuracy,'limitations':['real latent intention is not observed; do not compare simulation mode-specific loss rates to outcome-selected real FG groups','ablation removes generic risk only as sensitivity experiment; zero real risk is not estimated','early risk denominators exclude all <3sec period-remaining anchors','three seeds and all seasons seen-data; no baseline adoption or new production parameters']}
(R/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
protected=load(R/'protected-before.json');protected.update(load(R.parent/'step4-rebounds-turnover-time/protected-before.json'));issues=[f for f,h in protected.items() if not pathlib.Path(f).exists() or hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h];assert not issues
assert hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest()==(R/'protocol.sha256').read_text().strip()
(R/'audit.json').write_text(json.dumps({'protectedFiles':len(protected),'issues':issues,'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocolSHA':(R/'protocol.sha256').read_text().strip()},indent=2)+'\n',encoding='utf8');print(json.dumps({'pooled':pool,'accuracy':accuracy},indent=2))

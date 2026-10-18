import json,pathlib,numpy as np,sys
version=sys.argv[1] if len(sys.argv)>1 else 'baseline'
R=pathlib.Path(__file__).parent
load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'))
p=load(R/'protocol.json'); truth=load(R.parent/'step4-rebounds-turnover-time/seed-arrays.json');ids=truth[p['seasons'][0]]['ids'];B=p['bootstrapDraws'];rng=np.random.default_rng(p['bootstrapSeed']);draw=rng.integers(0,30,(B,30));w=np.stack([(draw==i).sum(1) for i in range(30)],axis=1);sd=rng.integers(0,len(p['seeds']),(B,len(p['seeds'])))
keys=['n','nonshoot','shooting','fg','ft','loss','offensiveOrOtherFoul','periodEnd','anyNonshoot','earlyNonshoot','foulWithin3','foulWithin6','foulSeconds']
ix={k:i for i,k in enumerate(keys)}
def tally(gs,first):
 a=np.zeros((30,len(keys)))
 for g in gs:
  for r in g['rows']:
   if (first and not r['first']) or not r['windowEligible']:continue
   i=ids.index(g['ids'][r['off']]);dt=r['firstNonshootSeconds'];d={'n':1,r['boundary']:1,'anyNonshoot':r['nonshootBeforeAttempt'],'earlyNonshoot':r['earlyNonShootingFoul'],'foulWithin3':dt is not None and 0<=dt<=3,'foulWithin6':dt is not None and 0<=dt<=6,'foulSeconds':dt or 0}
   for k,v in d.items():a[i,ix[k]]+=v
 return a
def met(a):
 def ratio(k,d='n'):return np.divide(a[...,ix[k]],a[...,ix[d]],out=np.zeros_like(a[...,ix[k]]),where=a[...,ix[d]]>0)
 return {**{k:ratio(k) for k in ['nonshoot','shooting','fg','ft','loss','offensiveOrOtherFoul','periodEnd','anyNonshoot','earlyNonshoot']},'within3GivenFoul':ratio('foulWithin3','anyNonshoot'),'within6GivenFoul':ratio('foulWithin6','anyNonshoot'),'meanFoulSeconds':ratio('foulSeconds','anyNonshoot')}
real=load(R/'real.json');out={'allAnchors':{},'firstAnchors':{}};pooled={}
for first,name in [(False,'allAnchors'),(True,'firstAnchors')]:
 diffs=[];rm=[];sm=[]
 for season in p['seasons']:
  rc=tally(real[season]['games'],first);rs=met(rc.sum(0));rb=met(w@rc);allowed={g['id'] for g in real[season]['games']};cs=[];oldRates=[]
  for seed in p['seeds']:
   run=load(R/f'runs/{season}-{version}-{seed}.json');gs=[{'ids':[g['homeId'],g['awayId']],'rows':rows} for g,rows in zip(run['matches'],run['fullOreb']['games']) if g['id'] in allowed];cs.append(tally(gs,first));oldRates.append(run['options'].get('nonShootingFoulRate',0.04))
  cs=np.array(cs);ss={k:float(v.mean()) for k,v in met(cs.sum(1)).items()};bs=np.stack([w@c for c in cs],axis=1);bs=bs[np.arange(B)[:,None],sd];sb={k:v.mean(1) for k,v in met(bs).items()};diffs.append({k:sb[k]-rb[k] for k in rb});rm.append(rs);sm.append(ss)
  out[name][season]={'real':{k:float(v) for k,v in rs.items()},'baseline':ss,'realN':int(rc[:,ix['n']].sum()),'baselineN':float(cs[:,:,ix['n']].sum(1).mean()),'oldGateProbability':float(np.mean(oldRates))}
 pooled[name]={'real':{k:float(np.mean([m[k] for m in rm])) for k in rm[0]},'baseline':{k:float(np.mean([m[k] for m in sm])) for k in sm[0]}}
 pooled[name]['baselineMinusReal']={k:{'delta':pooled[name]['baseline'][k]-pooled[name]['real'][k],'joint95':np.quantile(np.mean([d[k] for d in diffs],axis=0),[.025,.975]).tolist()} for k in rm[0]}
ci=pooled['allAnchors']['baselineMinusReal']['nonshoot']['joint95'];condition=ci[0]>0
out.update({'simulationVersion':version} if version!='baseline' else {});out['pooled']=pooled;out['registeredExperimentConditionMet']=condition
out['interpretation']='first-event classifier is a discrete competing-event approximation; no inferred real putback intent or continuous hazard'
(R/('first-boundary-analysis.json' if version=='baseline' else 'first-boundary-analysis-'+version+'.json')).write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps({'condition':condition,'pooled':pooled},indent=2))


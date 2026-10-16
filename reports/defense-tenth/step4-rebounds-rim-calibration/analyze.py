import json,hashlib,sys,datetime
from pathlib import Path
import numpy as np
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
save=lambda n,x:(r/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=read(r/'protocol.json');assert hashlib.sha256((r/'protocol.json').read_bytes()).hexdigest()==(r/'protocol.sha256').read_text().strip()
real=read(r/'real.json')['results']
keys=['misses','immediateClock','fgOreb','postOrebClock','clock','natural']
def total(rows):return {k:sum(t.get(k,0) for t in rows) for k in keys}
def rate(z,n,d):return z[n]/z[d] if z[d] else 0
def subset(a,half):return [x for x in a if x['half']==half]
def simrows(s,mode,seed):
 x=read(r/f'runs/{s}-{mode}-{seed}.json');schedule=read(f'reports/defense-tenth/step4-t0/{s}/bundle.json')['league']['schedule'];idx={g['id']:i for i,g in enumerate(schedule)}
 return [dict(id=m['id'],half='train' if idx[m['id']]<len(schedule)/2 else 'test',**row) for m,row in zip(x['matches'],x['eventCounts'])]
train=total([x for s in p['seasons'] for x in subset(real[s],'train')]);target=rate(train,'immediateClock','misses')
def interpolate(grid):
 for a,b in zip(grid,grid[1:]):
  if a['rate']<=target<=b['rate']:
   return a['p']+(b['p']-a['p'])*(target-a['rate'])/(b['rate']-a['rate'])
 return min(grid,key=lambda x:abs(x['rate']-target))['p']
grid=[];seedGrids={seed:[] for seed in p['seeds']}
for prob in p['grid']:
 rows=[]
 for seed in p['seeds']:
  a=[x for s in p['seasons'] for x in subset(simrows(s,str(prob),seed),'train')]
  z=total(a);seedGrids[seed].append({'p':prob,'rate':rate(z,'immediateClock','misses')});rows+=a
 z=total(rows);grid.append({'p':prob,'rate':rate(z,'immediateClock','misses'),'counts':z})
selected=interpolate(grid)
if '--select' in sys.argv:
 # p=0 must reproduce adopted baseline on every sampled game.
 parity=[]
 for s in p['seasons']:
  for seed in p['seeds']:
   a=read(r/f'runs/{s}-0-{seed}.json');b=read(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{s}-split-{seed}.json');lookup={m['id']:m for m in b['matches']}
   assert all(m==lookup[m['id']] for m in a['matches']);parity.append({'season':s,'seed':seed,'games':len(a['matches']),'passed':True})
 save('selection.json',{'selectedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pEffective':selected,'physicalNoRimIdentified':False,'targetTrainRate':target,'grid':grid,'seedwiseFits':[interpolate(v) for v in seedGrids.values()],'parity':parity})
 print(json.dumps({'pEffective':selected,'target':target,'grid':[(x['p'],x['rate']) for x in grid]}));sys.exit()
selection=read(r/'selection.json');assert selection['pEffective']==selected
rng=np.random.default_rng(p['bootstrapSeed'])
def interval(rows,n,d):
 a=np.array([[x.get(n,0),x.get(d,0)] for x in rows],float);out=[]
 for _ in range(p['bootstrap']):
  z=a[rng.integers(len(a),size=len(a))].sum(axis=0);out.append(z[0]/z[1] if z[1] else 0)
 return np.quantile(out,[.025,.975]).tolist()
results=[]
for s in p['seasons']+['pooled']:
 seasons=p['seasons'] if s=='pooled' else [s]
 for half in ['train','test']:
  truth=[x for season in seasons for x in subset(real[season],half)]
  available={x['id'] for x in truth}
  simulated=[x for season in seasons for seed in p['seeds'] for x in subset(simrows(season,'selected',seed),half) if x['id'] in available]
  z=total(truth);v=total(simulated)
  row={'season':s,'half':half,'realGames':len(truth),'simGames':len(simulated),'real':z,'sim':v}
  for metric,n,d in [('immediateRate','immediateClock','misses'),('postOrebRate','postOrebClock','fgOreb')]:
   ci=interval(truth,n,d);rr=rate(z,n,d);sr=rate(v,n,d)
   row[metric]={'real':rr,'sim':sr,'realGameBootstrap95':ci,'pass':bool(ci[0]<=sr<=ci[1])}
  row['clockPerTeamGame']={'real':z['clock']/(2*len(truth)),'sim':v['clock']/(2*len(simulated))}
  results.append(row)
# Full-season league metrics use the same pooled count definition as the previous baseline.
old=read('reports/defense-tenth/step4-rebounds-turnover-time/analysis.json')['cells']
league=[]
def metrics(z,g):
 poss=z['fga']-z['oreb']+z['tov']+.44*z['fta']
 return {'eff':100*z['pts']/poss,'tov':z['tov']/g,'fg':100*z['fgm']/z['fga'],'three':100*z['fg3m']/z['fg3a'],'oreb':z['oreb']/g,'ppg':z['pts']/g,'poss':poss/g}
for s in p['seasons']:
 base=next(x for x in old if x['season']==s and x['version']=='split')
 out=[]
 for seed in p['seeds']:
  x=read(r/f'runs/{s}-selected-{seed}.json');z={k:sum(t['stats'][k] for t in x['teams']) for k in x['teams'][0]['stats']}
  out.append(metrics(z,2*len(x['matches'])))
 avg={k:float(np.mean([a[k] for a in out])) for k in out[0]};t=base['target'];b=base['global']
 baseline=[]
 for seed in p['seeds']:
  x=read(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{s}-split-{seed}.json');z={k:sum(v['stats'][k] for v in x['teams']) for k in x['teams'][0]['stats']};baseline.append(metrics(z,2*len(x['matches'])))
 baseline={k:float(np.mean([a[k] for a in baseline])) for k in baseline[0]}

 gates={'efficiency':abs(avg['eff']-t['offensiveRatingProxy'])<=.5,'turnovers':abs(avg['tov']-t['turnovers'])<=.2,'fg':abs(avg['fg']-t['fg'])<=abs(baseline['fg']-t['fg'])+.1,'three':abs(avg['three']-t['three'])<=abs(baseline['three']-t['three'])+.1}
 league.append({'season':s,'candidate':avg,'baselineSameSeeds':baseline,'baseline20seed':{k:b[v] for k,v in {'eff':'offensiveRatingProxy','tov':'turnovers','fg':'fg','three':'three','oreb':'oreb'}.items() if v in b},'target':{'eff':t['offensiveRatingProxy'],'tov':t['turnovers'],'fg':t['fg'],'three':t['three']},'gates':gates})
hold=next(x for x in results if x['season']=='pooled' and x['half']=='test')
clockPass=abs(hold['clockPerTeamGame']['sim']-hold['clockPerTeamGame']['real'])<=.1
passed=hold['immediateRate']['pass'] and hold['postOrebRate']['pass'] and clockPass and all(all(x['gates'].values()) for x in league)
save('analysis.json',{'selection':selection,'eventResults':results,'league':league,'pooledHoldoutClockPass':clockPass,'allGatesPass':bool(passed),'adopted':False,'note':'Three diagnostic seeds; no franchise+seed accuracy claims. More seeds only if event and league gates pass.'})
print(json.dumps({'allGatesPass':bool(passed),'holdout':hold,'league':league}))

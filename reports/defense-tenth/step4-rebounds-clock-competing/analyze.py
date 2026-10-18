import json,hashlib,sys
from pathlib import Path
import numpy as np
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
save=lambda n,x:(r/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=read(r/'protocol.json');assert hashlib.sha256((r/'protocol.json').read_bytes()).hexdigest()==(r/'protocol.sha256').read_text().strip()
real=read('reports/defense-tenth/step4-rebounds-rim-calibration/real.json')['results']
keys=['misses','immediateClock','fgOreb','postOrebClock','clock','natural']
seasons=p['seasons'];seeds=p['diagnosticSeeds'];modes=['baseline','fresh','post','combined']
cache={};parity=[];schedule={}
for s in seasons:
 sc=read(f'reports/defense-tenth/step4-t0/{s}/bundle.json')['league']['schedule'];schedule[s]={x['id']:i for i,x in enumerate(sc)}
 for mode in modes:
  for seed in seeds:
   x=read(r/f'runs/{s}-{mode}-{seed}.json');cache[s,mode,seed]=x
   if mode=='baseline':
    b=read(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{s}-split-{seed}.json');assert b['matches']==x['matches'];assert b['teams']==x['teams'];parity.append({'season':s,'seed':seed,'games':len(x['matches']),'scoreAndPlayersIdentical':True})
# Bootstrap independent real games and paired simulated seeds/games within each season.
# Event adaptation diagnostics; not a claim of team prediction improvement.
rng=np.random.default_rng(p['bootstrapSeed']);boot=p['eventBootstrap'];rows=[]
for mode in modes:
 for half in ['train','test']:
  realArrays=[];simArrays=[];z=np.zeros(6);v=np.zeros(6);ng=0;sn=0
  for s in seasons:
   truth=[t for t in real[s] if t['half']==half];ids=[t['id'] for t in truth];a=np.array([[t[k] for k in keys] for t in truth],float)
   b=[]
   for seed in seeds:
    x=cache[s,mode,seed];look={m['id']:row for m,row in zip(x['matches'],x['eventCounts'])};b.append([[look[i][k] for k in keys] for i in ids])
   b=np.array(b,float);realArrays.append(a);simArrays.append(b);z+=a.sum(axis=0);v+=b.mean(axis=0).sum(axis=0);ng+=len(a);sn+=len(a)*len(seeds)
  estimates=[]
  for _ in range(boot):
   aa=np.zeros(6);bb=np.zeros(6)
   # Same seed index resampling across all seasons; independently resample games per season.
   ss=rng.integers(len(seeds),size=len(seeds))
   for a,b in zip(realArrays,simArrays):
    ai=rng.integers(len(a),size=len(a));bi=rng.integers(len(a),size=len(a));aa+=a[ai].sum(axis=0);bb+=b[ss][:,bi].mean(axis=0).sum(axis=0)
   estimates.append([bb[1]/bb[0]-aa[1]/aa[0],bb[3]/bb[2]-aa[3]/aa[2]])
  ci=np.quantile(estimates,[.025,.975],axis=0)
  rate=lambda x,n,d:float(x[n]/x[d])
  a={'mode':mode,'half':half,'realGames':ng,'simGames':sn,'real':dict(zip(keys,z.tolist())),'simPerSeedMean':dict(zip(keys,v.tolist()))}
  gates=[]
  for j,(name,n,d) in enumerate([('immediateRate',1,0),('postOrebRate',3,2)]):
   lo,hi=ci[:,j];a[name]={'real':rate(z,n,d),'sim':rate(v,n,d),'difference':rate(v,n,d)-rate(z,n,d),'difference95':[float(lo),float(hi)],'pass':bool(lo<=0<=hi)};gates.append(lo<=0<=hi)
  a['clockPerTeamGame']={'real':float(z[4]/(2*ng)),'sim':float(v[4]/(2*ng))};a['clockPass']=bool(abs(v[4]-z[4])/(2*ng)<=.1);a['eventGatesPass']=bool(all(gates) and a['clockPass'])
  a['clockPathsPerTeamGame']={'real':{'immediate':float(z[1]/(2*ng)),'postOreb':float(z[3]/(2*ng)),'other':float((z[4]-z[1]-z[3])/(2*ng))},'sim':{'immediate':float(v[1]/(2*ng)),'postOreb':float(v[3]/(2*ng)),'other':float((v[4]-v[1]-v[3])/(2*ng))}}
  rows.append(a)
old=read('reports/defense-tenth/step4-rebounds-turnover-time/analysis.json')['cells'];league=[]
def metrics(x):
 z={k:sum(t['stats'][k] for t in x['teams']) for k in x['teams'][0]['stats']};g=2*len(x['matches']);poss=z['fga']-z['oreb']+z['tov']+.44*z['fta']
 return {'eff':100*z['pts']/poss,'tov':z['tov']/g,'fg':100*z['fgm']/z['fga'],'three':100*z['fg3m']/z['fg3a'],'oreb':z['oreb']/g,'dreb':z['dreb']/g,'ppg':z['pts']/g,'poss':poss/g,'clock':z['clockTov']/g,'nonClockTov':(z['tov']-z['clockTov'])/g}
for s in seasons:
 target=next(x['target'] for x in old if x['season']==s and x['version']=='split')
 def avg(mode):
  aa=[metrics(cache[s,mode,seed]) for seed in seeds];return {k:float(np.mean([a[k] for a in aa])) for k in aa[0]}
 b=avg('baseline');c=avg('combined')
 raw=read(('data/season-source' if s=='2025-26' else f'data/defense-seventh/{s}')+'/team-games.json')['data']['resultSets'][0];logs=[dict(zip(raw['headers'],z)) for z in raw['rowSet']]
 truth={'oreb':float(np.mean([v['OREB'] for v in logs])),'dreb':float(np.mean([v['DREB'] for v in logs])),'eff':target['offensiveRatingProxy'],'tov':target['turnovers'],'fg':target['fg'],'three':target['three']}
 gates={'eff':abs(c['eff']-truth['eff'])<=.5}
 for k in ['tov','fg','three','oreb','dreb']:gates[k]=abs(c[k]-truth[k])<=abs(b[k]-truth[k])+.1
 league.append({'season':s,'baseline':b,'combined':c,'truth':truth,'gates':gates})
core=next(x for x in rows if x['mode']=='combined' and x['half']=='test')['eventGatesPass']
save('diagnostics.json',{'eventResults':rows,'league':league,'parity':parity,'eventGatesPass':core,'leagueGatesPass':bool(all(all(x['gates'].values()) for x in league))})
print(json.dumps({'eventGatesPass':core,'combinedHoldout':next(x for x in rows if x['mode']=='combined' and x['half']=='test'),'league':league}))

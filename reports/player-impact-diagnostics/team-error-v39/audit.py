"""Exact accounting of team scoring errors; no fitted model changes."""
import json,hashlib,math,csv
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
R=Path('reports/player-impact-diagnostics/team-error-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();R.mkdir(exist_ok=True)
SEASONS=['2022-23','2023-24','2024-25','2025-26'];SEEDS=[20261012,20261013,20261014];hashes={};sources={};rows=[];sourceAudit=[]
seedfile='reports/defense-tenth/step4-rebounds-turnover-time/seed-arrays.json';seedTruth=read(seedfile);hashes[seedfile]=sha(seedfile)
work=Path('reports/player-impact-v29/workload-game-rows.jsonl');hashes[work.as_posix()]=sha(work)
for line in work.open(encoding='utf-8'):
 r=json.loads(line);key=(r['season'],r['gameId']);assert sources.setdefault(key,r['source'])==r['source']
names={'pts':'points','fga':'fieldGoalsAttempted','fgm':'fieldGoalsMade','fg3a':'threePointersAttempted','fg3m':'threePointersMade','fta':'freeThrowsAttempted','ftm':'freeThrowsMade','oreb':'reboundsOffensive','dreb':'reboundsDefensive','ast':'assists','stl':'steals','blk':'blocks','tov':'turnovers','pf':'foulsPersonal'}
def stats(t):
 s=t['statistics'];o={k:s[v] for k,v in names.items()};assert o['pts']==2*o['fgm']+o['fg3m']+o['ftm'];return Counter(o)
def components(pred,actual):
 out={}
 for zone,a,m,points in [('two','fga','fgm',2),('three','fg3a','fg3m',3),('ft','fta','ftm',1)]:
  pa=pred[a]-(pred['fg3a'] if zone=='two' else 0);pm=pred[m]-(pred['fg3m'] if zone=='two' else 0);aa=actual[a]-(actual['fg3a'] if zone=='two' else 0);am=actual[m]-(actual['fg3m'] if zone=='two' else 0);pr=pm/pa;ar=am/aa
  out[zone+'Volume']=points*(pa-aa)*(pr+ar)/2/82;out[zone+'Accuracy']=points*(pr-ar)*(pa+aa)/2/82
 assert math.isclose(sum(out.values()),(pred['pts']-actual['pts'])/82,abs_tol=1e-10)
 return out
for season in SEASONS:
 bundle=Path(f'reports/defense-tenth/step4-t0/{season}/bundle.json');hashes[bundle.as_posix()]=sha(bundle);b=read(bundle);truth={t['id']:{'own':Counter(),'opp':Counter(),'wins':0,'games':0} for t in b['league']['teams']};schedule={g['id']:g for g in b['league']['schedule']}
 for (s,gid),file in sources.items():
  if s!=season:continue
  raw=read(file);hashes[file]=sha(file);d=raw.get('data',raw);game=d.get('game',d.get('boxScoreTraditional'));fixture=schedule[gid];teams=[game['homeTeam'],game['awayTeam']];ts=[stats(t) for t in teams]
  assert {t['teamId'] for t in teams}=={fixture['homeId'],fixture['awayId']},(season,gid)
  byId={t['teamId']:v for t,v in zip(teams,ts)};assert byId[fixture['homeId']]['pts']==fixture['observed']['homeScore'] and byId[fixture['awayId']]['pts']==fixture['observed']['awayScore'],(season,gid)
  for i,t in enumerate(teams):
   q=truth[t['teamId']];q['own'].update(ts[i]);q['opp'].update(ts[1-i]);q['games']+=1;q['wins']+=int(ts[i]['pts']>ts[1-i]['pts'])
 assert all(t['games']==82 for t in truth.values());disagreements=[]
 for t in b['league']['teams']:
  q=truth[t['id']];j=seedTruth[season]['ids'].index(t['id']);target=seedTruth[season]['truth'];assert q['wins']==target['wins'][j];assert math.isclose(q['own']['pts']/82,target['off'][j],abs_tol=1e-10);assert math.isclose(q['opp']['pts']/82,target['allowed'][j],abs_tol=1e-10)
  if 'observed' not in t:continue
  for k in ['fgm','fga','fg3m','fg3a','fta','ftm','ast','tov']:
   if q['own'][k]!=t['observed'][k.upper()]:disagreements.append({'teamId':t['id'],'metric':k,'boxTotal':q['own'][k],'seasonAggregate':t['observed'][k.upper()]})
 sourceAudit.append({'season':season,'games':1230,'seasonVsBoxDisagreements':disagreements})
 for version in ['control','v39']:
  predicted=defaultdict(lambda:{'own':Counter(),'opp':Counter(),'wins':0.,'shotNoise':0.})
  for seed in SEEDS:
   file=f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{season}-split-{seed}.json' if version=='control' else f'reports/player-impact-v39/runs/{season}-rotation-space-full-{seed}.json';hashes[file]=sha(file);run=read(file)
   for t in run['teams']:
    q=predicted[t['id']]
    for group,key in [('own','stats'),('opp','opponent')]:
     for k,v in t[key].items():
      if isinstance(v,(int,float)):q[group][k]+=v/3
    q['wins']+=t['wins']/3
  for t in b['league']['teams']:
   tid=t['id'];q=predicted[tid];a=truth[tid];parts={};details={}
   for group,sign in [('own',1),('opp',-1)]:
    cs=components(q[group],a[group]);parts.update({group+'_'+k:sign*v for k,v in cs.items()});details[group]={'actual':dict(a[group]),'predicted':dict(q[group])}
   error=((q['own']['pts']-q['opp']['pts'])-(a['own']['pts']-a['opp']['pts']))/82;assert math.isclose(sum(parts.values()),error,abs_tol=1e-10)
   shotNoise=((2*q['own']['fgm']+q['own']['fg3m'])-(2*q['own']['xfgm']+q['own']['x3m'])-(2*q['opp']['fgm']+q['opp']['fg3m'])+(2*q['opp']['xfgm']+q['opp']['x3m']))/82
   rows.append({'season':season,'version':version,'teamId':tid,'name':t['name'],'actualWins':a['wins'],'predictedWins':q['wins'],'winsError':q['wins']-a['wins'],'netError':error,'components':parts,'shotNoiseNet':shotNoise,'expectedFGNetError':error-shotNoise,'stats':details})
 print(season,'source scores and scoring decompositions verified',flush=True)
summaries=[]
for version in ['control','v39']:
 for season in SEASONS+['ALL']:
  rs=[r for r in rows if r['version']==version and (season=='ALL' or r['season']==season)];e=np.array([r['netError'] for r in rs]);den=float(np.mean(e*e));keys=list(rs[0]['components']);cs={k:np.array([r['components'][k] for r in rs]) for k in keys};projection={k:float(np.mean(e*v)/den) for k,v in cs.items()};assert math.isclose(sum(projection.values()),1,abs_tol=1e-10)
  groups={k:float(sum(v for key,v in projection.items() if key.endswith(k))) for k in ['Volume','Accuracy']};groups.update({k:float(sum(v for key,v in projection.items() if key.startswith(k+'_'))) for k in ['own','opp']})
  summaries.append({'version':version,'season':season,'teams':len(rs),'netRMSE':float(np.sqrt(den)),'winsMAE':float(np.mean([abs(r['winsError']) for r in rs])),'expectedFGNetRMSE':float(np.sqrt(np.mean([r['expectedFGNetError']**2 for r in rs]))),'componentMeanAbsolute':{k:float(np.mean(abs(v))) for k,v in cs.items()},'netErrorProjection':projection,'groupProjection':groups,'shotNoiseMeanAbsolute':float(np.mean([abs(r['shotNoiseNet']) for r in rs]))})
hashes[str(R/'audit.py').replace('\\','/')]=sha(R/'audit.py');out={'scope':'Retrospective arithmetic decomposition only, no model change or fitted coefficients. MSE projection E[error*component]/E[error²] sums to1 but can be negative or >1 due cancellation; neither causal attribution nor independent variance. Symmetric exact count/rate decomposition of2P/3P/FT makes; individual and opponent side separate. ShotNoise removes only conditional FG make draws; FT and upstream randomness remain.','sourceAudit':sourceAudit,'summaries':summaries,'rows':rows,'hashes':hashes}
(R/'audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for s in summaries:
 if s['season']=='ALL':print(json.dumps(s,indent=2),flush=True)

"""Explore performance tails so a small league MAE cannot hide specialist errors."""
import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scores=read(R/'scores.json');result=[]
specs=[('blocksBelow1','blk36',lambda p:p['metrics']['blk36']['actual']<1),('blocksAtLeast1','blk36',lambda p:p['metrics']['blk36']['actual']>=1),('blocksAtLeast2','blk36',lambda p:p['metrics']['blk36']['actual']>=2),('assistsAtLeast8','ast36',lambda p:p['metrics']['ast36']['actual']>=8),('pointsAtLeast25','pts36',lambda p:p['metrics']['pts36']['actual']>=25)]
for c in scores['cells']:
 if c['version'] not in ['v39','rotation-space']:continue
 for label,metric,select in specs:
  ps=[p for p in c['players'] if p['minutes']>=500 and p['metrics'].get(metric) and select(p)]
  assert ps;w=sum(p['minutes'] for p in ps)
  rows=[{'playerId':p['playerId'],'name':p['name'],'actualMinutes':p['minutes'],'actual':p['metrics'][metric]['actual'],'predicted':p['metrics'][metric]['predicted'],'error':p['metrics'][metric]['predicted']-p['metrics'][metric]['actual']} for p in ps]
  result.append({'season':c['season'],'version':c['version'],'cohort':label,'metric':metric,'players':len(ps),'actualMinutes':w,'mae':sum(p['actualMinutes']*abs(p['error']) for p in rows)/w,'signedBias':sum(p['actualMinutes']*p['error'] for p in rows)/w,'underestimatedPlayers':sum(p['error']<0 for p in rows),'rows':rows})
out={'scope':'Exploratory descriptive performance cohorts, >=500 actual season minutes, season-internal minute weighting. Thresholds use observed outcomes so noise/regression to mean can affect tails; not a preselected causal test or a tuning objective. Cohorts overlap. Runtime unchanged.','rows':result,'hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'scores.json',R/'skill-cohort-errors.py']}}
(R/'skill-cohort-errors.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for version in ['v39','rotation-space']:
 for label,metric,_ in specs:
  rs=[r for r in result if r['version']==version and r['cohort']==label]
  print(json.dumps({'version':version,'cohort':label,'playerSeasons':sum(r['players'] for r in rs),'underestimatedPlayerSeasons':sum(r['underestimatedPlayers'] for r in rs),'fourSeasonEqualMAE':sum(r['mae'] for r in rs)/4,'fourSeasonEqualBias':sum(r['signedBias'] for r in rs)/4}))

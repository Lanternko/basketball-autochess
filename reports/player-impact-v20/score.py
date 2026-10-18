import json,importlib.util
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v20');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('box','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
old=box.read
def mapped(p):
 p=Path(p)
 if not p.exists() and p.parent in [Path('reports/player-impact-v19/runs'),root/'runs']:
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 return old(p)
box.read=mapped
cells=[]
import sys
for season in sys.argv[1:] or ['2025-26']:
 for folder,label in [(Path('reports/player-impact-v19'),'v19'),(root,'v20')]:
  c=box.score(season,'rotation-space',[20261012],folder);c['version']=label;cells.append(c)
  print(season,label,'MAE',{k:round(c['summary']['ALL'][k]['mae'],3) for k in ['pts36','ast36','fta36','fga36','fgPct','threePct']},'team',c['teamMetrics'],flush=True)

truth=read('reports/player-impact-v1/2025-26-on-court-truth.json');on=[]
roles={p['playerId']:p['roleGroup'] for p in next(s for s in box.baseline['seasons'] if s['season']=='2025-26')['players']}
for folder,label in [(Path('reports/player-impact-v19'),'v19'),(root,'v20')]:
 run=read(folder/'runs/2025-26-rotation-space-strict-20261012.json');assert {m['id'] for m in run['matches']}==set(truth['gameIds'])
 pred={p['playerId']:p for p in run['onCourt']['players']};rows=[]
 for p in truth['players']:
  q=pred.get(p['playerId']);metrics={}
  for name,g,m,a in [('onTeamFG','on','fgm','fga'),('onTeam3P','on','fg3m','fg3a'),('onTeammateFG','teammates','fgm','fga'),('onTeammate3P','teammates','fg3m','fg3a'),('offTeamFG','off','fgm','fga'),('offTeam3P','off','fg3m','fg3a')]:
   tr=p[g];pr=q[g] if q else {};metrics[name]={'actual':100*tr[m]/tr[a],'predicted':100*pr[m]/pr[a]} if tr.get(a,0)>=100 and pr.get(a,0)>0 else None
  for name,a,b in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
   x=metrics[a];y=metrics[b];metrics[name]={'actual':x['actual']-y['actual'],'predicted':x['predicted']-y['predicted']} if x and y else None
  rows.append({'playerId':p['playerId'],'name':p['name'],'minutes':p['on'].get('seconds',0)/60,'roleGroup':roles[p['playerId']],'metrics':metrics})
 on.append({'version':label,'summary':{k:box.metric(rows,k) for k in rows[0]['metrics']},'players':rows})
 print(label,'onCourtMAE',{k:round(q['mae'],3) for k,q in on[-1]['summary'].items()},flush=True)
(root/'scores.json').write_text(json.dumps({'limits':'Single matching seed pilot, not adoption or a full Top50. Measured contest exposure correction, source centers recomputed; all v19 FT and creator policies retained. All source rates already know this season. Counts per36, actual-minute weights>=500; source rates already know the season.','cells':cells,'onCourt':on},ensure_ascii=False,indent=2),encoding='utf-8')

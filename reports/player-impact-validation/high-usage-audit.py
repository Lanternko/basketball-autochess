"""Keep high-usage player errors visible beside the all-player mean."""
import csv,json,sys,importlib.util
from pathlib import Path
import numpy as np

root=Path('reports/player-impact-validation')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py')
box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
cells=read(root/'confirmation-scores.json')['cells']
corrected={c['season']:c for c in read('reports/player-impact-team-clock/scores.json')['cells']}
cells=[corrected[c['season']] if c['version']=='terminal-flow' else c for c in cells]
if len(sys.argv)>1:cells=read(sys.argv[1])['cells']
output=Path(sys.argv[2]) if len(sys.argv)>2 else root/'high-usage-audit.json'
truth={s['season']:{p['playerId']:p for p in s['players']} for s in box.baseline['seasons']}
results=[];detail=[]
for c in cells:
 season=c['season'];players=truth[season]
 def usage(p):
  m=p['metrics'];return m['fga36']['actual']+.44*m['fta36']['actual']+m['tov36']['actual']
 eligible=[p for p in players.values() if p['minutes']>=500]
 cutoff=float(np.quantile([usage(p) for p in eligible],.8))
 high={p['playerId'] for p in eligible if usage(p)>=cutoff}
 rows=[p for p in c['players'] if p['playerId'] in high]
 results.append({'season':season,'version':c['version'],'seeds':len(c['seeds']),'sourceUsesPer36Cutoff':cutoff,
  'metrics':{k:box.metric(rows,k) for k in c['summary']['ALL']}})
 for p in rows:
  detail.append({'season':season,'version':c['version'],'playerId':p['playerId'],'name':p['name'],'minutes':p['minutes'],'sourceUsesPer36':usage(players[p['playerId']]),'metrics':p['metrics']})
out={'definition':'Exploratory post-diagnostic subgroup: each season top quintile by actual FGA+.44FTA+TOV per36 among players with at least500 actual minutes. Threshold depends only on observed role, never names or simulation residuals. Errors weighted by actual minutes; overall averages can hide these players. Same-season reconstruction, no prospective or causal claim.','cells':results,'players':detail}
output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for version in dict.fromkeys(c['version'] for c in results):
 cs=[c for c in results if c['version']==version]
 print(version,{k:round(float(np.mean([c['metrics'][k]['mae'] for c in cs])),3) for k in ['pts36','ast36','fga36','fgPct','threePct']})

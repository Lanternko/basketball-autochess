import json
from pathlib import Path
from collections import defaultdict
from statistics import mean
R=Path('reports/player-impact-v50');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
source=read('reports/player-impact-v49/scores.json');cells=[];drivers=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 base,cand=[next(c for c in source['cells'] if c['season']==season and c['variant']==v) for v in ['v47','v49']]
 bp={p['playerId']:p for p in base['individualPlayers']};rows=[]
 for q in cand['individualPlayers']:
  if q['minutes']<500:continue
  b=bp[q['playerId']];m=q['metrics'];bm=b['metrics'];actual=m['pts36']['actual'];err=m['pts36']['predicted']-actual;old=bm['pts36']['predicted']-actual
  fga=m['fga36'];ep=m['pts36']['predicted']/fga['predicted'];ea=actual/fga['actual']
  volume=(fga['predicted']-fga['actual'])*(ep+ea)/2;eff=(ep-ea)*(fga['predicted']+fga['actual'])/2
  assert abs(volume+eff-err)<1e-10
  rows.append({'playerId':q['playerId'],'name':q['name'],'role':q['roleGroup'],'minutes':q['minutes'],'baselineError':old,'rotationError':err,'absoluteErrorChange':abs(err)-abs(old),'shotVolumeTerm':volume,'pointsPerFGATermIncludingFT':eff})
 total=sum(q['minutes'] for q in rows)
 for role in ['ALL','G','F','C']:
  group=rows if role=='ALL' else [q for q in rows if q['role']==role]
  if not group:continue
  w=sum(q['minutes'] for q in group)
  avg=lambda k:sum(q['minutes']*q[k] for q in group)/w
  cells.append({'season':season,'role':role,'players':len(group),'pts36BaselineMAE':sum(q['minutes']*abs(q['baselineError']) for q in group)/w,'pts36RotationMAE':sum(q['minutes']*abs(q['rotationError']) for q in group)/w,'fga36MAEbaseline':base['individualSummary'][role]['fga36']['mae'],'fga36MAErotation':cand['individualSummary'][role]['fga36']['mae'],'volumeAbsoluteTerm':sum(q['minutes']*abs(q['shotVolumeTerm']) for q in group)/w,'efficiencyAbsoluteTerm':sum(q['minutes']*abs(q['pointsPerFGATermIncludingFT']) for q in group)/w})
 drivers.append({'season':season,'largestWeightedRegressions':sorted(rows,key=lambda q:q['minutes']*q['absoluteErrorChange'],reverse=True)[:15]})
out={'description':'Arithmetic scoring-error decomposition only, not causal attribution. PTS/FGA includes FT scoring. Separate absolute terms can cancel. Actual-minute weights and eligibility inherited from frozen v49 scorer.','cells':cells,'drivers':drivers}
(R/'offense-diagnosis.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(cells))

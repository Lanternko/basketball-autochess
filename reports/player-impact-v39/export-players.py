import csv,json
from collections import Counter,defaultdict
from pathlib import Path
root=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(root/'scores.json');cell=next(c for c in scores['cells'] if c['season']=='2025-26' and c['version']=='rotation-space');on={p['playerId']:p for p in cell['onCourtPlayers']}
actual=defaultdict(Counter);pred=defaultdict(Counter);strict=defaultdict(Counter);predon=defaultdict(lambda:defaultdict(Counter))
keys=['pts','fgm','fga','fg3m','fg3a','fta','ftm','oreb','dreb','ast','tov','stl','blk']
for t in read('reports/defense-tenth/step4-t0/2025-26/bundle.json')['league']['teams']:
 for p in t['roster']:actual[p['playerId']].update({k:p['observed'][k.upper()] for k in keys});actual[p['playerId']]['MIN']+=p['observed']['MIN']
for seed in [20261012,20261013,20261014]:
 for group,target in [('full',pred),('strict',strict)]:
  r=read(root/f'runs/2025-26-rotation-space-{group}-{seed}.json')
  for t in r['teams']:
   for p in t['players']:
    for k,n in p['stats'].items():
     if isinstance(n,(int,float)):target[p['playerId']][k]+=n/3
  if group=='strict':
   for p in r['onCourt']['players']:
    for g in ['on','off','teammates','own']:
     for k,n in p[g].items():predon[p['playerId']][g][k]+=n/3
truth={p['playerId']:p for p in read('reports/player-impact-v1/2025-26-on-court-truth.json')['players']}
exposure=read('reports/player-impact-v20/2025-26-defense-exposure.json')['cards'];defaudit={p['playerId']:p for s in read('reports/player-impact-v28/defense-curve-audit.json')['seasons'] if s['season']=='2025-26' for p in s['rows'] if p['zone']=='short'}
configs={'onTeamFG':('on','fga'),'onTeam3P':('on','fg3a'),'onTeammateFG':('teammates','fga'),'onTeammate3P':('teammates','fg3a'),'offTeamFG':('off','fga'),'offTeam3P':('off','fg3a'),'onOpponentFG':('on','opp_fga'),'onOpponent3P':('on','opp_fg3a')}
deps={p['playerId']:p for season in read('reports/player-impact-v30/dependence-audit.json')['seasons'] if season['season']=='2025-26' for p in season['rows']}
rows=[]
for p in cell['players']:
 pid=p['playerId'];a=actual[pid];q=pred[pid];r={'playerId':pid,'name':p['name'],'position':p['position'],'roleGroup':p['roleGroup'],'actualMinutes':p['minutes'],'predictedMinutes':p['predictedMinutes'],'minutesError':p['predictedMinutes']-p['minutes'],'primaryBasicSample':p['minutes']>=500}
 assert abs(a['MIN']-p['minutes'])<1e-7 and abs(q['seconds']/60-p['predictedMinutes'])<1e-7
 for k in keys:
  for label,n in [('actual',a[k]),('predicted',q[k]),('error',q[k]-a[k])]:r[k+'Total_'+label]=n
 for k,m in p['metrics'].items():
  for label in ['actual','predicted']:r[k+'_'+label]=m[label] if m else None
  r[k+'_error']=m['predicted']-m['actual'] if m else None;r[k+'_primary']=p['minutes']>=500 and m is not None
 o=on[pid];r['strictActualMinutes']=o['minutes'];r['strictPredictedMinutes']=strict[pid]['seconds']/60
 for k,m in o['metrics'].items():
  for label in ['actual','predicted']:r[k+'_'+label]=m[label] if m else None
  r[k+'_error']=m['predicted']-m['actual'] if m else None;r[k+'_primary']=o['minutes']>=500 and m is not None
 for k,(g,att) in configs.items():r[k+'_actualAttempts']=truth[pid][g].get(att,0);r[k+'_simulatedAttemptsPerSeed']=predon[pid][g][att]
 d=defaudit.get(pid);r['rimSourceAttempts']=exposure[str(pid)]['short']['attempts'];r['rimSourceRawDifference']=exposure[str(pid)]['short']['rawDifference'];r['rimExistingShrunkDifference']=d['sourcePosterior'] if d else None;r['rimOldCurveDifference']=d['throughCurve'] if d else None;r['rimRestoredDifference']=d['difference'] if d else None
 dep=deps[pid];r['creationDependence_oldProxy']=dep['oldDependence'];r['creationDependence_sourceRole']=dep['sourceDependence'];r['creationDependence_sourceReceived']=dep['sourceReceived'];r['creationDependence_sourceTerminal']=dep['sourceTerminal']
 rows.append(r)
assert len(rows)==582 and len({p['playerId'] for p in rows})==582
with (root/'2025-26-player-validation.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('All players',len(rows),'columns',len(rows[0]),'full and strict exposure separated; per-seed total/minute averages.')

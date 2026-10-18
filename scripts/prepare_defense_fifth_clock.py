"""Forecast league pace from pre-cutoff data, select trend via past-only CV.
No later outcome, team coefficient, margin or win enters calibration targets.
"""
import json,datetime
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'reports/defense-fifth'
read=lambda f:json.loads((R/f).read_text(encoding='utf-8'))
l=read('data/season-league.json');d=read('data/season-source/team-games.json')['data']['resultSets'][0];rows=[dict(zip(d['headers'],r)) for r in d['rowSet']];by={(r['GAME_ID'],r['TEAM_ID']):r for r in rows};base=datetime.date.fromisoformat(l['schedule'][0]['date'])
p=lambda r:r['FGA']-r['OREB']+r['TOV']+.44*r['FTA']
for k in [25,41,55]:
 counter={};train=[];future=[]
 for g in l['schedule']:
  for t in [g['homeId'],g['awayId']]:counter[t]=counter.get(t,0)+1
  x=(datetime.date.fromisoformat(g['date'])-base).days
  if max(counter[g['homeId']],counter[g['awayId']])<=k:train.append((x,(p(by[g['id'],g['homeId']])+p(by[g['id'],g['awayId']]))/2))
  else:future.extend([x for t in [g['homeId'],g['awayId']] if counter[t]>k])
 a=np.array(train);dates=np.unique(a[:,0]);cuts=[np.quantile(dates,q) for q in [.5,.65,.8]];losses={'constant':[],'linear':[]}
 for t in cuts:
  tm=a[:,0]<=t;vm=(a[:,0]>t)&(a[:,0]<=t+.2*(dates[-1]-dates[0]));X=np.column_stack((np.ones(tm.sum()),a[tm,0]));b=np.linalg.lstsq(X,a[tm,1],rcond=None)[0]
  if not vm.any():continue
  losses['constant'].append(float(np.mean((a[vm,1]-a[tm,1].mean())**2)));losses['linear'].append(float(np.mean((a[vm,1]-b[0]-b[1]*a[vm,0])**2)))
 b=np.linalg.lstsq(np.column_stack((np.ones(len(a)),a[:,0])),a[:,1],rcond=None)[0];use=np.mean(losses['linear'])<np.mean(losses['constant']);target=float(b@[1,np.mean(future)]) if use else float(a[:,1].mean())
 o={'cutoff':k,'trainingGames':len(a),'trainingPace':float(a[:,1].mean()),'futureScheduleMeanDay':float(np.mean(future)),'linearCoefficients':b.tolist(),'chronologicalCV':losses,'useTrend':bool(use),'predictedPace':target,'ratio':target/float(a[:,1].mean()),'method':'Shared league pace target; only pre-cutoff pair box proxies. Past-only chronological3fold CV constant vs linear calendar trend, fixed before heldout scoring. Future schedule dates only. No future outcomes. This predicts rather than forces actual later pace.'}
 (O/f'pace-forecast-pre{k}.json').write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8');print(json.dumps(o),flush=True)

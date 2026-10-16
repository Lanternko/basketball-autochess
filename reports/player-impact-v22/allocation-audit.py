"""Separate historical minute composition from event-rate reconstruction errors."""
import csv,json
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
root=Path('reports/player-impact-v22');root.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
protocol=read('reports/player-impact-v21/validation-protocol.json')
metrics={'pts':'PTS','ast':'AST','tov':'TOV','fga':'FGA','fgm':'FGM','fg3a':'FG3A','fg3m':'FG3M','fta':'FTA','ftm':'FTM','oreb':'OREB','dreb':'DREB','stl':'STL','blk':'BLK'}
rows=[];players=[];summary=[]
for season in protocol['seasons']:
 source=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams']
 for version in ['v20','v21']:
  pred=defaultdict(lambda:defaultdict(Counter));simteams={}
  for seed in protocol['seeds']:
   for t in read(f'reports/player-impact-{version}/runs/{season}-rotation-space-full-{seed}.json')['teams']:
    x=simteams.setdefault(t['id'],Counter());x['games']+=t['games']/len(protocol['seeds'])
    for p in t['players']:
     pred[t['id']][p['playerId']].update({k:v/len(protocol['seeds']) for k,v in p['stats'].items() if isinstance(v,(int,float))})
  for t in source:
   a=Counter();atmins=Counter();simulation=Counter();actualmins=0;simmins=0;absminerror=0
   for p in t['roster']:
    obs=p['observed'];q=pred[t['id']][p['playerId']];amin=obs['MIN'];smin=q['seconds']/60
    actualmins+=amin;simmins+=smin;absminerror+=abs(smin-amin)
    pr={'season':season,'version':version,'team':t['name'],'playerId':p['playerId'],'name':p['name'],'actualMinutes':amin,'simulatedMinutes':smin,'minuteDifference':smin-amin}
    for k,v in metrics.items():
     a[k]+=obs[v];simulation[k]+=q[k];expected=smin*obs[v]/amin if amin else 0;atmins[k]+=expected
     pr[k+'_sourceAtSimulatedMinutes']=expected;pr[k+'_eventResidual']=q[k]-expected
    players.append(pr)
   row={'season':season,'version':version,'teamId':t['id'],'team':t['name'],'actualTeamPlayerMinutes':actualmins,'simulatedTeamPlayerMinutes':simmins,'absoluteMinuteDifference':absminerror,'actualGameMinutes':actualmins/(5*82),'simulatedGameMinutes':simmins/(5*82)}
   for k in metrics:
    row.update({k+'_actual':a[k]/82,k+'_sourceAtSimulatedMinutes':atmins[k]/82,k+'_simulated':simulation[k]/82,k+'_minuteCompositionDifference':(atmins[k]-a[k])/82,k+'_eventDifference':(simulation[k]-atmins[k])/82})
   rows.append(row)
  cells=[r for r in rows if r['season']==season and r['version']==version]
  entry={'season':season,'version':version,'metrics':{k:{'bias':float(np.mean([r[k+'_simulated']-r[k+'_actual'] for r in cells])),'minuteCompositionMAE':float(np.mean([abs(r[k+'_minuteCompositionDifference']) for r in cells])),'eventMAE':float(np.mean([abs(r[k+'_eventDifference']) for r in cells]))} for k in metrics},'meanActualGameMinutes':float(np.mean([r['actualGameMinutes'] for r in cells])),'meanSimulatedGameMinutes':float(np.mean([r['simulatedGameMinutes'] for r in cells]))}
  summary.append(entry);print(season,version,'PTS',entry['metrics']['pts'],'TOV',entry['metrics']['tov'],'gameMinutes',entry['meanActualGameMinutes'],entry['meanSimulatedGameMinutes'],flush=True)
for filename,rs in [('allocation-teams.csv',rows),('allocation-players.csv',players)]:
 with (root/filename).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
(root/'allocation-audit.json').write_text(json.dumps({'design':'Descriptive decomposition: actual per-team-stint box count / actual minutes times simulated minutes. This is not a counterfactual prediction: actual rate also reflects role, pace, teammates and opponents. Residuals are diagnostics only, never player-name calibration offsets. Team-only clock TOV excluded from simulated personal totals.','summary':summary,'teams':rows},ensure_ascii=False,indent=2),encoding='utf-8')

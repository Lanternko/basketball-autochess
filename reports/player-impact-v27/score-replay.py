import json,csv
from pathlib import Path
root=Path('reports/player-impact-v27');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));season='2025-26'
r=read(root/f'rotation-replay-{season}-20261012.json');assert r['games']==1188 and r['limit']==0
truth=read(root/f'{season}-strict-basic-truth.json');actual={p['playerId']:p for p in truth['players']};on={p['playerId']:p for p in read(f'reports/player-impact-v1/{season}-on-court-truth.json')['players']};box={p['playerId']:p for p in r['actual']}
for pid,p in actual.items():assert abs(p['seconds']-box[pid]['seconds'])<1e-5
box_diffs=[{'playerId':pid,'name':p['name'],'pbpPoints':p['stats']['pts'],'boxPoints':box[pid]['points']} for pid,p in actual.items() if p['stats']['pts']!=box[pid]['points']]
configs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a'),'onOpponentFG':('on','opp_fgm','opp_fga'),'onOpponent3P':('on','opp_fg3m','opp_fg3a')}
versions={};flat=[]
for version,v in r['variants'].items():
 pred={p['playerId']:p['stats'] for p in v['players']};pc={p['playerId']:p for p in v['onCourt']['players']};rows=[]
 for k in ['fga','fgm','fg3a','fg3m']:
  total=sum(p[k] for p in pred.values());assert sum(p['on'][k] for p in pc.values())==5*total;assert sum(p['own'][k] for p in pc.values())==total;assert sum(p['teammates'][k] for p in pc.values())==4*total
 for pid,p in actual.items():
  t=p['stats'];q=pred[pid];M=p['seconds']/60;N=q['seconds']/60;metrics={}
  def pair(key,av,pv,eligible=True):metrics[key]={'actual':av,'predicted':pv,'error':pv-av if av is not None and pv is not None else None,'primary':M>=500 and eligible}
  for k in ['pts','ast','tov','stl','blk','oreb','dreb','fga','fta']:
   pair(k+'36',36*t[k]/M if M else None,36*q[k]/N if N else None)
  pair('reb36',36*(t['oreb']+t['dreb'])/M if M else None,36*(q['oreb']+q['dreb'])/N if N else None)
  for key,m,a in [('fgPct','fgm','fga'),('threePct','fg3m','fg3a')]:pair(key,100*t[m]/t[a] if t[a] else None,100*q[m]/q[a] if q[a] else None,t[a]>=100)
  for key,(group,m,a) in configs.items():
   x=on[pid][group];y=pc.get(pid,{}).get(group,{})
   pair(key,100*x.get(m,0)/x[a] if x.get(a,0) else None,100*y.get(m,0)/y[a] if y.get(a,0) else None,x.get(a,0)>=100)
  for key,x,y in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
   A=metrics[x];B=metrics[y];pair(key,A['actual']-B['actual'] if A['actual'] is not None and B['actual'] is not None else None,A['predicted']-B['predicted'] if A['predicted'] is not None and B['predicted'] is not None else None,A['primary'] and B['primary'])
  row={'version':version,'playerId':pid,'name':p['name'],'actualMinutes':M,'simulatedMinutes':N,'metrics':metrics};rows.append(row)
  f={k:row[k] for k in ['version','playerId','name','actualMinutes','simulatedMinutes']}
  for k in t:f[k+'Total_actual']=t[k];f[k+'Total_predicted']=q[k]
  for k,vals in metrics.items():
   for x,val in vals.items():f[k+'_'+x]=val
  for k,(g,m,a) in configs.items():f[k+'_actualAttempts']=on[pid][g].get(a,0);f[k+'_predictedAttempts']=pc.get(pid,{}).get(g,{}).get(a,0)
  flat.append(f)
 summaries={}
 for key in rows[0]['metrics']:
  eligible=[p for p in rows if p['metrics'][key]['primary'] and p['metrics'][key]['error'] is not None];den=sum(p['actualMinutes'] for p in eligible)
  summaries[key]={'players':len(eligible),'minuteWeightedMAE':sum(p['actualMinutes']*abs(p['metrics'][key]['error']) for p in eligible)/den if den else None}
 versions[version]={'summary':summaries,'players':rows}
 print(version,{k:round(summaries[k]['minuteWeightedMAE'],4) for k in ['pts36','ast36','tov36','stl36','blk36','dreb36','fgPct','threePct','onTeamFG','onOpponentFG']},flush=True)
out={'season':season,'gamesPerVersion':1188,'seed':20261012,'scope':r['scope'],'scoring':'Strict same-game PBP individual counts and source-stint minutes, independently reconciled FG/DREB ledgers. Actual-minute weighted >=500 minutes; FG/3P and on-court denominator>=100. All582 retained. One seed, fixed historical horizon and no foul-out in all arms. Not comparable to ordinary-season win gates.','sourcePbpVersusOfficialBoxPointDiscrepancies':box_diffs,'versions':versions}
(root/'rotation-replay-scores.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'rotation-replay-all-players.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
print('box PTS discrepancies',len(box_diffs),'CSV rows',len(flat),'columns',len(flat[0]))

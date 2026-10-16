"""Publish all-player diagnostics without declaring a failed candidate adopted."""
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
root=Path('reports/player-impact-v25');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(root/'scores.json');protocol=read(root/'validation-protocol.json');season='2025-26'
current=next(c for c in scores['cells'] if c['season']==season and c['version']=='rotation-space')
previous=next(c for c in scores['cells'] if c['season']==season and c['version']=='v24')
source=read(f'reports/player-impact-v21/{season}-terminal-risk.json');tracking=read(f'reports/player-impact-v21/{season}-tracking.json');pbsource=read(f'reports/player-impact-v22/{season}-putback-events.json');pbrates=read(f'reports/player-impact-v22/{season}-putback-rates.json');pbsim=defaultdict(Counter)
choices=read(f'reports/player-impact-v23/{season}-choice-rates.json');choice_source=read(f'reports/player-impact-v23/{season}-putback-choices.json')
dreb_source=read(Path('reports/player-impact-v24')/f'{season}-dreb-rates.json')
contact_source=read(root/f'{season}-contact-recipient.json');ftsim=defaultdict(Counter);contactsim=defaultdict(Counter)
provenance={p['playerId']:p for p in read('reports/player-impact-v20/2025-26-measurement-provenance.json')['rows']}
actual=defaultdict(Counter);pred=defaultdict(Counter);onc=defaultdict(lambda:defaultdict(Counter))
for t in read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams']:
 for p in t['roster']:actual[p['playerId']].update(p['observed'])
for seed in protocol['seeds']:
 for t in read(root/f'runs/{season}-rotation-space-full-{seed}.json')['teams']:
  for p in t['players']:
   pred[p['playerId']].update({k:v/len(protocol['seeds']) for k,v in p['stats'].items() if isinstance(v,(float,int))})
 strict=read(root/f'runs/{season}-rotation-space-strict-{seed}.json')
 for pid,counts in strict['ftAudit']['players'].items():ftsim[int(pid)].update({k:v/len(protocol['seeds']) for k,v in counts.items()})
 for pid,counts in strict['contactAudit']['players'].items():contactsim[int(pid)].update({k:v/len(protocol['seeds']) for k,v in counts.items()})
 for pid,pb in strict['putbackAudit']['players'].items():pbsim[int(pid)].update({k:v/len(protocol['seeds']) for k,v in pb.items()})
 for p in strict['onCourt']['players']:
  for g in ['on','off','teammates','own']:onc[p['playerId']][g].update(p[g])
truth={p['playerId']:p for p in read(f'reports/player-impact-v1/{season}-on-court-truth.json')['players']}
counts={'pts':'PTS','ast':'AST','oreb':'OREB','dreb':'DREB','stl':'STL','blk':'BLK','tov':'TOV','fga':'FGA','fg3a':'FG3A','fta':'FTA'}
onconfigs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a'),'onOpponentFG':('on','opp_fgm','opp_fga'),'onOpponent3P':('on','opp_fg3m','opp_fg3a')}
rows=[]
for p in current['players']:
 pid=p['playerId'];a=actual[pid];b=pred[pid];risk=source['cards'][str(pid)];tm=tracking['cards'][str(pid)]
 row={'playerId':pid,'name':p['name'],'position':p['position'],'roleLowConfidence':provenance[pid]['role']['lowConfidence'],'actualMinutes':a['MIN'],'simulatedMinutes':b['seconds']/60,'primarySummarySample':a['MIN']>=500,'movementSourceAvailable':tm.get('movement') is not None,'movementUsedAsSkill':False,'unknownOffBall':70,'unknownScreen':70,'unknownHandle':70,'unknownBreakDouble':70,'terminalSourceOpportunities':risk['opportunities'],'terminalDeadProbability':risk['deadProbability'],'terminalNeutralLiveProbability':risk['neutralLiveProbability']}
 def pair(key,av,pv):
  row[key+'_actual']=av;row[key+'_predicted']=pv;row[key+'_error']=pv-av if av is not None and pv is not None else None
 for k,obs in counts.items():
  pair(k+'Total',a[obs],b[k] if b['seconds'] else None)
  pair(k+'36',36*a[obs]/a['MIN'] if a['MIN'] else None,36*b[k]/(b['seconds']/60) if b['seconds'] else None)
 pair('rebTotal',a['OREB']+a['DREB'],b['oreb']+b['dreb'] if b['seconds'] else None)
 pair('reb36',36*(a['OREB']+a['DREB'])/a['MIN'] if a['MIN'] else None,36*(b['oreb']+b['dreb'])/(b['seconds']/60) if b['seconds'] else None)
 for key,am,aa,pm,pa in [('fgPct','FGM','FGA','fgm','fga'),('threePct','FG3M','FG3A','fg3m','fg3a')]:
  pair(key,100*a[am]/a[aa] if a[aa] else None,100*b[pm]/b[pa] if b[pa] else None)
  row[key+'_actualAttempts']=a[aa];row[key+'_simulatedAttempts']=b[pa];row[key+'_primarySummarySample']=a['MIN']>=500 and a[aa]>=100
 for key,(g,m,n) in onconfigs.items():
  ta=truth[pid][g];pr=onc[pid][g]
  pair(key,100*ta.get(m,0)/ta[n] if ta.get(n,0) else None,100*pr[m]/pr[n] if pr[n] else None)
  row[key+'_actualAttempts']=ta.get(n,0);row[key+'_simulatedAttemptsPerSeed']=pr[n]/len(protocol['seeds']);row[key+'_primarySummarySample']=a['MIN']>=500 and ta.get(n,0)>=100
 for key,x,y in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
  av=row[x+'_actual']-row[y+'_actual'] if row[x+'_actual'] is not None and row[y+'_actual'] is not None else None
  pv=row[x+'_predicted']-row[y+'_predicted'] if row[x+'_predicted'] is not None and row[y+'_predicted'] is not None else None
  pair(key,av,pv)
 pb=pbsource['cards'][str(pid)];sp=pbsim[pid]
 row.update(putbackSourceAttempts=pb['attempts'],putbackSourceMakes=pb['makes'],putbackPosteriorFG=pbrates['cards'][str(pid)]['rate'],putbackSimulatedAttemptsPerSeed=sp['fga'],putbackSimulatedMakesPerSeed=sp['fgm'],putbackSourceFG=pb['makes']/pb['attempts'] if pb['attempts'] else None,putbackSimulatedFG=sp['fgm']/sp['fga'] if sp['fga'] else None,putbackSimulatedExpectedFG=sp['expectedMakes']/sp['fga'] if sp['fga'] else None)
 cm=choices['cards'][str(pid)];cs=choice_source['cards'][str(pid)]
 row.update(putbackSourceFGRebounds=cs.get('fgReboundOpportunities',0),putbackEligibleSourceRebounds=cm['rebounds'],putbackEligibleSourceFGA=cm['fastFga'],putbackSourceSurvivalSum=cm['survivalSum'],putbackChoicePosterior=cm['selectionProbabilityMAP'],putbackExpectedSourceFGA=cm['selectionProbabilityMAP']*cm['survivalSum'],putbackStyleFixedUnderCounterfactual=True)
 dm=dreb_source['cards'][str(pid)]
 row.update(drebSourceTeamWonOpportunities=dm['sourceTeamWonOpportunities'],drebSourceCaptured=dm['sourceDreb'],drebRecipientStrength=dm['strength'],drebSourceExpectedCaptured=dm['sourceExpectedDreb'],drebRecipientIsCausalSkill=False)
 cm=contact_source['cards'][str(pid)];row.update(contactSourceDrawn=cm['sourceDrawnContacts'],contactSourceTeamOpportunities=cm['sourceContactOpportunities'],contactSourceExpectedDrawn=cm['sourceExpectedContacts'],contactRecipientStrength=cm['strength'],contactRecipientIsCausalSkill=False)
 for kind in ['shooting','andOne','nonShooting','intentional','technical','unresolved']:row['strictFta_'+kind+'_perSeed']=ftsim[pid][kind]
 for kind in ['nonShooting','intentional']:row['strictContacts_'+kind+'_perSeed']=contactsim[pid][kind]
 rows.append(row)
assert len(rows)==582 and len({r['playerId'] for r in rows})==582
with (root/f'{season}-player-validation.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


print({'players':len(rows),'columns':len(rows[0])})

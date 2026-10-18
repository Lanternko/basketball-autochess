import json,importlib.util,csv,hashlib,sys
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
ROOT=Path('reports/player-impact-v21');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
oldread=box.read
def trialread(p):
 p=Path(p)
 if not p.exists() and p.parent in [Path('reports/player-impact-v21/runs'),Path('reports/player-impact-v20/runs')]:
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 run=oldread(p)
 if p.parent==Path('reports/defense-tenth/step4-rebounds-turnover-time/runs'):
  for t in run['teams']:
   attributed=sum(q['stats'].get('clockTov',0) for q in t['players'])
   assert attributed==t['stats'].get('clockTov',0)
   for q in t['players']:
    stats=q['stats'];clock=stats.get('clockTov',0)
    assert stats['tov']>=clock and stats.get('deadTov',0)>=clock
    stats['tov']-=clock;stats['deadTov']-=clock;stats['clockTov']=0
 return run
box.read=trialread
pilot='--pilot' in sys.argv;prefix='pilot-' if pilot else '';protocol=read(ROOT/('pilot-protocol-2025-26.json' if pilot else 'validation-protocol.json'));cells=[]
configs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),
 'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a'),'onOpponentFG':('on','opp_fgm','opp_fga'),'onOpponent3P':('on','opp_fg3m','opp_fg3a')}
for season in protocol['seasons']:
 truth=read(f'reports/player-impact-v1/{season}-on-court-truth.json');actual={p['playerId']:p for p in truth['players']}
 base=next(s for s in box.baseline['seasons'] if s['season']==season);roles={p['playerId']:p['roleGroup'] for p in base['players']}
 for version in ['control','v20']+protocol['variants']:
  c=box.score(season,'rotation-space' if version=='v20' else version,protocol['seeds'],Path('reports/player-impact-v20' if version=='v20' else 'reports/player-impact-v21'));c['version']=version;pred=defaultdict(lambda:defaultdict(Counter))
  for seed in protocol['seeds']:
   f=Path('reports/player-impact-validation')/f'control/{season}-{seed}.json' if version=='control' else Path(f'reports/player-impact-v21/runs/{season}-{version}-strict-{seed}.json')
   if version=='v20':f=Path(f'reports/player-impact-v20/runs/{season}-rotation-space-strict-{seed}.json')
   run=read(f);assert len(run['matches'])==truth['strictGames']
   assert {m['id'] for m in run['matches']}==set(truth['gameIds'])
   ps=run['onCourt']['players'];total={k:sum(t['stats'][k] for t in run['teams']) for k in ['fga','fgm','fg3a','fg3m']}
   for k,n in total.items():
    assert sum(p['on'][k] for p in ps)==5*n
    assert sum(p['own'][k] for p in ps)==n
    assert sum(p['teammates'][k] for p in ps)==4*n
   for p in ps:
    for group in ['on','off','teammates','own']:pred[p['playerId']][group].update(p[group])
  rows=[]
  for pid,t in actual.items():
   p=pred[pid];metrics={}
   for name,(group,m,a) in configs.items():
    tr=t[group];pr=p[group];tv=100*tr.get(m,0)/tr[a] if tr.get(a,0)>=100 else None;pv=100*pr[m]/pr[a] if pr[a] else None
    metrics[name]={'actual':tv,'predicted':pv} if tv is not None and pv is not None else None
   for name,a,b in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
    x=metrics[a];y=metrics[b];metrics[name]={'actual':x['actual']-y['actual'],'predicted':x['predicted']-y['predicted']} if x and y else None
   rows.append({'playerId':pid,'name':t['name'],'minutes':t['on'].get('seconds',0)/60,'roleGroup':roles[pid],'metrics':metrics})
  c['onCourtSummary']={g:{k:box.metric(rows,k,g) for k in rows[0]['metrics']} for g in ['ALL','G','F','C']};c['onCourtPlayers']=rows;cells.append(c)
  print(season,version,'MAE',{k:round(c['summary']['ALL'][k]['mae'],3) for k in ['pts36','ast36','tov36','stl36','oreb36','dreb36','blk36','fgPct','threePct']},'team',c['teamMetrics'],'on-court',{k:round(c['onCourtSummary']['ALL'][k]['mae'],3) for k in ['onTeamFG','onTeam3P','onTeammateFG','onTeammate3P']},flush=True)
aggregate={}
for v in ['control','v20']+protocol['variants']:
 cs=[c for c in cells if c['version']==v];aggregate[v]={'individualMAE':{k:float(np.mean([c['summary']['ALL'][k]['mae'] for c in cs])) for k in cs[0]['summary']['ALL']},
  'team':{k:float(np.mean([c['teamMetrics'][k] for c in cs])) for k in cs[0]['teamMetrics']},
  'onCourtMAE':{k:float(np.mean([c['onCourtSummary']['ALL'][k]['mae'] for c in cs])) for k in cs[0]['onCourtSummary']['ALL']}}
result={'controlClockAccounting':'Player TOV/deadTov in archived control are reduced by attributed shot-clock violations, now team-only; team totals and every match unchanged. Candidate already uses team-only clock accounting.','design':'All four seen seasons; three seeds each; same-season reconstruction; matching strict PBP games for on/off. Actual-minute weighted errors at >=500 actual minutes. All players exported, trades combined by playerId. Not causal on/off or prospective accuracy.','aggregate':aggregate,'cells':cells}
(ROOT/(prefix+'scores.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/(prefix+'all-players.csv')).open('w',newline='',encoding='utf-8-sig') as f:
 keys=list(cells[0]['players'][0]['metrics']);fields=['season','version','playerId','name','position','roleGroup','minutes','predictedMinutes','primarySample']+[k+'_'+z for k in keys for z in ['actual','predicted','error']];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for c in cells:
  for p in c['players']:
   row={k:p[k] for k in fields[:8] if k in p};row.update(season=c['season'],version=c['version'],primarySample=p['minutes']>=500)
   for k,q in p['metrics'].items():
    if q:row.update({k+'_actual':q['actual'],k+'_predicted':q['predicted'],k+'_error':q['predicted']-q['actual']})
   w.writerow(row)
with (ROOT/(prefix+'all-players-on-court.csv')).open('w',newline='',encoding='utf-8-sig') as f:
 keys=list(cells[0]['onCourtPlayers'][0]['metrics']);fields=['season','version','playerId','name','roleGroup','minutes','primarySample']+[k+'_'+z for k in keys for z in ['actual','predicted','error']];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for c in cells:
  for p in c['onCourtPlayers']:
   row={k:p[k] for k in ['playerId','name','roleGroup','minutes']};row.update(season=c['season'],version=c['version'],primarySample=p['minutes']>=500)
   for k,q in p['metrics'].items():
    if q:row.update({k+'_actual':q['actual'],k+'_predicted':q['predicted'],k+'_error':q['predicted']-q['actual']})
   w.writerow(row)
print('FOUR-SEASON AGGREGATE',json.dumps(aggregate,indent=2),flush=True)

import json,importlib.util
from pathlib import Path
ROOT=Path('reports/player-impact-v1');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
oldread=box.read
def trialread(p):
 p=Path(p)
 if not p.exists() and p.parent==ROOT/'runs':
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 return oldread(p)
box.read=trialread
season='2025-26';seed=20261012;versions=['control','creation-flow','creation-flow-balanced'];cells=[]
control=read(ROOT/f'runs/{season}-control-full-{seed}.json');old=read(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{season}-split-{seed}.json')
assert control['matches']==old['matches'] and control['teams']==old['teams'],'Control gameplay drift'
truth=read(ROOT/f'{season}-on-court-truth.json');actual={p['playerId']:p for p in truth['players']}
baseline=next(s for s in box.baseline['seasons'] if s['season']==season);roles={p['playerId']:p['roleGroup'] for p in baseline['players']}
for field in ['fga','fgm','fg3a','fg3m']:
 assert sum(p['on'].get(field,0) for p in truth['players'])==5*sum(p['own'].get(field,0) for p in truth['players']),field
for v in versions:
 c=box.score(season,v,[seed],ROOT);cells.append(c)
 run=read(ROOT/f'runs/{season}-{v}-strict-{seed}.json');assert len(run['matches'])==truth['strictGames']
 pred={p['playerId']:p for p in run['onCourt']['players']};rows=[]
 configs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),
 'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a'),'onOpponentFG':('on','opp_fgm','opp_fga'),'onOpponent3P':('on','opp_fg3m','opp_fg3a')}
 for pid,t in actual.items():
  p=pred.get(pid);metrics={}
  for name,(group,m,a) in configs.items():
   tr=t[group];pr=p[group] if p else {};tv=100*tr.get(m,0)/tr[a] if tr.get(a,0)>=100 else None;pv=100*pr.get(m,0)/pr[a] if pr.get(a,0)>0 else None
   metrics[name]={'actual':tv,'predicted':pv} if tv is not None and pv is not None else None
  for name,a,b in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
   x=metrics[a];y=metrics[b];metrics[name]={'actual':x['actual']-y['actual'],'predicted':x['predicted']-y['predicted']} if x and y else None
  rows.append({'playerId':pid,'name':t['name'],'minutes':t['on'].get('seconds',0)/60,'roleGroup':roles[pid],'metrics':metrics})
 c['onCourtSummary']={g:{k:box.metric(rows,k,g) for k in rows[0]['metrics']} for g in ['ALL','G','F','C']};c['onCourtPlayers']=rows
 # Conservation of exact shot attribution in the observer.
 total={k:sum(t['stats'][k] for t in run['teams']) for k in ['fga','fgm','fg3a','fg3m']}
 for k in total:
  assert sum(p['on'][k] for p in pred.values())==5*total[k]
  assert sum(p['own'][k] for p in pred.values())==total[k]
  assert sum(p['teammates'][k] for p in pred.values())==4*total[k]
 print(v,'individual MAE',{k:round(c['summary']['ALL'][k]['mae'],3) for k in ['pts36','ast36','tov36','oreb36','dreb36','blk36','stl36','fgPct','threePct']},'team',c['teamMetrics'],flush=True)
 print(v,'on-court MAE',{k:round(c['onCourtSummary']['ALL'][k]['mae'],3) for k in configs},flush=True)
(ROOT/'scores-diagnostic.json').write_text(json.dumps({'season':season,'seed':seed,'label':'One-seed mechanism diagnosis, no promotion or forecasting claim','cells':cells},ensure_ascii=False,indent=2),encoding='utf-8')
for v in versions:
 c=next(c for c in cells if c['version']==v)
 for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Stephen Curry','Neemias Queta']:
  p=next(p for p in c['players'] if p['name']==name);print(v,name,[(k,tuple(round(z,2) for z in p['metrics'][k].values())) for k in ['pts36','ast36','fga36']],flush=True)

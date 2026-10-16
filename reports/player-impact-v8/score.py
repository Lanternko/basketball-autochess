import json,importlib.util
from pathlib import Path
ROOT=Path('reports/player-impact-v8');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
oldread=box.read
def mapped(p):
 p=Path(p)
 if p.parent==ROOT/'runs':
  version=p.stem.removeprefix('2025-26-').removesuffix('-20261012');return oldread(ROOT/f'runs/2025-26-{version}-full-20261012.json')
 return oldread(p)
box.read=mapped
truth=read('reports/player-impact-v1/2025-26-on-court-truth.json');cells=[]
roles={p['playerId']:p['roleGroup'] for p in next(s for s in box.baseline['seasons'] if s['season']=='2025-26')['players']}
configs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a')}

for v in ['elastic-flow','elastic-creation','elastic-space']:
 c=box.score('2025-26',v,[20261012],ROOT);run=read(ROOT/f'runs/2025-26-{v}-strict-20261012.json');ps={p['playerId']:p for p in run['onCourt']['players']};rows=[]
 for t in truth['players']:
  p=ps.get(t['playerId']);metrics={}
  for k,(g,m,a) in configs.items():
   actual=t[g];pred=p[g] if p else {};tv=100*actual.get(m,0)/actual[a] if actual.get(a,0)>=100 else None;pv=100*pred.get(m,0)/pred[a] if pred.get(a,0)>0 else None
   metrics[k]={'actual':tv,'predicted':pv} if tv is not None and pv is not None else None
  for name,x,y in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
   metrics[name]={'actual':metrics[x]['actual']-metrics[y]['actual'],'predicted':metrics[x]['predicted']-metrics[y]['predicted']} if metrics[x] and metrics[y] else None
  rows.append({'playerId':t['playerId'],'name':t['name'],'minutes':t['on'].get('seconds',0)/60,'roleGroup':roles[t['playerId']],'metrics':metrics})
 c['onCourtSummary']={k:box.metric(rows,k) for k in rows[0]['metrics']};c['onCourtPlayers']=rows;cells.append(c)
 print(v,'team',c['teamMetrics'],'individualMAE',{k:round(c['summary']['ALL'][k]['mae'],3) for k in ['pts36','ast36','fgPct','threePct']},'on-courtMAE',{k:round(q['mae'],3) for k,q in c['onCourtSummary'].items()},flush=True)
(ROOT/'scores.json').write_text(json.dumps({'limits':'Single-seed mechanism check, four-season validation still required. Context center uses empirical input cards but does not fit on/off or ranking targets. Alpha and beta fit real actor choices in prior three seasons; check season is historically seen, not blind.', 'cells':cells},ensure_ascii=False,indent=2),encoding='utf-8')

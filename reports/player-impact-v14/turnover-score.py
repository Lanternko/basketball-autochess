import json,importlib.util
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('reports/player-impact-v14');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
out=[]
keys=['tov','liveTov','passStolenAgainst','handleStolenAgainst','passTov','handleTov']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 actual=read(Path('reports/player-impact-validation')/f'{season}-turnover-truth.json');roles={p['playerId']:p['roleGroup'] for p in next(s for s in box.baseline['seasons'] if s['season']==season)['players']}
 for version in ['control','rotation-space']:
  sums=defaultdict(Counter)
  for seed in [20261012,20261013,20261014]:
   run=read(Path('reports/player-impact-validation')/f'control/{season}-{seed}.json' if version=='control' else f'reports/player-impact-v14/runs/{season}-{version}-strict-{seed}.json')
   assert len(run['matches'])==actual['games']
   for t in run['teams']:
    for p in t['players']:
     q=p['stats'];handle=q['touchTov']-q['deadTov']+q['clockTov'];pas=q['liveTov']-handle;assert handle>=0 and pas>=0
     sums[p['playerId']].update({'minutes':q['seconds']/60,'tov':q['tov'],'liveTov':q['liveTov'],'passStolenAgainst':pas,'handleStolenAgainst':handle,'passTov':pas+q['passOutTov'],'handleTov':handle+q['handlingOutTov'],'assignedClock':q['clockTov']})
  rows=[]
  for p in actual['players']:
   pid=p['playerId'];s=sums[pid];metrics={k:{'actual':36*p['counts'].get(k,0)/p['minutes'],'predicted':36*s[k]/s['minutes']} if p['minutes'] and s['minutes'] else None for k in keys}
   rows.append({**{k:p[k] for k in ['playerId','name','minutes']},'roleGroup':roles[pid],'metrics':metrics})
  c={'season':season,'version':version,'games':actual['games'],'summary':{g:{k:box.metric(rows,k,g) for k in keys} for g in ['ALL','G','F','C']},'players':rows};out.append(c)
  if season=='2025-26':print(version,{g:{k:(round(c['summary'][g][k]['actual'],3),round(c['summary'][g][k]['predicted'],3),round(c['summary'][g][k]['mae'],3)) for k in keys} for g in ['ALL','G','C']},flush=True)
(ROOT/'turnover-scores.json').write_text(json.dumps({'limits':'Strict same-game comparison; all known player IDs; exact offensive subtype partitions. Candidate clock turnovers are team-only, with zero individual clock debit; archived control retains its original attribution. No observed pass/touch denominators, so per-pass/per-dribble risk cannot be declared accurate.','cells':out},ensure_ascii=False,indent=2),encoding='utf-8')

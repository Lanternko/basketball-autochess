import json,sys
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-v46');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));protocol=read(ROOT/'protocol.json');seasons=sys.argv[1:] or protocol['seasons'];out=[]
for season in seasons:
 truth=read(f'reports/player-impact-v42/{season}-defense-truth.json');actual={p['playerId']:p for p in truth['players']}
 def metric(p,key):
  z='short' if 'short' in key else 'long';stat='M' if 'FGpct' in key else 'A';delta=key.startswith('delta')
  def arm(a):
   c=p[a];den=c.get(z+'A',0) if stat=='M' else c.get('fga',0)
   return 100*c.get(z+stat,0)/den if den>=100 else None
  a=arm('on');b=arm('off');return a-b if delta and a is not None and b is not None else None if delta else a
 keys=['onshortFGpct','onlongFGpct','onshortShare','onlongShare','deltashortFGpct','deltashortShare']
 for variant in ['v45','v46']:
  for seed in protocol['seeds']:
   run=read(f'reports/player-impact-{variant}/runs/{season}-{variant}-strict-{seed}.json');players={p['playerId']:p for p in run['defense']['players']};mae={}
   for k in keys:
    pairs=[(p,players[p['playerId']]) for p in actual.values() if p['onSeconds']/60>=500 and metric(p,k) is not None and metric(players[p['playerId']],k) is not None];mae[k]=sum(p['onSeconds']*abs(metric(q,k)-metric(p,k)) for p,q in pairs)/sum(p['onSeconds'] for p,q in pairs)
   w=players.get(1641705);out.append({'season':season,'variant':variant,'seed':seed,'defenseMAE':mae,'wemby':{k:metric(w,k) for k in keys} if w else None})
result={'scope':'Per-seed Monte Carlo diagnostic; not independent real-world seasons or formal confidence intervals. Main reported errors pool three seeds before calculating rates.','rows':out};prefix='' if len(seasons)==4 else '-'.join(seasons)+'-';(ROOT/(prefix+'seed-check.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))

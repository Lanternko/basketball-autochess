"""Apply the existing per-minute DREB allocation to actual source risk sets."""
import json
from pathlib import Path
from collections import Counter,defaultdict

root=Path('reports/player-impact-v24')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
out={}
for season in ['2022-23','2023-24','2024-25','2025-26']:
 src=read(root/f'{season}-dreb-risksets.json');obs=defaultdict(Counter)
 for t in read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams']:
  for p in t['roster']:obs[p['playerId']].update({k:p['observed'][k] for k in ['MIN','DREB']})
 total=sum(obs.values(),Counter());prior=total['DREB']/total['MIN'];weights={pid:(p['DREB']+240*prior)/(p['MIN']+240) for pid,p in obs.items()}
 actual=Counter();expected=Counter()
 for g in src['games']:
  for recipient,*lineup in g['rows']:
   actual[recipient]+=1;den=sum(weights[pid] for pid in lineup)
   for pid in lineup:expected[pid]+=weights[pid]/den
 players=[{'playerId':pid,'name':name,'actualDreb':actual[int(pid)],'expectedOldAllocation':expected[int(pid)],'error':expected[int(pid)]-actual[int(pid)]} for pid,name in src['players'].items()]
 result={'meanAbsoluteCountError':sum(abs(p['error']) for p in players)/len(players),'players':players};out[season]=result
 print(season,'MAE',result['meanAbsoluteCountError'],flush=True)
 if season=='2025-26':print([p for p in players if int(p['playerId']) in [201939,203999,1628983,1629029,1629674]],flush=True)
(root/'old-source-allocation-audit.json').write_text(json.dumps({'design':'Current v23 240-minute-prior DREB/min weights applied to exactly the actual five and actual team-won individual DREB events. Does not involve simulation, different team opportunity totals, player minutes or names in fitting. This diagnostic uses full same-season observed box rates; not a blind validation.','seasons':out},indent=2),encoding='utf-8')

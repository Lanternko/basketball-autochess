"""Diagnostic decomposition only; never feed team residuals back into player cards."""
import json,csv
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
root=Path('reports/player-impact-v21');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
protocol=read(root/'validation-protocol.json');out=[]
for season in protocol['seasons']:
 actual=read('reports/defense-tenth/step4-rebounds-turnover-time/seed-arrays.json')[season]
 truth={tid:{k:values[i] for k,values in actual['truth'].items()} for i,tid in enumerate(actual['ids'])}
 observed={t['id']:t for t in read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams']}
 runs={}
 for version in ['v20','v21']:
  sums=defaultdict(Counter)
  for seed in protocol['seeds']:
   for t in read(f'reports/player-impact-{version}/runs/{season}-rotation-space-full-{seed}.json')['teams']:
    for side,key in [('stats','own'),('opponent','opp')]:
     for k in ['pts','ast','fga','fgm','fg3a','fg3m','tov','stl','oreb','dreb','fta','ftm']:
      sums[t['id']][key+'_'+k]+=t[side].get(k,0)/(82*len(protocol['seeds']))
    sums[t['id']]['wins']+=t['wins']/len(protocol['seeds'])
  runs[version]=sums
 for tid,t in observed.items():
  before,after=runs['v20'][tid],runs['v21'][tid];target=truth[tid]
  row={'season':season,'teamId':tid,'team':t['name'],'actualNet':target['net'],'actualWins':target['wins']}
  for v,x in [('v20',before),('v21',after)]:
   row.update({v+'_'+k:val for k,val in x.items()});row[v+'_net']=x['own_pts']-x['opp_pts'];row[v+'_netError']=row[v+'_net']-target['net']
  row['deltaNet']=row['v21_net']-row['v20_net'];row['deltaTovMargin']=(after['opp_tov']-after['own_tov'])-(before['opp_tov']-before['own_tov'])
  row['deltaNetAbsoluteError']=abs(row['v21_netError'])-abs(row['v20_netError']);out.append(row)
 summary=[r for r in out if r['season']==season]
 x=np.array([r['deltaTovMargin'] for r in summary]);y=np.array([r['deltaNet'] for r in summary])
 print(season,'corrDeltaNetTovMargin',round(float(np.corrcoef(x,y)[0,1]),4),'largestNetRegressions',[(r['team'],round(r['deltaNetAbsoluteError'],3),round(r['deltaTovMargin'],3)) for r in sorted(summary,key=lambda r:-r['deltaNetAbsoluteError'])[:5]],flush=True)
with (root/'team-impact-audit.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
(root/'team-impact-audit.json').write_text(json.dumps({'design':'Matched three seeds; descriptive team-level decomposition only. Changes also change subsequent RNG paths, so observed net change is not an exact isolated causal turnover value. No residual is fed into model.','rows':out},ensure_ascii=False,indent=2),encoding='utf-8')

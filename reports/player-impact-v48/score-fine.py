import json,csv,sys
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
ROOT=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));protocol=read(ROOT/'protocol.json');source=read(Path('reports/player-impact-v45/make-evaluation.json'));choice=read(Path('reports/player-impact-v45/choice-evaluation.json'));cells=[]
zones={'ra':['ra'],'paint':['paint'],'mid':['mid'],'corner':['corner'],'arc':['arc'],'short':['ra','paint'],'long':['corner','arc']}
seasons=sys.argv[1:] or protocol['seasons'];assert all(s in protocol['seasons'] for s in seasons);prefix='' if seasons==protocol['seasons'] else '-'.join(seasons)+'-'
for season in seasons:
 actual=next(s for s in source['seasons'] if s['season']==season);actualShares={p['playerId']:p for s in choice['seasons'] if s['season']==season for p in s['players']};counts=defaultdict(lambda:{'on':Counter(),'off':Counter()})
 for seed in protocol['seeds']:
  run=read(ROOT/f'runs/{season}-v48-strict-{seed}.json');assert run['fineDefense']['freshOnly']
  for p in run['fineDefense']['players']:
   for arm in ['on','off']:counts[p['playerId']][arm].update(p[arm])
 rows=[]
 for p in actual['players']:
  metrics={}
  for name,zz in zones.items():
   if name not in p['metrics']:continue
   pred={}
   for arm in ['on','off']:
    c=counts[p['playerId']][arm];n=sum(c[z+'A'] for z in zz);m=sum(c[z+'M'] for z in zz);pred[arm]=100*m/n if n else None
   if any(v is None for v in pred.values()):continue
   pred['delta']=pred['on']-pred['off'];metrics[name]={arm:{'actual':p['metrics'][name][arm]['actual'],'predicted':pred[arm],'error':pred[arm]-p['metrics'][name][arm]['actual']} for arm in ['on','off','delta']}
  shares={}
  for name,zz in zones.items():
   truth=actualShares[p['playerId']]['metrics'].get(name)
   if not truth:continue
   pred={}
   for arm in ['on','off']:
    c=counts[p['playerId']][arm];n=c['fga'];pred[arm]=100*sum(c[z+'A'] for z in zz)/n if n else None
   if any(v is None for v in pred.values()):continue
   pred['delta']=pred['on']-pred['off'];shares[name]={arm:{'actual':truth[arm]['actual'],'predicted':pred[arm],'error':pred[arm]-truth[arm]['actual']} for arm in ['on','off','delta']}
  rows.append({'playerId':p['playerId'],'name':p['name'],'minutes':p['minutes'],'metrics':metrics,'shareMetrics':shares})
 summary={}
 for z in zones:
  for arm in ['on','delta']:
   rs=[p for p in rows if p['minutes']>=500 and z in p['metrics']];den=sum(p['minutes'] for p in rs)
   summary[z+':'+arm]={'players':len(rs),'mae':sum(p['minutes']*abs(p['metrics'][z][arm]['error']) for p in rs)/den,'bias':sum(p['minutes']*p['metrics'][z][arm]['error'] for p in rs)/den}
   rs=[p for p in rows if p['minutes']>=500 and z in p['shareMetrics']];den=sum(p['minutes'] for p in rs)
   summary[z+':'+arm+'Share']={'players':len(rs),'mae':sum(p['minutes']*abs(p['shareMetrics'][z][arm]['error']) for p in rs)/den,'bias':sum(p['minutes']*p['shareMetrics'][z][arm]['error'] for p in rs)/den}
 cells.append({'season':season,'summary':summary,'players':rows})
 print(json.dumps({'season':season,'summary':summary,'wemby':next(({k:p[k] for k in ['metrics','shareMetrics']} for p in rows if p['playerId']==1641705),None)}),flush=True)
(ROOT/(prefix+'fine-scores.json')).write_text(json.dumps({'scope':'Fresh recorded FGA only, >=500 source minutes. Make rates require >=100 actual zone attempts both on and off; shares require >=100 actual total fresh attempts in each arm. Three-seed pooled simulation fine counts. No archived five-zone simulation baseline; source cross-fitted expectations are a different validation condition.','cells':cells}),encoding='utf-8')

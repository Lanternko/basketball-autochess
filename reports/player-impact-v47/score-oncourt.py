"""Compare unchanged observational offense definitions after the FT-only fix."""
import json
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
R=Path('reports/player-impact-v47');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));baseline=read(R/'diagnosis.json');protocol=read(R/'protocol.json');cells=[]
def rates(p):
 out={}
 for arm in ['on','off','teammates']:
  c=p[arm];a=c['fga'];three=c['fg3a'];two=a-three
  for suffix,m,n in [('FGpct',c['fgm'],a),('threePct',c['fg3m'],three),('twoPct',c['fgm']-c['fg3m'],two),('threeShare',three,a),('eFGpct',c['fgm']+.5*c['fg3m'],a)]:out[arm+suffix]=100*m/n if n else None
 for k in ['FGpct','threePct','twoPct','threeShare','eFGpct']:
  a,b=out['on'+k],out['off'+k];out['delta'+k]=a-b if a is not None and b is not None else None
 return out
for old in baseline['cells']:
 season=old['season'];pred=defaultdict(lambda:{k:Counter() for k in ['on','off','teammates']});seedvalues=defaultdict(list)
 for seed in protocol['seeds']:
  run=read(R/f'runs/{season}-v47-strict-{seed}.json')
  for p in run['onCourt']['players']:
   for arm in ['on','off','teammates']:pred[p['playerId']][arm].update(p[arm])
   seedvalues[p['playerId']].append(rates(p))
 rows=[]
 for b in old['onCourtPlayers']:
  pid=b['playerId'];pr=rates(pred[pid]);actual=rates(b['actualCounts']);metrics={}
  for k,m in b['metrics'].items():
   assert abs(m['actual']-actual[k])<1e-9
   if pr[k] is None:continue
   rs=[c[k] for c in seedvalues[pid] if c[k] is not None];metrics[k]={'actual':actual[k],'baseline':m['predicted'],'predicted':pr[k],'error':pr[k]-actual[k],'seedMin':min(rs),'seedMax':max(rs)}
  rows.append({'playerId':pid,'name':b['name'],'minutes':b['minutes'],'metrics':metrics})
 summary={}
 for k,v in old['onCourtSummary'].items():
  eligible={b['playerId'] for b in old['onCourtPlayers'] if b['minutes']>=500 and k in b['metrics'] and all(b['actualCounts'][a]['fg3a']>=100 for a in ['on','off','teammates'])};rs=[r for r in rows if r['playerId'] in eligible and k in r['metrics']];assert len(rs)==v['players'];den=sum(r['minutes'] for r in rs);recomputed=sum(r['minutes']*abs(r['metrics'][k]['baseline']-r['metrics'][k]['actual']) for r in rs)/den;assert abs(recomputed-v['mae'])<1e-9
  summary[k]={'players':len(rs),'baselineMAE':v['mae'],'candidateMAE':sum(r['minutes']*abs(r['metrics'][k]['error']) for r in rs)/den}
 cells.append({'season':season,'summary':summary,'curry':next(r for r in rows if r['playerId']==201939),'players':rows})
(R/'offense-oncourt-scores.json').write_text(json.dumps({'scope':baseline['scope'],'summaryEligibility':baseline['onCourtSummaryEligibility'],'baseline':'v46','candidate':'v47','cells':cells},ensure_ascii=False),encoding='utf-8');print(json.dumps({'seasons':len(cells),'baselineValuesIndependentlyReproduced':True,'curry2025':cells[-1]['curry']['metrics']}))

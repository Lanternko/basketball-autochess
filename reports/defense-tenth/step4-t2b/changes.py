import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,ast,hashlib
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.stats import rankdata
O=Path(__file__).resolve().parent;R=O.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
P=read(O/'protocol.json');p={'uncertainty':{'rng':P['portability']['rng']}}
tree=ast.parse((R/'reports/defense-tenth/step4-t2/analyze.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['corr','evaluate']],type_ignores=[]),'frozen-bootstrap-functions','exec'),globals())
data=read(O/'portability-samples.json');out=[];periods=[]
for m in sorted({x['metric'] for x in data['adjacent']}):
 for group in ['same','moved','seasonMove','officialTradeParticipant']:
  source=data['adjacent'] if group in ['same','moved'] else data['within'];rows=[r for r in source if r['metric']==m and (r['group']==group or group=='officialTradeParticipant' and r['confirmed'])]
  for season in sorted({x['period'] for x in rows}):
   rr=[r for r in rows if r['period']==season];periods.append({'metric':m,'group':group,'period':season,**evaluate(rr,m+group+season)})
  if len(rows)<10:continue
  ids=sorted({r['id'] for r in rows});teams=sorted({t for r in rows for t in r['teams']});ix={k:i for i,k in enumerate(ids)};ti={k:i for i,k in enumerate(teams)}
  pi=np.array([ix[r['id']] for r in rows]);t0=np.array([ti[r['teams'][0]] for r in rows]);t1=np.array([ti[r['teams'][-1]] for r in rows]);delta=np.array([r['y']-r['x'] for r in rows]);order=sorted({r['period'] for r in rows});masks=[np.array([r['period']==v for r in rows]) for v in order]
  rng=np.random.default_rng(P['portability']['rng']^int(hashlib.sha256((m+group+'delta').encode()).hexdigest()[:8],16));mean=[];absolute=[]
  for start in range(0,20000,500):
   tc=rng.multinomial(len(teams),np.ones(len(teams))/len(teams),size=500);pc=rng.multinomial(len(ids),np.ones(len(ids))/len(ids),size=500);w=(tc[:,t0]+tc[:,t1])/2*pc[:,pi];v=np.zeros(500);a=np.zeros(500);valid=np.ones(500,bool)
   for mask in masks:
    ww=w[:,mask];sw=ww.sum(axis=1);safe=np.maximum(sw,1e-100);v+=ww@delta[mask]/safe/len(masks);a+=ww@np.abs(delta[mask])/safe/len(masks);valid&=sw>0
   mean.extend(v[valid]);absolute.extend(a[valid])
  out.append({'metric':m,'group':group,'n':len(rows),'meanChangePP':float(np.mean([delta[mask].mean() for mask in masks])),'meanAbsoluteChangePP':float(np.mean([np.abs(delta[mask]).mean() for mask in masks])),'changeCI95':np.quantile(mean,[.025,.975]).tolist(),'absoluteChangeCI95':np.quantile(absolute,[.025,.975]).tolist(),'validBootstrap':len(mean),'label':'descriptive before-after change; not organizer or trade causal effect'})
 print('CHANGES',m,flush=True)
(O/'portability-changes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
(O/'portability-by-period.json').write_text(json.dumps(periods,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')

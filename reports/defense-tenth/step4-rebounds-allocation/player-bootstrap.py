import json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
read=lambda f:json.loads((R/f).read_text(encoding='utf-8'))
d=read('player-arrays.json');p=read('protocol.json');B=p['uncertainty']['bootstrap'];rng=np.random.default_rng(p['uncertainty']['seed'])
fr=rng.integers(0,30,(B,30));se=rng.integers(0,20,(B,20));cw=np.stack([(se==i).sum(1) for i in range(20)],axis=1)/20
bs={};points={}
for season,s in d.items():
 ids=s['ids'];cluster=np.array([ids.index(a['cluster']) for a in s['truth']]);weight=np.array([a['minutes'] for a in s['truth']]);target=np.array([a['actualPer36'] for a in s['truth']]);group=np.eye(30)[cluster]
 bs[season]={};points[season]={}
 for version,v in s['versions'].items():
  reb=np.array(v['orebs']);minutes=np.array(v['minutes']);rate=36*reb.mean(0)/minutes.mean(0);error=rate-target
  points[season][version]={'MAE':float((weight*abs(error)).sum()/weight.sum()),'RMSE':float(np.sqrt((weight*error*error).sum()/weight.sum()))}
  result={k:np.zeros(B) for k in ['MAE','RMSE']}
  for start in range(0,B,500):
   end=min(B,start+500);m=cw[start:end]@minutes;r=cw[start:end]@reb;pred=np.divide(36*r,m,out=np.zeros_like(r),where=m>0);err=pred-target
   denominator=np.broadcast_to(weight@group,(end-start,30));maenum=(abs(err)*weight)@group;mse=(err*err*weight)@group;idx=fr[start:end]
   den=np.take_along_axis(denominator,idx,axis=1).sum(1)
   result['MAE'][start:end]=np.take_along_axis(maenum,idx,axis=1).sum(1)/den
   result['RMSE'][start:end]=np.sqrt(np.take_along_axis(mse,idx,axis=1).sum(1)/den)
  bs[season][version]=result
 print(season,points[season],flush=True)
out={}
for seasons in [[s]for s in d]+[list(d)]:
 name=seasons[0] if len(seasons)==1 else 'four-seasons-equal';row={'versions':{},'paired':{}}
 for k in ['MAE','RMSE']:
  boot={v:np.mean([bs[s][v][k] for s in seasons],axis=0) if k=='MAE' else np.sqrt(np.mean([bs[s][v][k]**2 for s in seasons],axis=0)) for v in ['acquisition','allocation']}
  point={v:float(np.mean([points[s][v][k] for s in seasons])) if k=='MAE' else float(np.sqrt(np.mean([points[s][v][k]**2 for s in seasons]))) for v in boot}
  for v in boot:row['versions'].setdefault(v,{})[k]={'point':point[v],'joint95':np.quantile(boot[v],[.025,.975]).tolist()}
  row['paired'][k]={'point':point['allocation']-point['acquisition'],'joint95':np.quantile(boot['allocation']-boot['acquisition'],[.025,.975]).tolist()}
 out[name]=row
(R/'joint-player-intervals.json').write_text(json.dumps({'replicates':B,'scheme':p['uncertainty'],'comparisons':out},indent=2)+'\n',encoding='utf-8');print(json.dumps(out['four-seasons-equal']),flush=True)

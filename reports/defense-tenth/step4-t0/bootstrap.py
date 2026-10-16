import json
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
R=Path(__file__).resolve().parent
d=json.loads((R/'seed-arrays.json').read_text());p=json.loads((R/'protocol.json').read_text());rng=np.random.default_rng(p['uncertainty']['seed']);B=p['uncertainty']['bootstrap']
fr=rng.integers(0,30,(B,30));se=rng.integers(0,20,(B,20));counts=np.stack([(se==i).sum(1) for i in range(20)],axis=1)/20
def metric(x,y,w,z):
    x=x-x.mean(-1,keepdims=True);y=y-y.mean(-1,keepdims=True)
    sx=np.sqrt((x*x).mean((-1,-2)));sy=np.sqrt((y*y).mean((-1,-2)));cov=(x*y).mean((-1,-2));px=rankdata(x,axis=-1);py=rankdata(y,axis=-1);px-=px.mean(-1,keepdims=True);py-=py.mean(-1,keepdims=True)
    return {'netRMSE':np.sqrt(((x-y)**2).mean((-1,-2))),'Pearson':cov/(sx*sy),'Spearman':(px*py).mean((-1,-2))/np.sqrt((px*px).mean((-1,-2))*(py*py).mean((-1,-2))),'calibrationSlope':cov/(sx*sx),'SDRatio':sx/sy,'winsMAE':abs(w-z).mean((-1,-2)),'winsRMSE':np.sqrt(((w-z)**2).mean((-1,-2)))}
out={};allseasons=list(d)
for selected in [[s] for s in allseasons]+[allseasons]:
    key=selected[0] if len(selected)==1 else 'four-seasons-equal';results={};points={}
    for v in ['pure','v3']:
        xs=[];ys=[];ws=[];zs=[];xp=[];yp=[];wp=[];zp=[]
        for s in selected:
            a=d[s];net=np.array(a['versions'][v]['net']);wins=np.array(a['versions'][v]['wins']);truth=np.array(a['truth']['net']);tw=np.array(a['truth']['wins']);bn=counts@net;bw=counts@wins
            xs.append(np.take_along_axis(bn,fr,axis=1));ws.append(np.take_along_axis(bw,fr,axis=1));ys.append(truth[fr]);zs.append(tw[fr]);xp.append(net.mean(0));wp.append(wins.mean(0));yp.append(truth);zp.append(tw)
        results[v]=metric(np.stack(xs,1),np.stack(ys,1),np.stack(ws,1),np.stack(zs,1));points[v]=metric(np.stack(xp),np.stack(yp),np.stack(wp),np.stack(zp))
    out[key]={'versions':{v:{k:{'point':float(points[v][k]),'joint95':np.quantile(vals,[.025,.975]).tolist()} for k,vals in results[v].items()} for v in results},'pureMinusV3':{k:{'point':float(points['pure'][k]-points['v3'][k]),'joint95':np.quantile(results['pure'][k]-results['v3'][k],[.025,.975]).tolist()} for k in results['pure']}}
(R/'joint-intervals.json').write_text(json.dumps({'replicates':B,'method':p['uncertainty'],'comparisons':out},indent=2)+'\n');print(json.dumps({s:j['pureMinusV3']['netRMSE'] for s,j in out.items()}))

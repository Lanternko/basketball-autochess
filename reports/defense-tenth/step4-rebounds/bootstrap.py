import json
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=read(R/'seed-arrays.json');p=read(R/'protocol.json');B=p['uncertainty']['bootstrap'];rng=np.random.default_rng(p['uncertainty']['seed'])
fr=rng.integers(0,30,(B,30));se=rng.integers(0,20,(B,20));counts=np.stack([(se==i).sum(1) for i in range(20)],axis=1)/20
def centered(x):return x-x.mean(-1,keepdims=True)
def rms(x):return np.sqrt((x*x).mean((-1,-2)))
def corr(x,y):
    a=centered(x);b=centered(y);return(a*b).mean((-1,-2))/(rms(a)*rms(b))
def metrics(a,y):
    x=centered(a['net']);t=centered(y['net']);sx=rms(x);sy=rms(t);cov=(x*t).mean((-1,-2))
    return {'netRMSE':rms(x-t),'Pearson':cov/(sx*sy),'Spearman':corr(rankdata(x,axis=-1),rankdata(t,axis=-1)),'calibrationSlope':cov/(sx*sx),'SDRatio':sx/sy,'winsMAE':abs(a['wins']-y['wins']).mean((-1,-2)),'winsRMSE':rms(a['wins']-y['wins']),'DREB_RMSE':rms(centered(a['dreb']-y['dreb'])),'DREB_Correlation':corr(a['dreb'],y['dreb']),'DREB_SDRatio':rms(centered(a['dreb']))/rms(centered(y['dreb'])),'defenseProxyRMSE':rms(centered(a['drtg']-y['drtg'])),'defenseCorrelation':corr(a['drtg'],y['drtg']),'defenseSDRatio':rms(centered(a['drtg']))/rms(centered(y['drtg'])),'offenseRMSE':rms(centered(a['off']-y['off'])),'defenseRMSE':rms(centered(a['allowed']-y['allowed']))}
out={};keys=list(d)
for selected in [[s]for s in keys]+[keys]:
    label=selected[0] if len(selected)==1 else 'four-seasons-equal';bs={};pts={}
    for v in ['T0','pooled','dreb']:
        aa={};yy={};ap={};yp={}
        for k in d[selected[0]]['truth']:
            aa[k]=np.stack([np.take_along_axis(counts@np.array(d[s]['versions'][v][k]),fr,axis=1) for s in selected],axis=1)
            yy[k]=np.stack([np.array(d[s]['truth'][k])[fr] for s in selected],axis=1)
            ap[k]=np.stack([np.array(d[s]['versions'][v][k]).mean(0) for s in selected]);yp[k]=np.stack([np.array(d[s]['truth'][k]) for s in selected])
        bs[v]=metrics(aa,yy);pts[v]=metrics(ap,yp)
    pairs={}
    for a,b in [('dreb','pooled'),('dreb','T0'),('pooled','T0')]:
        pairs[a+'Minus'+b]={k:{'point':float(pts[a][k]-pts[b][k]),'joint95':np.quantile(bs[a][k]-bs[b][k],[.025,.975]).tolist()} for k in pts[a]}
    out[label]={'versions':{v:{k:{'point':float(pts[v][k]),'joint95':np.quantile(bs[v][k],[.025,.975]).tolist()} for k in pts[v]} for v in pts},'paired':pairs}
    print(label,json.dumps(pairs['drebMinuspooled']['netRMSE']),flush=True)
(R/'joint-intervals.json').write_text(json.dumps({'replicates':B,'scheme':p['uncertainty'],'comparisons':out},indent=2)+'\n',encoding='utf-8')

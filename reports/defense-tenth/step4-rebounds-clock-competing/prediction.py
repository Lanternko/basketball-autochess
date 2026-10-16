import json
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
p=read(R/'protocol.json');old=read('reports/defense-tenth/step4-rebounds-turnover-time/seed-arrays.json');d={}
for s in p['seasons']:
 q=old[s];v={k:[] for k in q['truth']}
 for seed in p['fullSeeds']:
  x=read(R/f'runs/{s}-combined-{seed}.json');assert len(x['matches'])==1230;look={t['id']:t for t in x['teams']}
  for tid in q['ids']:
   t=look[tid];assert t['games']==82
  for k in v:
   row=[]
   for tid in q['ids']:
    t=look[tid];a=t['stats'];b=t['opponent'];n=t['games'];poss=(a['fga']-a['oreb']+a['tov']+.44*a['fta']+b['fga']-b['oreb']+b['tov']+.44*b['fta'])/2
    row.append((a['pts']-b['pts'])/n if k=='net' else t['wins'] if k=='wins' else a['pts']/n if k=='off' else b['pts']/n if k=='allowed' else 100*a['dreb']/(a['dreb']+b['oreb']) if k=='dreb' else 100*a['oreb']/(a['oreb']+b['dreb']) if k=='oreb' else 100*b['pts']/poss if k=='drtg' else 100*a['pts']/poss)
   v[k].append(row)
 d[s]={'ids':q['ids'],'truth':q['truth'],'versions':{'baseline':q['versions']['split'],'combined':v}}
(R/'seed-arrays.json').write_text(json.dumps(d)+'\n',encoding='utf8')
B=p['predictionBootstrap'];rng=np.random.default_rng(p['bootstrapSeed']);fr=rng.integers(0,30,(B,30));se=rng.integers(0,20,(B,20));counts=np.stack([(se==i).sum(1) for i in range(20)],axis=1)/20
def centered(x):return x-x.mean(-1,keepdims=True)
def rms(x):return np.sqrt((x*x).mean((-1,-2)))
def corr(x,y):
    a=centered(x);b=centered(y);return(a*b).mean((-1,-2))/(rms(a)*rms(b))
def metrics(a,y):
    x=centered(a['net']);t=centered(y['net']);sx=rms(x);sy=rms(t);cov=(x*t).mean((-1,-2))
    return {'netRMSE':rms(x-t),'Pearson':cov/(sx*sy),'Spearman':corr(rankdata(x,axis=-1),rankdata(t,axis=-1)),'calibrationSlope':cov/(sx*sx),'SDRatio':sx/sy,'winsMAE':abs(a['wins']-y['wins']).mean((-1,-2)),'winsRMSE':rms(a['wins']-y['wins']),'winSlope':cov*0+corr(a['net'],a['wins'])*rms(centered(a['wins']))/sx,'OREB_MAE':abs(centered(a['oreb']-y['oreb'])).mean((-1,-2)),'OREB_RMSE':rms(centered(a['oreb']-y['oreb'])),'OREB_RawMAE':abs(a['oreb']-y['oreb']).mean((-1,-2)),'OREB_Correlation':corr(a['oreb'],y['oreb']),'OREB_SDRatio':rms(centered(a['oreb']))/rms(centered(y['oreb'])),'DREB_RMSE':rms(centered(a['dreb']-y['dreb'])),'DREB_Correlation':corr(a['dreb'],y['dreb']),'DREB_SDRatio':rms(centered(a['dreb']))/rms(centered(y['dreb'])),'defenseProxyRMSE':rms(centered(a['drtg']-y['drtg'])),'defenseCorrelation':corr(a['drtg'],y['drtg']),'defenseSDRatio':rms(centered(a['drtg']))/rms(centered(y['drtg'])),'offenseRMSE':rms(centered(a['off']-y['off'])),'defenseRMSE':rms(centered(a['allowed']-y['allowed']))}
out={};keys=list(d)
for selected in [[s]for s in keys]+[keys]:
    label=selected[0] if len(selected)==1 else 'four-seasons-equal';bs={};pts={}
    for v in ['baseline','combined']:
        aa={};yy={};ap={};yp={}
        for k in d[selected[0]]['truth']:
            aa[k]=np.stack([np.take_along_axis(counts@np.array(d[s]['versions'][v][k]),fr,axis=1) for s in selected],axis=1)
            yy[k]=np.stack([np.array(d[s]['truth'][k])[fr] for s in selected],axis=1)
            ap[k]=np.stack([np.array(d[s]['versions'][v][k]).mean(0) for s in selected]);yp[k]=np.stack([np.array(d[s]['truth'][k]) for s in selected])
        bs[v]=metrics(aa,yy);pts[v]=metrics(ap,yp)
    pairs={}
    for a,b in [('combined','baseline')]:
        pairs[a+'Minus'+b]={k:{'point':float(pts[a][k]-pts[b][k]),'joint95':np.quantile(bs[a][k]-bs[b][k],[.025,.975]).tolist()} for k in pts[a]}
    out[label]={'versions':{v:{k:{'point':float(pts[v][k]),'joint95':np.quantile(bs[v][k],[.025,.975]).tolist()} for k in pts[v]} for v in pts},'paired':pairs}
    print(label,json.dumps(pairs['combinedMinusbaseline']['netRMSE']),flush=True)
(R/'joint-intervals.json').write_text(json.dumps({'replicates':B,'scheme':'paired franchise and seed shared across seasons; centered per season; equal season weight','comparisons':out},indent=2)+'\n',encoding='utf-8')

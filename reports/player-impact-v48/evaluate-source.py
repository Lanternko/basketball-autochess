import json
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));proto=read(R/'protocol.json');sigma=read(R/'selection.json')['selectedSigma'];cells=[]
for season in proto['seasons']:
 data=read(f'reports/player-impact-v45/{season}-fga-data.json');ids=[p['playerId'] for p in data['players']];minutes=np.zeros(len(ids));idx={pid:i for i,pid in enumerate(ids)}
 for gid,f,ps in data['minutes']:
  for pid,m in ps:minutes[idx[pid]]+=m
 counts={}
 for label,a in [('baseline',0),('candidate',sigma)]:
  fits=[read(R/'fits'/f'{season}-sigma{a:g}-fold{fold}.json') for fold in range(5)];counts[label]={z:{key:{arm:sum(np.array(f['models'][zi]['counters'][key][arm]) for f in fits) for arm in ['on','off','teammates']} for key in ['actualAttempts','actualMakes','predictedMakes']} for zi,z in enumerate(proto['zones'])}
 rows=[]
 for i,player in enumerate(data['players']):
  metrics={}
  for name,zz in [('ra',['ra']),('paint',['paint']),('mid',['mid']),('short',['ra','paint']),('two',['ra','paint','mid'])]:
   values={}
   for arm in ['on','off','teammates']:
    n=sum(counts['baseline'][z]['actualAttempts'][arm][i] for z in zz);m=sum(counts['baseline'][z]['actualMakes'][arm][i] for z in zz)
    if n<100:continue
    values[arm]={'attempts':int(n),'makes':int(m),'actual':100*m/n,**{label:100*sum(counts[label][z]['predictedMakes'][arm][i] for z in zz)/n for label in counts}}
   if 'on' in values and 'off' in values:values['delta']={k:values['on'][k]-values['off'][k] for k in ['actual','baseline','candidate']}
   metrics[name]=values
  rows.append({**player,'minutes':float(minutes[i]),'metrics':metrics})
 summary={}
 for name in ['ra','paint','mid','short','two']:
  for arm in ['on','off','teammates','delta']:
   rs=[p for p in rows if p['minutes']>=500 and arm in p['metrics'][name]];den=sum(p['minutes'] for p in rs);summary[name+':'+arm]={'players':len(rs),**{label:sum(p['minutes']*abs(p['metrics'][name][arm][label]-p['metrics'][name][arm]['actual']) for p in rs)/den for label in counts}}
 cells.append({'season':season,'summary':summary,'players':rows});print(json.dumps({'season':season,'summary':summary,'curry':next(p for p in rows if p['playerId']==201939)}))
(R/'source-evaluation.json').write_text(json.dumps({'scope':'Whole-game cross-fitted fresh two-point make expectation on actual shots and lineups. Fixed training-only defender offsets; jointly estimated shooter and other-four-teammate coefficients. Not causal gravity or future prediction. >=500 source minutes, >=100 actual zone attempts per reported arm.','cells':cells},ensure_ascii=False),encoding='utf-8')

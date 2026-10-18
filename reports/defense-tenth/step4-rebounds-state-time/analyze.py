import json,pathlib,numpy as np
r=pathlib.Path('reports/defense-tenth/step4-rebounds-state-time')
p=json.loads((r/'protocol.json').read_text());real=json.loads((r/'real.json').read_text());states=p['states'];seasons=p['seasons'];seeds=p['seeds']
ids=[t['id'] for t in json.loads(pathlib.Path('reports/defense-tenth/step4-t0/2025-26/bundle.json').read_text(encoding='utf8'))['league']['teams']];index={v:i for i,v in enumerate(ids)}
R=np.zeros((4,30,8,6));S=np.zeros((4,3,30,8,6));result={'seasons':{},'scope':'all available official regular-season games; three diagnostic seeds; seen answers','parity':[]}
def summarize(games,arr):
 vals=[[[] for _ in range(3)] for _ in states];audit={};kinds={};draws={};nanchors=np.zeros(8)
 for g in games:
  for k,v in g['audit'].items():audit[k]=audit.get(k,0)+v
  for side,state,*tail in g['rows']:
   nanchors[state]+=1;team=index[g['awayId'] if side else g['homeId']]
   for m,val in enumerate(tail[:3]):
    if val is not None:arr[team,state,2*m]+=val;arr[team,state,2*m+1]+=1;vals[state][m].append(val)
   key=str(tail[3]);kinds[key]=kinds.get(key,0)+1
  for side,origin,putback,seconds,limit in g.get('draws',[]):draws.setdefault(origin+('Putback' if putback else ''),[]).append(seconds)
 out={}
 for si,state in enumerate(states):
  out[state]={'anchors':int(nanchors[si])}
  for m,name in enumerate(['first','segment','full']):
   a=np.array(vals[si][m]);out[state][name]={'n':len(a),'mean':float(a.mean()) if len(a) else None,'median':float(np.median(a)) if len(a) else None,'p90':float(np.quantile(a,.9)) if len(a) else None}
 return {'states':out,'audit':audit,'firstKinds':kinds,'draws':{k:{'n':len(v),'mean':float(np.mean(v)),'median':float(np.median(v)),'p90':float(np.quantile(v,.9))} for k,v in draws.items()}}
for si,season in enumerate(seasons):
 rg=real[season]['games'];allowed={g['id'] for g in rg};rr=summarize(rg,R[si]);sim=[]
 for ji,seed in enumerate(seeds):
  data=json.loads((r/'runs'/f'{season}-calibrated-{seed}.json').read_text());result['parity'].append(data['parity']);sg=[g for g in data['games'] if g['id'] in allowed];sim.append(summarize(sg,S[si,ji]))
 result['seasons'][season]={'real':rr,'sim':sim,'missing':real[season]['missing'],'failures':real[season]['failures'],'scoreAudit':real[season]['scoreAudit']}
 print('SUMMARIZED',season,flush=True)
# Equal season, count-weighted within each season; bootstrap franchise and seed jointly across seasons.
rng=np.random.default_rng(20261015);B=20000
wc=np.array([np.bincount(x,minlength=30) for x in rng.integers(0,30,(B,30))]);sc=np.array([np.bincount(x,minlength=3)/3 for x in rng.integers(0,3,(B,3))]);br=[];bs=[]
for si in range(4):
 br.append(np.einsum('bi,ikm->bkm',wc,R[si]));bs.append(np.einsum('bj,bi,jikm->bkm',sc,wc,S[si]))
br=np.array(br);bs=np.array(bs);rv=R.sum(axis=1);sv=S.mean(axis=1).sum(axis=1)
result['pooled']={}
for k,state in enumerate(states):
 result['pooled'][state]={}
 for m,name in enumerate(['first','segment','full']):
  rm=(rv[:,k,2*m]/rv[:,k,2*m+1]).mean();sm=(sv[:,k,2*m]/sv[:,k,2*m+1]).mean()
  d=(bs[:,:,k,2*m]/bs[:,:,k,2*m+1]-br[:,:,k,2*m]/br[:,:,k,2*m+1]).mean(axis=0)
  result['pooled'][state][name]={'real':float(rm),'sim':float(sm),'difference':float(sm-rm),'joint95':np.quantile(d,[.025,.975]).tolist()}
for x in [rv,sv]:pass
rw=rv[:,:,1]/rv[:,:,1].sum(axis=1,keepdims=True);sw=sv[:,:,1]/sv[:,:,1].sum(axis=1,keepdims=True);rm=rv[:,:,0]/rv[:,:,1];sm=sv[:,:,0]/sv[:,:,1]
result['decomposition']={'realFirstMean':float((rw*rm).sum(axis=1).mean()),'simFirstMean':float((sw*sm).sum(axis=1).mean()),'withinState':float((rw*(sm-rm)).sum(axis=1).mean()),'composition':float(((sw-rw)*sm).sum(axis=1).mean()),'contributions':{s:{'withinState':float((rw[:,k]*(sm[:,k]-rm[:,k])).mean()),'composition':float(((sw[:,k]-rw[:,k])*sm[:,k]).mean()),'realFrequency':float(rw[:,k].mean()),'simFrequency':float(sw[:,k].mean())} for k,s in enumerate(states)}}
(r/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(r/'joint-arrays.npz',real=R,sim=S,franchises=ids)
print(json.dumps({'pooled':result['pooled'],'decomposition':result['decomposition']},indent=2))

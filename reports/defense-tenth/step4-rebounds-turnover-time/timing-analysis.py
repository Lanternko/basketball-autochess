import json,pathlib,numpy as np
r=pathlib.Path('reports/defense-tenth/step4-rebounds-turnover-time')
old=pathlib.Path('reports/defense-tenth/step4-rebounds-state-time')
load=lambda f:json.loads(f.read_text(encoding='utf8'))
p=load(r/'protocol.json');real=load(old/'real.json');ids=sorted({g['homeId'] for s in p['seasons'] for g in real[s]['games']});idx={t:i for i,t in enumerate(ids)}
R=np.zeros((4,30,8,6));S=np.zeros((2,4,3,30,8,6));audits={}
def add(games,a):
 audit={}
 for g in games:
  for k,v in g['audit'].items():audit[k]=audit.get(k,0)+v
  for side,state,first,segment,full,kind in g['rows']:
   team=idx[g['awayId'] if side else g['homeId']]
   for m,x in enumerate([first,segment,full]):
    if x is not None:a[team,state,2*m]+=x;a[team,state,2*m+1]+=1
 return audit
for si,s in enumerate(p['seasons']):
 allowed={g['id'] for g in real[s]['games']};audits[s]={'real':add(real[s]['games'],R[si]),'calibrated':[],'split':[]}
 for ji,seed in enumerate(p['diagnosticSeeds']):
  for vi,v in enumerate(['calibrated','split']):
   data=load(old/'runs'/f'{s}-calibrated-{seed}.json') if v=='calibrated' else load(r/'runs'/f'{s}-split-{seed}.json')
   games=data['games'] if v=='calibrated' else data['stateTiming'];audits[s][v].append(add([g for g in games if g['id'] in allowed],S[vi,si,ji]))
 print('TIMING',s,flush=True)
rng=np.random.default_rng(p['uncertainty']['seed']);B=p['uncertainty']['bootstrap'];wc=np.array([np.bincount(x,minlength=30) for x in rng.integers(0,30,(B,30))]);sc=np.array([np.bincount(x,minlength=3)/3 for x in rng.integers(0,3,(B,3))])
br=np.array([np.einsum('bi,ikm->bkm',wc,R[si]) for si in range(4)])
bs=np.array([[np.einsum('bj,bi,jikm->bkm',sc,wc,S[vi,si]) for si in range(4)] for vi in range(2)])
rp=R.sum(axis=1);sp=S.mean(axis=2).sum(axis=2);out={}
for k,state in enumerate(['made','dreb','liveTurnover','deadTurnover','playerOreb','teamOreb','ftOreb','foulRetained']):
 out[state]={}
 for m,name in enumerate(['first','segment','full']):
  truth=(rp[:,k,2*m]/rp[:,k,2*m+1]).mean();pred=(sp[:,:,k,2*m]/sp[:,:,k,2*m+1]).mean(axis=1)
  btruth=(br[:,:,k,2*m]/br[:,:,k,2*m+1]).mean(axis=0);bpred=(bs[:,:,:,k,2*m]/bs[:,:,:,k,2*m+1]).mean(axis=1)
  delta=bpred[1]-bpred[0];ae=abs(bpred[1]-btruth)-abs(bpred[0]-btruth)
  out[state][name]={'real':float(truth),'calibrated':float(pred[0]),'split':float(pred[1]),'change':float(pred[1]-pred[0]),'joint95':np.quantile(delta,[.025,.975]).tolist(),'absoluteErrorChange':float(abs(pred[1]-truth)-abs(pred[0]-truth)),'absoluteErrorChangeJoint95':np.quantile(ae,[.025,.975]).tolist()}
(r/'timing-analysis.json').write_text(json.dumps({'pooled':out,'audits':audits,'scheme':'20,000 franchise+3 diagnostic seed paired across seasons; descriptive'},indent=2)+'\n')
print(json.dumps({s:out[s] for s in ['liveTurnover','deadTurnover']},indent=2))

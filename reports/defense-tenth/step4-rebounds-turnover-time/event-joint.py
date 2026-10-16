import json,pathlib,numpy as np
r=pathlib.Path('reports/defense-tenth/step4-rebounds-turnover-time');load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf-8'));p=load(r/'protocol.json');p['seeds']=p['diagnosticSeeds'];real=load('reports/defense-tenth/step4-rebounds-after/real.json');rng=np.random.default_rng(20261015);B=20000
teams=sorted({int(x['homeId']) for s in p['seasons'] for x in load(f'reports/defense-tenth/step4-t0/{s}/bundle.json')['league']['schedule']});idx={t:i for i,t in enumerate(teams)}
keys=['immediateProxy','otherShot','earlyLoss','laterLoss','foul','meanSeconds','shortShotPct','longShotPct','fgPct','sameShooterPct','firstFgPointsPerOreb'];A=np.zeros((4,10,30,len(keys),2))
def add(s,v,t,x):
 i=idx[int(t)];shot=x['category'] in ['immediateProxy','otherShot']
 for k,key in enumerate(keys):
  den=1;num=0
  if key in keys[:5]:num=100*(x['category']==key)
  elif key=='meanSeconds':den=x.get('seconds') is not None;num=x.get('seconds') or 0
  elif key=='firstFgPointsPerOreb':num=x.get('points',0) if shot else 0
  else:
   den=int(shot)
   if key=='shortShotPct':num=100*(shot and x.get('zone')=='short')
   if key=='longShotPct':num=100*(shot and x.get('zone')=='long')
   if key=='fgPct':num=100*(shot and x.get('made',False))
   if key=='sameShooterPct':num=100*(shot and x.get('same',False))
  A[s,v,i,k]+=[num,den]
for si,s in enumerate(p['seasons']):
 for g in real[s]['games']:
  for x in g['rows']:add(si,0,x['teamId'],x)
 valid={g['id'] for g in real[s]['games']}
 for vi,seed in enumerate(p['seeds'],1):
  d=load(r/f'runs/{s}-split-{seed}.json')
  for m,rows in zip(d['matches'],d['postOreb']['games']):
   if m['id'] not in valid:continue
   for x in rows:add(si,vi,m['homeId'] if x['off']==0 else m['awayId'],x)
for si,s in enumerate(p['seasons']):
 for vi,seed in enumerate(p['seeds'],4):
  d=load(f'reports/defense-tenth/step4-rebounds-after/runs/{s}-allocation-{seed}.json');valid={g['id'] for g in real[s]['games']}
  for m,rows in zip(d['matches'],d['postOreb']['games']):
   if m['id'] not in valid:continue
   for x in rows:add(si,vi,m['homeId'] if x['off']==0 else m['awayId'],x)
for si,s in enumerate(p['seasons']):
 for vi,seed in enumerate(p['seeds'],7):
  d=load(f'reports/defense-tenth/step4-rebounds-clock/runs/{s}-calibrated-{seed}.json');valid={g['id'] for g in real[s]['games']}
  for m,rows in zip(d['matches'],d['postOreb']['games']):
   if m['id'] not in valid:continue
   for x in rows:add(si,vi,m['homeId'] if x['off']==0 else m['awayId'],x)
counts=np.array([np.bincount(x,minlength=30) for x in rng.integers(0,30,(B,30))]);sc=np.array([np.bincount(x,minlength=3)/3 for x in rng.integers(0,3,(B,3))]);realDraw=[];simDraw=[];points=[]
for si in range(4):
 rt=np.einsum('bt,tkd->bkd',counts,A[si,0]);st=np.einsum('bt,vtkd->bvkd',counts,A[si,1:4]);stRatio=np.einsum('bv,bvk->bk',sc,st[:,:,:,0]/st[:,:,:,1])
 realDraw.append(rt[:,:,0]/rt[:,:,1]);simDraw.append(stRatio);rs=A[si,0].sum(axis=0);ss=A[si,1:4].sum(axis=1);points.append(np.mean(ss[:,:,0]/ss[:,:,1],axis=0)-rs[:,0]/rs[:,1])
draw=np.mean(simDraw,axis=0)-np.mean(realDraw,axis=0);point=np.mean(points,axis=0);out={key:{'simulationMinusReal':float(point[k]),'joint95':np.quantile(draw[:,k],[.025,.975]).tolist()} for k,key in enumerate(keys)}
allocationDraw=[];allocationPoint=[]
for si in range(4):
 at=np.einsum('bt,vtkd->bvkd',counts,A[si,4:7]);allocationDraw.append(np.einsum('bv,bvk->bk',sc,at[:,:,:,0]/at[:,:,:,1]));ass=A[si,4:7].sum(axis=1);allocationPoint.append(np.mean(ass[:,:,0]/ass[:,:,1],axis=0))
cd=np.mean(simDraw,axis=0)-np.mean(allocationDraw,axis=0);cp=np.mean([np.mean(A[si,1:4].sum(axis=1)[:,:,0]/A[si,1:4].sum(axis=1)[:,:,1],axis=0) for si in range(4)],axis=0)-np.mean(allocationPoint,axis=0)
paired={key:{'point':float(cp[k]),'joint95':np.quantile(cd[:,k],[.025,.975]).tolist()} for k,key in enumerate(keys)}
putbackDraw=[];putbackPoint=[]
for si in range(4):
 pt=np.einsum('bt,vtkd->bvkd',counts,A[si,7:10]);putbackDraw.append(np.einsum('bv,bvk->bk',sc,pt[:,:,:,0]/pt[:,:,:,1]));ps=A[si,7:10].sum(axis=1);putbackPoint.append(np.mean(ps[:,:,0]/ps[:,:,1],axis=0))
pd=np.mean(simDraw,axis=0)-np.mean(putbackDraw,axis=0);pp=np.mean([np.mean(A[si,1:4].sum(axis=1)[:,:,0]/A[si,1:4].sum(axis=1)[:,:,1],axis=0) for si in range(4)],axis=0)-np.mean(putbackPoint,axis=0)
pairedPutback={key:{'point':float(pp[k]),'joint95':np.quantile(pd[:,k],[.025,.975]).tolist()} for k,key in enumerate(keys)}
(r/'event-joint-intervals.json').write_text(json.dumps({'bootstrap':B,'seeds':p['seeds'],'method':'paired franchise and seed across seasons; equal season weight; diagnostic only','metrics':out,'candidateMinusAllocation':paired,'candidateMinusCalibrated':pairedPutback},indent=2));print(json.dumps(out,indent=2))

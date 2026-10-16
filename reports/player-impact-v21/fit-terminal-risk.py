"""Fit event-count shrinkage; no simulated outcomes, OVR, names, or 2025-26 target fit."""
import json, hashlib, math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
ROOT=Path('reports/player-impact-v21')
SEASONS=['2022-23','2023-24','2024-25','2025-26']
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources={s:read(ROOT/f'{s}-terminal-events.json') for s in SEASONS}
datasets={}
for season,src in sources.items():
 rows=np.array([[*r,g['fold']] for g in src['games'] for r in g['rows']],dtype=float)
 ids=np.array(sorted(p['playerId'] for p in src['players']),dtype=np.int64)
 ix=np.searchsorted(ids,rows[:,0].astype(np.int64));assert np.all(ids[ix]==rows[:,0])
 datasets[season]=(src,rows,ids,ix)

def counts(rows,ix,size,mask):
 n=np.bincount(ix[mask],rows[mask,1],minlength=size)
 d=np.bincount(ix[mask],rows[mask,2],minlength=size)
 l=np.bincount(ix[mask],rows[mask,3],minlength=size)
 w=np.bincount(ix[mask],rows[mask,1]*rows[mask,4],minlength=size)
 return n,d,l,w

folds=[]
for s in SEASONS[:3]:
 src,r,ids,ix=datasets[s]
 for f in range(5):
  test=r[:,5]==f;n,d,l,w=counts(r,ix,len(ids),~test)
  folds.append((s,f,n,d,l,w,r[test],ix[test]))

def score(kappa,detail=False):
 losses=[]
 for season,fold,n,d,l,w,r,ix in folds:
  qd=(d+kappa*d.sum()/n.sum())/(n+kappa)
  ql=(l+kappa*l.sum()/w.sum())/(w+kappa)
  pd=qd[ix];pl=ql[ix]*r[:,4];po=1-pd-pl
  if np.any(po<=0):return 1e100
  loss=-float(np.sum(r[:,2]*np.log(pd)+r[:,3]*np.log(pl)+(r[:,1]-r[:,2]-r[:,3])*np.log(po)))
  losses.append({'season':season,'fold':fold,'nll':loss,'events':int(r[:,1].sum())})
 return losses if detail else sum(x['nll'] for x in losses)

fit=minimize_scalar(lambda x:score(math.exp(x)),bounds=(math.log(.001),math.log(100000)),method='bounded',options={'xatol':1e-7})
assert fit.success
kappa=math.exp(fit.x)
f=ROOT/'terminal-risk-prior.json'
if f.exists():raise RuntimeError('Preserve prior fit')
hashes={str(ROOT/f'{s}-terminal-events.json'):sha(ROOT/f'{s}-terminal-events.json') for s in SEASONS}
hashes[str(ROOT/'fit-terminal-risk.py')]=sha(ROOT/'fit-terminal-risk.py')
output={'kappaEvents':kappa,'fitSeasons':SEASONS[:3],'excludedFitSeason':'2025-26','folds':5,'design':'Whole-game folds by numeric game ID mod 5. Minimize held-out categorical negative log likelihood of dead turnover, live non-pass turnover, other terminal event. Each source event uses actual opponent lineup pressure. Dead risk is (dead+kappa*leagueDead)/(N+kappa); neutral live risk is (live+kappa*leagueLive)/(sumNPressure+kappa). One shared prior strength, not fitted to player names, ranks, team wins, simulation errors or on/off. Source full-season defender STL covariate includes held-out games: conditional reconstruction, not prospective accuracy. 2025-26 source counts used only for its final descriptive cards.','nll':{'fitted':score(kappa),'nearUnshrunk':score(.001),'pooledApprox':score(100000)},'foldScores':score(kappa,True),'sourceHashes':hashes,'references':{}}
for season,(src,r,ids,ix) in datasets.items():
 n,d,l,w=counts(r,ix,len(ids),np.ones(len(r),dtype=bool));pd=d.sum()/n.sum();pl=l.sum()/w.sum()
 qd=(d+kappa*pd)/(n+kappa);ql=(l+kappa*pl)/(w+kappa)
 # Runtime pressure is bounded [0.4,1.8]. Reject invalid extrapolation, never silently clip.
 assert np.all(qd+ql*1.8<.95)
 cards={str(int(pid)):{'opportunities':int(n[i]),'dead':int(d[i]),'live':int(l[i]),'pressureWeightedOpportunities':float(w[i]),'deadProbability':float(qd[i]),'neutralLiveProbability':float(ql[i])} for i,pid in enumerate(ids)}
 reference={'deadProbability':float(pd),'neutralLiveProbability':float(pl),'kappaEvents':kappa}
 output['references'][season]=reference
 target=ROOT/f'{season}-terminal-risk.json'
 if target.exists():raise RuntimeError('Preserve source cards')
 target.write_text(json.dumps({'season':season,'reference':reference,'cards':cards,'sourceCounts':src['totals'],'sourceHash':hashes[str(ROOT/f'{season}-terminal-events.json')],'fitCodeHash':hashes[str(ROOT/'fit-terminal-risk.py')]},indent=2),encoding='utf-8')
 print(season,'N',int(n.sum()),'dead',int(d.sum()),'live',int(l.sum()),'prior',reference,flush=True)
f.write_text(json.dumps(output,indent=2),encoding='utf-8')
print('FIT',kappa,output['nll'],flush=True)

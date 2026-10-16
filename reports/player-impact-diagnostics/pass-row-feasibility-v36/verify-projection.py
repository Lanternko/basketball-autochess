"""Independent dual, column-first log-space solution for the masked 6x5 prior."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
R=Path('reports/player-impact-diagnostics/pass-row-feasibility-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[R/'prototype-verification.json',R/'source-prototype-verification.json'];samples=[]
for f in files:
 d=read(f);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
 samples+=d['samples']
maximum=0.
for s in samples:
 k=np.array(s['prior']);rows=np.array(s['rows']);cols=np.array(s['columns']);support=k>0;lk=np.full(k.shape,-np.inf);lk[support]=np.log(k[support]);u=np.zeros(6);v=np.zeros(5);converged=False
 for iteration in range(20000):
  v=np.log(cols)-logsumexp(lk+u[:,None],axis=0)
  u=np.log(rows)-logsumexp(lk+v[None,:],axis=1)
  joint=np.exp(lk+u[:,None]+v[None,:])
  if max(np.max(np.abs(joint.sum(axis=0)-cols)),np.max(np.abs(joint.sum(axis=1)-rows)))<1e-12:
   converged=True;break
 assert converged
 actual=np.array(s['joint']);maximum=max(maximum,float(np.max(np.abs(actual-joint))));assert np.max(np.abs(actual-joint))<1e-9
 assert np.all(actual[5]>0) and np.all(actual[support]>0) and np.all(actual[~support]==0)
 assert np.max(np.abs(actual.sum(axis=0)-cols))<1e-8 and np.max(np.abs(actual.sum(axis=1)-rows))<1e-8
out={'passed':True,'sampledSourceAndMean70Matrices':len(samples),'maxAbsoluteDifferenceToIndependentDualSolve':maximum,'scope':'Independent masked transport solve, positive own support, unchanged passer rows and conserved finisher columns. Source non-strict cases, engine, full-game and OVR still unimplemented/unverified.','hashes':{str(p).replace('\\','/'):sha(p) for p in [*files,R/'verify-projection.py']}}
(R/'projection-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

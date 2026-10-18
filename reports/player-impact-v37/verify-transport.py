"""Independent column-first log-space solves of strict and non-strict matrices."""
import hashlib,json
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.special import logsumexp
R=Path('reports/player-impact-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(R/'transport-samples.json');maximum=0.;counts=Counter()
for s in d['samples']:
 k=np.array(s['prior']);actual=np.array(s['joint']);cols=np.array(s['terminal']);counts[s['branch']]+=1
 if s['branch']=='fixed-pass-rows':
  rows=np.array([*s['oldRows'],s['ownPool']]);support=k>0;lk=np.full(k.shape,-np.inf);lk[support]=np.log(k[support]);u=np.zeros(6);v=np.zeros(5);converged=False
  for iteration in range(20000):
   v=np.log(cols)-logsumexp(lk+u[:,None],axis=0)
   u=np.log(rows)-logsumexp(lk+v[None,:],axis=1)
   expected=np.exp(lk+u[:,None]+v[None,:])
   if max(np.max(np.abs(expected.sum(axis=0)-cols)),np.max(np.abs(expected.sum(axis=1)-rows)))<1e-12:converged=True;break
  assert converged and np.max(np.abs(actual.sum(axis=1)-rows))<1e-8
  assert np.all(actual[5]>0) and np.all(actual[support]>0) and np.all(actual[~support]==0)
 else:
  assert s['branch']=='relaxed-source-columns'
  ms=s['measurements'];recv=np.array([m['receiveOpportunityRate'] for m in ms]);p=np.array([m['passOpportunityRate'] for m in ms]);selfrate=np.array([m['selfOpportunityRate'] for m in ms])
  independent=p[:,None]*recv[None,:]/(recv.sum()-recv[:,None]);np.fill_diagonal(independent,selfrate);assert np.max(np.abs(independent-k))<1e-12
  expected=np.exp(np.log(independent)-logsumexp(np.log(independent),axis=0)[None,:]+np.log(cols)[None,:]);assert np.all(actual>0)
 maximum=max(maximum,float(np.max(np.abs(actual-expected))));assert np.max(np.abs(actual-expected))<1e-9 and np.max(np.abs(actual.sum(axis=0)-cols))<1e-8
assert counts['fixed-pass-rows']>100 and counts['relaxed-source-columns']>0
files=[R/'transport-samples.json',R/'verify-transport.py',R/'model.mjs']
out={'passed':True,'sampledLineups':len(d['samples']),'branchSamples':dict(counts),'maxAbsoluteDifferenceToIndependentLogSpaceSolve':maximum,'scope':'Independent masked own-pool projection with fixed passer rows, and independent unfitted source-column projection for non-strict inputs. No accuracy certification.','hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(R/'transport-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

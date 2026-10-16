"""Independently solve sampled transport in log-space and verify kernel construction."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
R=Path('reports/player-impact-v35');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(R/'transport-samples.json');assert len(d['samples'])>=180
for p,h in d['hashes'].items():assert sha(p)==h,p
maxError=0;below=0;above=0
for sample in d['samples']:
 m=sample['measurements'];terminal=np.array([x['terminalOpportunityRate'] for x in m]);own=np.array([x['selfOpportunityRate'] for x in m]);passing=np.array([x['passOpportunityRate'] for x in m]);received=np.array([x['receiveOpportunityRate'] for x in m])
 creator=(own+passing)*terminal.sum()/(own+passing).sum()
 kernel=np.zeros((5,5))
 for i in range(5):
  for j in range(5):kernel[i,j]=own[i] if i==j else passing[i]*received[j]/(received.sum()-received[i])
 assert np.allclose(kernel,sample['kernel'],rtol=1e-12,atol=1e-12);assert np.allclose(creator,sample['creator'],rtol=1e-12,atol=1e-12)
 lk=np.log(kernel);alpha=np.zeros(5);beta=np.zeros(5)
 for _ in range(10000):
  # Column-first dual updates differ from JS row-first primal scaling.
  beta=np.log(terminal)-logsumexp(lk+alpha[:,None],axis=0)
  alpha=np.log(creator)-logsumexp(lk+beta[None,:],axis=1)
  joint=np.exp(lk+alpha[:,None]+beta[None,:])
  if np.max(np.abs(joint.sum(axis=0)-terminal))<1e-13:break
 else:raise AssertionError('Independent dual iteration failed')
 error=float(np.max(np.abs(joint-np.array(sample['joint']))));assert error<1e-8;maxError=max(maxError,error)
 assert np.all(joint>0);assert np.allclose(joint.sum(axis=1),creator,atol=1e-10);assert np.allclose(joint.sum(axis=0),terminal,atol=1e-10)
 kl=lambda a:float(np.sum(a*(np.log(a)-lk)-a+kernel))
 alternative=creator[:,None]*terminal[None,:]/terminal.sum()
 assert kl(joint)<=kl(alternative)+1e-10
 below+=int((joint.diagonal()<own-1e-8).sum());above+=int((joint.diagonal()>own+1e-8).sum())
assert below and above
out={'passed':True,'sampledLineups':len(d['samples']),'maxAbsoluteDifferenceToIndependentLogSpaceSolve':maxError,'selfBelowSourceCases':below,'selfAboveSourceCases':above,'scope':'Kernel, marginals, positive own support, independent dual numerical solve and feasible alternative objective. Sampled arithmetic audit only, not source roles as causal capabilities. All source-five marginal checks are separate in source-verification.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'transport-samples.json',R/'verify-transport.py',R/'model.mjs']}}
f=R/'transport-verification.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

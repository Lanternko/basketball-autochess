"""Independently reconstruct the terminal-column KL projection in log space."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();d=read(R/'transport-samples.json');k=read(R/'marked-fit.json')['selfScale'];maximum=0.
for s in d['samples']:
 ms=s['measurements'];v=np.array([m['receiveOpportunityRate'] for m in ms]);p=np.array([m['passOpportunityRate'] for m in ms]);selfrate=np.array([m['selfOpportunityRate'] for m in ms]);t=np.array(s['terminal'])
 prior=p[:,None]*v[None,:]/(v.sum()-v[:,None]);np.fill_diagonal(prior,selfrate)
 assert np.max(np.abs(prior-np.array(s['kernel'])))<1e-12 and s['selfScale']==k
 scaled=prior.copy();scaled[np.diag_indices(5)]*=k
 logs=np.log(scaled);expected=np.exp(logs-logsumexp(logs,axis=0)[None,:]+np.log(t)[None,:]);actual=np.array(s['joint'])
 maximum=max(maximum,float(np.max(np.abs(expected-actual))));assert np.max(np.abs(expected-actual))<1e-10
 assert np.all(actual>0) and np.max(np.abs(actual.sum(axis=0)-t))<1e-10
 # KKT: one common scale per receiver column, no imposed creator row total.
 ratios=actual/scaled;assert np.max(np.ptp(ratios,axis=0))<1e-10
 def kl(x):return np.sum(x*np.log(x/scaled)-x+scaled)
 feasible=np.ones((5,1))*t[None,:]/5;assert kl(actual)<=kl(feasible)+1e-9
files=[R/'transport-samples.json',R/'marked-fit.json',R/'verify-transport.py',R/'model.mjs']
out={'passed':True,'sampledLineups':len(d['samples']),'maxAbsoluteDifferenceToIndependentLogSpaceSolve':maximum,'selfScale':k,'terminalColumnsAndPositiveOwnSupport':True,'scope':'Positive source prior projected only to terminal columns; creator rows are not constrained. Deterministic source/mean70 diagnostic sample, no accuracy certification.','hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(R/'transport-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

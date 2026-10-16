"""Verify the support criterion with a separate linear program, not Sinkhorn."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
R=Path('reports/player-impact-diagnostics/pass-row-feasibility-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=read(R/'audit.json');mean=read('reports/player-impact-v36/flow-audit.json')['mean70'];samples=[]
for p in mean:samples.append({'tag':{'mean70Subject':p['playerId']},'terminal':[q['terminal'] for q in p['rows']],'passerRows':[q['previousPass'] for q in p['rows']]})
for s in audit['seasons']:
 for p in s['exceptions']:samples.append({'tag':{'season':s['season'],'gameId':p['gameId'],'teamId':p['teamId'],'startIndex':p['startIndex']},'terminal':p['terminal'],'passerRows':p['passerRows']})
edges=[(i,j) for i in range(6) for j in range(5) if i==5 or i!=j];constraints=[]
for i in range(6):constraints.append([int(a==i) for a,b in edges]+[0])
for j in range(5):constraints.append([int(b==j) for a,b in edges]+[0])
A=np.array(constraints,float);B=np.zeros((len(edges),len(edges)+1))
for k in range(len(edges)):B[k,k]=-1;B[k,-1]=1
details=[];feasible=0
for s in samples:
 t=np.array(s['terminal']);r=np.array(s['passerRows']);own=float(t.sum()-r.sum());assert own>=-1e-12
 own=max(0,own);margins=np.r_[r,own,t];tol=1e-10*max(1,t.sum());strict=own>tol and min(t.sum()-t-r)>tol
 objective=np.zeros(len(edges)+1);objective[-1]=-1
 solved=linprog(objective,A_ub=B,b_ub=np.zeros(len(edges)),A_eq=A,b_eq=margins,bounds=[(0,None)]*(len(edges)+1),method='highs')
 assert solved.success,solved.message
 eps=solved.x[-1];assert np.max(np.abs(A@solved.x-margins))<1e-7
 if strict:assert eps>1e-9;feasible+=1
 else:assert abs(eps)<1e-8
 details.append({'tag':s['tag'],'strictHallFeasible':bool(strict),'maxCommonPositiveEdgeMass':eps})
files=[R/'audit.json',R/'audit.mjs',R/'verify.py',Path('reports/player-impact-v36/flow-audit.json')]
out={'passed':True,'allMean70Subjects':len(mean),'sourceNonStrictExceptions':len(samples)-len(mean),'linearProgramsSolved':len(samples),'strictlyFeasibleCases':feasible,'scope':'Independent LP max-min support checks, 582 natural-role mean70 lineups plus all non-strict source exceptions with unsupported marks. Does not choose the eventual allocation prior or prove simulated accuracy. No runtime changes.',
 'samples':details,'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(R/'lp-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k not in ['samples','hashes']},indent=2))

"""Independent rowwise likelihood/gradient reconstruction, without fitter helpers."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.special import expit
ROOT=Path('reports/player-impact-v42');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
selection=read(ROOT/'choice-selection.json');source={};checks=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 d=read(f'reports/player-impact-v40/{season}-fga-data.json');lookup={p['playerId']:i for i,p in enumerate(d['players'])};rows=d['rows'];k=len(lookup)
 for r in rows:assert r[1]==int(hashlib.sha256(r[0].encode()).hexdigest()[:8],16)%5
 source[season]={'k':k,'own':np.array([lookup[r[3]] for r in rows]),'ds':np.array([[lookup[p] for p in r[5]] for r in rows]),'n':np.array([r[6] for r in rows],float),'zone':np.array([r[2] for r in rows]),'fold':np.array([r[1] for r in rows])}
for f in sorted((ROOT/'choice-fits').glob('*.json')):
 fit=read(f);d=source[fit['season']];k=d['k'];fold=fit['fold'];sigma=fit['sigma']
 for branch in fit['branches']:
  zone=d['zone'];mask=np.ones(len(zone),bool) if branch['branch']=='three' else zone!=0
  target=zone==0 if branch['branch']=='three' else zone==2
  test=mask&(np.ones(len(zone),bool) if fold is None else d['fold']==fold);train=mask&(np.ones(len(zone),bool) if fold is None else d['fold']!=fold)
  a=np.array(branch['shooterLogits']);b=np.array(branch['defenderLogits']);eta=branch['intercept']+a[d['own']]+b[d['ds']].sum(axis=1)
  nll=float(np.sum(d['n'][test]*(np.logaddexp(0,eta[test])-target[test]*eta[test])));assert abs(nll-branch['nll'])<1e-6,(f,branch['branch'],nll,branch['nll'])
  residual=d['n'][train]*(expit(eta[train])-target[train]);mu=float(np.sum(d['n'][train]*target[train])/np.sum(d['n'][train]));base=np.log(mu/(1-mu))
  ownGrad=np.bincount(d['own'][train],weights=residual,minlength=k)+.5*(expit(base+a)-mu)
  defGrad=np.bincount(d['ds'][train].ravel(),weights=np.repeat(residual,5),minlength=k)+b/sigma**2 if sigma else np.zeros(k)
  maxgrad=max(float(np.max(abs(ownGrad))),float(np.max(abs(defGrad))),abs(float(residual.sum())));assert maxgrad<=.0011,(f,maxgrad)
  checks.append({'file':str(f).replace('\\','/'),'branch':branch['branch'],'nll':nll,'maxGradient':maxgrad})
for branch in ['three','paintGivenTwo']:
 table=[]
 for sigma in [0,.05,.1,.2]:
  files=[read(f) for f in (ROOT/'choice-fits').glob('*.json') if read(f)['season']!='2025-26' and read(f)['fold'] is not None and read(f)['sigma']==sigma]
  assert len(files)==15
  bs=[next(b for b in doc['branches'] if b['branch']==branch) for doc in files];table.append({'sigma':sigma,'nll':sum(b['nll'] for b in bs),'trials':sum(b['testTrials'] for b in bs)})
 minimum=min(r['nll']/r['trials'] for r in table);selected=min(r['sigma'] for r in table if r['nll']/r['trials']<=minimum+1e-10);assert selection['selectedSigma'][branch]==selected
for filename in ['select-fit-hashes.json','final-fit-hashes.json']:
 for p,h in read(ROOT/filename).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
target=[]
for branch in ['three','paintGivenTwo']:
 values=[]
 for sigma in sorted({0,selection['selectedSigma'][branch]}):
  docs=[read(ROOT/'choice-fits'/f'2025-26-sigma{sigma}-fold{fold}.json') for fold in range(5)];bs=[next(b for b in d['branches'] if b['branch']==branch) for d in docs];values.append({'sigma':sigma,'nll':sum(b['nll'] for b in bs),'trials':sum(b['testTrials'] for b in bs)})
 target.append({'branch':branch,'scores':values})
out={'passed':True,'independentRowwiseNllAndGradient':True,'wholeGameFoldRebuilt':True,'olderOnlySelectionVerified':True,'sourceHashesPassed':True,'checks':checks,'targetHeldoutDiagnosticNotSelection':target}
(ROOT/'choice-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'passed':True,'branchesChecked':len(checks),'targetHeldout':target}),flush=True)

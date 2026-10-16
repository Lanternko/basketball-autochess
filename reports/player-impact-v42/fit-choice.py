import json, sys, hashlib, importlib.util
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from scipy import sparse
from scipy.special import expit, logit

ROOT=Path('reports/player-impact-v42')
spec=importlib.util.spec_from_file_location('make_fitlib','reports/player-impact-v40/fitlib.py')
lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
_cache={}
def data(season):
 if season in _cache:return _cache[season]
 doc=json.loads(Path(f'reports/player-impact-v40/{season}-fga-data.json').read_text(encoding='utf-8'))
 ids=[p['playerId'] for p in doc['players']];lookup={p:i for i,p in enumerate(ids)};k=len(ids)
 groups={}
 for gid,fold,z,pid,own,defenders,n,m in doc['rows']:
  key=(gid,fold,pid,tuple(defenders));r=groups.setdefault(key,[0,0,0]);r[z]+=n
 keys=list(groups);counts=np.array(list(groups.values()),float);own=np.array([lookup[r[2]] for r in keys]);ds=np.array([[lookup[p] for p in r[3]] for r in keys]);n=len(keys)
 x=sparse.csr_matrix((np.ones(n*7),(np.repeat(np.arange(n),7),np.column_stack([own,k+ds,np.full(n,2*k)]).ravel())),shape=(n,2*k+1))
 result={'ids':ids,'k':k,'x':x,'x0':x[:,list(range(k))+[2*k]],'counts':counts,'folds':np.array([r[1] for r in keys])}
 _cache[season]=result;return result

def task(job):
 season,sigma,fold=job;d=data(season);out=[]
 for branch in ['three','paintGivenTwo']:
  n=d['counts'].sum(axis=1) if branch=='three' else d['counts'][:,1:].sum(axis=1)
  b=d['counts'][:,0] if branch=='three' else d['counts'][:,2]
  train=(n>0)&(np.ones(len(n),bool) if fold is None else d['folds']!=fold)
  test=(n>0)&(np.ones(len(n),bool) if fold is None else d['folds']==fold)
  mu=b[train].sum()/n[train].sum();matrix=d['x'] if sigma else d['x0']
  t={'x':matrix[train],'n':n[train],'b':b[train],'mu':mu,'nu':.5,'base':float(logit(mu)),'k':d['k'],'sigma':sigma}
  params,diagnostic=lib.fit(t);eta=matrix[test]@params;nll=float(np.sum(n[test]*np.logaddexp(0,eta)-b[test]*eta))
  assert np.isfinite(nll)
  out.append({'branch':branch,'intercept':float(params[-1]),'shooterLogits':params[:d['k']].tolist(),'defenderLogits':params[d['k']:2*d['k']].tolist() if sigma else [0.]*d['k'],'trainingTrials':int(n[train].sum()),'testTrials':int(n[test].sum()),'nll':nll,'fit':diagnostic})
 return {'season':season,'sigma':sigma,'fold':fold,'playerIds':d['ids'],'branches':out}

def main():
 protocol=json.loads((ROOT/'protocol.json').read_text(encoding='utf-8'));seasons=protocol['seasons'];grid=[0,.05,.1,.2]
 directory=ROOT/'choice-fits';directory.mkdir(exist_ok=True)
 path=lambda j:directory/f'{j[0]}-sigma{j[1]}-fold{j[2]}.json'
 stage=sys.argv[1]
 if stage=='select':jobs=[(s,sigma,fold) for s in seasons[:3] for sigma in grid for fold in range(5)]
 else:
  selected=json.loads((ROOT/'choice-selection.json').read_text(encoding='utf-8'))['selectedSigma']
  jobs=[(s,sigma,None) for s in seasons for sigma in sorted(set(selected.values()))]+[('2025-26',sigma,fold) for sigma in sorted({0,*selected.values()}) for fold in range(5)]
 with ProcessPoolExecutor(max_workers=4) as pool:
  pending={pool.submit(task,j):j for j in jobs if not path(j).exists()}
  for i,future in enumerate(as_completed(pending),1):
   j=pending[future];result=future.result();path(j).write_text(json.dumps(result),encoding='utf-8');print(json.dumps({'stage':stage,'done':i,'pending':len(pending),'job':j}),flush=True)
 if stage=='select':
  tables={};selected={}
  for branch in ['three','paintGivenTwo']:
   table=[]
   for sigma in grid:
    rows=[next(b for b in json.loads(path(j).read_text(encoding='utf-8'))['branches'] if b['branch']==branch) for j in jobs if j[1]==sigma]
    table.append({'sigma':sigma,'nll':sum(r['nll'] for r in rows),'trials':sum(r['testTrials'] for r in rows)})
   minimum=min(r['nll']/r['trials'] for r in table);selected[branch]=min(r['sigma'] for r in table if r['nll']/r['trials']<=minimum+1e-10);tables[branch]=table
  (ROOT/'choice-selection.json').write_text(json.dumps({'selectedSigma':selected,'olderOnlyScores':tables},indent=2),encoding='utf-8');print(json.dumps(selected),flush=True)
 else:
  assembled=[]
  for season in seasons:
   branches=[];ids=None
   for branch,sigma in selected.items():
    doc=json.loads(path((season,sigma,None)).read_text(encoding='utf-8'));ids=doc['playerIds'] if ids is None else ids;assert ids==doc['playerIds'];branches.append(next(b for b in doc['branches'] if b['branch']==branch))
   assembled.append({'season':season,'playerIds':ids,'branches':branches})
  (ROOT/'choice-fit.json').write_text(json.dumps({'seasons':assembled,'selectedSigma':selected}),encoding='utf-8')
 hashes={str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'protocol.json',ROOT/'fit-choice.py',Path('reports/player-impact-v40/fitlib.py'),*[Path(f'reports/player-impact-v40/{s}-fga-data.json') for s in seasons]]}
 (ROOT/f'{stage}-fit-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
if __name__=='__main__':main()

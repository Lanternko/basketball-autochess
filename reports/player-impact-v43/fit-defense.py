"""Convex heavy-tail shrinkage; choose only using older-season heldout games."""
import json,sys,importlib.util,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
from scipy.special import expit
spec=importlib.util.spec_from_file_location('fitlib','reports/player-impact-v40/fitlib.py')
lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
ROOT=Path('reports/player-impact-v43')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
base_loss=lib.loss_gradient;base_hessian=lib.hessian

def loss(params,t):
    value,grad=base_loss(params,t)
    if t['sigma'] and t.get('tail'):
        k=t['k'];d=params[k:2*k];s=t['sigma'];delta=s*t['tail'];r=np.sqrt(1+(d/delta)**2)
        value+=float(np.sum(delta**2*(r-1)/s**2)-np.dot(d,d)/(2*s*s))
        grad[k:2*k]+=d/(s*s*r)-d/(s*s)
    return value,grad

def hessian(params,t):
    h=base_hessian(params,t)
    if t['sigma'] and t.get('tail'):
        k=t['k'];s=t['sigma'];d=params[k:2*k];delta=s*t['tail'];diag=np.zeros(len(params));diag[k:2*k]=((1+(d/delta)**2)**(-1.5)-1)/(s*s)
        h=h+sparse.diags(diag)
    return h.tocsc()

def task(job):
    season,sigma,tail,fold=job
    path=ROOT/'fits'/f'{season}-sigma{sigma:g}-tail{tail:g}-fold{fold}.json'
    if path.exists():return str(path)
    lib.loss_gradient=loss;lib.hessian=hessian
    x=lib.data(season);zones=[]
    for zi,z in enumerate(['long','mid','short']):
        t=lib.prepare(x,zi,fold,sigma);t['tail']=tail
        params,diagnostic=lib.fit(t);raw=x['zones'][zi];test=~t['mask'] if fold is not None else t['mask']
        eta=(raw['x'][test] if sigma else raw['x0'][test])@params
        nll=float(np.sum(raw['n'][test]*np.logaddexp(0,eta)-raw['b'][test]*eta))
        zones.append({'zone':z,'intercept':float(params[-1]),'shooterLogits':params[:x['k']].tolist(),'defenderLogits':params[x['k']:2*x['k']].tolist() if sigma else [0.]*x['k'],'fit':diagnostic,'nll':nll,'evaluatedFga':float(raw['n'][test].sum()),'trainingFga':float(t['n'].sum())})
    path.write_text(json.dumps({'season':season,'sigma':sigma,'tail':tail,'heldoutFold':fold,'playerIds':x['ids'],'zones':zones}),encoding='utf-8')
    return str(path)

if __name__=='__main__':
    (ROOT/'fits').mkdir(exist_ok=True)
    older=['2022-23','2023-24','2024-25']
    # tail=0 is Gaussian. tail=1 is convex pseudo-Huber, quadratic near zero,
    # linear for outliers; no manually identified elite-player class.
    candidates=[(0,0),(.025,0),(.05,0),(.1,0),(.025,1),(.05,1),(.1,1)]
    jobs=[(s,sigma,tail,f) for s in older for sigma,tail in candidates for f in range(5)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i,f in enumerate(as_completed([pool.submit(task,j) for j in jobs])):
            f.result()
            if (i+1)%10==0:print(json.dumps({'phase':'older-selection','done':i+1,'total':len(jobs)}),flush=True)
    cells=[];selected={}
    for z in ['long','mid','short']:
        scores=[]
        for sigma,tail in candidates:
            vals=[next(v for v in read(ROOT/'fits'/f'{s}-sigma{sigma:g}-tail{tail:g}-fold{f}.json')['zones'] if v['zone']==z) for s in older for f in range(5)]
            scores.append({'zone':z,'sigma':sigma,'tail':tail,'nll':sum(v['nll'] for v in vals),'fga':sum(v['evaluatedFga'] for v in vals)})
        best=min(scores,key=lambda v:(v['nll']/v['fga'],v['sigma'],v['tail']));selected[z]={'sigma':best['sigma'],'tail':best['tail']};cells+=scores
    selection={'design':'Older three seasons only; whole-game five-fold heldout binomial NLL. Each zone independently selected. Gaussian and convex pseudo-Huber at prespecified scales; target excluded.','candidates':cells,'selected':selected}
    (ROOT/'selection.json').write_text(json.dumps(selection,indent=2),encoding='utf-8');print(json.dumps(selection),flush=True)
    pairs=set((v['sigma'],v['tail']) for v in selected.values())
    jobs=[(s,a,b,None) for s in older+['2025-26'] for a,b in pairs]+[('2025-26',a,b,f) for a,b in pairs for f in range(5)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(task,j) for j in jobs]):f.result()
    seasons=[]
    for s in older+['2025-26']:
        zones=[]
        for z,choice in selected.items():
            f=read(ROOT/'fits'/f"{s}-sigma{choice['sigma']:g}-tail{choice['tail']:g}-foldNone.json")
            zones.append(next(v for v in f['zones'] if v['zone']==z))
        seasons.append({'season':s,'playerIds':f['playerIds'],'zones':zones})
    (ROOT/'fit.json').write_text(json.dumps({'selected':selected,'seasons':seasons}),encoding='utf-8')

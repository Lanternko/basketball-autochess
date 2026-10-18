"""Receiver-controlled passed-shot production association; never a causal skill label."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

ROOT=Path('reports/player-impact-v30');ROOT.mkdir(exist_ok=True)
SEASONS=['2022-23','2023-24','2024-25','2025-26']
files=[f'reports/player-impact-v21/raw/{s}/passing-pairs-league.json' for s in SEASONS]
hashfile=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
protocol=dict(design=__doc__,trainingSeasons=SEASONS[:3],targetSeason=SEASONS[-1],folds=5,
    foldPolicy='Entire directed team/passer/recipient pair held out together across shot types; deterministic SHA256 first8 digits mod5. Not game/time holdout, no causal teammate independence claim.',
    receiverPrecisionGrid=[5.,20.,80.],passerPrecisionGrid=[5.,20.,80.,320.],
    criterion='Summed held-out binomial negative log likelihood per FGA, training seasons only. Receiver-only null chooses its own precision. 2025-26 only tests preselected hyperparameters. No names, ranks, simulation residuals or on/off fitting.',
    hashes={f:hashfile(f) for f in files}|{str(Path(__file__).as_posix()):hashfile(__file__)})
pf=ROOT/'fit-protocol.json';assert not pf.exists(),'Preserve frozen fit protocol'
pf.write_text(json.dumps(protocol,indent=2),encoding='utf-8')

def data(season,zone):
    doc=json.loads(Path(f'reports/player-impact-v21/raw/{season}/passing-pairs-league.json').read_text(encoding='utf-8'))
    t=next(r for r in doc['data']['resultSets'] if r['name']=='PassesMade')
    rows=[dict(zip(t['headers'],r)) for r in t['rowSet']]
    rows=[r for r in rows if r['PLAYER_ID']!=r['PASS_TEAMMATE_PLAYER_ID'] and r['FG'+zone+'A']>0]
    ids=sorted(set(r['PLAYER_ID'] for r in rows)|set(r['PASS_TEAMMATE_PLAYER_ID'] for r in rows));idx={p:i for i,p in enumerate(ids)}
    a=np.array([idx[r['PLAYER_ID']] for r in rows]);b=np.array([idx[r['PASS_TEAMMATE_PLAYER_ID']] for r in rows])
    y=np.array([r['FG'+zone+'M'] for r in rows],dtype=float);n=np.array([r['FG'+zone+'A'] for r in rows],dtype=float)
    assert np.all(y<=n)
    folds=np.array([int(hashlib.sha256(f"{r['TEAM_ID']}/{r['PLAYER_ID']}/{r['PASS_TEAMMATE_PLAYER_ID']}".encode()).hexdigest()[:8],16)%5 for r in rows])
    return dict(ids=ids,a=a,b=b,y=y,n=n,folds=folds,rows=rows)

def fit(d,mask,receiver_precision,passer_precision):
    a,b,y,n=[d[k][mask] for k in ['a','b','y','n']];size=len(d['ids']);joint=passer_precision is not None
    initial=np.zeros(1+size*(2 if joint else 1));p=y.sum()/n.sum();initial[0]=np.log(p/(1-p))
    def evaluate(v):
        eta=v[0]+v[1+b]
        if joint:eta=eta+v[1+size+a]
        loss=np.sum(n*np.logaddexp(0,eta)-y*eta)+.5*receiver_precision*np.sum(v[1:1+size]**2)
        residual=n*expit(eta)-y
        gradient=np.empty_like(v);gradient[0]=residual.sum()
        gradient[1:1+size]=np.bincount(b,weights=residual,minlength=size)+receiver_precision*v[1:1+size]
        if joint:
            loss+=.5*passer_precision*np.sum(v[1+size:]**2)
            gradient[1+size:]=np.bincount(a,weights=residual,minlength=size)+passer_precision*v[1+size:]
        return loss,gradient
    result=minimize(evaluate,initial,jac=True,method='L-BFGS-B',options=dict(maxiter=1200,ftol=1e-12,gtol=1e-6))
    assert result.success,(result.message,result.fun)
    return result.x

def predict(d,v):
    size=len(d['ids']);eta=v[0]+v[1+d['b']]
    if len(v)>1+size:eta=eta+v[1+size+d['a']]
    return eta

def loss(d,eta,mask):
    return float(np.sum(d['n'][mask]*np.logaddexp(0,eta[mask])-d['y'][mask]*eta[mask]))

datasets={(s,z):data(s,z) for s in SEASONS for z in ['2','3']}
cv=[];chosen={}
for zone in ['2','3']:
    configs=[(kr,kp) for kr in protocol['receiverPrecisionGrid'] for kp in [None,*protocol['passerPrecisionGrid']]]
    for kr,kp in configs:
        scores=[]
        for season in SEASONS[:3]:
            d=datasets[season,zone]
            for fold in range(5):
                test=d['folds']==fold;v=fit(d,~test,kr,kp)
                scores.append(dict(season=season,fold=fold,nll=loss(d,predict(d,v),test),attempts=float(d['n'][test].sum())))
        row=dict(zone=zone,receiverPrecision=kr,passerPrecision=kp,nll=sum(x['nll'] for x in scores),attempts=sum(x['attempts'] for x in scores),foldScores=scores)
        row['nllPerAttempt']=row['nll']/row['attempts'];cv.append(row)
        print(json.dumps({k:v for k,v in row.items() if k!='foldScores'}),flush=True)
    choices=[r for r in cv if r['zone']==zone]
    chosen[zone]={model:min([r for r in choices if (r['passerPrecision'] is not None)==(model=='joint')],key=lambda r:r['nllPerAttempt'])
        for model in ['receiverOnly','joint']}

fits={};target=[]
for season in SEASONS:
    zones={}
    for zone in ['2','3']:
        d=datasets[season,zone];models={}
        for model,choice in chosen[zone].items():
            v=fit(d,np.ones(len(d['n']),dtype=bool),choice['receiverPrecision'],choice['passerPrecision'])
            m=len(d['ids']);models[model]=dict(intercept=float(v[0]),receiverEffects={str(pid):float(v[1+i]) for i,pid in enumerate(d['ids'])},
                passerEffects={str(pid):float(v[1+m+i]) if model=='joint' else 0 for i,pid in enumerate(d['ids'])},
                trainingNll=loss(d,predict(d,v),np.ones(len(d['n']),dtype=bool)),attempts=float(d['n'].sum()))
            if season=='2025-26':
                scores=[];pred=np.zeros(len(d['n']))
                for fold in range(5):
                    test=d['folds']==fold;vv=fit(d,~test,choice['receiverPrecision'],choice['passerPrecision']);eta=predict(d,vv);pred[test]=expit(eta[test])
                    scores.append(dict(fold=fold,nll=loss(d,eta,test),attempts=float(d['n'][test].sum())))
                target.append(dict(zone=zone,model=model,nll=sum(s['nll'] for s in scores),attempts=float(d['n'].sum()),foldScores=scores,
                    predictions=[dict(teamId=r['TEAM_ID'],passerId=r['PLAYER_ID'],receiverId=r['PASS_TEAMMATE_PLAYER_ID'],made=int(y),attempts=int(n),fold=int(f),probability=float(p))
                        for r,y,n,f,p in zip(d['rows'],d['y'],d['n'],d['folds'],pred)]))
        zones[zone]=models
    fits[season]=zones
out=dict(design='Regularized binomial logit: intercept + receiver effect (+ passer effect). Two-point and three-point attempts separate. Source passed-shot association after controlling recipient identity and coarse shot points; does NOT observe shot distance within2pt, defender, openness, dribbles, potential-assist eligibility or causal pass quality. Whole-pair holdouts retain season/team dependencies. No automatic engine adoption.',chosen={z:{m:{k:v for k,v in r.items() if k!='foldScores'} for m,r in v.items()} for z,v in chosen.items()},cv=cv,target=target,fits=fits,protocolSHA256=hashfile(pf))
(ROOT/'passing-fit.json').write_text(json.dumps(out),encoding='utf-8')
for row in target:print(json.dumps({k:v for k,v in row.items() if k not in ['predictions','foldScores']}),flush=True)

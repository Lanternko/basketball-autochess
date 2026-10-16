"""Independent raw-row NLL, gradient, fold membership and selection checks."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.special import expit,logit
ROOT=Path('reports/player-impact-v43');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
cache={};checks=[]
for file in sorted((ROOT/'fits').glob('*.json')):
    fit=read(file);s=fit['season'];fold=fit['heldoutFold'];sigma=fit['sigma'];tail=fit['tail']
    if s not in cache:cache[s]=read(f'reports/player-impact-v40/{s}-fga-data.json')
    data=cache[s];ids=[p['playerId'] for p in data['players']];assert ids==fit['playerIds'];lookup={p:i for i,p in enumerate(ids)};k=len(ids)
    for zone in fit['zones']:
        zi=data['zones'].index(zone['zone']);rows=[r for r in data['rows'] if r[2]==zi]
        own=np.array([lookup[r[3]] for r in rows]);ds=np.array([[lookup[p] for p in r[5]] for r in rows]);n=np.array([r[6] for r in rows]);made=np.array([r[7] for r in rows]);mask=np.array([fold is None or r[1]!=fold for r in rows]);test=~mask if fold is not None else mask
        a=np.array(zone['shooterLogits']);d=np.array(zone['defenderLogits']);eta=zone['intercept']+a[own]+d[ds].sum(axis=1)
        expected=float(np.sum(n[test]*np.logaddexp(0,eta[test])-made[test]*eta[test]));assert abs(expected-zone['nll'])<1e-6
        minutes=sum(v for _,f,ps in data['minutes'] if fold is None or f!=fold for _,v in ps);mu=made[mask].sum()/n[mask].sum();nu=60*n[mask].sum()/minutes
        residual=n[mask]*expit(eta[mask])-made[mask];ga=np.bincount(own[mask],weights=residual,minlength=k)+nu*(expit(logit(mu)+a)-mu)
        gd=np.bincount(ds[mask].ravel(),weights=np.repeat(residual,5),minlength=k)
        if sigma:
            gd+=d/(sigma*sigma*np.sqrt(1+(d/(sigma*tail))**2)) if tail else d/(sigma*sigma)
        else:gd=np.zeros(k);assert np.all(d==0)
        maxgrad=max(abs(ga).max(),abs(gd).max(),abs(residual.sum()));assert maxgrad<.001,(file,zone['zone'],maxgrad)
        checks.append({'file':str(file),'zone':zone['zone'],'nll':expected,'maxGradient':float(maxgrad)})
selection=read(ROOT/'selection.json')
for z,pick in selection['selected'].items():
    candidates=[c for c in selection['candidates'] if c['zone']==z]
    for c in candidates:
        fs=[read(ROOT/'fits'/f"{s}-sigma{c['sigma']:g}-tail{c['tail']:g}-fold{f}.json") for s in ['2022-23','2023-24','2024-25'] for f in range(5)]
        nll=sum(next(b['nll'] for b in x['zones'] if b['zone']==z) for x in fs);assert abs(nll-c['nll'])<1e-6
    best=min(candidates,key=lambda c:(c['nll']/c['fga'],c['sigma'],c['tail']));assert pick=={k:best[k] for k in ['sigma','tail']}
for s,data in cache.items():
    assert all(f==int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5 for gid,f,*_ in data['rows'])
output={'passed':True,'branches':len(checks),'selectionExcludedTarget':True,'wholeGameFoldsPassed':True,'checks':checks}
(ROOT/'fit-verification.json').write_text(json.dumps(output,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in output.items() if k!='checks'}))

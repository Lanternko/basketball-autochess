"""Individual-only, source-season-only opportunity/conversion ablations."""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import math
import numpy as np
from register import HERE, ROOT, SEASONS, sha, dump

def read(f):
    return __import__('json').loads(f.read_text(encoding='utf-8'))

def corr(a,b):
    return float(np.corrcoef(a,b)[0,1]) if len(a)>=3 and np.std(a)>0 and np.std(b)>0 else None

def valid(x):
    return isinstance(x,(int,float)) and math.isfinite(x)

def prepare():
    old=read(ROOT/'reports/defense-tenth/step4-rebounds-talent/features.json')
    seasons,quality={},[]
    for season in SEASONS:
        doc=read(ROOT/f'reports/defense-tenth/step4-rebounds-talent/raw/tracking/{season}-Rebounding.json')
        s=doc['data']['resultSets'][0]
        groups=defaultdict(list)
        for row in s['rowSet']:
            r=dict(zip(s['headers'],row));groups[r['PLAYER_ID']].append(r)
        duplicate=[pid for pid,rs in groups.items() if len(rs)!=1]
        by={pid:rs[0] for pid,rs in groups.items() if len(rs)==1}
        issues=[];rows=[];identity=[]
        for f in old[season]:
            r={k:f[k] for k in ['id','name','season','team','minutes','oreb','rate','pct']}
            t=by.get(r['id'],{})
            m,n,o,d=[t.get(k) for k in ['MIN','OREB_CHANCES','OREB','OREB_CHANCE_DEFER']]
            ok_minutes=valid(m) and m>0
            ok_chance=valid(n) and n>=0
            ok_oreb=valid(o) and o>=0
            raw_ok=ok_chance and n>0 and ok_oreb and o<=n
            adj_ok=raw_ok and valid(d) and 0<=d<=n and n-d>0 and o<=n-d
            r.update(chance36=36*n/m if ok_minutes and ok_chance else None,
                     conversion=o/n if raw_ok else None,
                     adjustedConversion=o/(n-d) if adj_ok else None,
                     trackingMinutes=m if valid(m) else None,
                     trackingChances=n if valid(n) else None,
                     trackingOreb=o if valid(o) else None,
                     trackingDeferred=d if valid(d) else None,
                     trackingReportedConversion=t.get('OREB_CHANCE_PCT'),
                     trackingReportedAdjusted=t.get('OREB_CHANCE_PCT_ADJ'))
            r['missingChance']=int(r['chance36'] is None)
            r['missingConversion']=int(r['conversion'] is None)
            if raw_ok and ok_minutes:
                identity.append(abs(r['chance36']*r['conversion']-36*o/m))
            if t:
                problems=[]
                if not ok_minutes:problems.append('nonpositive_or_invalid_MIN')
                if not ok_chance or not ok_oreb or (ok_chance and ok_oreb and o>n):problems.append('invalid_raw_counts')
                if valid(d) and ok_chance and (d<0 or d>n or (ok_oreb and o>n-d)):problems.append('invalid_adjusted_counts')
                if r['conversion'] is not None and valid(r['trackingReportedConversion']) and abs(r['conversion']-r['trackingReportedConversion'])>0.000501:
                    problems.append('raw_reported_percent_disagrees_with_count_ratio')
                if r['adjustedConversion'] is not None and valid(r['trackingReportedAdjusted']) and abs(r['adjustedConversion']-r['trackingReportedAdjusted'])>0.000501:
                    problems.append('adjusted_reported_percent_disagrees_with_count_ratio')
                if problems:issues.append({'id':r['id'],'name':r['name'],'problems':problems,
                    'MIN':m,'OREB':o,'chances':n,'deferred':d,
                    'reportedRaw':r['trackingReportedConversion'],'reportedAdjusted':r['trackingReportedAdjusted']})
            rows.append(r)
        total=sum(r['minutes'] for r in rows)
        quality.append({'season':season,'players':len(rows),'trackingRows':len(by),'duplicates':duplicate,
            'coverage':{f:{'n':sum(r[f] is not None for r in rows),
                'minuteFraction':sum(r['minutes'] for r in rows if r[f] is not None)/total}
                for f in ['chance36','conversion','adjustedConversion']},
            'trackedMinutes':sum(r['trackingMinutes'] or 0 for r in rows),'boxMinutes':total,
            'trackedMinutesCappedPerPlayerFraction':sum(min(r['minutes'],r['trackingMinutes'] or 0) for r in rows)/total,
            'trackedOreb':sum(r['trackingOreb'] or 0 for r in rows),'boxOreb':sum(r['oreb'] for r in rows),
            'maxProductIdentityError':max(identity,default=None),'issues':issues})
        seasons[season]=rows
    dump(HERE/'personal-inputs.json',seasons)
    dump(HERE/'data-quality.json',quality)
    return seasons

def pair_rows(seasons,source,target,outcome):
    before={r['id']:r for r in seasons[source]}
    rows=[]
    for r in seasons[target]:
        q=before.get(r['id'])
        if q is None or min(q['minutes'],r['minutes'])<100 or q['pct'] is None or q[outcome] is None or r[outcome] is None:
            continue
        rows.append({'id':r['id'],'name':r['name'],'team':r['team'],'season':target,'sourceSeason':source,
            'sourceMinutes':q['minutes'],'targetMinutes':r['minutes'],'y':r[outcome],
            'prior':q[outcome],'priorRate':q['rate'],'priorPct':q['pct'],
            'logMinutes':math.log1p(q['minutes']),'mover':q['team']!=r['team'],
            **{f:q[f] for f in ['chance36','conversion','adjustedConversion','missingChance','missingConversion']}})
    return rows

def columns(model,outcome):
    base=['prior','logMinutes']+(['priorPct'] if outcome=='rate' else [])
    if model=='persistence':return []
    if model=='pctOnly':return ['priorPct','logMinutes']
    if model=='history':return base
    return base+{'chance':['chance36'],'conversion':['conversion'],'both':['chance36','conversion'],
        'adjustedBoth':['chance36','adjustedConversion'],'missingOnly':['missingChance','missingConversion']}[model]

def matrix(rows,cols):
    return np.array([[np.nan if r[f] is None else r[f] for f in cols] for r in rows],dtype=float)

def transform(train,test):
    med=np.array([np.median(v[np.isfinite(v)]) if np.isfinite(v).any() else 0 for v in train.T])
    def impute(a):
        missing=~np.isfinite(a)
        return np.concatenate([np.where(missing,med,a),missing.astype(float)],axis=1)
    a,b=impute(train),impute(test)
    mu,sd=a.mean(0),a.std(0);sd[sd<1e-12]=1
    return (a-mu)/sd,(b-mu)/sd

def ridge_predict(a,b,y,w,ridge):
    aa,bb=transform(a,b)
    aa,bb=np.column_stack([np.ones(len(aa)),aa]),np.column_stack([np.ones(len(bb)),bb])
    sw=np.sqrt(w)
    penalty=np.diag([0]+[ridge]*(aa.shape[1]-1))
    coef=np.linalg.solve((aa*sw[:,None]).T@(aa*sw[:,None])+penalty,(aa*sw[:,None]).T@(y*sw))
    return bb@coef,coef

def fit(train,test,model,outcome,p):
    cols=columns(model,outcome)
    if model=='persistence':return np.array([r['prior'] for r in test]),{'columns':[],'lambda':None}
    a,b=matrix(train,cols),matrix(test,cols)
    y=np.array([r['y'] for r in train]);w=np.array([min(r['targetMinutes'],1000) for r in train],dtype=float);w/=w.mean()
    folds=np.array([int(hashlib.sha256(str(r['id']).encode()).hexdigest(),16)%5 for r in train])
    scores=[]
    for ridge in p['estimator']['grid']:
        errors=np.zeros(len(y))
        for fold in range(5):
            it,iv=folds!=fold,folds==fold
            predicted,_=ridge_predict(a[it],a[iv],y[it],w[it],ridge)
            errors[iv]=(predicted-y[iv])**2
        scores.append((float(np.average(errors,weights=w)),ridge))
    cv,lam=min(scores,key=lambda x:(x[0],-x[1]))
    predicted,coef=ridge_predict(a,b,y,w,lam)
    predicted=np.maximum(predicted,0)
    if outcome=='pct':predicted=np.minimum(predicted,100)
    return predicted,{'columns':cols,'lambda':lam,'CV_MSE':cv,'coefficientsStandardized':coef.tolist(),
        'trainRows':len(train),'testRows':len(test),'trainSources':sorted({r['sourceSeason'] for r in train}),
        'trainTargets':sorted({r['season'] for r in train}),'gridScores':scores}

def point_metrics(rows,pred,outcome):
    seasons=sorted({r['season'] for r in rows});y=np.array([r['y'] for r in rows]);error=pred-y
    minutes=np.array([r['targetMinutes'] for r in rows]);mae=[];mse=[];count=[]
    for season in seasons:
        mask=np.array([r['season']==season for r in rows]);m=minutes[mask];e=error[mask]
        mae.append(float(np.average(abs(e),weights=m)));mse.append(float(np.average(e**2,weights=m)))
        count.append(float(np.mean(abs(e)*m/36)))
    result={'n':len(rows),'seasons':len(seasons),'MAE':float(np.mean(mae)),
        'RMSE':float(np.sqrt(np.mean(mse))),'Pearson':corr(pred,y)}
    if outcome=='rate':result['conditionalCountMAE']=float(np.mean(count))
    return result

def intervals(rows,preds,outcome,p):
    B=p['uncertainty']['replicates'];rng=np.random.default_rng(p['uncertainty']['seed'])
    ids=sorted({r['id'] for r in rows});teams=sorted({r['team'] for r in rows})
    ii={pid:i for i,pid in enumerate(ids)};ti={team:i for i,team in enumerate(teams)}
    draws=rng.integers(0,len(teams),(B,len(teams)))
    fc=np.stack([(draws==i).sum(1) for i in range(len(teams))],axis=1)
    pc=rng.poisson(1,(B,len(ids)))
    weights=(fc[:,[ti[r['team']] for r in rows]]*pc[:,[ii[r['id']] for r in rows]]).astype(float)
    minutes=np.array([r['targetMinutes'] for r in rows]);y=np.array([r['y'] for r in rows])
    seasons=sorted({r['season'] for r in rows});equalweights=np.zeros_like(weights);countweights=np.zeros_like(weights)
    good=np.ones(B,dtype=bool)
    for season in seasons:
        ix=np.flatnonzero([r['season']==season for r in rows]);wm=weights[:,ix]*minutes[ix]
        dm=wm.sum(1);dc=weights[:,ix].sum(1);good&=(dm>0)&(dc>0)
        equalweights[:,ix]=wm/np.maximum(dm[:,None],1e-100)/len(seasons)
        countweights[:,ix]=weights[:,ix]/np.maximum(dc[:,None],1e-100)/len(seasons)
    equalweights,countweights=equalweights[good],countweights[good]
    point,boots={},{}
    for model,pred in preds.items():
        e=pred-y;point[model]=point_metrics(rows,pred,outcome)
        boots[model]={'MAE':equalweights@abs(e),'RMSE':np.sqrt(equalweights@(e**2))}
        if outcome=='rate':boots[model]['conditionalCountMAE']=countweights@(abs(e)*minutes/36)
    pairs={}
    for model in preds:
        for ref in ['persistence','history']:
            if model==ref:continue
            pairs[model+'Minus'+ref[0].upper()+ref[1:]]={}
            for metric in boots[model]:
                delta=boots[model][metric]-boots[ref][metric]
                pairs[model+'Minus'+ref[0].upper()+ref[1:]][metric]={
                    'point':point[model][metric]-point[ref][metric],
                    'joint95':np.quantile(delta,[.025,.975]).tolist(),
                    'jointBonferroni6':np.quantile(delta,[.05/12,1-.05/12]).tolist()}
    return {'versions':point,'paired':pairs,'bootstrapValid':int(good.sum()),'franchises':len(teams)}

def groups(rows):
    return {'all':np.ones(len(rows),dtype=bool),'movers':np.array([r['mover'] for r in rows]),
        'stayers':np.array([not r['mover'] for r in rows]),
        'lowSourceMinutes':np.array([r['sourceMinutes']<500 for r in rows]),
        'both500':np.array([min(r['sourceMinutes'],r['targetMinutes'])>=500 for r in rows])}

def stability(seasons):
    output=[]
    for source,target in zip(SEASONS,SEASONS[1:]):
        prev={r['id']:r for r in seasons[source]}
        pairs=[(prev[r['id']],r) for r in seasons[target] if r['id'] in prev and min(prev[r['id']]['minutes'],r['minutes'])>=100]
        for group in ['all','movers','stayers','both500']:
            selected=[(a,b) for a,b in pairs if group=='all' or (group=='movers' and a['team']!=b['team']) or
                (group=='stayers' and a['team']==b['team']) or (group=='both500' and min(a['minutes'],b['minutes'])>=500)]
            for feature in ['chance36','conversion','adjustedConversion','rate','pct']:
                validpairs=[(a[feature],b[feature]) for a,b in selected if a[feature] is not None and b[feature] is not None]
                output.append({'source':source,'target':target,'group':group,'feature':feature,
                    'n':len(validpairs),'Pearson':corr([a for a,b in validpairs],[b for a,b in validpairs])})
    return output

def run():
    p=read(HERE/'protocol.json');digest=(HERE/'protocol.sha256').read_text(encoding='utf-8').split()[0]
    assert sha(HERE/'protocol.json')==digest
    for f,h in p['inputHashes'].items():assert sha(ROOT/f)==h,f
    lock=HERE/'analysis-code-registration.json'
    if not lock.exists():dump(lock,{'at':datetime.now(timezone.utc).isoformat(),'sha256':sha(HERE/'analyze.py')})
    assert read(lock)['sha256']==sha(HERE/'analyze.py')
    seasons=prepare();dump(HERE/'stability.json',stability(seasons))
    results,fits,predictions={},{},{}
    for outcome in ['rate','pct']:
        pooledrows=[];pooledpred=defaultdict(list)
        for source,target in [('2023-24','2024-25'),('2024-25','2025-26')]:
            train=[]
            for a,b in zip(SEASONS,SEASONS[1:]):
                if b<=source:train+=pair_rows(seasons,a,b,outcome)
            test=pair_rows(seasons,source,target,outcome);label=target+'-'+outcome
            fits[label]={};preds={}
            for model in p['models']:
                preds[model],fits[label][model]=fit(train,test,model,outcome,p)
                pooledpred[model].extend(preds[model].tolist())
            results[label]={}
            for group,mask in groups(test).items():
                rows=[r for r,keep in zip(test,mask) if keep]
                results[label][group]=intervals(rows,{m:v[mask] for m,v in preds.items()},outcome,p) if len(rows)>=10 else {'n':len(rows),'status':'Insufficient group'}
            predictions[label]=[{**r,'predictions':{m:float(v[i]) for m,v in preds.items()}} for i,r in enumerate(test)]
            pooledrows.extend(test)
            print(label,'complete',len(test),flush=True)
        results['pooled-'+outcome]={}
        for group,mask in groups(pooledrows).items():
            rows=[r for r,keep in zip(pooledrows,mask) if keep]
            preds={m:np.array(v)[mask] for m,v in pooledpred.items()}
            results['pooled-'+outcome][group]=intervals(rows,preds,outcome,p) if len(rows)>=10 else {'n':len(rows),'status':'Insufficient group'}
    decision={}
    for model in ['chance','conversion','both']:
        main=results['2025-26-rate']['all']['paired']
        prereq=all(main[model+'Minus'+ref]['MAE']['jointBonferroni6'][1]<0 for ref in ['Persistence','History'])
        rmse=all(main[model+'Minus'+ref]['RMSE']['joint95'][0]<=0 for ref in ['Persistence','History'])
        notworse=True
        for season in ['2024-25','2025-26']:
            for group in ['all','movers']:
                for ref in ['Persistence','History']:
                    notworse &= results[season+'-rate'][group]['paired'][model+'Minus'+ref]['MAE']['joint95'][0]<=0
        decision[model]={'primaryMAEBothReferencesPass':prereq,'RMSEnotSignificantlyWorse':rmse,
            'replicationAndMoversNotSignificantlyWorse':bool(notworse),'supportedDevelopmentIncrement':bool(prereq and rmse and notworse)}
    dump(HERE/'fits.json',fits);dump(HERE/'predictions.json',predictions)
    dump(HERE/'results.json',{'at':datetime.now(timezone.utc).isoformat(),'protocolSHA256':digest,
        'label':p['label'],'uncertainty':p['uncertainty'],'results':results})
    dump(HERE/'decision.json',{'at':datetime.now(timezone.utc).isoformat(),'models':decision,
        'engineAdoption':False,'supportedCandidates':[m for m,x in decision.items() if x['supportedDevelopmentIncrement']]})
    print('Complete. Supported development candidates:',[m for m,x in decision.items() if x['supportedDevelopmentIncrement']],flush=True)

if __name__=='__main__':
    run()

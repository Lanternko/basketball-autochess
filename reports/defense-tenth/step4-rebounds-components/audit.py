"""Integrity and saved-output audit, without new modeling or engine work."""
from datetime import datetime, timezone
import math
import numpy as np
from analyze import read, pair_rows, groups, point_metrics, columns, stability
from register import ROOT, HERE, SEASONS, sha, dump

def main():
    checks=[]
    def check(name,ok,detail=None):
        checks.append({'name':name,'pass':bool(ok),'detail':detail})
    p=read(HERE/'protocol.json');r=read(HERE/'results.json')
    digest=(HERE/'protocol.sha256').read_text(encoding='utf-8').split()[0]
    check('Protocol SHA matches registration and output',sha(HERE/'protocol.json')==digest==r['protocolSHA256'])
    check('Registration code unchanged',sha(HERE/'register.py')==p['registrationCodeSHA256'])
    check('Manifest SHA unchanged',sha(HERE/'protected-before.json')==p['protectedManifestSHA256'])
    lock=read(HERE/'analysis-code-registration.json')
    check('Analysis code unchanged since before outputs',lock['sha256']==sha(HERE/'analyze.py'))
    check('UTC order: protocol then code lock then output',p['registeredAt']<lock['at']<r['at'])
    bad=[f for f,h in p['inputHashes'].items() if not (ROOT/f).is_file() or sha(ROOT/f)!=h]
    check('All registered input hashes unchanged',not bad,{'files':len(p['inputHashes']),'changed':bad})
    protected=read(HERE/'protected-before.json')
    bad=[f for f,h in protected.items() if not (ROOT/f).is_file() or sha(ROOT/f)!=h]
    now={f.relative_to(ROOT).as_posix() for scope in ['src','scripts','reports/defense-tenth']
         for f in (ROOT/scope).rglob('*') if f.is_file() and HERE not in f.parents}
    check('Protected files unchanged',not bad,{'files':len(protected),'changed':bad})
    check('No new files in protected scopes outside this batch',not(now-set(protected)),sorted(now-set(protected)))
    data=read(HERE/'personal-inputs.json');saved=read(HERE/'predictions.json');fits=read(HERE/'fits.json')
    old=read(ROOT/'reports/defense-tenth/step4-rebounds-talent/results.json')['results']
    old_features=read(ROOT/'reports/defense-tenth/step4-rebounds-talent/features.json')
    # Independent source joins: every saved feature must be an exact source-season value.
    leakage=[];source_mismatch=[];metric_errors=[];bounds=[];columns_errors=[]
    for outcome in ['rate','pct']:
        pooled=[]
        for source,target in [('2023-24','2024-25'),('2024-25','2025-26')]:
            label=target+'-'+outcome;rows=saved[label]
            expected=pair_rows(data,source,target,outcome)
            check('Saved cohort matches eligibility '+label,[r['id'] for r in rows]==[r['id'] for r in expected],len(rows))
            source_rows={x['id']:x for x in data[source]}
            target_rows={x['id']:x for x in data[target]}
            old_rows={x['id']:x for x in old_features[source]}
            for row in rows:
                q=source_rows[row['id']];t=target_rows[row['id']];oq=old_rows[row['id']]
                if not(row['sourceSeason']==source and row['season']==target and source<target):leakage.append((label,row['id']))
                for f in ['chance36','conversion','adjustedConversion','missingChance','missingConversion']:
                    if row[f]!=q[f]:source_mismatch.append((label,row['id'],f))
                if not(row['sourceMinutes']==q['minutes'] and row['prior']==q[outcome]
                       and row['priorRate']==oq['rate'] and row['priorPct']==oq['pct']
                       and row['logMinutes']==math.log1p(oq['minutes'])
                       and row['y']==t[outcome] and row['targetMinutes']==t['minutes']):
                    source_mismatch.append((label,row['id'],'history_or_label'))
                if set(row['predictions'])!=set(p['models']):bounds.append((label,row['id'],'model_set'))
                for m,v in row['predictions'].items():
                    if not math.isfinite(v) or v<0 or(outcome=='pct' and v>100):bounds.append((label,row['id'],m))
            for m,fit in fits[label].items():
                if fit['columns']!=columns(m,outcome):columns_errors.append((label,m))
                if m!='persistence':
                    if not(max(fit['trainTargets'])<=source and max(fit['trainSources'])<source):leakage.append((label,m,'train_time'))
                    best=min(fit['gridScores'],key=lambda x:(x[0],-x[1]))
                    if best[1]!=fit['lambda'] or abs(best[0]-fit['CV_MSE'])>1e-12:columns_errors.append((label,m,'CV_selection'))
                    if fit['lambda'] not in p['estimator']['grid']:columns_errors.append((label,m,'grid'))
            pooled.extend(rows)
            for g,mask in groups(rows).items():
                selected=[row for row,keep in zip(rows,mask) if keep]
                z=r['results'][label][g]
                for m in p['models']:
                    computed=point_metrics(selected,np.array([row['predictions'][m] for row in selected]),outcome)
                    if any(abs(computed[k]-z['versions'][m][k])>1e-11 for k in computed if computed[k] is not None):metric_errors.append((label,g,m))
        label='pooled-'+outcome
        for g,mask in groups(pooled).items():
            rows=[row for row,keep in zip(pooled,mask) if keep]
            for m in p['models']:
                computed=point_metrics(rows,np.array([row['predictions'][m] for row in rows]),outcome)
                z=r['results'][label][g]['versions'][m]
                if any(abs(computed[k]-z[k])>1e-11 for k in computed if computed[k] is not None):metric_errors.append((label,g,m))
    check('No future source/training data in saved predictions or fits',not leakage,leakage)
    check('All saved input features match source-season individual data',not source_mismatch,source_mismatch)
    check('Prediction finiteness, bounds and common model cohort',not bounds,bounds)
    check('Feature whitelist and train-only ridge choices',not columns_errors,columns_errors)
    check('All subgroup and equal-season pooled metrics recompute',not metric_errors,metric_errors)
    for outcome in ['rate','pct']:
        errors=[]
        for m,oldm in [('persistence','persistence'),('history','history'),('pctOnly','orebPctOnly')]:
            a=r['results']['2025-26-'+outcome]['all']['versions'][m]
            b=old['cross2025-'+outcome]['all']['versions'][oldm]
            errors.extend((m,k) for k in b if b[k] is not None and abs(a[k]-b[k])>1e-11)
        check('Previous primary baselines reproduced exactly '+outcome,not errors,errors)
    interval_errors=[];diff_errors=[];count_errors=[]
    for label,gs in r['results'].items():
        for g,z in gs.items():
            if z['bootstrapValid']!=20000:count_errors.append((label,g,z['bootstrapValid']))
            for pair,metrics in z['paired'].items():
                m,ref=pair.split('Minus');ref=ref[0].lower()+ref[1:]
                for metric,x in metrics.items():
                    if abs(x['point']-(z['versions'][m][metric]-z['versions'][ref][metric]))>1e-12:diff_errors.append((label,g,pair,metric))
                    for field in ['joint95','jointBonferroni6']:
                        a,b=x[field]
                        if not(math.isfinite(a) and math.isfinite(b) and a<=b):interval_errors.append((label,g,pair,metric,field))
                    if not(x['jointBonferroni6'][0]<=x['joint95'][0] and x['joint95'][1]<=x['jointBonferroni6'][1]):interval_errors.append((label,g,pair,'nested'))
    check('Every interval has 20000 valid paired draws',not count_errors,count_errors)
    check('All paired point differences match saved metrics',not diff_errors,diff_errors)
    check('Interval finiteness, ordering and nested coverage',not interval_errors,interval_errors)
    check('Stability results recompute from individual inputs',read(HERE/'stability.json')==stability(data))
    quality=read(HERE/'data-quality.json')
    check('Tracking product identity holds where defined',all(x['maxProductIdentityError']<1e-12 for x in quality))
    check('Duplicate tracking joins absent',all(not x['duplicates'] for x in quality))
    issues=[x for q in quality for x in q['issues']]
    check('Every flagged adjusted ratio excluded rather than clipped',all(
        next(r for r in data[q['season']] if r['id']==i['id'])['adjustedConversion'] is None
        for q in quality for i in q['issues'] if 'invalid_adjusted_counts' in i['problems']),
        [{'id':i['id'],'problems':i['problems']} for i in issues])
    d=read(HERE/'decision.json');decision_errors=[]
    for m in ['chance','conversion','both']:
        main=r['results']['2025-26-rate']['all']['paired']
        a=all(main[m+'Minus'+ref]['MAE']['jointBonferroni6'][1]<0 for ref in ['Persistence','History'])
        b=all(main[m+'Minus'+ref]['RMSE']['joint95'][0]<=0 for ref in ['Persistence','History'])
        c=all(r['results'][season+'-rate'][g]['paired'][m+'Minus'+ref]['MAE']['joint95'][0]<=0
              for season in ['2024-25','2025-26'] for g in ['all','movers'] for ref in ['Persistence','History'])
        expected={'primaryMAEBothReferencesPass':a,'RMSEnotSignificantlyWorse':b,
                  'replicationAndMoversNotSignificantlyWorse':c,'supportedDevelopmentIncrement':a and b and c}
        if d['models'][m]!=expected:decision_errors.append(m)
    check('Decision follows preregistration without post-hoc exceptions',not decision_errors,decision_errors)
    check('No engine adoption and no passing candidate',not d['engineAdoption'] and not d['supportedCandidates'])
    check('Report rendered', (HERE/'report.md').is_file())
    outputs={f.name:sha(f) for f in HERE.glob('*') if f.is_file() and f.name not in ['completion-audit.json','protected-before.json']}
    result={'at':datetime.now(timezone.utc).isoformat(),'pass':all(x['pass'] for x in checks),
            'protocolSHA256':digest,'checks':checks,'outputHashes':outputs,
            'limits':'No engine simulation, no seed sampling, no train-refit uncertainty. Flagged raw-data issues retained.'}
    dump(HERE/'completion-audit.json',result)
    print('Audit:',result['pass'],len(checks),'checks;',len(protected),'protected files unchanged' if not bad else 'protected-file changes')
    for x in checks:
        if not x['pass']:print('FAILED:',x['name'],str(x['detail'])[:1000])
    if not result['pass']:raise SystemExit(1)

if __name__=='__main__':main()

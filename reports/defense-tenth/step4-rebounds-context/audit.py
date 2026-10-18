"""Audit registration, date gates, source-only traits and immutable old artifacts."""
from datetime import datetime,timezone
import math
import numpy as np
from register import HERE,ROOT,SEASONS,read,dump,sha,table
from analyze import half,echoed_date,metrics

def main():
 checks=[]
 def check(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
 p=read(HERE/'protocol.json');r=read(HERE/'results.json');digest=(HERE/'protocol.sha256').read_text().split()[0]
 check('Protocol SHA unchanged',sha(HERE/'protocol.json')==digest==r['protocolSHA256'])
 check('Registration code unchanged',sha(HERE/'register.py')==p['registerSHA256'])
 check('Manifest intact',sha(HERE/'protected-before.json')==p['protectedSHA256'])
 lock=read(HERE/'analysis-code-registration.json');repair=read(HERE/'analysis-code-repair-1.json')
 check('Initial analysis source preserved',lock['sha256']==repair['initialSHA256']==sha(HERE/'analyze-initial.py'))
 check('Repair analysis source intact',repair['sha256']==sha(HERE/'analyze.py'))
 check('Initial gate outputs preserved',all(sha(HERE/f)==h for f,h in repair['preserved'].items()))
 check('Registration/code/repair precede final result',p['at']<lock['at']<repair['at']<r['at'])
 initial=read(HERE/'data-audit-initial.json')
 check('Initial failure limited to date formatting',all(x['errors'] and all(e['error']=='Echoed date mismatch' for e in x['errors']) for x in initial['seasons']))
 bad=[f for f,h in p['inputHashes'].items() if not (ROOT/f).is_file() or sha(ROOT/f)!=h]
 check('All frozen input hashes unchanged',not bad,{'n':len(p['inputHashes']),'changed':bad})
 protected=read(HERE/'protected-before.json');bad=[f for f,h in protected.items() if not(ROOT/f).is_file() or sha(ROOT/f)!=h]
 check('Protected code and prior reports unchanged',not bad,{'n':len(protected),'changed':bad})
 now={f.relative_to(ROOT).as_posix() for scope in ['src','scripts','reports/defense-tenth'] for f in (ROOT/scope).rglob('*') if f.is_file() and HERE not in f.parents}
 check('No files added outside this batch in protected scopes',not(now-set(protected)),sorted(now-set(protected)))
 fetch=read(HERE/'fetch-manifest.json')
 check('All eight requested acquisitions completed',len(fetch['sources'])==8 and not fetch['failures'])
 fl=read(HERE/'fetch-code-registration.json')
 check('Fetch code unchanged from before acquisition',fl['sha256']==sha(HERE/'fetch.mjs'))
 rawerrors=[]
 for x in fetch['sources']:
  doc=read(ROOT/x['file']);par=doc['data']['parameters']
  if sha(ROOT/x['file'])!=x['sha256']:rawerrors.append((x['season'],x['half'],'hash'))
  if echoed_date(par.get('DateFrom'))!=x['DateFrom'] or echoed_date(par.get('DateTo'))!=x['DateTo']:rawerrors.append((x['season'],x['half'],'dates'))
  if datetime.fromisoformat(doc['fetchedAt'].replace('Z','+00:00'))<datetime.fromisoformat(p['at']):rawerrors.append((x['season'],x['half'],'acquired_before_registration'))
 check('Raw hashes/date windows/time after registration',not rawerrors,rawerrors)
 data=read(HERE/'data-audit.json')
 check('All four seasons pass declared data gate',all(x['usable'] and not x['errors'] for x in data['seasons']))
 check('Every player half-count sum reconciles exactly',all(z['absoluteDifference']==0 for x in data['seasons'] for z in x['reconcile'].values()))
 cutofferrors=[];profileerrors=[];context_errors=[]
 profiles=read(HERE/'prefix-profiles.json');contexts=read(HERE/'lineup-contexts.json');samples=read(HERE/'samples.json')
 for s in SEASONS:
  cfg=p['sources'][s];games={x['GAME_ID']:x['GAME_DATE'][:10] for x in table(ROOT/cfg['teamGames']) if str(x['GAME_ID']).startswith('002')}
  ordered=sorted(games.items(),key=lambda x:(x[1],x[0]));cut=ordered[(len(ordered)-1)//2][1]
  if cut!=cfg['cutoff']:cutofferrors.append(s)
  by={}
  for x in table(ROOT/cfg['playerGames']):
   if x['GAME_ID'] not in games or half(games[x['GAME_ID']],cut)!='first':continue
   q=by.setdefault(str(x['PLAYER_ID']),{'MIN':0,'AST':0,'OREB':0})
   for k in q:q[k]+=x[k] or 0
  if by!=profiles[s]['firstBox']:profileerrors.append((s,'box'))
  tracking={str(x['PLAYER_ID']):x for x in table(HERE/f'raw/{s}-first.json')}
  if tracking!=profiles[s]['firstTracking']:profileerrors.append((s,'tracking'))
 check('Registered median calendar dates recompute',not cutofferrors,cutofferrors)
 check('Prefix profiles contain only corresponding earlier-period counts',not profileerrors,profileerrors)
 for x in samples:
  ca=contexts[x['season']]['first'][str(x['id'])];cb=contexts[x['season']]['second'][str(x['id'])];profile=profiles[x['season']];b=profile['firstBox'][str(x['id'])];t=profile['firstTracking'][str(x['id'])]
  expected={'prior':36*t['OREB_CHANCES']/t['MIN'],'conversion':t['OREB']/t['OREB_CHANCES'],'priorRate':36*b['OREB']/b['MIN'],'logMinutes':math.log1p(b['MIN']),'AST36':36*b['AST']/b['MIN'],'deltaRole':cb['role']-ca['role'],'deltaCompetition':cb['competition']-ca['competition']}
  if any(abs(x[k]-v)>1e-12 for k,v in expected.items()) or x['firstContext']!=ca or x['secondContext']!=cb:context_errors.append((x['season'],x['id']))
 check('Saved predictors source-prefix and context deltas exactly match',not context_errors,context_errors)
 fits=read(HERE/'fits.json');allowed=['prior','logMinutes','AST36'];fiterrors=[]
 for m,z in fits.items():
  cols=allowed+{'history':[],'role':['deltaRole'],'competition':['deltaCompetition'],'both':['deltaRole','deltaCompetition']}[m]
  best=min(z['gridScores'],key=lambda a:(a[0],-a[1]))
  if z['columns']!=cols or z['trainSeasons']!=p['estimator']['train'] or best[1]!=z['lambda'] or best[0]!=z['CV_MSE']:fiterrors.append(m)
 check('Whitelisted individual features and older train seasons only',not fiterrors,fiterrors)
 pred=read(HERE/'predictions.json');perrors=[];metricerrors=[];intervalerrors=[]
 sampleidx={(x['season'],x['id']):x for x in samples}
 for x in pred:
  original=sampleidx[x['season'],x['id']]
  if any(x[k]!=v for k,v in original.items()) or x['season'] not in p['estimator']['test']:perrors.append((x['season'],x['id'],'sample'))
  for m,v in x['predictionsChance'].items():
   if not math.isfinite(v) or v<0 or abs(v*x['conversion']-x['predictionsRate'][m])>1e-12:perrors.append((x['season'],x['id'],m))
  if x['predictionsChance']['chancePersistence']!=x['prior'] or x['predictionsRate']['boxPersistence']!=x['priorRate']:perrors.append((x['season'],x['id'],'baseline'))
 check('Saved forecasts and fixed prefix conversion follow protocol',not perrors,perrors)
 for outcome,ss in r['results'].items():
  for s,gs in ss.items():
   for g,z in gs.items():
    rows=[x for x in pred if (s=='pooled-test' or x['season']==s) and (g=='all' or x['mover'])]
    key='predictionsChance' if outcome=='chance' else 'predictionsRate'
    for m,v in z['versions'].items():
     calc=metrics(rows,np.array([x[key][m] for x in rows]),outcome)
     if any(v[k]!=calc[k] for k in calc):metricerrors.append((outcome,s,g,m))
    if z['bootstrapValid']!=20000:intervalerrors.append((outcome,s,g,'draw_count'))
    for pair,mm in z['paired'].items():
     m,ref=pair.split('Minus');ref=ref[0].lower()+ref[1:]
     for metric,x in mm.items():
      if abs(x['point']-(z['versions'][m][metric]-z['versions'][ref][metric]))>1e-12:intervalerrors.append((pair,'point'))
      for field in ['joint95','jointBonferroni6']:
       if not all(math.isfinite(v) for v in x[field]) or x[field][0]>x[field][1]:intervalerrors.append((pair,field))
      if not(x['jointBonferroni6'][0]<=x['joint95'][0]<=x['joint95'][1]<=x['jointBonferroni6'][1]):intervalerrors.append((pair,'nesting'))
 check('All season/pooled/subgroup metrics recompute',not metricerrors,metricerrors)
 check('20k paired draws and valid point/interval arithmetic',not intervalerrors,intervalerrors)
 decision=read(HERE/'decision.json');derrs=[]
 for m,z in decision['models'].items():
  main=r['results']['rate']['pooled-test']['all']['paired']
  a=all(main[m+'Minus'+ref]['MAE']['jointBonferroni6'][1]<0 for ref in ['BoxPersistence','History'])
  b=r['results']['chance']['pooled-test']['all']['paired'][m+'MinusHistory']['MAE']['joint95'][0]<=0
  c=all(r['results']['rate'][s][g]['paired'][m+'MinusBoxPersistence']['MAE']['joint95'][0]<=0 for s in p['estimator']['test'] for g in ['all','movers'])
  expected={'mainBothReferencesPass':a,'chanceNotWorse':b,'eachSeasonAndMoversNotWorse':c,'insufficientMoverGroup':False,'supported':a and b and c}
  if z!=expected:derrs.append(m)
 check('Decision obeys preregistration',not derrs,derrs)
 check('No passing candidate or engine adoption',not decision['supportedCandidates'] and not decision['engineAdoption'])
 geo=read(HERE/'geometry-inventory.json')
 check('Geometry inventory remains limited to three sampled games per season',len(geo)==12 and all(sum(x['season']==s for x in geo)==3 for s in SEASONS))
 check('Geometry sampled files unchanged',all(sha(ROOT/x['file'])==x['sha256'] for x in geo))
 check('Report present',(HERE/'report.md').is_file())
 output={'at':datetime.now(timezone.utc).isoformat(),'pass':all(x['pass'] for x in checks),'protocolSHA256':digest,'checks':checks,
         'outputHashes':{f.name:sha(f) for f in HERE.glob('*') if f.is_file() and f.name not in ['completion-audit.json','protected-before.json']},
         'limits':'Observed later lineups are oracle conditions. No engine/card changes, simulation seeds, causal identification or train-refit intervals.'}
 dump(HERE/'completion-audit.json',output)
 print('Audit',output['pass'],len(checks),'checks;',len(protected),'protected files')
 for x in checks:
  if not x['pass']:print('FAILED',x['name'],str(x['detail'])[:500])
 if not output['pass']:raise SystemExit(1)
if __name__=='__main__':main()

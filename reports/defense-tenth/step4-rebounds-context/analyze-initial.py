"""Prefix traits, observed lineup contexts, later-period opportunities; no engine."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from collections import defaultdict, Counter
from datetime import datetime, timezone
import math, hashlib
import numpy as np
from register import ROOT,HERE,SEASONS,read,dump,sha,table

def half(date,cutoff):return 'first' if date[:10]<=cutoff else 'second'
def ident(x):return x['id'] if isinstance(x,dict) else x
def corr(a,b):return float(np.corrcoef(a,b)[0,1]) if len(a)>2 and np.std(a)>0 and np.std(b)>0 else None
def ratio(a,b):return a/b if b>0 else None
def geometry(p):
 out=[]
 for s in SEASONS:
  directory=ROOT/('data/defense-a-source' if s=='2025-26' else f'data/defense-seventh/{s}/pbp')
  # The 2025 directory stores game documents alongside its manifest.
  files=sorted(f for f in directory.glob('*.json') if f.stem.startswith('002'))[:3]
  if s=='2025-26' and not files:
   man=read(ROOT/'data/defense-a-source/manifest.json')
   files=[ROOT/x['file'] for x in sorted(man['sources'],key=lambda x:x['id'])[:3]]
  for f in files:
   doc=read(f);a=doc['data']['game']['actions']
   trajectories=[]
   for i,e in enumerate(a):
    for k,v in e.items():
     if isinstance(v,list) and len(v)>=10 and all(isinstance(z,dict) and isinstance(z.get('x'),(int,float)) and isinstance(z.get('y'),(int,float)) for z in v):trajectories.append({'index':i,'field':k})
   out.append({'season':s,'file':f.relative_to(ROOT).as_posix(),'sha256':sha(f),'actions':len(a),
               'actionsWithNumericXY':sum(isinstance(e.get('x'),(int,float)) and isinstance(e.get('y'),(int,float)) for e in a),
               'tenPositionArrays':trajectories,'limitation':'Only three sampled game schemas; event XY does not represent ten-player trajectories.'})
 dump(HERE/'geometry-inventory.json',out)

def prepare(p):
 manifest=read(HERE/'fetch-manifest.json');byjob={(x['season'],x['half']):x for x in manifest['sources']}
 allrows=[];audit=[];exclusions=[];contexts={};prefixes={}
 for s in SEASONS:
  cfg=p['sources'][s];games={x['GAME_ID']:x['GAME_DATE'][:10] for x in table(ROOT/cfg['teamGames']) if str(x['GAME_ID']).startswith('002')}
  box=defaultdict(lambda:Counter());appear=defaultdict(set);names={};teammins=defaultdict(Counter)
  for x in table(ROOT/cfg['playerGames']):
   if x['GAME_ID'] not in games:continue
   h=half(games[x['GAME_ID']],cfg['cutoff']);pid=x['PLAYER_ID'];names[pid]=x['PLAYER_NAME']
   for k in ['MIN','AST','OREB']:box[h,pid][k]+=x[k] or 0
   appear[h,pid].add(x['GAME_ID']);teammins[h,pid][x['TEAM_ID']]+=x['MIN'] or 0
  tracked={};errors=[];jobdetails=[]
  for h in ['first','second']:
   job=byjob.get((s,h))
   if not job:errors.append({'half':h,'error':'No successful acquisition'});continue
   assert sha(ROOT/job['file'])==job['sha256']
   doc=read(ROOT/job['file']);params=doc['data'].get('parameters',{})
   if (params.get('DateFrom') or '')!=job['DateFrom'] or (params.get('DateTo') or '')!=job['DateTo']:
    errors.append({'half':h,'error':'Echoed date mismatch','echoed':[params.get('DateFrom'),params.get('DateTo')]})
   rr=table(ROOT/job['file']);ids=[x['PLAYER_ID'] for x in rr]
   if len(set(ids))!=len(ids):errors.append({'half':h,'error':'Duplicate player rows'})
   tracked[h]={x['PLAYER_ID']:x for x in rr}
   for x in rr:
    if x['GP']>len(appear[h,x['PLAYER_ID']]):errors.append({'half':h,'error':'GP exceeds date-window appearances','id':x['PLAYER_ID'],'trackingGP':x['GP'],'boxGP':len(appear[h,x['PLAYER_ID']])})
   jobdetails.append({'half':h,'rows':len(rr),'trackingMIN':sum(x['MIN'] for x in rr),'boxMIN':sum(z['MIN'] for (hh,pid),z in box.items() if hh==h),'trackingOREB':sum(x['OREB'] for x in rr),'boxOREB':sum(z['OREB'] for (hh,pid),z in box.items() if hh==h)})
  reconcile={}
  if len(tracked)==2:
   full={x['PLAYER_ID']:x for x in table(ROOT/cfg['fullTracking'])}
   for k in ['OREB','OREB_CHANCES']:
    diffs=[{'id':pid,'first':tracked['first'].get(pid,{}).get(k,0),'second':tracked['second'].get(pid,{}).get(k,0),'full':full.get(pid,{}).get(k,0)} for pid in set(full)|set(tracked['first'])|set(tracked['second'])]
    diffs=[x for x in diffs if x['first']+x['second']!=x['full']]
    denom=sum(x[k] for x in full.values());absolute=sum(abs(x['first']+x['second']-x['full']) for x in diffs)
    reconcile[k]={'absoluteDifference':absolute,'fullTotal':denom,'relativeDifference':ratio(absolute,denom),'rows':diffs}
    if absolute>denom*.01:errors.append({'error':'Split/full counts exceed1%','field':k,'relativeDifference':ratio(absolute,denom)})
  record={'season':s,'cutoff':cfg['cutoff'],'games':len(games),'jobs':jobdetails,'errors':errors,'reconcile':reconcile,'usable':not errors}
  audit.append(record)
  if errors:print('Data unusable',s,len(errors),flush=True);continue
  # Prefix-only individual traits. No player plus-minus or team results are read.
  chances={pid:36*x['OREB_CHANCES']/x['MIN'] for pid,x in tracked['first'].items() if x['MIN']>0}
  ast={pid:36*x['AST']/x['MIN'] for (hh,pid),x in box.items() if hh=='first' and x['MIN']>0}
  cm=float(np.median(list(chances.values())));am=float(np.median(list(ast.values())))
  prefixes[s]={'firstTracking':tracked['first'],'firstBox':{str(pid):dict(x) for (h,pid),x in box.items() if h=='first'},'imputeMedians':{'chance36':cm,'AST36':am}}
  aa=read(ROOT/cfg['strictAudit']);bad=set()
  for field in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames']:bad.update(ident(x) for x in aa[field])
  acc=defaultdict(lambda:np.zeros(5));strictgames=set()
  with (ROOT/cfg['stints']).open(encoding='utf-8') as stream:
   for line in stream:
    stint=__import__('json').loads(line);gid=stint['id']
    if gid in bad or gid not in games:continue
    strictgames.add(gid);h=half(games[gid],cfg['cutoff']);sec=stint['seconds']
    if sec<=0:continue
    for t in stint['teams']:
     lineup=t['players'];assert len(lineup)==5 and len(set(lineup))==5
     ar=[ast.get(pid,am) for pid in lineup];cr=[chances.get(pid,cm) for pid in lineup]
     leaders=[i for i,v in enumerate(ar) if v==max(ar)]
     for i,pid in enumerate(lineup):
      acc[h,pid]+=np.array([sec,sec/len(leaders) if i in leaders else 0,sec*(sum(cr)-cr[i]),sec if any(q not in chances for q in lineup if q!=pid) else 0,sec if any(q not in ast for q in lineup) else 0])
  assert len(strictgames)==aa['strictUsableGames'],(s,len(strictgames),aa['strictUsableGames'])
  record['strictGames']=len(strictgames);record['strictCoverage']=len(strictgames)/len(games)
  records={}
  for (h,pid),v in acc.items():
   records[h,pid]={'minutes':v[0]/60,'role':v[1]/v[0],'competition':v[2]/v[0],
                   'imputedChanceMinuteFraction':v[3]/v[0],'imputedASTMinuteFraction':v[4]/v[0]}
  contexts[s]={h:{str(pid):x for (hh,pid),x in records.items() if hh==h} for h in ['first','second']}
  selected=[]
  for pid in sorted(set(tracked['first'])|set(tracked['second'])|set(names)):
   a,b=tracked['first'].get(pid),tracked['second'].get(pid);u,v=box['first',pid],box['second',pid];ca,cb=records.get(('first',pid)),records.get(('second',pid));why=[]
   if not a or not b:why.append('tracking_missing_half')
   if min(u['MIN'],v['MIN'])<p['cohort']['MIN']:why.append('box_MIN_below_threshold')
   if a and b:
    if min(a['MIN'],b['MIN'])<p['cohort']['trackingMIN']:why.append('tracking_MIN_below_threshold')
    if a['OREB_CHANCES']<p['cohort']['firstHalfChances']:why.append('prefix_chances_below_threshold')
    if not(0<=a['OREB']<=a['OREB_CHANCES']):why.append('invalid_prefix_conversion')
    if b['OREB_CHANCES']<0:why.append('invalid_target_chances')
   if not ca or not cb:why.append('strict_context_missing')
   elif min(ca['minutes']/max(u['MIN'],1e-100),cb['minutes']/max(v['MIN'],1e-100))<p['cohort']['strictMinuteFraction']:why.append('strict_context_coverage_below_threshold')
   if why:exclusions.append({'season':s,'id':pid,'name':names.get(pid),'reasons':why});continue
   ta=max(teammins['first',pid],key=teammins['first',pid].get);tb=max(teammins['second',pid],key=teammins['second',pid].get)
   row={'season':s,'id':pid,'name':names[pid],'team':tb,'sourceTeam':ta,'mover':ta!=tb,
        'sourceMinutes':u['MIN'],'targetMinutes':v['MIN'],'prior':36*a['OREB_CHANCES']/a['MIN'],
        'targetChance':36*b['OREB_CHANCES']/b['MIN'],'conversion':a['OREB']/a['OREB_CHANCES'],
        'priorRate':36*u['OREB']/u['MIN'],'targetRate':36*v['OREB']/v['MIN'],
        'logMinutes':math.log1p(u['MIN']),'AST36':ast.get(pid,am),
        'deltaRole':cb['role']-ca['role'],'deltaCompetition':cb['competition']-ca['competition'],
        'firstContext':ca,'secondContext':cb}
   row['y']=row['targetChance']-row['prior'];selected.append(row)
  record['cohort']=len(selected);record['movers']=sum(x['mover'] for x in selected);allrows+=selected
  print('Prepared',s,'strict',len(strictgames),'cohort',len(selected),flush=True)
 dump(HERE/'data-audit.json',{'at':datetime.now(timezone.utc).isoformat(),'seasons':audit,'fetchFailures':manifest['failures']})
 dump(HERE/'prefix-profiles.json',prefixes);dump(HERE/'lineup-contexts.json',contexts);dump(HERE/'cohort-exclusions.json',exclusions);dump(HERE/'samples.json',allrows)
 return allrows,audit

def transform(a,b):
 med=np.median(a,axis=0);a=np.where(np.isfinite(a),a,med);b=np.where(np.isfinite(b),b,med)
 mu,sd=a.mean(0),a.std(0);sd[sd<1e-12]=1
 return np.column_stack([np.ones(len(a)),(a-mu)/sd]),np.column_stack([np.ones(len(b)),(b-mu)/sd])
def ridge(a,b,y,w,lam):
 a,b=transform(a,b);v=np.sqrt(w);penalty=np.diag([0]+[lam]*(a.shape[1]-1))
 coef=np.linalg.solve((a*v[:,None]).T@(a*v[:,None])+penalty,(a*v[:,None]).T@(y*v))
 return b@coef,coef
def fit(train,test,m,p):
 cols=['prior','logMinutes','AST36']+{'history':[],'role':['deltaRole'],'competition':['deltaCompetition'],'both':['deltaRole','deltaCompetition']}[m]
 a=np.array([[x[k] for k in cols] for x in train]);b=np.array([[x[k] for k in cols] for x in test]);y=np.array([x['y'] for x in train]);w=np.array([min(x['targetMinutes'],1000) for x in train],dtype=float);w/=w.mean()
 folds=np.array([int(hashlib.sha256(str(x['id']).encode()).hexdigest(),16)%5 for x in train]);scores=[]
 for lam in p['estimator']['grid']:
  err=np.zeros(len(train))
  for fold in range(5):
   it,iv=folds!=fold,folds==fold;pred,_=ridge(a[it],a[iv],y[it],w[it],lam);err[iv]=(pred-y[iv])**2
  scores.append((float(np.average(err,weights=w)),lam))
 cv,lam=min(scores,key=lambda x:(x[0],-x[1]));delta,coef=ridge(a,b,y,w,lam)
 return np.maximum(0,np.array([x['prior'] for x in test])+delta),{'columns':cols,'lambda':lam,'CV_MSE':cv,'gridScores':scores,'coefficientsStandardized':coef.tolist(),'trainSeasons':sorted({x['season'] for x in train}),'trainN':len(train)}

def metrics(rows,pred,outcome):
 y=np.array([x['targetChance' if outcome=='chance' else 'targetRate'] for x in rows]);e=pred-y;w=np.array([x['targetMinutes'] for x in rows]);ss=sorted({x['season'] for x in rows});mae=[];mse=[]
 for s in ss:
  ix=np.array([x['season']==s for x in rows]);mae.append(float(np.average(abs(e[ix]),weights=w[ix])));mse.append(float(np.average(e[ix]**2,weights=w[ix])))
 return {'n':len(rows),'seasons':len(ss),'MAE':float(np.mean(mae)),'RMSE':float(np.sqrt(np.mean(mse))),'Pearson':corr(pred,y)}
def intervals(rows,preds,outcome,p):
 ids=sorted({x['id'] for x in rows});teams=sorted({x['team'] for x in rows});ii={v:i for i,v in enumerate(ids)};ti={v:i for i,v in enumerate(teams)};B=p['uncertainty']['replicates'];rng=np.random.default_rng(p['uncertainty']['seed'])
 draws=rng.integers(0,len(teams),(B,len(teams)));tc=np.stack([(draws==i).sum(1) for i in range(len(teams))],axis=1);pc=rng.poisson(1,(B,len(ids)))
 weights=(tc[:,[ti[x['team']] for x in rows]]*pc[:,[ii[x['id']] for x in rows]]).astype(float);w=np.array([x['targetMinutes'] for x in rows]);ss=sorted({x['season'] for x in rows});norm=np.zeros_like(weights);good=np.ones(B,dtype=bool)
 for s in ss:
  ix=np.flatnonzero([x['season']==s for x in rows]);wm=weights[:,ix]*w[ix];den=wm.sum(1);good&=den>0;norm[:,ix]=wm/np.maximum(den[:,None],1e-100)/len(ss)
 norm=norm[good];y=np.array([x['targetChance' if outcome=='chance' else 'targetRate'] for x in rows]);points={};boots={}
 for m,pred in preds.items():
  points[m]=metrics(rows,pred,outcome);e=pred-y;boots[m]={'MAE':norm@abs(e),'RMSE':np.sqrt(norm@(e**2))}
 pairs={};refs=['chancePersistence','history'] if outcome=='chance' else ['boxPersistence','history']
 for m in preds:
  for ref in refs:
   if m==ref:continue
   pair=m+'Minus'+ref[0].upper()+ref[1:];pairs[pair]={}
   for metric in ['MAE','RMSE']:
    delta=boots[m][metric]-boots[ref][metric]
    pairs[pair][metric]={'point':points[m][metric]-points[ref][metric],'joint95':np.quantile(delta,[.025,.975]).tolist(),'jointBonferroni6':np.quantile(delta,[.05/12,1-.05/12]).tolist()}
 return {'versions':points,'paired':pairs,'bootstrapValid':int(good.sum()),'franchises':len(teams)}
def describe(rows):
 ans=[]
 for s in SEASONS+['pooled-test']:
  rr=[x for x in rows if x['season']==s or s=='pooled-test' and x['season'] in ['2024-25','2025-26']]
  if not rr:continue
  for f,th in [('deltaRole',.15),('deltaCompetition',1)]:
   y=np.array([x['y'] for x in rr]);xx=np.array([x[f] for x in rr]);w=np.array([x['targetMinutes'] for x in rr]);xm=np.average(xx,weights=w);ym=np.average(y,weights=w);den=np.sum(w*(xx-xm)**2)
   groups={}
   for label,mask in [('up',xx>=th),('down',xx<=-th),('small',abs(xx)<th)]:
    groups[label]={'n':int(mask.sum()),'meanChanceDelta':float(np.average(y[mask],weights=w[mask])) if mask.any() else None,'meanContextDelta':float(np.average(xx[mask],weights=w[mask])) if mask.any() else None}
   ans.append({'season':s,'feature':f,'n':len(rr),'Pearson':corr(xx,y),'weightedSlope':float(np.sum(w*(xx-xm)*(y-ym))/den) if den else None,'groups':groups})
 return ans
def run():
 p=read(HERE/'protocol.json');digest=(HERE/'protocol.sha256').read_text().split()[0];assert sha(HERE/'protocol.json')==digest
 for f,h in p['inputHashes'].items():assert sha(ROOT/f)==h,f
 lock=HERE/'analysis-code-registration.json'
 if not lock.exists():dump(lock,{'at':datetime.now(timezone.utc).isoformat(),'sha256':sha(HERE/'analyze.py')})
 assert read(lock)['sha256']==sha(HERE/'analyze.py')
 geometry(p);rows,audit=prepare(p);dump(HERE/'descriptive.json',describe(rows))
 usable={x['season'] for x in audit if x['usable']}
 if not set(p['estimator']['train']+p['estimator']['test']).issubset(usable):
  dump(HERE/'decision.json',{'supportedCandidates':[],'status':'Data gate failed; no fitting or substitution','engineAdoption':False});return
 train=[x for x in rows if x['season'] in p['estimator']['train']];test=[x for x in rows if x['season'] in p['estimator']['test']]
 assert len(train)>50 and len(test)>50
 preds={'chancePersistence':np.array([x['prior'] for x in test])};fits={}
 for m in ['history','role','competition','both']:preds[m],fits[m]=fit(train,test,m,p)
 pp={outcome:{} for outcome in ['chance','rate']}
 for outcome in pp:
  derived={m:v if outcome=='chance' else v*np.array([x['conversion'] for x in test]) for m,v in preds.items()}
  if outcome=='rate':derived['boxPersistence']=np.array([x['priorRate'] for x in test])
  for s in p['estimator']['test']+['pooled-test']:
   rr=[x for x in test if s=='pooled-test' or x['season']==s];sel=np.array([s=='pooled-test' or x['season']==s for x in test]);ps={m:v[sel] for m,v in derived.items()}
   pp[outcome][s]={}
   for g,mask in [('all',np.ones(len(rr),dtype=bool)),('movers',np.array([x['mover'] for x in rr]))]:
    chosen=[x for x,keep in zip(rr,mask) if keep]
    pp[outcome][s][g]=intervals(chosen,{m:v[mask] for m,v in ps.items()},outcome,p) if len(chosen)>=10 else {'n':len(chosen),'status':'Insufficient subgroup'}
  print('Evaluated',outcome,flush=True)
 predictions=[{**x,'predictionsChance':{m:float(v[i]) for m,v in preds.items()},'predictionsRate':{**{m:float(v[i]*x['conversion']) for m,v in preds.items()},'boxPersistence':x['priorRate']}} for i,x in enumerate(test)]
 decision={}
 for m in ['role','competition','both']:
  z=pp['rate']['pooled-test']['all']['paired'];a=all(z[m+'Minus'+ref]['MAE']['jointBonferroni6'][1]<0 for ref in ['BoxPersistence','History'])
  b=pp['chance']['pooled-test']['all']['paired'][m+'MinusHistory']['MAE']['joint95'][0]<=0
  c=True;insufficient=False
  for s in p['estimator']['test']:
   for g in ['all','movers']:
    z=pp['rate'][s][g]
    if 'paired' not in z:insufficient=True;c=False
    else:c &= z['paired'][m+'MinusBoxPersistence']['MAE']['joint95'][0]<=0
  decision[m]={'mainBothReferencesPass':a,'chanceNotWorse':b,'eachSeasonAndMoversNotWorse':bool(c),'insufficientMoverGroup':insufficient,'supported':bool(a and b and c)}
 dump(HERE/'fits.json',fits);dump(HERE/'predictions.json',predictions);dump(HERE/'results.json',{'at':datetime.now(timezone.utc).isoformat(),'protocolSHA256':digest,'results':pp,'label':'Four seen seasons; prefix traits and oracle later lineups; not blind or causal.'})
 dump(HERE/'decision.json',{'status':'Completed offline diagnostic','models':decision,'supportedCandidates':[m for m,x in decision.items() if x['supported']],'engineAdoption':False})
 print('Complete',len(train),len(test),[m for m,x in decision.items() if x['supported']],flush=True)
if __name__=='__main__':run()

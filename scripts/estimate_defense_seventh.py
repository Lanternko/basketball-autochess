"""Past-only ability estimate; random and forward game validation are separate outputs.
Reuse frozen sixth feature/likelihood definitions without executing their main program.
"""
import ast, sys, time
from defense_seventh_data import *
k=int(sys.argv[1]);mode=sys.argv[2] if len(sys.argv)>2 else 'forward';d=Data(k);P=d.P
O=R/'reports/defense-seventh';O.mkdir(exist_ok=True)
tree=ast.parse((R/'scripts/estimate_defense_sixth.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'sixth-feature-definitions','exec'))
ordered=sorted(d.trainids,key=lambda g:(d.gmap[g]['date'],g));grid=[3,10,30,100,300,1000,3000]
dates=sorted({d.gmap[g]['date'] for g in ordered});folds=[]
if mode=='forward':
 edges=[dates[int((len(dates)-1)*q)] for q in [.5,2/3,5/6,1]]
 for lo,hi in zip(edges[:-1],edges[1:]):
  allowed={g for g in ordered if d.gmap[g]['date']<=lo};valid={g for g in ordered if lo<d.gmap[g]['date']<=hi};folds.append((allowed,valid))
else:
 fold={g:int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%3 for g in ordered}
 folds=[({g for g in ordered if fold[g]!=f},{g for g in ordered if fold[g]==f}) for f in range(3)]
models={};start=time.time()
for role in [False,True]:
 scores={p:0. for p in grid};prior_loss=0;audits=[]
 for allowed,valid in folds:
  tm=np.array([g in allowed for g in d.gids]);vm=np.array([g in valid for g in d.gids]);a,_,_,_=features(allowed,role);beta,diag=prior_fit(a,tm);offset=a@beta
  e=np.clip(offset[vm],-8,8);prior_loss+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
  audits.append(dict(training=sorted(allowed),validation=sorted(valid),lastTrainingDate=max(d.gmap[g]['date'] for g in allowed),firstValidationDate=min(d.gmap[g]['date'] for g in valid),prior=diag))
  for l in grid:
   b,_=fit_count(d,tm,l,offset);e=np.clip(offset[vm]+d.A[vm]@b,-8,8);scores[l]+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
 selected=min(scores,key=scores.get);a,fo,fd,stats=features(d.trainids,role);beta,dp=prior_fit(a,d.train);b,dr=fit_count(d,d.train,selected,a@beta);no=fo.shape[1]
 models['role' if role else 'plain']=dict(priorOffense=(fo@beta[1:1+no]).tolist(),priorDefenseAllowed=(fd@beta[1+no:]).tolist(),offenseResidual=b[1:1+P].tolist(),defenseResidual=b[1+P:].tolist(),intercept=float(beta[0]+b[0]),priorIntercept=float(beta[0]),priorCVLoss=prior_loss,CV={'selected':selected,'loss':scores,'mode':mode,'folds':audits},diagnostics={'prior':dp,'residual':dr},roleFeatures=role)
 print('FIT',k,mode,role,selected,round(time.time()-start,1),flush=True)
result=dict(cutoff=k,validation=mode,players=d.pids,trainGames=ordered,minutes=d.minutes.tolist(),leaguePPP=d.leaguePPP,models=models,trainingSelectRole=models['role']['priorCVLoss']<models['plain']['priorCVLoss'],zeroExposurePointsDropped=d.zeroY,sources={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['scripts/estimate_defense_seventh.py','scripts/estimate_defense_sixth.py','scripts/defense_sixth_data.py','reports/defense-b1/stints.jsonl']})
destination=R/(CONFIG['root']+f'/ability-model-{mode}.json') if CONFIG.get('root') else O/f'model-pre{k}-{mode}.json'
destination.write_text(json.dumps(result,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

"""Independent previous-season prior experiment, never modifies frozen v4.
200 estimated player possessions pseudo exposure; fixed before prior outcomes.
Full previous joint effects are a prior offset, updated by current residuals.
Forward validation rebuilds all current features within its training fold.
"""
import ast,sys,time
from defense_seventh_data import *
k=int(sys.argv[1]);d=Data(k);P=d.P
previous=read('reports/defense-seventh/2024-25/calendar-82/ability-model-forward.json')
lookup={p:i for i,p in enumerate(previous['players'])}
tree=ast.parse((R/'scripts/estimate_defense_sixth.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'sixth-prior-definitions','exec'))
dates=sorted({d.gmap[g]['date'] for g in d.trainids});edges=[dates[int((len(dates)-1)*q)] for q in [.5,2/3,5/6,1]]
folds=[({g for g in d.trainids if d.gmap[g]['date']<=lo},{g for g in d.trainids if lo<d.gmap[g]['date']<=hi}) for lo,hi in zip(edges[:-1],edges[1:])]
grid=[3,10,30,100,300,1000,3000];models={};audit=[]
for role in [False,True]:
 old=previous['models']['role' if role else 'plain'];pw=np.array(previous['minutes']);old_o=np.array(old['priorOffense'])+np.array(old['offenseResidual']);old_d=np.array(old['priorDefenseAllowed'])+np.array(old['defenseResidual'])
 old_o-=pw@old_o/pw.sum();old_d-=pw@old_d/pw.sum()
 def offset_for(allowed):
  a,fo,fd,stats=features(allowed,role);tm=np.array([g in allowed for g in d.gids]);beta,diag=prior_fit(a,tm);no=fo.shape[1]
  co=fo@beta[1:1+no];cd=fd@beta[1+no:];w=stats[:,0]/48*100;share=w/(w+200);cw=np.maximum(w,0)
  po=np.array([old_o[lookup[p]] if p in lookup else co[i] for i,p in enumerate(d.pids)]);pd=np.array([old_d[lookup[p]] if p in lookup else cd[i] for i,p in enumerate(d.pids)])
  # Preserve current league intercept: center both priors on current exposure.
  if cw.sum():
   po+=cw@co/cw.sum()-cw@po/cw.sum();pd+=cw@cd/cw.sum()-cw@pd/cw.sum()
  o=share*co+(1-share)*po;v=share*cd+(1-share)*pd
  offset=beta[0]+d.X[:,:P]@o+d.X[:,P:]@v
  return offset,o,v,float(beta[0]),diag,share
 scores={l:0. for l in grid};prior_loss=0.;fa=[]
 for allowed,valid in folds:
  tm=np.array([g in allowed for g in d.gids]);vm=np.array([g in valid for g in d.gids]);offset,*_=offset_for(allowed);e=np.clip(offset[vm],-8,8);prior_loss+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
  fa.append({'lastTrainingDate':max(d.gmap[g]['date'] for g in allowed),'firstValidationDate':min(d.gmap[g]['date'] for g in valid),'training':sorted(allowed),'validation':sorted(valid)})
  for l in grid:
   b,_=fit_count(d,tm,l,offset);e=np.clip(offset[vm]+d.A[vm]@b,-8,8);scores[l]+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
 selected=min(scores,key=scores.get);offset,o,v,intercept,diag,share=offset_for(d.trainids);b,dr=fit_count(d,d.train,selected,offset)
 models['role' if role else 'plain']=dict(priorOffense=o.tolist(),priorDefenseAllowed=v.tolist(),offenseResidual=b[1:1+P].tolist(),defenseResidual=b[1+P:].tolist(),intercept=intercept+float(b[0]),priorIntercept=intercept,priorCVLoss=prior_loss,CV={'selected':selected,'loss':scores,'mode':'forward','folds':fa},diagnostics={'prior':diag,'residual':dr},roleFeatures=role,currentShare=share.tolist())
 print('PRIOR FIT',k,role,selected,flush=True)
result=dict(cutoff=k,players=d.pids,trainGames=sorted(d.trainids),minutes=d.minutes.tolist(),leaguePPP=d.leaguePPP,models=models,previousSeasonPrior=True,method='Fixed200 estimated possessions previous joint-effect prior offset; current fold box/position/MPG prior for players absent in previous season. Current residual ridge selected using three forward folds. Previous defense residual informs the joint likelihood only; deployment defense-residual switch remains off.',previousSource=hashlib.sha256((R/'reports/defense-seventh/2024-25/calendar-82/ability-model-forward.json').read_bytes()).hexdigest())
(R/CONFIG['root']/'ability-model-forward.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

"""Exact error identity and LOTO information diagnostics; never model inputs."""
from defense_sixth_data import *
from scipy.stats import t as student
import sys
sel=read('reports/defense-sixth/selection.json');variant=sel['cardVersion'];neutral=sel.get('neutral',False)
def runs(label,folder='defense-sixth'):
 return [read(f['file']) for f in read(f'reports/{folder}/{label}-seeds.json')['files']]
def team_pred(rs):
 ids=[t['id'] for t in rs[0]['teams']];return ids,np.array([[np.mean([(r['stats']['pts']-r['opponent']['pts'])/r['games'] for q in rs for r in q['teams'] if r['id']==t]) for t in ids]])[0]
d=Data(41);ids,s0=team_pred(runs('train-v3-41'));_,s1=team_pred(runs('train-ability'+('-neutral' if neutral else '')+'-41'));truth=read('reports/defense-sixth/diagnosis.json')['phaseTruth'];lookup=lambda phase:np.array([next(r['net'] for r in truth[phase] if r['id']==t) for t in ids]);r0=lookup('train');r1=lookup('post');center=lambda x:x-x.mean();r0=center(r0);r1=center(r1)
decomposition={}
for version,label,folder,st in [('v3','holdout-normalized','defense-fourth',s0),('final',variant+('-neutral' if neutral else '')+'-41','defense-sixth',s1)]:
 _,sp=team_pred(runs(label,folder));st=center(st);sp=center(sp);components=np.array([st-r0,sp-st,r0-r1]);e=sp-r1;assert np.max(abs(components.sum(axis=0)-e))<1e-9;MSE=float(np.mean(e*e));shares=components@e/len(e)/MSE
 decomposition[version]=dict(RMSE=float(np.sqrt(MSE)),trainingMetrics=metrics(r0,st),componentRMSE=np.sqrt(np.mean(components**2,axis=1)).tolist(),signedMSEContributions=(shares*MSE).tolist(),signedMSEShares=shares.tolist(),crossCovariance=(components@components.T/len(e)).tolist(),teams=[dict(id=t,trainMismatch=float(components[0,i]),modelRosterMinuteScheduleShift=float(components[1,i]),actualSeasonShift=float(components[2,i]),total=float(e[i])) for i,t in enumerate(ids)],simpleRMSE=float(np.sqrt(np.mean(components[2]**2))))
 # Quantify minute/availability change in fixed, analytic player coordinates separately.
 card=read(f'reports/defense-sixth/pre41-{variant}-projection.json') if version=='final' else None
 pvalues={(p['teamId'],p['id']):(p['after']['offense']-p['after']['defenseAllowed'] if card else p['offense']-p['defenseAllowed']) for p in (card['players'] if card else d.cards['players'])}
 actual_weights=[]
 for test in [False,True]:
  scores=[]
  for tid in ids:
   boxes=[b for b in d.box if b['TEAM_ID']==tid and (d.order[b['GAME_ID'],tid]>41)==test];den=sum(b['MIN'] for b in boxes);scores.append(sum(b['MIN']*pvalues.get((tid,b['PLAYER_ID']),0) for b in boxes)/den)
  actual_weights.append(np.array(scores))
 decomposition[version]['analyticActualMinuteShift']=center(actual_weights[1]-actual_weights[0]).tolist()
 sim_strength=[]
 for rr in [runs('train-v3-41' if version=='v3' else 'train-ability'+('-neutral' if neutral else '')+'-41'),runs(label,folder)]:
  vec=[]
  for tid in ids:
   rows=[t for run in rr for t in run['teams'] if t['id']==tid];den=sum(p['stats']['seconds'] for t in rows for p in t['players']);vec.append(sum(p['stats']['seconds']*pvalues.get((tid,p['playerId']),0) for t in rows for p in t['players'])/den)
  sim_strength.append(np.array(vec))
 opp_strength=[]
 for post in [False,True]:
  strength=dict(zip(ids,sim_strength[int(post)]));scores=[]
  for tid in ids:
   fixtures=[g for g in d.league['schedule'] if tid in [g['homeId'],g['awayId']] and (d.order[g['id'],tid]>41)==post];scores.append(np.mean([strength[g['awayId'] if g['homeId']==tid else g['homeId']] for g in fixtures]))
  opp_strength.append(np.array(scores))
 own_shift=center(sim_strength[1]-sim_strength[0]);opponent_shift=center(opp_strength[1]-opp_strength[0]);decomposition[version]['inputShiftProxyParts']={'simulatedMinuteAbilityShift':own_shift.tolist(),'opponentScheduleAbilityShift':opponent_shift.tolist(),'unrepresentedEngineTransferRemainder':(components[1]-own_shift+opponent_shift).tolist(),'method':'Additive fixed card proxy only: model player-seconds weights, opponent phase-average ability exposure on schedule, then exact leftover against engine transfer. Mixed-cutoff boundary games use opponent phase averages. Diagnostic approximation, not causal or probability inputs.'}
 decomposition[version]['inputShiftCaveat']='Exact engine pre/post shift includes conditional active/starter lists, trained MPG redistribution, opponents/schedule and finite seed noise. Actual-minute analytic shift is a separate diagnostic, not the entire term or an engine input. Three signed MSE projections include correlations; they are not independent causal variance percentages.'
info={};simple=read('reports/defense-fifth/simple-baselines.json')['splits'];rng=np.random.default_rng(20261221)
for k in [25,41,55]:
 label=variant+('-neutral' if neutral else '')+'-'+str(k);_,sim=team_pred(runs(label));s=simple[str(k)]['teams'];x=np.array([next(t['trainNet'] for t in s if t['id']==tid) for tid in ids]);y=np.array([next(t['trueNet'] for t in s if t['id']==tid) for tid in ids]);X=np.column_stack((np.ones(30),x,sim));pred=np.zeros(30);simplepred=np.zeros(30);coef=[]
 for j in range(30):
  train=np.arange(30)!=j;b=np.linalg.lstsq(X[train],y[train],rcond=None)[0];coef.append(b);pred[j]=X[j]@b;c=np.linalg.lstsq(X[train,:2],y[train],rcond=None)[0];simplepred[j]=X[j,:2]@c
 boots=[]
 for _ in range(2000):
  draw=rng.integers(0,30,30);foldcoef=[]
  for held in draw:
   tr=draw[draw!=held];foldcoef.append(np.linalg.lstsq(X[tr],y[tr],rcond=None)[0][2])
  boots.append(float(np.mean(foldcoef)))
 full=np.linalg.lstsq(X,y,rcond=None)[0];info[str(k)]=dict(simulationCoefficientMeanLOTO=float(np.mean(coef,axis=0)[2]),simulationCoefficientFull=float(full[2]),teamBootstrap95=np.quantile(boots,[.025,.975]).tolist(),LOTONetRMSE=float(np.sqrt(np.mean((pred-y)**2))),LOTOComparatorOnlyRMSE=float(np.sqrt(np.mean((simplepred-y)**2))),method='Each prediction excludes that team, fit true post net on intercept+pre net+simulation net; coefficient average over30 leave-one-team fits, interval from2000 team resamples redoing leave-all-copies-of-one-team-out (not engine seeds). Same season and overlapping cutoffs; diagnostic only, no product regression output.')
save('information-diagnosis.json',dict(decomposition=decomposition,incrementalInformation=info))
print('INFORMATION',info,flush=True)

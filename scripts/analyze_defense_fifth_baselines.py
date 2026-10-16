"""Cheap chronological comparators and fixed-margin variance scenarios.
Team identity joins/evaluation only; this script supplies no engine inputs.
"""
import json, hashlib
from pathlib import Path
import numpy as np
from scipy.special import expit, ndtr
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parents[1]; O=R/'reports/defense-fifth';O.mkdir(parents=True,exist_ok=True)
def read(f):return json.loads((R/f).read_text(encoding='utf-8'))
def table(f):
 d=read(f)['data']['resultSets'][0];return [dict(zip(d['headers'],r)) for r in d['rowSet']]
league=read('data/season-league.json');ids=[t['id'] for t in league['teams']];pi={t:i for i,t in enumerate(ids)}
order={};counter=dict.fromkeys(ids,0)
for g in league['schedule']:
 for t in [g['homeId'],g['awayId']]:counter[t]+=1;order[g['id'],t]=counter[t]
logs=table('data/season-source/team-games.json');by={(r['GAME_ID'],r['TEAM_ID']):r for r in logs}
def score(net,wins,truth):
 a=truth[:,0];b=np.array(net);e=np.array(wins)-truth[:,1];ac=a-a.mean();bc=b-b.mean()
 return dict(netRMSE=float(np.sqrt(np.mean((ac-bc)**2))),netCorrelation=float(np.corrcoef(a,b)[0,1]),netSDRatio=float(np.std(b)/np.std(a)),calibrationSlope=float(np.dot(bc,ac)/np.dot(bc,bc)),winMAE=float(np.mean(abs(e))),winRMSE=float(np.sqrt(np.mean(e*e))))
splits={}
for k in [25,41,55]:
 train=[];test=[];within=[];pf=[];pa=[]
 for t in ids:
  rows=[by[g['id'],t] for g in league['schedule'] if t in [g['homeId'],g['awayId']]]
  margins=np.array([r['PLUS_MINUS'] for r in rows]);train.append([margins[:k].mean(),sum(r['WL']=='W' for r in rows[:k])]);test.append([margins[k:].mean(),sum(r['WL']=='W' for r in rows[k:])]);within.append(np.var(margins[:k],ddof=1));pf.append(sum(r['PTS'] for r in rows[:k]));pa.append(sum(by[r['GAME_ID'],next(i for i in ids if (r['GAME_ID'],i) in by and i!=t)]['PTS'] for r in rows[:k]))
 train=np.array(train);truth=np.array(test);net=train[:,0];rate=train[:,1]/k
 noise=np.mean(within)/k;shrink=float(np.clip(1-noise/np.var(net),0,1))
 # Common Pythagorean exponent estimated exclusively from the training totals.
 x=np.log(np.array(pf)/np.array(pa));y=train[:,1]
 f=lambda gamma:float(np.sum(k*np.logaddexp(0,gamma*x)-y*gamma*x))
 fit=minimize_scalar(f,bounds=(0,40),method='bounded');gamma=float(fit.x)
 wraw=rate*(82-k);wpyth=expit(gamma*x)*(82-k)
 methods={'first_net_and_winrate':score(net,wraw,truth),'shrunk_net_and_winrate':score(net.mean()+shrink*(net-net.mean()),wraw,truth),'first_net_and_pythagorean':score(net,wpyth,truth),'shrunk_net_and_pythagorean':score(net.mean()+shrink*(net-net.mean()),wpyth,truth)}
 splits[str(k)]={'cutoff':k,'shrinkage':shrink,'trainingMeanMargin':float(net.mean()),'trainingWithinGameMarginVariance':float(np.mean(within)),'pythagoreanExponent':gamma,'metrics':methods,'teams':[dict(id=t,name=league['teams'][i]['name'],trainNet=float(net[i]),trueNet=float(truth[i,0]),trueWins=float(truth[i,1]),shrunkNet=float(net.mean()+shrink*(net[i]-net.mean())),rateWins=float(wraw[i]),pythagoreanWins=float(wpyth[i])) for i,t in enumerate(ids)]}
def load(label):return [read(x['file']) for x in read('reports/defense-fourth/'+label+'-seeds.json')['files']]
sigma=read('reports/defense-b1/variance-sources.json')['real']['marginResidualSD'];scenarios={}
for label,k in [('final-normalized',0),('holdout-normalized',41)]:
 runs=load(label);m=np.array([[g['scoreA']-g['scoreB'] for g in r['matches']] for r in runs]);fixtures=runs[0]['matches'];truth=np.array([[np.mean([by[g['id'],t]['PLUS_MINUS'] for g in fixtures if t in [g['homeId'],g['awayId']] and order[g['id'],t]>k]),sum(by[g['id'],t]['WL']=='W' for g in fixtures if t in [g['homeId'],g['awayId']] and order[g['id'],t]>k)] for t in ids]);currentSigma=np.mean([r['analysis']['marginResidualSD'] for r in runs])
 def scenario(draw,s):
  mu=m[draw].mean(axis=0);w=np.zeros(30);net=np.zeros(30);count=np.zeros(30)
  for j,g in enumerate(fixtures):
   p=ndtr(mu[j]/s)
   for t,sign,prob in [(g['homeId'],1,p),(g['awayId'],-1,1-p)]:
    if order[g['id'],t]<=k:continue
    i=pi[t];w[i]+=prob;net[i]+=sign*mu[j];count[i]+=1
  return score(net/count,w,truth)
 all=np.arange(20);now=scenario(all,currentSigma);fixed=scenario(all,sigma);actual_w=np.mean([[next(t['wins'] for t in r['teams'] if t['id']==i) for i in ids] for r in runs],axis=0);actual=score(np.zeros(30),actual_w,truth)
 rng=np.random.default_rng(20261201);samples=[]
 for _ in range(2000):
  d=rng.integers(0,20,20);a=scenario(d,currentSigma);b=scenario(d,sigma);samples.append([b['winMAE']-a['winMAE'],b['winRMSE']-a['winRMSE']])
 scenarios[label]={'sigmaCurrent':currentSigma,'sigmaIdeal':sigma,'normalCurrent':now,'normalIdeal':fixed,'actualEngineWins':{'winMAE':actual['winMAE'],'winRMSE':actual['winRMSE']},'idealMinusNormalCurrent95':dict(zip(['winMAE','winRMSE'],np.quantile(samples,[.025,.975],axis=0).T.tolist())),'MAEGain':now['winMAE']-fixed['winMAE'],'MAEGainVersusActualEngine':actual['winMAE']-fixed['winMAE'],'scope':'Mean of 20 per-fixture simulated margins held fixed; Gaussian residual with observed regulation SD. All team means therefore unchanged. Finite-seed fixture means include sampling error, availability variation and OT; this is a hypothetical variance scenario, not a mathematical upper bound or adoptable score patch.'}
out={'splits':splits,'varianceScenarios':scenarios,'definition':'Centered net RMSE; population SD; calibration slope = true on predicted with intercept. Shrinkage = max(0,1 - training within-team margin variance / (K * between-team mean variance)), estimated only pre-cutoff. Pythagorean exponent fitted only pre-cutoff. Team identities evaluation joins only.','sources':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['data/season-league.json','data/season-source/team-games.json','scripts/analyze_defense_fifth_baselines.py']}}
(O/'simple-baselines.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'41':splits['41']['metrics'],'shrink41':splits['41']['shrinkage'],'scenarios':scenarios},ensure_ascii=False),flush=True)

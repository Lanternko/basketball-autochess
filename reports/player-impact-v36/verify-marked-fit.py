"""Direct categorical probabilities and an analytic score equation verify the fit."""
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();fit=read(R/'marked-fit.json');protocol=read(R/'marked-protocol.json')
for obj in [protocol,fit]:
 for p,h in obj['hashes'].items():assert sha(p)==h,p
names={p['playerId']:p for c in read('reports/player-impact-v30/scores.json')['cells'] if c['season']=='2025-26' and c['version']=='rotation-space' for p in c['players']}
training={};summary=[];playerTotals=defaultdict(lambda:defaultdict(float));rng=np.random.default_rng(20261019)
for season in [*protocol['trainingSeasons'],protocol['checkSeason']]:
 d=read(R/f'{season}-marked-data.json');xs=[];game=defaultdict(lambda:[0.,0.]);nlls=[0.,0.];n=0
 for r in d['rows']:
  for i,pid in enumerate(r[6]):
   actual=np.array([r[8][i],r[7][i]-r[8][i]-sum(r[9][i]),*r[9][i]],float)
   a,b,c,e,z,w,g=r[10][i];assert min(a,b,c,z)>0
   pair=[]
   for index,k in enumerate([1.,fit['selfScale']]):
    probs=np.array([(k*c+e),(k*z+w),*g],float)/(k*a+b)
    assert np.all(probs>=0) and abs(probs.sum()-1)<1e-12 and probs[2+i]==0
    assert not np.any((actual>0)&(probs<=0))
    value=-sum(float(v)*math.log(float(p)) for v,p in zip(actual,probs) if v)
    pair.append(value);nlls[index]+=value
    if season==protocol['checkSeason']:
     tag='priorOne' if index==0 else 'fitted';target=playerTotals[pid]
     target[tag+'Nll']+=value;target[tag+'ExpectedSelfMakes']+=r[7][i]*probs[0];target[tag+'ExpectedAssistedMakes']+=r[7][i]*probs[2:].sum();target[tag+'ExpectedMisses']+=r[7][i]*probs[1]
     if index==0:target['freshAttempts']+=r[7][i];target['actualSelfMakes']+=r[8][i];target['actualAssistedMakes']+=sum(r[9][i])
   game[r[0]][0]+=pair[0]-pair[1];game[r[0]][1]+=r[7][i];n+=r[7][i]
   if r[7][i]:xs.append([r[7][i],r[8][i],actual[1],a,b,c,e,z,w,r[1]])
 expected=next(s for s in fit['seasons'] if s['season']==season)
 assert abs(nlls[0]-expected['priorOneNll'])<1e-6 and abs(nlls[1]-expected['fittedNll'])<1e-6 and n==expected['freshAttempts']
 gs=np.array(list(game.values()));boots=np.empty(2000)
 for j in range(2000):
  draw=gs[rng.integers(len(gs),size=len(gs))];boots[j]=draw[:,0].sum()/draw[:,1].sum()
 summary.append({'season':season,'attempts':n,'priorOneNll':nlls[0],'fittedNll':nlls[1],'gainPerFga':(nlls[0]-nlls[1])/n,'fixedSourceWholeGameBootstrap95':np.quantile(boots,[.025,.975]).tolist()})
 if season in protocol['trainingSeasons']:training[season]=np.array(xs,float)
 print(json.dumps(summary[-1]),flush=True)
 del d,xs

def score(logk,fold=None):
 k=math.exp(logk);parts=[]
 for x in training.values():
  if fold is not None:x=x[x[:,9]!=fold]
  n,s,m,a,b,c,d,e,f=x[:,:9].T
  derivative=n*(k*a/(k*a+b))-s*(k*c/(k*c+d))-m*(k*e/(k*e+f))
  parts.append(derivative.sum()/n.sum())
 return sum(parts)/len(parts)

independent=[]
for fold in [None,0,1,2,3,4]:
 lo,hi=-1.,1.
 while score(lo,fold)>0:lo*=2
 while score(hi,fold)<0:hi*=2
 root=brentq(lambda k:score(k,fold),lo,hi,xtol=1e-12)
 expected=fit if fold is None else next(f for f in fit['folds'] if f['fold']==fold)
 assert abs(root-expected['logSelfScale'])<1e-6,(fold,root,expected['logSelfScale'])
 independent.append({'excludedGameFold':fold,'independentLogSelfScale':root,'reportedLogSelfScale':expected['logSelfScale']})
assert len(names)==582
rows=[]
for pid,p in names.items():
 v=playerTotals.get(pid);row={'playerId':pid,'name':p['name'],'actualSeasonMinutes':p['minutes'],'strictPbpAvailable':bool(v)}
 for field in ['freshAttempts','actualSelfMakes','actualAssistedMakes','priorOneNll','fittedNll','priorOneExpectedSelfMakes','fittedExpectedSelfMakes','priorOneExpectedAssistedMakes','fittedExpectedAssistedMakes','priorOneExpectedMisses','fittedExpectedMisses']:row[field]=v[field] if v else ''
 row['gainPerFga']=(v['priorOneNll']-v['fittedNll'])/v['freshAttempts'] if v else '';rows.append(row)
with (R/'2025-26-conditional-mark-scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
files=[R/'marked-protocol.json',R/'marked-fit.json',R/'verify-marked-fit.py',R/'2025-26-conditional-mark-scores.csv',*[R/f'{s}-marked-data.json' for s in [*protocol['trainingSeasons'],protocol['checkSeason']]]]
out={'passed':True,'sourceProbabilityPartitionsChecked':True,'allNllsRecomputedFromDirectCategoryProbabilities':True,'analyticScoreRootVerifiedAllSixFits':independent,'seasons':summary,'allPlayers':582,'playersWithPbp':len(playerTotals),
 'scope':'Probabilities conditioned on actual shooter/stint FGA, with frozen v30 source contexts. Expected makes in CSV are conditional reconstruction, never full simulation, OVR or causal estimates. Whole-game bootstrap fixes descriptors and fitted scale, not parameter/model uncertainty.',
 'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(R/'marked-fit-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k not in ['hashes','seasons']},indent=2))

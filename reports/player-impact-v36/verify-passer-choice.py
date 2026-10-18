"""Direct weighted choice probabilities independently verify the identity diagnostic."""
import hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(R/'passer-choice-diagnostic.json');inputs=read(R/'passer-choice-inputs.json');old=inputs['beta'];beta=d['diagnosticFit']['beta'];rng=np.random.default_rng(20261020);out=[];maximum=0.
for p,h in d['hashes'].items():assert sha(p)==h,p
for season in ['2022-23','2023-24','2024-25','2025-26']:
 source=read(R/f'{season}-marked-data.json');rates=inputs['inputs'][season];loss=[0.,0.];games=defaultdict(lambda:[0.,0.]);gradient=0.;total=0
 for r in source['rows']:
  raw=np.array([rates[str(r[2])][str(pid)] for pid in r[6]]);totalPass=raw.sum();previous=raw**old;previous*=totalPass/previous.sum();candidate=raw**beta;candidate*=totalPass/candidate.sum()
  for i in range(5):
   y=np.array(r[9][i]);n=int(y.sum())
   if not n:continue
   g=np.array(r[10][i][6]);prob=g/g.sum();changed=g*(candidate/previous);q=changed/changed.sum();alternative=g*raw**(beta-old);alternative/=alternative.sum()
   maximum=max(maximum,float(np.max(np.abs(q-alternative))));assert np.max(np.abs(q-alternative))<1e-12
   positive=y>0;assert np.all(prob[positive]>0) and np.all(q[positive]>0)
   a=-float(np.sum(y[positive]*np.log(prob[positive])));b=-float(np.sum(y[positive]*np.log(q[positive])));loss[0]+=a;loss[1]+=b;games[r[0]][0]+=a-b;games[r[0]][1]+=n;total+=n
   gradient+=n*float(np.sum(q*np.log(raw)))-float(np.sum(y*np.log(raw)))
 expected=next(s for s in d['seasons'] if s['season']==season)
 assert abs(loss[0]-expected['old']['nll'])<1e-6 and abs(loss[1]-expected['fitted']['nll'])<1e-6 and total==expected['old']['assistedMakes']
 assert abs(gradient/total-expected['fitted']['gradientPerMake'])<1e-10
 values=np.array(list(games.values()));boot=[]
 for j in range(2000):
  chosen=values[rng.integers(len(values),size=len(values))];boot.append(float(chosen[:,0].sum()/chosen[:,1].sum()))
 out.append({'season':season,'assistedMakes':total,'oldNll':loss[0],'fittedNll':loss[1],'gainPerAssistedMake':(loss[0]-loss[1])/total,'fixedSourceWholeGameBootstrap95':np.quantile(boot,[.025,.975]).tolist()});print(json.dumps(out[-1]),flush=True)
assert abs(sum(s['fitted']['gradientPerMake'] for s in d['seasons'][:3])/3)<1e-10
files=[R/'passer-choice-diagnostic.json',R/'passer-choice-inputs.json',R/'verify-passer-choice.py']
result={'passed':True,'runtimeChanged':False,'allDirectCategoryNllAndScoresRecomputed':True,'maximumDifferenceToExplicitRenormalizedPassPriors':maximum,'seasons':out,'scope':'Conditional assister identity only. Whole-game intervals fix source predictions and the fitted diagnostic beta; no parameter uncertainty, no inferred total creation or OVR benefit.',
 'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(R/'passer-choice-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

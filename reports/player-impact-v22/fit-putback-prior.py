import json,math,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import minimize_scalar
root=Path('reports/player-impact-v22');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
seasons=['2022-23','2023-24','2024-25','2025-26'];sources={s:read(root/f'{s}-putback-events.json') for s in seasons};folds=[]
for s in seasons[:3]:
 for fold in range(5):
  train=defaultdict(Counter);test=defaultdict(Counter)
  for g in sources[s]['games']:
   dest=test if g['fold']==fold else train
   for e in g['events']:dest[e['playerId']].update({'a':1,'m':e['made']})
  total=sum(train.values(),Counter());prior=total['m']/total['a']
  folds.append((s,fold,train,test,prior))
def score(k,detail=False):
 out=[]
 for s,f,train,test,prior in folds:
  nll=0
  for pid,row in test.items():
   p=(train[pid]['m']+k*prior)/(train[pid]['a']+k)
   nll-=row['m']*math.log(p)+(row['a']-row['m'])*math.log1p(-p)
  out.append({'season':s,'fold':f,'events':sum(r['a'] for r in test.values()),'nll':nll})
 return out if detail else sum(r['nll'] for r in out)
fit=minimize_scalar(lambda x:score(math.exp(x)),bounds=(math.log(.001),math.log(100000)),method='bounded');assert fit.success;k=math.exp(fit.x)
out={'kappaAttempts':k,'fitSeasons':seasons[:3],'checkSeason':'2025-26','design':'Common Beta prior strength chosen by five whole-game folds on preceding three seasons, scoring recorded-FGA conditional binomial NLL of same-player 0-3s putbacks following FG rebounds. No simulated output, name, rank or on/off target fitted. 2025-26 was historically seen; this is descriptive source estimation, not a blind forward claim.','foldScores':score(k,True),'nll':{'fitted':score(k),'nearUnshrunk':score(.001),'pooledApprox':score(100000)},'sourceHashes':{str(root/f'{s}-putback-events.json'):hashlib.sha256((root/f'{s}-putback-events.json').read_bytes()).hexdigest() for s in seasons},'codeHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'references':{}}
for s,src in sources.items():
 rate=src['totals']['fieldGoalMakes']/src['totals']['fieldGoalAttempts'];cards={pid:{**r,'rate':(r['makes']+k*rate)/(r['attempts']+k)} for pid,r in src['cards'].items()}
 ref={'leagueRecordedFG':rate,'kappaAttempts':k};out['references'][s]=ref
 f=root/f'{s}-putback-rates.json'
 if f.exists():raise RuntimeError('Preserve prior cards')
 f.write_text(json.dumps({'season':s,'reference':ref,'cards':cards,'sourceHash':out['sourceHashes'][str(root/f'{s}-putback-events.json')],'fitCodeHash':out['codeHash']},indent=2),encoding='utf-8');print(s,ref,flush=True)
f=root/'putback-prior.json'
if f.exists():raise RuntimeError('Preserve prior fit')
f.write_text(json.dumps(out,indent=2),encoding='utf-8');print('FIT',k,out['nll'],flush=True)

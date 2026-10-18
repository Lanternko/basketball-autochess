"""Estimate one shooting-only FTR sample-size prior from source game counts, not OVR.

FGA and classified shooting FTA are count tokens, not independent Bernoulli trials (FTs cluster).
The log score is a working prediction criterion; no binomial uncertainty claim.
Five game folds predict the held-out shootingFTA/(FGA+shootingFTA) count mix. Train three prior
seasons equally; inspect already-seen2025-26 separately, never choose by ranks.
"""
import json,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import minimize_scalar

root=Path('reports/player-impact-v19');output=root/'ftr-prior.json'
if output.exists():raise RuntimeError('Preserve the fitted artifact; use a new version')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
seasons=['2022-23','2023-24','2024-25','2025-26'];data={};coverage=[];hashes={};references={}
for season in seasons:
 bundle=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');official=defaultdict(Counter)
 for t in bundle['league']['teams']:
  for p in t['roster']:official[p['playerId']].update({k:p['observed'][k] for k in ['FGA','FTA','MIN']})
 ids=sorted(official);ix={pid:i for i,pid in enumerate(ids)};folds=np.zeros((5,len(ids),2));games=0;unknown=Counter()
 sourceFile=root/f'{season}-ft-kinds.json';source=read(sourceFile);hashes[str(sourceFile)]=hashlib.sha256(sourceFile.read_bytes()).hexdigest()
 for gid,rows in source['games'].items():
  fold=int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5;games+=1
  for pid,c in rows.items():
   if int(pid) not in ix:unknown[pid]+=c.get('fga',0)+c.get('shooting',0);continue
   folds[fold,ix[int(pid)],0]+=c.get('fga',0);folds[fold,ix[int(pid)],1]+=c.get('shooting',0)
 data[season]=folds
 references[season]={'counts':{str(pid):{'FGA':int(folds[:,ix[pid],0].sum()),'FTA':int(folds[:,ix[pid],1].sum()),'MIN':official[pid]['MIN']} for pid in ids},'leagueFtr':float(folds[:,:,1].sum()/folds[:,:,0].sum()),'scope':'Strict PBP classified shooting FTA per recorded FGA, not total official FTA. MIN is full-season metadata only.'}
 coverage.append({'season':season,'games':games,'players':len(ids),'fga':int(folds[:,:,0].sum()),'fta':int(folds[:,:,1].sum()),'unknownActorTokens':dict(unknown)})
 print(coverage[-1],flush=True)

def score(kappa,selected):
 scores=[]
 for season in selected:
  folds=data[season];total=folds.sum(axis=0);loss=0;tokens=0
  for held in folds:
   train=total-held;ratio=train[:,1].sum()/train[:,0].sum()
   denominator=train.sum(axis=1)+kappa*(1+ratio)
   q=np.divide(train[:,1]+kappa*ratio,denominator,out=np.full(len(train),ratio/(1+ratio)),where=denominator>0)
   q=np.clip(q,1e-12,1-1e-12)
   loss-=np.sum(held[:,1]*np.log(q)+held[:,0]*np.log1p(-q));tokens+=held.sum()
  scores.append(float(loss/tokens))
 return sum(scores)/len(scores)

fit=minimize_scalar(lambda x:score(math.exp(x),seasons[:3]),bounds=(math.log(.01),math.log(10000)),method='bounded',options={'xatol':1e-9})
assert fit.success
kappa=math.exp(fit.x)
out={'design':__doc__,'kappaFga':kappa,'posteriorFtr':'(shootingFTA + kappa*leagueShootingFTR)/(FGA + kappa)','trainingSeasons':seasons[:3],'checkSeason':seasons[3],'coverage':coverage,
 'scores':{s:{'rawClippedNll':score(0,[s]),'halfFgaPriorNll':score(.5,[s]),'fittedPriorNll':score(kappa,[s]),'hundredFgaPriorNll':score(100,[s])} for s in seasons},
 'references':references,'sourceHashes':hashes,'scriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
output.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['references','sourceHashes']},ensure_ascii=False,indent=2))

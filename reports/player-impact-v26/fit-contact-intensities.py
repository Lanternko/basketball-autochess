"""Frozen source-only empirical Bayes token intensities; no engine residual tuning."""
import json,hashlib,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar

root=Path('reports/player-impact-v26')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
seasons=['2022-23','2023-24','2024-25','2025-26'];sources={s:read(root/f'{s}-contact-intensities.json') for s in seasons}
source_hashes={str(root/f'{s}-contact-intensities.json'):sha(root/f'{s}-contact-intensities.json') for s in seasons}
for src in sources.values():
 for f,h in src['hashes'].items():assert sha(f)==h,(f,'Source drift');source_hashes[f]=h
source_hashes[str(Path(__file__))]=sha(__file__)
folds=[]
for season in seasons[:3]:
 src=sources[season];ids=list(src['cards']);index={pid:i for i,pid in enumerate(ids)};a=np.zeros((5,len(ids),3))
 for game in src['games']:
  for pid,c in game['players'].items():a[game['fold'],index[pid]]+=[c.get(k,0) for k in ['minutes','contacts','terminal']]
 for fold in range(5):
  test=a[fold];train=a.sum(axis=0)-test
  assert np.all(train[:,0]>=-1e-6)
  train[:,0]=np.maximum(train[:,0],0)
  folds.append((season,fold,train,test))

def score(kappa,kind):
 loss=0.
 for season,fold,train,test in folds:
  mu=train[:,kind].sum()/train[:,0].sum()
  rate=(train[:,kind]+kappa*mu)/(train[:,0]+kappa) if math.isfinite(kappa) else np.full(len(train),mu)
  predicted=test[:,0]*rate;mask=test[:,0]>0
  assert np.all(test[~mask,kind]==0)
  loss+=float(np.sum(predicted[mask]-test[mask,kind]*np.log(predicted[mask])))
 return loss

fits={}
for kind,name in [(1,'contacts'),(2,'terminal')]:
 result=minimize_scalar(lambda z:score(math.exp(z),kind),bounds=(-8,20),method='bounded',options={'xatol':1e-7})
 assert result.success
 kappa=math.exp(result.x);uniform=score(float('inf'),kind)
 assert -7.99<result.x<19.99,'Boundary fit: examine limiting model before using'
 fits[name]={'priorMinutes':kappa,'cvPoissonNllWithoutConstants':score(kappa,kind),'weakPriorMinutes0_1Nll':score(.1,kind),'leagueOnlyNll':uniform,'wholeGameFolds':5,'trainingSeasons':seasons[:3]}
 assert fits[name]['cvPoissonNllWithoutConstants']<uniform
 print(name, fits[name],flush=True)

for season,src in sources.items():
 target=root/f'{season}-contact-rates.json';assert not target.exists(),'Preserve previously frozen fitted rates'
 M=src['totals']['playerMinutes'];muC=src['totals']['contacts']/M
 totalN=sum(c.get('terminal',0) for c in src['cards'].values());muN=totalN/M
 cards={}
 for pid,c in src['cards'].items():
  minutes=c.get('minutes',0);C=c.get('contacts',0);N=c.get('terminal',0)
  assert minutes>0 or (C==0 and N==0)
  kC=fits['contacts']['priorMinutes'];kN=fits['terminal']['priorMinutes']
  cards[pid]={'sourceMinutes':minutes,'sourceContacts':C,'sourceTerminal':N,'contactRate':(C+kC*muC)/(minutes+kC),'terminalRate':(N+kN*muN)/(minutes+kN)}
 unassigned=src['totals']['unassignedTerminal']/(M/5)
 out={'season':season,'design':'Independent Gamma-Poisson posterior source token rates (events per floor minute); contact/terminal priors selected by 2022-25 whole-game folds. Not causal skill, no team/win/on-off/OVR or simulation residual fit. Floor minutes include endgame whereas counts exclude source action-time policy; ordinary-state exposure not separately identified. Candidate joint lineup odds require runtime validation.','priorMinutes':{k:v['priorMinutes'] for k,v in fits.items()},'leagueContactRate':muC,'leagueTerminalRate':muN,'unassignedTerminalRatePerTeamMinute':unassigned,'cards':cards}
 target.write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(season,'cards',len(cards),'muC',muC,'muN',muN,'unassigned',unassigned,flush=True)
out={'model':'Independent Gamma-Poisson posterior (count+kappa*leagueRate)/(minutes+kappa); separate source CV for C and N. Lineup candidate P(contact)=sum(C rates)/(sum(C rates)+sum(N rates)+unassigned team N rate). Victim rates normalized over five.','fits':fits,'sourceHashes':source_hashes,'selectionScope':'2022-23 to2024-25 only; 2025-26 rates fitted after prior selection. Descriptive same-season production/style, not prospective or causal estimates.'}
(root/'contact-intensity-prior.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

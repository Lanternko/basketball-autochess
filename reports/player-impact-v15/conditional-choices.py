"""Source-choice diagnostic: marginal per-minute rates need not be lineup odds.

Fits no simulated box residual, shooting outcome, on/off or OVR target. The base
season-rate inputs already use all games; the game split is a conditional-choice
check, not a blind or prospective player evaluation. Not an adopted model.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,re,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import minimize

root=Path('reports/player-impact-v15');season=sys.argv[1] if len(sys.argv)>1 else '2025-26'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds'])
cards=read(f'reports/player-impact-v6/{season}-cards.json')['cards']
bundle=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
observed=defaultdict(Counter);names={}
for t in bundle['league']['teams']:
 for p in t['roster']:
  names[p['playerId']]=p['name'];observed[p['playerId']].update({k:p['observed'][k] for k in ['MIN','DREB']})
ids=sorted(observed);index={pid:i for i,pid in enumerate(ids)}
minutes=np.array([observed[pid]['MIN'] for pid in ids])
fresh=np.array([sum(cards[str(pid)]['freshShotCounts'].get(z+'A',0) for z in ['long','mid','short']) for pid in ids])
dreb=np.array([observed[pid]['DREB'] for pid in ids])
priors={'shot':60.,'dreb':240.}
base={k:(n+priors[k]*n.sum()/minutes.sum())/(minutes+priors[k]) for k,n in [('shot',fresh),('dreb',dreb)]}
penalties={k:priors[k]*n.sum()/minutes.sum() for k,n in [('shot',fresh),('dreb',dreb)]}
stintfile=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
stints=defaultdict(list)
for line in stintfile.read_text(encoding='utf-8').splitlines():
 s=json.loads(line)
 if s['id'] in valid:stints[s['id']].append(s)
manifest=read(Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')/'manifest.json')
counts={k:[defaultdict(Counter),defaultdict(Counter)] for k in base};sourcehashes={}
def seconds(c):
 m=re.match(r'PT(?:(\d+)M)?([\d.]+)S',c)
 return int(m[1] or 0)*60+float(m[2])
for source in manifest['sources']:
 if source['id'] not in valid:continue
 f=Path(source['file']);actions=read(f)['data']['game']['actions'];sourcehashes[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
 split=int(hashlib.sha256(source['id'].encode()).hexdigest()[:8],16)%2
 pending=None;putbacks=set()
 for i,e in enumerate(actions):
  k=e.get('actionType');sub=e.get('subType')
  if k in ['2pt','3pt'] and e.get('isFieldGoal'):
   if pending and e.get('personId')==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and k=='2pt' and e.get('area')!='Mid-Range' and 0<=seconds(pending['clock'])-seconds(e['clock'])<=3:putbacks.add(i)
   pending=None
  elif k=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
  elif k in ['turnover','freethrow','foul','period','jumpball'] or k=='rebound' and sub=='defensive':pending=None
 for s in stints[source['id']]:
  teams={t['teamId']:tuple(sorted(t['players'])) for t in s['teams']}
  for i in range(s['startIndex'],s['endIndex']):
   e=actions[i];kind=None
   if e.get('isFieldGoal') and e.get('actionType') in ['2pt','3pt'] and i not in putbacks:kind='shot'
   elif e.get('actionType')=='rebound' and e.get('subType')=='defensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):kind='dreb'
   if not kind:continue
   own=teams.get(e.get('teamId'));pid=e.get('personId')
   assert own and pid in own,(source['id'],i,kind,pid,own)
   counts[kind][split][own][pid]+=1

def arrays(rows):
 x=np.array([[index[pid] for pid in lineup] for lineup in rows],dtype=int)
 n=np.array([[count[pid] for pid in lineup] for lineup,count in rows.items()],dtype=float)
 return x,n
def objective(delta,x,n,logbase,penalty=0):
 z=logbase[x]+delta[x];z-=z.max(axis=1,keepdims=True);e=np.exp(z);den=e.sum(axis=1,keepdims=True);prob=e/den
 loss=-(n*(z-np.log(den))).sum()
 gradient=np.bincount(x.ravel(),weights=(n.sum(axis=1,keepdims=True)*prob-n).ravel(),minlength=len(ids))
 if penalty:
  loss+=penalty*np.sum(np.exp(delta)-delta-1);gradient+=penalty*(np.exp(delta)-1)
 return loss,gradient
out={'season':season,'adopted':False,'design':__doc__,'regularizer':'Poisson log-odds prior: lambda*(exp(delta)-delta-1), centered at original minute-smoothed rates. Lambda is league rate times original60min shot or240min DREB prior. Fixed before fitting; no ranking selection. Actual choices condition on the five eligible players; DREB remains conditional allocation only, no team rebound probability change.','choices':{},'sourceHashes':sourcehashes}
for kind in base:
 train=arrays(counts[kind][0]);check=arrays(counts[kind][1]);merged=defaultdict(Counter)
 for part in counts[kind]:
  for lineup,n in part.items():merged[lineup].update(n)
 full=arrays(merged);logbase=np.log(base[kind]);zero=np.zeros(len(ids));penalty=penalties[kind]
 fit=minimize(lambda d:objective(d,*train,logbase,penalty),zero,jac=True,method='L-BFGS-B',options={'maxiter':500,'ftol':1e-11,'gtol':1e-6})
 final=minimize(lambda d:objective(d,*full,logbase,penalty),zero,jac=True,method='L-BFGS-B',options={'maxiter':500,'ftol':1e-11,'gtol':1e-6})
 assert fit.success and final.success,(fit.message,final.message)
 cells={'trainEvents':int(train[1].sum()),'checkEvents':int(check[1].sum()),'checkNllMarginalRate':objective(zero,*check,logbase)[0]/check[1].sum(),'checkNllConditionalFit':objective(fit.x,*check,logbase)[0]/check[1].sum(),'priorPseudoEvents':penalty,
  'cards':{str(pid):{'name':names[pid],'minutes':float(minutes[i]),'marginalWeight':float(base[kind][i]),'conditionalOddsMultiplier':float(np.exp(final.x[i])),'conditionalWeight':float(base[kind][i]*np.exp(final.x[i]))} for i,pid in enumerate(ids)}}
 out['choices'][kind]=cells;print(kind,{k:v for k,v in cells.items() if k!='cards'},flush=True)
 for pid in [201939,1628983,1629029,203999,1629674]:print(cells['cards'][str(pid)],flush=True)
out['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(root/f'{season}-conditional-choices.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')

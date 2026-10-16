"""One global usage elasticity from strict, observed shooter choices; no names."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
ROOT=Path('reports/player-impact-v8');ROOT.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
seasons=['2022-23','2023-24','2024-25','2025-26'];data={};coverage=[];hashes={}
def sec(c):
 m=re.match(r'PT(?:(\d+)M)?([\d.]+)S',c);return int(m[1] or 0)*60+float(m[2])
for season in seasons:
 truth=read(f'reports/player-impact-v1/{season}-on-court-truth.json');valid=set(truth['gameIds']);cards=read(f'reports/player-impact-v6/{season}-cards.json')['cards'];b=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');minutes=Counter()
 for t in b['league']['teams']:
  for p in t['roster']:minutes[p['playerId']]+=p['observed']['MIN']
 assists=Counter();
 for t in b['league']['teams']:
  for p in t['roster']:assists[p['playerId']]+=p['observed']['AST']
 prior=sum(assists.values())/sum(minutes.values());rate={pid:(assists[pid]+60*prior)/(m+60) for pid,m in minutes.items()}
 sf=Path('reports/defense-b1' if season=='2025-26' else f'reports/defense-seventh/{season}/stints');stints=defaultdict(list)
 for line in (sf/'stints.jsonl').open(encoding='utf-8'):
  s=json.loads(line)
  if s['id'] in valid:stints[s['id']].append(s)
 manifest=read(Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')/'manifest.json');counts=defaultdict(Counter);joined=0;excluded=0
 for spec in manifest['sources']:
  if spec['id'] not in valid:continue
  f=Path(spec['file']);actions=read(f)['data']['game']['actions'];hashes[str(f).replace('\\','/')]=hashlib.sha256(f.read_bytes()).hexdigest();pending=None;putbacks=set()
  for i,e in enumerate(actions):
   k=e.get('actionType');sub=e.get('subType')
   if k in ['2pt','3pt'] and e.get('isFieldGoal'):
    if pending and e.get('personId')==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and k=='2pt' and e.get('area')!='Mid-Range' and 0<=sec(pending['clock'])-sec(e['clock'])<=3:putbacks.add(i)
    pending=None
   elif k=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
   elif k in ['turnover','freethrow','foul','period','jumpball'] or k=='rebound' and sub=='defensive':pending=None
  for s in stints[spec['id']]:
   teams={t['teamId']:tuple(sorted(t['players'])) for t in s['teams']}
   for i in range(s['startIndex'],s['endIndex']):
    e=actions[i]
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt']:continue
    if not e.get('assistPersonId'):continue
    if i in putbacks:excluded+=1;continue
    ids=tuple(pid for pid in teams[e['teamId']] if pid!=e['personId']);assert e['assistPersonId'] in ids
    counts[ids][e['assistPersonId']]+=1;joined+=1
 logs=np.array([[np.log(rate[pid]) for pid in ids] for ids in counts]);n=np.array([[q[pid] for pid in ids] for ids,q in counts.items()],dtype=float);data[season]=(logs,n)
 coverage.append({'season':season,'strictGames':len(valid),'assistedMakesJoined':joined,'excludedPutbackProxyAttempts':excluded,'lineups':len(counts)})
 print(season,coverage[-1],flush=True)
def loss(alpha,ss):
 vals=[]
 for season in ss:
  x,n=data[season];z=alpha*x;mx=z.max(axis=1,keepdims=True);lp=z-mx-np.log(np.exp(z-mx).sum(axis=1,keepdims=True));vals.append(float(-(n*lp).sum()/n.sum()))
 return sum(vals)/len(vals)
def fit(ss):
 lo,hi=.25,3
 for i in range(45):
  a=lo+(hi-lo)/3;b=hi-(hi-lo)/3
  if loss(a,ss)<loss(b,ss):hi=b
  else:lo=a
 return (lo+hi)/2
alpha=fit(seasons[:3]);out={'design':'Post-diagnostic global scalar, fit against assister CHOICES conditional on an assisted make, not FG% or player names or rankings. Strict five-player lineups, immediate OREB proxy attempts excluded. 60-minute source AST rate prior. Seasons equally weighted. Fit 2022-25; 2025-26 check was already seen historically, not genuinely blind.',
 'beta':alpha,'trainingSeasons':seasons[:3],'checkSeason':seasons[3],'coverage':coverage,'perSeason':[{'season':s,'fitAlpha':fit([s]),'nllAlpha1':loss(1,[s]),'nllTrainingAlpha':loss(alpha,[s])} for s in seasons],
 'usagePolicy':'This estimates observed relative assister demand conditional on a known assisted make. If adopted, conserve each lineup total terminal demand while exponentiating relative player terminal rates. Do not exponentiate shooting FG% or OVR.', 'sourceHashes':hashes}
(ROOT/'assist-fit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='sourceHashes'},ensure_ascii=False,indent=2),flush=True)

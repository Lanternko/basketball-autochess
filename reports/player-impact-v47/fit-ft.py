"""Select a common FT count prior on older seasons' heldout whole games."""
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-v47');hashes={}
def read(p):
 p=Path(p);hashes[p.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text(encoding='utf-8'))
cards=read(R/'source-cards.json');grid=[0,1,2,5,10,20,40,60,100,200];prepared=[]
for season in cards['seasons']:
 s=season['season'];file=f'data/defense-seventh/{s}/player-games.json' if s!='2025-26' else 'data/season-source/player-games.json';rs=read(file)['data']['resultSets'][0];rows=[dict(zip(rs['headers'],r)) for r in rs['rowSet']];games=set(season['gameIds']);totals=defaultdict(Counter);folds=[defaultdict(Counter) for _ in range(5)]
 for p in rows:
  if p['GAME_ID'] not in games:continue
  pid=p['PLAYER_ID'];f=int(hashlib.sha256(p['GAME_ID'].encode()).hexdigest()[:8],16)%5
  for k in ['FTM','FTA']:
   totals[pid][k]+=p[k];folds[f][pid][k]+=p[k]
 expected=defaultdict(Counter)
 for p in season['players']:
  for k in ['FTM','FTA']:expected[p['playerId']][k]+=p['observed'][k]
 assert all(totals[pid]==c for pid,c in expected.items()),s
 assert set(totals)==set(expected),s
 prepared.append({'season':s,'totals':totals,'folds':folds,'players':season['players']})
def crossfit(data,kappa):
 totalm=sum(c['FTM'] for c in data['totals'].values());totala=sum(c['FTA'] for c in data['totals'].values());nll=0.;att=0;errors=[]
 for test in data['folds']:
  heldm=sum(c['FTM'] for c in test.values());helda=sum(c['FTA'] for c in test.values());prior=(totalm-heldm)/(totala-helda)
  for pid,c in test.items():
   n=c['FTA'];m=c['FTM'];train=data['totals'][pid];ta=train['FTA']-n;tm=train['FTM']-m
   p=(tm+kappa*prior)/(ta+kappa) if ta+kappa else prior;p=np.clip(p,1e-9,1-1e-9)
   nll-=m*np.log(p)+(n-m)*np.log1p(-p);att+=n
   if n>=10:errors.append((n,abs(p-m/n)))
 return {'season':data['season'],'nll':float(nll),'attempts':att,'nllPerAttempt':float(nll/att),'weightedPlayerFoldMAE_pp':float(100*sum(n*e for n,e in errors)/sum(n for n,e in errors))}
table=[]
for k in grid:
 cells=[crossfit(d,k) for d in prepared[:3]];table.append({'kappa':k,'meanNllPerAttempt':float(np.mean([c['nllPerAttempt'] for c in cells])),'cells':cells})
selected=min(table,key=lambda r:(r['meanNllPerAttempt'],-r['kappa']))['kappa'];references={};checks=[]
for d in prepared:
 mean=sum(p['FTM'] for p in d['totals'].values())/sum(p['FTA'] for p in d['totals'].values());byid={pid:{'makes':c['FTM'],'attempts':c['FTA'],'probability':(c['FTM']+selected*mean)/(c['FTA']+selected) if c['FTA']+selected else mean} for pid,c in d['totals'].items()};references[d['season']]={'leagueProbability':mean,'players':byid};checks.append(crossfit(d,selected))
fit={'kappa':selected,'grid':grid,'selectionSeasons':[d['season'] for d in prepared[:3]],'targetExcludedFromSelection':True,'selection':'Minimum equal-season mean whole-game-five-fold heldout FT Bernoulli NLL per attempt; ties prefer stronger shrinkage. Same-season reconstruction, not future prediction. Player-game official logs exactly reconciled with frozen v46 observed FT totals, including traded players.','table':table,'crossfitChecks':checks,'references':references,'sourceSHA256':hashes}
(R/'ft-fit.json').write_text(json.dumps(fit,ensure_ascii=False),encoding='utf-8');print(json.dumps({'kappa':selected,'scores':[{k:v for k,v in r.items() if k!='cells'} for r in table],'crossfitChecks':checks}))

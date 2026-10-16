"""Independent raw-log reconstruction of every FT prior selection cell."""
import hashlib,json,math
from pathlib import Path
from collections import defaultdict
R=Path('reports/player-impact-v47');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));fit=read(R/'ft-fit.json');cards=read(R/'source-cards.json');cells=[];rootChecks=[]
for p,h in fit['sourceSHA256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
for s in cards['seasons']:
 season=s['season'];raw=read(f'data/defense-seventh/{season}/player-games.json' if season!='2025-26' else 'data/season-source/player-games.json')['data']['resultSets'][0];header=raw['headers'];indices={k:header.index(k) for k in ['PLAYER_ID','GAME_ID','FTM','FTA']};games=set(s['gameIds']);rows=[r for r in raw['rowSet'] if r[indices['GAME_ID']] in games];counts=defaultdict(lambda:[0,0]);folds=[defaultdict(lambda:[0,0]) for _ in range(5)]
 for r in rows:
  pid=r[indices['PLAYER_ID']];gid=r[indices['GAME_ID']];m,a=r[indices['FTM']],r[indices['FTA']];counts[pid][0]+=m;counts[pid][1]+=a;fold=int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5;folds[fold][pid][0]+=m;folds[fold][pid][1]+=a
 totalM=sum(c[0] for c in counts.values());totalA=sum(c[1] for c in counts.values());prior=totalM/totalA;ref=fit['references'][season];assert abs(ref['leagueProbability']-prior)<1e-12
 for pid,(m,a) in counts.items():
  p=ref['players'][str(pid)];assert p['makes']==m and p['attempts']==a;assert abs(p['probability']-(m+fit['kappa']*prior)/(a+fit['kappa']))<1e-12
 maxerr=0.
 for p in s['players']:
  m,a=counts[p['playerId']];old=max(.56,min(.9,(m+100*prior)/(a+100)));maxerr=max(maxerr,abs(old-p['oldProbability']))
 assert maxerr<1e-12
 models={k:0. for k in fit['grid']};models['legacy100cap']=0.;runtimeMin=1.;runtimeMax=0.
 for test in folds:
  tm=sum(c[0] for c in test.values());ta=sum(c[1] for c in test.values());trainMean=(totalM-tm)/(totalA-ta)
  for pid,(m,a) in test.items():
   pm,pa=counts[pid];pm-=m;pa-=a
   for k in models:
    n=100 if k=='legacy100cap' else k;p=(pm+n*trainMean)/(pa+n) if pa+n else trainMean
    if k=='legacy100cap':p=max(.56,min(.9,p))
    if k==fit['kappa']:runtimeMin=min(runtimeMin,p);runtimeMax=max(runtimeMax,p)
    p=max(1e-9,min(1-1e-9,p));models[k]-=m*math.log(p)+(a-m)*math.log1p(-p)
 assert runtimeMin>=.30 and runtimeMax<=.98
 if season in fit['selectionSeasons']:
  for row in fit['table']:
   expected=next(c for c in row['cells'] if c['season']==season);assert abs(models[row['kappa']]-expected['nll'])<1e-7
 selectedCheck=next(c for c in fit['crossfitChecks'] if c['season']==season);assert abs(models[fit['kappa']]-selectedCheck['nll'])<1e-7
 cells.append({'season':season,'attempts':totalA,'legacyNllPerAttempt':models['legacy100cap']/totalA,'newNllPerAttempt':models[fit['kappa']]/totalA,'crossfitProbabilityRange':[runtimeMin,runtimeMax]});rootChecks.append({'season':season,'rosterEntries':len(s['players']),'legacy100PriorAnd56To90PctClampExactlyReproduced':True,'maxError':maxerr})
assert fit['selectionSeasons']==[s['season'] for s in cards['seasons'][:3]] and '2025-26' not in fit['selectionSeasons']
assert fit['kappa']==min(fit['table'],key=lambda r:(sum(c['nllPerAttempt'] for c in r['cells'])/3,-r['kappa']))['kappa']
result={'passed':True,'allTenGridCellsEachOlderSeasonIndependentlyVerified':True,'targetExcludedFromSelection':True,'referencesRebuiltFromRawPlayerGames':True,'noSelectedFoldRuntimeClampMismatch':True,'legacyRootCauseChecks':rootChecks,'crossfitComparison':cells}
(R/'fit-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))

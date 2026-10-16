"""Independently regroup conditional scores, bootstrap, folds and all-player export."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path('reports/player-impact-v33')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fit=read(ROOT/'compensation-fit.json');protocol=read(ROOT/'fit-protocol.json')
assert fit['protocolSHA256']==sha(ROOT/'fit-protocol.json')
for p,h in protocol['hashes'].items():assert sha(p)==h,p
for f in ['data-verification.json','probability-verification.json']:
 d=read(ROOT/f);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p

def close(a,b):
 assert np.allclose(a,b,rtol=2e-12,atol=2e-8),(a,b)

def aggregate(ids,values,n):
 out=np.zeros(n);np.add.at(out,ids,values);return out

summaries=[];cached={};targetPlayers={};targetGames={}
for summary in fit['seasons']:
 season=summary['season'];d=read(ROOT/f'{season}-conditional-data.json');ix={c:i for i,c in enumerate(d['columns'])};rows=d['rows']
 col=lambda c:np.asarray([r[ix[c]] for r in rows],dtype=float)
 a,b,sm,sb,am=(col(c) for c in ['attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected'])
 count,own,assisted=(col(c) for c in ['attempts','selfMakes','assistedMakes']);teamTotal=count.sum(axis=1)
 keys=np.asarray([str(r[ix['gameId']])+'|'+str(r[ix['teamId']])+'|'+str(p) for r in rows for p in r[ix['playerIds']]])
 unique,groups=np.unique(keys,return_inverse=True);ng=len(unique)
 gameIds,game=np.unique(np.asarray([r[ix['gameId']] for r in rows]),return_inverse=True)
 folds=np.asarray([int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%5 for g in gameIds]);nGame=len(gameIds)
 gameAttempts=aggregate(game,teamTotal,nGame)
 groupCounts=aggregate(groups,count.ravel(),ng)
 def score(lam,detail=False):
  u=a+lam*b;den=u.sum(axis=1);p=u/den[:,None]
  mass=teamTotal[:,None]*p
  groupTotal=aggregate(groups,mass.ravel(),ng)
  q=mass/groupTotal[groups].reshape(mass.shape)
  primary=-count*np.log(q)
  out={'primaryNll':float(primary.sum()),'attempts':float(count.sum()),'gameLoss':aggregate(game,primary.sum(axis=1),nGame),'groupPrimary':aggregate(groups,primary.ravel(),ng),'p':p}
  if detail:
   ownRate=sm+lam*sb;ownMass=teamTotal[:,None]*ownRate/den[:,None]
   ownTotal=aggregate(groups,ownMass.ravel(),ng)[groups].reshape(ownMass.shape)
   ownQ=np.divide(ownMass,ownTotal,out=np.zeros_like(ownMass),where=ownTotal>0)
   ownLoss=-own*np.log(np.maximum(ownQ,1e-12))
   fraction=ownRate/(ownRate+am);bounded=np.clip(fraction,1e-12,1-1e-12)
   out.update(selfMadeScoringFloorNll=float(ownLoss.sum()),selfMakes=int(own.sum()),unsupportedSelfAllocationMakes=int(own[ownQ<=0].sum()),undefinedSelfAllocationMakes=int(own[ownTotal<=0].sum()),madeMarkNll=float((-own*np.log(bounded)-assisted*np.log1p(-bounded)).sum()),madeCount=int((own+assisted).sum()),unsupportedSelfMakes=int(own[fraction<=0].sum()),unsupportedAssistedMakes=int(assisted[fraction>=1].sum()),shooterChoiceNll=float((-count*np.log(p)).sum()),groupSelf=aggregate(groups,ownLoss.ravel(),ng))
  return out
 for record in summary['measurements']:
  actual=score(record['lambdaValue'],True)
  for k,v in record.items():
   if k not in ['label','lambdaValue']:close(actual[k],v)
 old=score(1,True);new=score(fit['training']['lambdaValue'],True)
 cached[season]={'old':old,'new':new,'folds':folds,'attempts':gameAttempts}
 assert len(unique)==summary['playerGameGroups'] and int((groupCounts>0).sum())==summary['positiveAttemptGroups']
 ratio=(np.log(new['p'])-np.log(old['p'])).ravel();lo=np.full(ng,np.inf);hi=np.full(ng,-np.inf)
 np.minimum.at(lo,groups,ratio);np.maximum.at(hi,groups,ratio)
 # The actual fitted endpoint is zero in this experiment, so this equals endpoint comparison.
 assert fit['training']['lambdaValue']==0
 informative=(groupCounts>0)&(hi-lo>1e-8)
 assert int(informative.sum())==summary['informativePlayerGames']
 if season=='2025-26':
  for i,gid in enumerate(gameIds):targetGames[gid]={'attempts':gameAttempts[i],'oldNll':old['gameLoss'][i],'fittedNll':new['gameLoss'][i]}
  playerIds=np.asarray([int(k.rsplit('|',1)[1]) for k in unique])
  groupOwn=aggregate(groups,own.ravel(),ng);groupAssisted=aggregate(groups,assisted.ravel(),ng)
  for pid in sorted(set(playerIds)):
   mask=playerIds==pid
   targetPlayers[int(pid)]={'playerId':int(pid),'strictGames':int(mask.sum()),'freshFga':int(groupCounts[mask].sum()),'unassistedMakes':int(groupOwn[mask].sum()),'assistedMakes':int(groupAssisted[mask].sum()),'informativeGames':int(informative[mask].sum()),'sourcePrimaryOldNll':float(old['groupPrimary'][mask].sum()),'sourcePrimaryFittedNll':float(new['groupPrimary'][mask].sum()),'sourceSelfMadeOldScoringFloorNll':float(old['groupSelf'][mask].sum()),'sourceSelfMadeFittedScoringFloorNll':float(new['groupSelf'][mask].sum())}
 else:
  # Independently recalculate all 101 training grid points and extended grid.
  vals={}
  for lam in sorted(set([x['lambdaValue'] for x in fit['training']['grid']]+[x['lambdaValue'] for x in fit['extendedDiagnostic']['grid']])):vals[lam]=score(lam)
  cached[season]['grid']=vals
 summaries.append({'season':season,'passed':True,'freshAttempts':int(count.sum())})
 print(json.dumps(summaries[-1]),flush=True)

older=list(cached)[:3]
for field in ['training','extendedDiagnostic']:
 for g in fit[field]['grid']:close(g['nllPerAttempt'],np.mean([cached[s]['grid'][g['lambdaValue']]['primaryNll']/cached[s]['grid'][g['lambdaValue']]['attempts'] for s in older]))
 assert fit[field]['lambdaValue']==min(fit[field]['grid'],key=lambda x:x['nllPerAttempt'])['lambdaValue']==0
for fold in fit['olderGameFolds']:
 assert fold['lambdaValue']==0
 for check in fold['checks']:
  c=cached[check['season']];mask=c['folds']==fold['fold']
  close(check['heldoutGames'],int(mask.sum()));close(check['attempts'],c['attempts'][mask].sum())
  close(check['oldNll'],c['old']['gameLoss'][mask].sum());close(check['fittedNll'],c['new']['gameLoss'][mask].sum())
 for lam in [g['lambdaValue'] for g in fit['training']['grid']]:
  loss=np.mean([c['grid'][lam]['gameLoss'][c['folds']!=fold['fold']].sum()/c['attempts'][c['folds']!=fold['fold']].sum() for s in older for c in [cached[s]]])
  if lam==0:best=loss
  assert loss>=best-1e-12
for p in fit['targetPlayers']:
 r=targetPlayers[p['playerId']]
 for k,v in p.items():close(r[k],v)
for g in fit['targetGames']:
 for k,v in targetGames[g['gameId']].items():close(g[k],v)
games=sorted(targetGames);gain=np.asarray([targetGames[g]['oldNll']-targetGames[g]['fittedNll'] for g in games]);attempts=np.asarray([targetGames[g]['attempts'] for g in games])
rng=np.random.default_rng(20261017);bootstrap=[]
for _ in range(2000):
 sample=rng.integers(len(games),size=len(games));bootstrap.append(gain[sample].sum()/attempts[sample].sum())
close(np.quantile(bootstrap,[.025,.975]),fit['conditionalWholeGameBootstrap95PerAttempt'])
olderGain=np.mean([(cached[s]['old']['primaryNll']-cached[s]['new']['primaryNll'])/cached[s]['old']['attempts'] for s in older])
close(olderGain,fit['olderHeldoutGainPerAttempt']);close(gain.sum(),fit['checkPrimaryGain']);close(gain.sum()/attempts.sum(),fit['checkGainPerAttempt'])
assert not fit['candidatePrimaryGatePassed']

source=Path('reports/player-impact-v31/2025-26-player-validation.csv');roster=list(csv.DictReader(source.open(encoding='utf-8-sig',newline='')))
assert len(roster)==len({r['playerId'] for r in roster})==582
assert set(targetPlayers)<=set(int(r['playerId']) for r in roster)
rows=[]
fields=['playerId','name','position','sourceCoverage','strictGames','freshFga','unassistedMakes','assistedMakes','informativeGames','sourcePrimaryOldNll','sourcePrimaryFittedNll','primaryNllGain','gainPerFreshFga','sourceSelfMadeOldScoringFloorNll','sourceSelfMadeFittedScoringFloorNll']
for player in roster:
 pid=int(player['playerId']);r={'playerId':pid,'name':player['name'],'position':player['position'],'sourceCoverage':'strict-PBP-present' if pid in targetPlayers else 'no-strict-PBP'}
 if pid in targetPlayers:
  r.update(targetPlayers[pid]);r['primaryNllGain']=r['sourcePrimaryOldNll']-r['sourcePrimaryFittedNll'];r['gainPerFreshFga']=r['primaryNllGain']/r['freshFga'] if r['freshFga'] else ''
 rows.append(r)
f=ROOT/'2025-26-all-player-conditional-scores.csv';assert not f.exists()
with f.open('w',encoding='utf-8-sig',newline='') as file:
 writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader();writer.writerows(rows)
assert sum(r.get('freshFga',0) for r in rows)==203079
out={'passed':True,'seasons':summaries,'rosterPlayers':len(rows),'strictPbpPlayers':len(targetPlayers),'missingPlayers':[r['name'] for r in rows if r['sourceCoverage']=='no-strict-PBP'],'allScoresAndGridRecomputed':True,'allOlderGameFoldsRecomputed':True,'fixedFitWholeGameBootstrapReplicates':2000,'allPlayerExportRejoined':True,'hashes':{str(p).replace('\\','/'):sha(p) for p in [ROOT/'verify-fit.py',ROOT/'fit-compensation.py',ROOT/'fit-protocol.json',ROOT/'compensation-fit.json',ROOT/'data-verification.json',ROOT/'probability-verification.json',f,source]}}
outFile=ROOT/'fit-verification.json';assert not outFile.exists();outFile.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2),flush=True)

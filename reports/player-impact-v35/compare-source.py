"""Compare fixed v35 to v30 predictions reconstructed in v33; no parameter fit."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-v35');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=read('reports/player-impact-v33/compensation-fit.json')
allPlayers=[];seasons=[];hashes={}
for season in ['2022-23','2023-24','2024-25','2025-26']:
 oldFile=Path(f'reports/player-impact-v33/{season}-conditional-data.json');newFile=R/f'{season}-conditional-data.json'
 old,new=read(oldFile),read(newFile)
 for k,v in old['coverage'].items():
  if k!='cappedInterceptions':assert new['coverage'][k]==v,(season,k)
 assert old['columns']==new['columns']
 ix={k:i for i,k in enumerate(old['columns'])};assert [r[:10] for r in old['rows']]==[r[:10] for r in new['rows']]
 rows=old['rows'];keys=np.asarray([str(r[0])+'|'+str(r[2])+'|'+str(pid) for r in rows for pid in r[6]])
 unique,groups=np.unique(keys,return_inverse=True);gameIds,game=np.unique(np.asarray([r[0] for r in rows]),return_inverse=True)
 counts=np.asarray([r[7] for r in rows]);own=np.asarray([r[8] for r in rows]);assisted=np.asarray([r[9] for r in rows]);totals=counts.sum(axis=1,keepdims=True)
 aggregate=lambda values:np.bincount(groups,weights=values.ravel(),minlength=len(unique))
 def score(doc,lam):
  a,b,sm,sb,am=[np.asarray([r[ix[k]] for r in doc['rows']]) for k in ['attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected']]
  u=a+lam*b;selfRate=sm+lam*sb;den=u.sum(axis=1,keepdims=True);p=u/den
  mass=totals*p;g=aggregate(mass);loss=-counts*np.log(mass/g[groups].reshape(mass.shape))
  ownMass=totals*selfRate/den;ownDen=aggregate(ownMass)[groups].reshape(ownMass.shape)
  ownQ=np.divide(ownMass,ownDen,out=np.zeros_like(ownMass),where=ownDen>0)
  selfLoss=-own*np.log(np.clip(ownQ,1e-12,1));fraction=selfRate/(selfRate+am);bounded=np.clip(fraction,1e-12,1-1e-12)
  mark=-own*np.log(bounded)-assisted*np.log1p(-bounded)
  gameLoss=np.bincount(game,weights=loss.sum(axis=1),minlength=len(gameIds))
  return {'primaryNll':float(loss.sum()),'attempts':int(counts.sum()),'shooterChoiceNll':float((-counts*np.log(p)).sum()),'selfMadeScoringFloorNll':float(selfLoss.sum()),'madeMarkScoringFloorNll':float(mark.sum()),'unsupportedSelfMakes':int(own[selfRate<=0].sum()),'unsupportedAssistedMakes':int(assisted[fraction>=1].sum()),'undefinedSelfAllocationMakes':int(own[ownDen<=0].sum()),'gameLoss':gameLoss,'groupLoss':aggregate(loss),'groupSelf':aggregate(selfLoss),'groupMark':aggregate(mark),'selfRate':selfRate}
 a,b=score(old,1),score(new,0)
 ref=next(s for s in baseline['seasons'] if s['season']==season)['measurements'][1]
 for k in ['primaryNll','attempts','shooterChoiceNll','selfMadeScoringFloorNll','unsupportedSelfMakes','unsupportedAssistedMakes','undefinedSelfAllocationMakes']:assert np.isclose(a[k],ref[k],atol=1e-7,rtol=1e-11),(season,k)
 assert np.all(b['selfRate']>0) and b['unsupportedSelfMakes']==0 and b['undefinedSelfAllocationMakes']==0
 gameAttempts=np.bincount(game,weights=totals.ravel(),minlength=len(gameIds));gain=a['gameLoss']-b['gameLoss']
 rng=np.random.default_rng(20261018);boot=[]
 for _ in range(2000):
  sample=rng.integers(len(gameIds),size=len(gameIds));boot.append(float(gain[sample].sum()/gameAttempts[sample].sum()))
 results={label:{k:v for k,v in score.items() if isinstance(v,(int,float))} for label,score in [('v30',a),('v35',b)]}
 result={'season':season,'coverage':new['coverage'],'scores':results,'primaryGain':float(gain.sum()),'gainPerAttempt':float(gain.sum()/counts.sum()),'fixedSourceWholeGameBootstrap95PerAttempt':np.quantile(boot,[.025,.975]).tolist(),'games':[{'gameId':gid,'attempts':int(gameAttempts[i]),'oldNll':float(a['gameLoss'][i]),'newNll':float(b['gameLoss'][i])} for i,gid in enumerate(gameIds)]}
 seasons.append(result)
 if season=='2025-26':
  playerIds=np.asarray([int(k.rsplit('|',1)[1]) for k in unique]);groupN=aggregate(counts);groupOwn=aggregate(own);groupAssisted=aggregate(assisted)
  for pid in sorted(set(playerIds)):
   mask=playerIds==pid;eventMask=np.asarray([r[6] for r in rows])==pid
   allPlayers.append({'playerId':int(pid),'sourceGames':int(mask.sum()),'freshFga':int(groupN[mask].sum()),'selfMakes':int(groupOwn[mask].sum()),'assistedMakes':int(groupAssisted[mask].sum()),'sourcePrimary_v30':float(a['groupLoss'][mask].sum()),'sourcePrimary_v35':float(b['groupLoss'][mask].sum()),'sourcePrimaryGain':float((a['groupLoss'][mask]-b['groupLoss'][mask]).sum()),'unsupportedSelf_v30':int(own[eventMask & (a['selfRate']<=0)].sum()),'unsupportedSelf_v35':int(own[eventMask & (b['selfRate']<=0)].sum())})
 for f in [oldFile,newFile]:hashes[str(f).replace('\\','/')]=sha(f)
 print(json.dumps({k:v for k,v in result.items() if k!='games'}),flush=True)
roster=list(csv.DictReader(Path('reports/player-impact-v31/2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='')));by={p['playerId']:p for p in allPlayers};rows=[]
for p in roster:
 pid=int(p['playerId']);rows.append({'playerId':pid,'name':p['name'],'position':p['position'],'sourceCoverage':'strict-PBP-present' if pid in by else 'no-strict-PBP',**by.get(pid,{})})
assert len(rows)==582 and sum(r.get('freshFga',0) for r in rows)==203079
f=R/'2025-26-source-comparison.csv';assert not f.exists()
with f.open('w',encoding='utf-8-sig',newline='') as out:
 writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
hashes[str(f).replace('\\','/')]=sha(f);hashes[str(R/'compare-source.py').replace('\\','/')]=sha(R/'compare-source.py')
out={'passed':True,'design':__doc__,'scope':'Whole-game fixed-source bootstrap, seed20261018,2000replicates each. Same-season full descriptors, no crossfit, not independent causal trials. Secondary floor scores explicitly diagnostic; zero support not hidden. New source centering is recomputed for new flow. No adoption/OVR.','allSourceSelfMakesNowSupported':True,'seasons':seasons,'players':allPlayers,'hashes':hashes}
f=R/'source-comparison.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')

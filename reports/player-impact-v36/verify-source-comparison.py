"""Independent dictionary/factorized likelihood audit, avoiding comparison scorer arrays."""
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=read(R/'source-comparison.json');assert out['passed']
for p,h in out['hashes'].items():assert sha(p)==h,p
close=lambda a,b:math.isclose(a,b,abs_tol=2e-7,rel_tol=1e-10)
targetPlayers={};seasons=[]
for s in out['seasons']:
 season=s['season'];computed={}
 for label,folder,lam in [('v30','reports/player-impact-v33',1),('v36',str(R),0)]:
  d=read(Path(folder)/f'{season}-conditional-data.json');groups={};gameFga=defaultdict(int);shooter=0;mark=0;unsupported=0;unsupportedAssisted=0;undefined=0;ownFloor=0
  for row in d['rows']:
   gid,_,tid,_,_,_,ids,counts,own,assisted,a,b,sm,sb,am=row
   total=sum(counts);u=[x+lam*y for x,y in zip(a,b)];den=sum(u);gameFga[gid]+=total
   for i,pid in enumerate(ids):
    key=(gid,tid,pid);g=groups.setdefault(key,{'n':0,'mass':0,'nLogMass':0,'own':0,'ownMass':0,'ownEvents':[],'mark':0,'unsupported':0,'assisted':0})
    mass=total*u[i]/den;selfRate=sm[i]+lam*sb[i];selfMass=total*selfRate/den
    g['n']+=counts[i];g['mass']+=mass;g['nLogMass']+=counts[i]*math.log(mass);g['own']+=own[i];g['ownMass']+=selfMass;g['ownEvents'].append((own[i],selfMass));g['assisted']+=assisted[i]
    fraction=selfRate/(selfRate+am[i]);bounded=max(1e-12,min(1-1e-12,fraction))
    g['mark']-=own[i]*math.log(bounded)+assisted[i]*math.log1p(-bounded)
    if selfRate==0:unsupported+=own[i];g['unsupported']+=own[i]
    if fraction==1:unsupportedAssisted+=assisted[i]
    shooter-=counts[i]*math.log(u[i]/den)
  gameNll=defaultdict(float);perPlayer=defaultdict(lambda:defaultdict(float))
  for (gid,tid,pid),g in groups.items():
   loss=g['n']*math.log(g['mass'])-g['nLogMass'];gameNll[gid]+=loss
   ownLoss=0
   if g['ownMass']==0:undefined+=g['own']
   for count,mass in g['ownEvents']:
    probability=mass/g['ownMass'] if g['ownMass'] else 0
    ownLoss-=count*math.log(max(1e-12,min(1,probability)))
   ownFloor+=ownLoss;mark+=g['mark']
   p=perPlayer[pid];p['sourceGames']+=1;p['freshFga']+=g['n'];p['selfMakes']+=g['own'];p['assistedMakes']+=g['assisted'];p['primary']+=loss;p['unsupported']+=g['unsupported']
  score={'primaryNll':sum(gameNll.values()),'attempts':sum(gameFga.values()),'shooterChoiceNll':shooter,'selfMadeScoringFloorNll':ownFloor,'madeMarkScoringFloorNll':mark,'unsupportedSelfMakes':unsupported,'unsupportedAssistedMakes':unsupportedAssisted,'undefinedSelfAllocationMakes':undefined}
  for k,v in s['scores'][label].items():assert close(score[k],v),(season,label,k,score[k],v)
  computed[label]=(gameNll,gameFga,perPlayer)
 for g in s['games']:
  gid=g['gameId'];assert g['attempts']==computed['v30'][1][gid]==computed['v36'][1][gid]
  assert close(g['oldNll'],computed['v30'][0][gid]) and close(g['newNll'],computed['v36'][0][gid])
 gids=sorted(computed['v30'][0]);gain=np.asarray([computed['v30'][0][g]-computed['v36'][0][g] for g in gids]);attempts=np.asarray([computed['v30'][1][g] for g in gids])
 assert close(float(gain.sum()),s['primaryGain']) and close(float(gain.sum()/attempts.sum()),s['gainPerAttempt'])
 rng=np.random.default_rng(20261018);boot=[]
 for _ in range(2000):
  sample=rng.integers(len(gids),size=len(gids));boot.append(float(gain[sample].sum()/attempts[sample].sum()))
 assert np.allclose(np.quantile(boot,[.025,.975]),s['fixedSourceWholeGameBootstrap95PerAttempt'],atol=1e-10,rtol=1e-8)
 if season=='2025-26':
  for p in out['players']:
   pid=p['playerId'];a,b=computed['v30'][2][pid],computed['v36'][2][pid]
   for k in ['sourceGames','freshFga','selfMakes','assistedMakes']:assert a[k]==b[k]==p[k]
   for k,v in [('sourcePrimary_v30',a['primary']),('sourcePrimary_v36',b['primary']),('sourcePrimaryGain',a['primary']-b['primary']),('unsupportedSelf_v30',a['unsupported']),('unsupportedSelf_v36',b['unsupported'])]:assert close(p[k],v),(pid,k)
   targetPlayers[pid]=p
 seasons.append({'season':season,'games':len(gids),'passed':True,'unsupportedSelf_v30':computed['v30'][2] and s['scores']['v30']['unsupportedSelfMakes'],'unsupportedSelf_v36':s['scores']['v36']['unsupportedSelfMakes']})
 print(json.dumps(seasons[-1]),flush=True)
csvFile=R/'2025-26-source-comparison.csv';rows=list(csv.DictReader(csvFile.open(encoding='utf-8-sig',newline='')));assert len(rows)==582
for row in rows:
 pid=int(row['playerId'])
 if pid in targetPlayers:
  for k,v in targetPlayers[pid].items():assert close(float(row[k]),v),(pid,k)
 else:assert row['sourceCoverage']=='no-strict-PBP' and row['freshFga']==''
files=[R/'source-comparison.json',csvFile,R/'verify-source-comparison.py']
result={'passed':True,'independentFactorizedScores':True,'allWholeGameBootstrapsRecomputed':True,'all582PlayerRowsVerified':True,'seasons':seasons,'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
f=R/'source-comparison-verification.json';assert not f.exists();f.write_text(json.dumps(result,indent=2),encoding='utf-8')

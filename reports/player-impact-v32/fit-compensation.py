"""Estimate source role compensation from within-player, within-game shot allocation."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar

ROOT=Path('reports/player-impact-v32');SEASONS=['2022-23','2023-24','2024-25','2025-26']
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[ROOT/f'{s}-conditional-data.json' for s in SEASONS]
protocol=dict(trainingSeasons=SEASONS[:3],checkSeason=SEASONS[3],folds=5,
    primary='Conditional allocation of each player-team-game fresh FGA total across that same game\'s actual lineups. Expected mass in stint = observed team fresh FGA count * predicted shooter probability. Player-game normalization cancels a fixed player-game shooting-volume level. This is a working conditional score, not independent causal trials.',
    parameter='lambda in[0,1]: v31 supported-self at0, v30 full residual-self at1. One common scalar, equal season weighting by NLL per actual FGA. Grid101 then bounded local refinement plus endpoints; extended[0,2] sensitivity is diagnostic only.',
    validation='Five whole-game folds in older three seasons, then fixed older fit checked on previously seen2025-26. Source role/rate/FG/foul and usage descriptors are frozen same-season inputs and are NOT cross-fitted, so this is NOT a genuinely blind/prospective/causal validation. No ranks/names/wins/onoff/simulation residual fitting.',
    secondary=['Unassisted made-FG allocation within same player-team-game, conditioning on its actual total; exact model own/caught EV choice.',
        'Assisted versus unassisted mark conditional on a made FG; scoring-only1e-12 probability floor with unsupported outcome counts reported.',
        'Standard shooter-choice multinomial within the five, with all FGA independent of makes.'],
    uncertainty='Target whole-game block bootstrap2000, seed20261017, fixed source descriptors and fitted parameter; no refit or source/model uncertainty.',
    candidateGate='Only consider an interior fitted mixture if older held-out primary gain>0, target primary gain>0 and its fixed-fit whole-game bootstrap95 lower bound>0. Any such candidate still needs ordinary four-season validation and complete OVR; boundaries or contradictory diagnostics do not justify a new adopted model.',
    hashes={str(f).replace('\\','/'):sha(f) for f in files}|{str(Path(__file__)).replace('\\','/'):sha(__file__)})
pf=ROOT/'fit-protocol.json';assert not pf.exists(),'Preserve frozen compensation fit protocol';pf.write_text(json.dumps(protocol,indent=2),encoding='utf-8')

class Dataset:
    def __init__(self,season):
        self.season=season;doc=read(ROOT/f'{season}-conditional-data.json');rows=doc['rows'];self.coverage=doc['coverage']
        ix={k:i for i,k in enumerate(doc['columns'])};self.gameIds=sorted({r[ix['gameId']] for r in rows});gameIndex={g:i for i,g in enumerate(self.gameIds)}
        self.game=np.array([gameIndex[r[ix['gameId']]] for r in rows]);self.fold=np.array([r[ix['gameFold']] for r in rows])
        for g,f in zip(self.game,self.fold):assert f==int(hashlib.sha256(self.gameIds[g].encode()).hexdigest()[:8],16)%5
        self.players=np.array([r[ix['playerIds']] for r in rows]);self.count=np.array([r[ix['attempts']] for r in rows],dtype=float)
        self.selfMade=np.array([r[ix['selfMakes']] for r in rows],dtype=float);self.assistedMade=np.array([r[ix['assistedMakes']] for r in rows],dtype=float)
        self.a=np.array([r[ix['attemptBase']] for r in rows]);self.b=np.array([r[ix['attemptSlope']] for r in rows]);self.sm=np.array([r[ix['selfMakeBase']] for r in rows]);self.sb=np.array([r[ix['selfMakeSlope']] for r in rows]);self.am=np.array([r[ix['assistedMakeExpected']] for r in rows])
        keys={};groups=[]
        for r in rows:
            for pid in r[ix['playerIds']]:
                key=(r[ix['gameId']],r[ix['teamId']],pid)
                if key not in keys:keys[key]=len(keys)
                groups.append(keys[key])
        self.group=np.array(groups);self.groups=len(keys);self.groupKeys=list(keys)
        self.groupN=np.bincount(self.group,weights=self.count.ravel(),minlength=self.groups)
        self.groupS=np.bincount(self.group,weights=self.selfMade.ravel(),minlength=self.groups)
        self.groupGame=np.array([gameIndex[k[0]] for k in keys]);self.groupFold=np.array([int(hashlib.sha256(k[0].encode()).hexdigest()[:8],16)%5 for k in keys])
        self.total=self.count.sum(axis=1,keepdims=True)
        assert self.count.sum()==doc['coverage']['freshAttempts'] and self.selfMade.sum()==doc['coverage']['selfMakes'] and self.assistedMade.sum()==doc['coverage']['assistedMakes']
        assert np.all(self.a>0) and np.all(self.b>=0) and np.all(self.selfMade+self.assistedMade<=self.count)

    def calculate(self,lam,details=False):
        u=self.a+lam*self.b;den=u.sum(axis=1,keepdims=True);p=u/den
        mass=self.total*p;g=np.bincount(self.group,weights=mass.ravel(),minlength=self.groups)
        lp=np.log(mass)-np.log(g[self.group].reshape(mass.shape))
        primary=-self.count*lp
        gameLoss=np.bincount(self.game,weights=primary.sum(axis=1),minlength=len(self.gameIds))
        gameAttempts=np.bincount(self.game,weights=self.total.ravel(),minlength=len(self.gameIds))
        result=dict(primaryNll=float(primary.sum()),attempts=float(self.count.sum()),gameLoss=gameLoss,gameAttempts=gameAttempts)
        if details:
            sm=self.sm+lam*self.sb
            massSelf=self.total*sm/den;gs=np.bincount(self.group,weights=massSelf.ravel(),minlength=self.groups)
            assert np.all(massSelf>0) and np.all(gs>0)
            selfLoss=-self.selfMade*(np.log(massSelf)-np.log(gs[self.group].reshape(massSelf.shape)))
            made=sm+self.am;selfFraction=sm/made
            unsupportedSelf=int(self.selfMade[selfFraction<=0].sum());unsupportedAssisted=int(self.assistedMade[selfFraction>=1].sum())
            bounded=np.clip(selfFraction,1e-12,1-1e-12)
            markLoss=-self.selfMade*np.log(bounded)-self.assistedMade*np.log1p(-bounded)
            shooterLoss=-self.count*np.log(p)
            groupPrimary=np.bincount(self.group,weights=primary.ravel(),minlength=self.groups)
            groupSelf=np.bincount(self.group,weights=selfLoss.ravel(),minlength=self.groups)
            result.update(selfMadeNll=float(selfLoss.sum()),selfMakes=int(self.selfMade.sum()),madeMarkNll=float(markLoss.sum()),madeCount=int((self.selfMade+self.assistedMade).sum()),unsupportedSelfMakes=unsupportedSelf,unsupportedAssistedMakes=unsupportedAssisted,
                shooterChoiceNll=float(shooterLoss.sum()),groupPrimary=groupPrimary,groupSelf=groupSelf,
                groupPredictedAttempts=g,sourceProbabilities=p)
        return result

data={s:Dataset(s) for s in SEASONS}

def objective(lam,seasons,excludeFold=None):
    scores=[]
    for season in seasons:
        d=data[season];r=d.calculate(lam)
        if excludeFold is None:scores.append(r['primaryNll']/r['attempts'])
        else:
            # Games are never split between training and held-out label sets.
            folds=np.array([int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%5 for g in d.gameIds]);m=folds!=excludeFold
            scores.append(float(r['gameLoss'][m].sum()/r['gameAttempts'][m].sum()))
    return float(np.mean(scores))

def fit(seasons,excludeFold=None,upper=1):
    grid=np.linspace(0,upper,101);losses=[objective(float(v),seasons,excludeFold) for v in grid];i=int(np.argmin(losses))
    lo=grid[max(0,i-1)];hi=grid[min(100,i+1)]
    opt=minimize_scalar(lambda v:objective(v,seasons,excludeFold),bounds=(lo,hi),method='bounded',options={'xatol':1e-9})
    candidates=[(float(grid[i]),losses[i]),(float(opt.x),float(opt.fun)),(0,losses[0]),(upper,losses[-1])]
    lam,loss=min(candidates,key=lambda p:p[1]);return dict(lambdaValue=lam,nllPerAttempt=loss,grid=[dict(lambdaValue=float(a),nllPerAttempt=b) for a,b in zip(grid,losses)])

train=fit(SEASONS[:3]);lam=train['lambdaValue'];extended=fit(SEASONS[:3],upper=2)
print(json.dumps(dict(trainingLambda=lam,extendedDiagnosticLambda=extended['lambdaValue'])),flush=True)
folds=[]
for fold in range(5):
    fitted=fit(SEASONS[:3],excludeFold=fold);chosen=fitted['lambdaValue'];checks=[]
    for season in SEASONS[:3]:
        d=data[season];gameFolds=np.array([int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%5 for g in d.gameIds]);m=gameFolds==fold
        old=d.calculate(1);new=d.calculate(chosen)
        checks.append(dict(season=season,heldoutGames=int(m.sum()),attempts=float(old['gameAttempts'][m].sum()),oldNll=float(old['gameLoss'][m].sum()),fittedNll=float(new['gameLoss'][m].sum())))
    folds.append(dict(fold=fold,lambdaValue=chosen,checks=checks));print(json.dumps(folds[-1]),flush=True)

summaries=[];targetGames=[];perPlayer=[]
for season,d in data.items():
    measurements={label:d.calculate(value,True) for label,value in [('supportedOnly',0),('fullCompensation',1),('olderFit',lam)]}
    results=[]
    for label,r in measurements.items():results.append(dict(label=label,lambdaValue={'supportedOnly':0,'fullCompensation':1,'olderFit':lam}[label],**{k:v for k,v in r.items() if isinstance(v,(int,float))}))
    # Count conditional player-game groups with at least two supported stints and
    # a change in relative predicted allocation between the two endpoints.
    p0=measurements['supportedOnly']['sourceProbabilities'];p1=measurements['fullCompensation']['sourceProbabilities']
    logRatio=(np.log(p0)-np.log(p1)).ravel();groupMin=np.full(d.groups,np.inf);groupMax=np.full(d.groups,-np.inf)
    np.minimum.at(groupMin,d.group,logRatio);np.maximum.at(groupMax,d.group,logRatio)
    informative=(d.groupN>0)&(groupMax-groupMin>1e-8)
    summaries.append(dict(season=season,coverage=d.coverage,playerGameGroups=d.groups,positiveAttemptGroups=int((d.groupN>0).sum()),informativePlayerGames=int(informative.sum()),measurements=results))
    if season==SEASONS[-1]:
        old=measurements['fullCompensation'];new=measurements['olderFit']
        for j,gid in enumerate(d.gameIds):targetGames.append(dict(gameId=gid,attempts=float(old['gameAttempts'][j]),oldNll=float(old['gameLoss'][j]),fittedNll=float(new['gameLoss'][j])))
        ids=sorted(set(int(pid) for pid in d.players.ravel()))
        for pid in ids:
            ix=np.array([i for i,k in enumerate(d.groupKeys) if k[2]==pid]);mask=d.players==pid
            perPlayer.append(dict(playerId=pid,strictGames=len(ix),freshFga=int(d.groupN[ix].sum()),unassistedMakes=int(d.groupS[ix].sum()),assistedMakes=int(d.assistedMade[mask].sum()),informativeGames=int(informative[ix].sum()),
                sourcePrimaryOldNll=float(old['groupPrimary'][ix].sum()),sourcePrimaryFittedNll=float(new['groupPrimary'][ix].sum()),sourceSelfMadeOldNll=float(old['groupSelf'][ix].sum()),sourceSelfMadeFittedNll=float(new['groupSelf'][ix].sum())))

gain=np.array([r['oldNll']-r['fittedNll'] for r in targetGames]);attempts=np.array([r['attempts'] for r in targetGames]);rng=np.random.default_rng(20261017)
boot=[]
for _ in range(2000):
    ix=rng.integers(len(gain),size=len(gain));boot.append(float(gain[ix].sum()/attempts[ix].sum()))
ci=np.quantile(boot,[.025,.975]).tolist()
olderGain=float(np.mean([np.sum([c['oldNll']-c['fittedNll'] for f in folds for c in f['checks'] if c['season']==s])/np.sum([c['attempts'] for f in folds for c in f['checks'] if c['season']==s]) for s in SEASONS[:3]]))
passes=0<lam<1 and olderGain>0 and gain.sum()>0 and ci[0]>0
out=dict(design=__doc__,protocolSHA256=sha(pf),training=train,extendedDiagnostic=extended,olderGameFolds=folds,
    olderHeldoutGainPerAttempt=olderGain,checkPrimaryGain=float(gain.sum()),checkGainPerAttempt=float(gain.sum()/attempts.sum()),conditionalWholeGameBootstrap95PerAttempt=ci,candidatePrimaryGatePassed=bool(passes),
    seasons=summaries,targetGames=targetGames,targetPlayers=perPlayer,
    decision='Only a conditional source allocation criterion; no causal self-creation capability claim, no model adoption or new OVR.')
f=ROOT/'compensation-fit.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['training','extendedDiagnostic','olderGameFolds','seasons','targetGames','targetPlayers']},indent=2),flush=True)

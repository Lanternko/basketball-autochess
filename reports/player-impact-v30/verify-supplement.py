"""Independently recheck stored probe, passing and tracking accounting; not skill certification."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path('reports/player-impact-v30')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):
    assert math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10),(a,b)
def hashes(doc):
    for p,h in doc['hashes'].items():assert sha(p)==h,p

protocol=read(ROOT/'ovr-probe-protocol.json');hashes(protocol)
checkpoint=read(ROOT/'ovr-probe-checkpoint.json');manifest=read(ROOT/'ovr-probe-manifest.json')
assert sha(ROOT/'ovr-probe-checkpoint.json')==manifest['checkpointSHA256']
summary=read(ROOT/'ovr-probe-summary.json')
old={r['result']['playerId']:r['result'] for r in read('reports/player-impact-v29/checkpoint.json')['rows']}
assert set(protocol['ids'])=={r['result']['playerId'] for r in checkpoint['rows']}
assert len(checkpoint['rows'])==10 and sum(r['result']['simulatedGames'] for r in checkpoint['rows'])==9600
by={p['playerId']:p for p in summary['players']}
def check_estimate(values,result):
    groups=defaultdict(list)
    for (op,i),v in values.items():groups[op].append(v)
    assert len(groups)==30 and all(len(v)==4 for v in groups.values())
    # Equal opponent weights, paired seats averaged before variance estimation.
    means=[sum(v)/len(v) for v in groups.values()]
    mean=sum(means)/30
    se=math.sqrt(sum(sum((x-sum(v)/4)**2 for x in v)/3/4 for v in groups.values())/900)
    close(result['mean'],mean);close(result['standardError'],se)
    for a,b in zip(result['ci95'],[mean-1.96*se,mean+1.96*se]):close(a,b)

for row in checkpoint['rows']:
    p=row['result'];assert p['simulatedGames']==960
    assert {a['arm'] for a in p['arms']}=={'fullCapCounterfactual','supportedHealthy'}
    before={a['arm']:a for a in old[p['playerId']]['arms']}
    reported={a['arm']:a for a in by[p['playerId']]['arms']}
    for a in p['arms']:
        b=before[a['arm']];assert a['minutes']==b['minutes'] and len(a['games'])==len(b['games'])==120
        new={};prior={}
        for x,y in zip(a['games'],b['games']):
            for k in ['opponent','seed','i','phase']:assert x[k]==y[k]
            assert len(x['pair'])==len(y['pair'])==2 and {v['side'] for v in x['pair']}=={0,1}
            for xx,yy in zip(x['pair'],y['pair']):
                assert xx['side']==yy['side'] and xx['playerMinutes']==yy['playerMinutes']
                close(xx['playerMinutes'],a['minutes'])
                s=xx['playerStats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'] and s['ast']>=0
                assert 0<=s['fg3m']<=s['fg3a']<=s['fga'] and 0<=s['fgm']<=s['fga']
            key=(x['opponent'],x['i']);assert key not in new
            new[key]=sum(z['margin']-z['baselineMargin'] for z in x['pair'])/2
            prior[key]=sum(z['margin']-z['baselineMargin'] for z in y['pair'])/2
        r=reported[a['arm']]
        check_estimate(new,r['v30']);check_estimate(prior,r['v28'])
        check_estimate({k:new[k]-prior[k] for k in new},r['pairedChange'])

fp=read(ROOT/'fit-protocol.json');hashes(fp)
fit=read(ROOT/'passing-fit.json');assert sha(ROOT/'fit-protocol.json')==fit['protocolSHA256']
ps=read(ROOT/'passing-summary.json');assert sha(ROOT/'passing-fit.json')==ps['passingFitSHA256']
for zone in ['2','3']:
    for model in ['receiverOnly','joint']:
        candidates=[c for c in fit['cv'] if c['zone']==zone and (c['passerPrecision'] is not None)==(model=='joint')]
        best=min(candidates,key=lambda c:c['nllPerAttempt'])
        assert {k:v for k,v in best.items() if k!='foldScores'}==fit['chosen'][zone][model]
        assert {x['season'] for c in candidates for x in c['foldScores']}==set(fp['trainingSeasons'])
        for c in candidates:
            close(c['nll'],sum(x['nll'] for x in c['foldScores']))
            close(c['attempts'],sum(x['attempts'] for x in c['foldScores']))
            close(c['nllPerAttempt'],c['nll']/c['attempts'])
combined={}
for target in fit['target']:
    zone=target['zone'];doc=read('reports/player-impact-v21/raw/2025-26/passing-pairs-league.json')
    t=next(t for t in doc['data']['resultSets'] if t['name']=='PassesMade')
    source=[dict(zip(t['headers'],r)) for r in t['rowSet']]
    source=[r for r in source if r['PLAYER_ID']!=r['PASS_TEAMMATE_PLAYER_ID'] and r['FG'+zone+'A']>0]
    assert len(source)==len(target['predictions'])
    losses=defaultdict(float);attempts=Counter()
    sign=1 if target['model']=='receiverOnly' else -1
    for r,q in zip(source,target['predictions']):
        team,a,b=r['TEAM_ID'],r['PLAYER_ID'],r['PASS_TEAMMATE_PLAYER_ID']
        fold=int(hashlib.sha256(f'{team}/{a}/{b}'.encode()).hexdigest()[:8],16)%5
        assert (q['teamId'],q['passerId'],q['receiverId'],q['fold'],q['made'],q['attempts'])==(team,a,b,fold,r['FG'+zone+'M'],r['FG'+zone+'A'])
        p=q['probability'];assert 0<p<1
        loss=-q['made']*math.log(p)-(q['attempts']-q['made'])*math.log1p(-p)
        losses[fold]+=loss;attempts[fold]+=q['attempts']
        key=(team,a,b);combined[key]=combined.get(key,0)+sign*loss
    close(target['nll'],sum(losses.values()));close(target['attempts'],sum(attempts.values()))
    for f in target['foldScores']:close(f['nll'],losses[f['fold']]);close(f['attempts'],attempts[f['fold']])
close(ps['combinedNllGain'],sum(combined.values()));assert ps['jointPairBlocks']==len(combined)
rng=np.random.default_rng(20261016);values=np.array(list(combined.values()))
boot=[rng.choice(values,size=len(values),replace=True).sum() for _ in range(2000)]
for a,b in zip(ps['conditionalPairBootstrap95'],np.quantile(boot,[.025,.975])):close(a,b)

tracking=read(ROOT/'shot-tracking-audit.json');hashes(tracking)
fetch=read(ROOT/'shot-tracking-fetch-2022-23_2023-24_2024-25_2025-26.json')
assert len(fetch['jobs'])==12 and not fetch['failures']
for job in fetch['jobs']:
    assert sha(job['file'])==job['sha256']
    doc=read(job['file']);t=doc['data']['resultSets'];t=t[0] if isinstance(t,list) else t
    rows=[dict(zip(t['headers'],r)) for r in t['rowSet']]
    assert len(rows)==job['rows']
    audit=next(s for s in tracking['seasons'] if s['season']==job['season'])
    k={'Drives':'drives','CatchShoot':'catchShoot','PullUpShot':'pullUp'}[job['measure']]
    actual={p['playerId']:p[k] for p in audit['players']}
    assert actual=={r['PLAYER_ID']:r for r in rows}
    for field,stats in audit['totals'][job['measure']].items():
        close(stats['knownSum'],sum(r[field] for r in rows if r[field] is not None))
        assert stats['nullRows']==sum(r[field] is None for r in rows)

out=dict(passed=True,probePlayers=10,probeGames=9600,allProbeEstimatesAndPairedIntervalsRecomputed=True,
    sourcePassingPairCountsAndFoldsRechecked=True,allStoredHeldoutLossesRecomputed=True,
    conditionalPairBootstrapRecomputed=True,trackingFiles=12,allTrackingRowsExactlyPreserved=True,
    scope='Accounting and conditional estimates only; no causal or OVR adoption certification.',
    hashes={str(p).replace('\\','/'):sha(p) for p in [Path(__file__),ROOT/'ovr-probe-protocol.json',ROOT/'ovr-probe-checkpoint.json',ROOT/'ovr-probe-summary.json',ROOT/'fit-protocol.json',ROOT/'passing-fit.json',ROOT/'passing-summary.json',ROOT/'shot-tracking-audit.json']})
(ROOT/'supplement-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

"""Independently recheck stored probe, passing and tracking accounting; not skill certification."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path('reports/player-impact-v37')
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
old={r['result']['playerId']:r['result'] for r in read('reports/player-impact-v30/ovr-probe-checkpoint.json')['rows']}
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
        check_estimate(new,r['v37']);check_estimate(prior,r['v30'])
        check_estimate({k:new[k]-prior[k] for k in new},r['pairedChange'])

out=dict(passed=True,probePlayers=10,probeGames=9600,allProbeEstimatesAndPairedIntervalsRecomputed=True,
    scope='Fixed-input paired simulation estimates only; no causal or ranking certification.',
    hashes={str(p).replace('\\','/'):sha(p) for p in [Path(__file__),ROOT/'ovr-probe-protocol.json',ROOT/'ovr-probe-checkpoint.json',ROOT/'ovr-probe-summary.json']})
(ROOT/'supplement-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

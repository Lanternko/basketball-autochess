import hashlib
import json
import math
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-v30');fit=json.loads((ROOT/'passing-fit.json').read_text(encoding='utf-8'))
zones=[];combined={}
for zone in ['2','3']:
    target={x['model']:x for x in fit['target'] if x['zone']==zone}
    gains=[]
    for a,b in zip(target['receiverOnly']['predictions'],target['joint']['predictions']):
        for field in ['teamId','passerId','receiverId','made','attempts','fold']:assert a[field]==b[field]
        y,n,p,q=a['made'],a['attempts'],a['probability'],b['probability']
        gain=-y*math.log(p/q)-(n-y)*math.log((1-p)/(1-q));gains.append(gain)
        key=(a['teamId'],a['passerId'],a['receiverId']);combined[key]=combined.get(key,0)+gain
    zone_result=dict(zone=zone,attempts=target['receiverOnly']['attempts'],heldoutPairs=len(gains),
        receiverOnlyNll=target['receiverOnly']['nll'],jointNll=target['joint']['nll'],
        heldoutNllGain=sum(gains),
        receiverOnlyNllPerAttempt=target['receiverOnly']['nll']/target['receiverOnly']['attempts'],
        jointNllPerAttempt=target['joint']['nll']/target['joint']['attempts'],
        priorSelection=fit['chosen'][zone])
    zones.append(zone_result)
rng=np.random.default_rng(20261016);v=np.array(list(combined.values()))
boot=np.array([rng.choice(v,size=len(v),replace=True).sum() for _ in range(2000)])
out=dict(design='Target held-out-pair NLL differences with hyperparameters selected on older seasons. Positive gain favors passer+receiver model. Conditional pair-block bootstrap combines 2pt/3pt contributions for the same directed team/passer/receiver pair; fixed fitted predictions only, does not refit folds or cover team/season/parameter uncertainty. No runtime passing bonus.',zones=zones,
    jointPairBlocks=len(v),combinedNllGain=float(v.sum()),conditionalPairBootstrap95=np.quantile(boot,[.025,.975]).tolist(),
    passingFitSHA256=hashlib.sha256((ROOT/'passing-fit.json').read_bytes()).hexdigest())
(ROOT/'passing-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['zones','design']}))

import json
import math
import statistics
from pathlib import Path
ROOT=Path('reports/player-impact-v37')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
current=read(ROOT/'ovr-probe-checkpoint.json');previous=read('reports/player-impact-v30/ovr-probe-checkpoint.json')
old={p['result']['playerId']:p['result'] for p in previous['rows']}
assert len(current['rows'])==10
def estimate(values):
    grouped={}
    for (j,i),v in values.items():grouped.setdefault(j,[]).append(v)
    mean=statistics.mean(statistics.mean(v) for v in grouped.values())
    se=math.sqrt(sum(statistics.variance(v)/len(v) for v in grouped.values())/len(grouped)**2)
    return dict(mean=mean,standardError=se,ci95=[mean-1.96*se,mean+1.96*se])
players=[]
for row in current['rows']:
    p=row['result'];before={a['arm']:a for a in old[p['playerId']]['arms']};arms=[]
    for a in p['arms']:
        b=before[a['arm']];assert a['minutes']==b['minutes']
        for ga,gb in zip(a['games'],b['games']):
            for key in ['opponent','seed','i','phase']:assert ga[key]==gb[key]
            for pa,pb in zip(ga['pair'],gb['pair']):assert pa['side']==pb['side'] and pa['playerMinutes']==pb['playerMinutes']
        def margin(g):return statistics.mean(v['margin']-v['baselineMargin'] for v in g['pair'])
        new={(g['opponent'],g['i']):margin(g) for g in a['games']};prior={(g['opponent'],g['i']):margin(g) for g in b['games']}
        arms.append(dict(arm=a['arm'],minutes=a['minutes'],v30=estimate(prior),v37=estimate(new),
            pairedChange=estimate({k:new[k]-prior[k] for k in new})))
    players.append(dict(playerId=p['playerId'],name=p['name'],position=p['position'],arms=arms))
out=dict(design='Current v37 vs archived v30 matched workload experiment: same source load, cap, natural position, four distinct mean70 profiles, opponent primaries, two seats/phases and seeds. Both versions compare against their own matched same-minute average70 baseline. Self/receive flow and context recentering also affect synthetic teammates; source roles and attributes unchanged. Conditional simulation CIs only; 10 selected players, no full OVR or ranking claim.',players=players,
    simulatedGames=sum(p['result']['simulatedGames'] for p in current['rows']))
(ROOT/'ovr-probe-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(players=len(players),games=out['simulatedGames'])))

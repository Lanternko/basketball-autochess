import json,math
from pathlib import Path
from collections import defaultdict
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
p=read(R/'probe-protocol.json');state=read(R/'probe-checkpoint.json');source=read('reports/player-impact-v29/workload-source.json')
assert len(state['rows'])==20
by={(r['job']['id'],r['job']['variant']):r['result'] for r in state['rows']}
def estimate(values):
 groups=defaultdict(list)
 for (op,i),x in values.items():groups[op].append(x)
 assert len(groups)==30 and all(len(xs)==4 for xs in groups.values())
 mean=sum(sum(xs)/4 for xs in groups.values())/30;se=math.sqrt(sum(sum((x-sum(xs)/4)**2 for x in xs)/3/4 for xs in groups.values())/900)
 return {'mean':mean,'standardError':se,'ci95':[mean-1.96*se,mean+1.96*se]}
def margins(arm):return {(g['opponent'],g['i']):sum(x['margin']-x['baselineMargin'] for x in g['pair'])/2 for g in arm['games']}
def stats(arm,key):return {(g['opponent'],g['i']):sum(x['playerStats'][key] for x in g['pair'])/2 for g in arm['games']}
def difference(a,b):assert set(a)==set(b);return {k:a[k]-b[k] for k in a}
players=[]
for pid in p['ids']:
 a,b=by[pid,'v39'],by[pid,'v41'];arms=[]
 for x in a['arms']:
  y=next(t for t in b['arms'] if t['arm']==x['arm']);assert x['minutes']==y['minutes'];av,bv=margins(x),margins(y)
  counts={k:{'v39PerWorkloadGame':estimate(stats(x,k)),'v41PerWorkloadGame':estimate(stats(y,k)),'change':estimate(difference(stats(y,k),stats(x,k)))} for k in x['games'][0]['pair'][0]['playerStats']}
  arms.append({'arm':x['arm'],'minutes':x['minutes'],'v39':estimate(av),'v41':estimate(bv),'change':estimate(difference(bv,av)),'stats':counts})
 healthy=next(t for t in arms if t['arm']=='supportedHealthy')
 rates=sorted([h['documentedInjuryIllnessGames']/h['listedGames'] for h in source['players'][str(pid)]['history'].values() if h['historyCoverageAdequate']],reverse=True);persistent=rates[1] if len(rates)>1 else 0
 sensitivity={v:[{'coefficient':c,'persistentRate':persistent,'healthyContribution':healthy[v]['mean'],'deduction':max(0,healthy[v]['mean'])*c*persistent,'adjustedContribution':healthy[v]['mean']-max(0,healthy[v]['mean'])*c*persistent} for c in [0,.05,.1]] for v in p['variants']}
 extension={v:estimate(difference(margins(next(t for t in by[pid,v]['arms'] if t['arm']=='fullCapCounterfactual')),margins(next(t for t in by[pid,v]['arms'] if t['arm']=='supportedHealthy')))) for v in p['variants']}
 players.append({'playerId':pid,'name':a['name'],'position':a['position'],'arms':arms,'fullCapMinusSupportedContribution':extension,'reliabilitySensitivity':sensitivity})
out={'scope':'Selected10 diagnostic players; canonical source roles and raw attributes unchanged. Two workloads,30 fixed opponents,4 seeds/rotation phases, two seats, paired average70 replacement baseline. Conditional approximate normal Monte Carlo CIs use within-opponent seed variance; no multiplicity correction or model/source uncertainty. Source defense association and same-season reconstruction, not causal NBA impact, a full ranking or adoption. Recurrence coefficients are disclosed preference sensitivities, not medical estimates.','players':players,'simulatedGames':sum(r['result']['simulatedGames'] for r in state['rows'])}
assert out['simulatedGames']==19200
(R/'probe-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('Summarized10 players,19200 paired workload diagnostic games.')

import json,math
from pathlib import Path
from collections import defaultdict
R=Path('reports/player-impact-v38');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));state=read(R/'checkpoint.json')
assert len(state['rows'])==20
by={(r['job']['id'],r['job']['variant']):r['result'] for r in state['rows']}
archived={v:{r['result']['playerId']:r['result'] for r in read(f'reports/player-impact-{v}/ovr-probe-checkpoint.json')['rows']} for v in ['v30','v37']}
def estimate(values):
 g=defaultdict(list)
 for (op,i),x in values.items():g[op].append(x)
 assert len(g)==30 and all(len(xs)==4 for xs in g.values())
 mean=sum(sum(xs)/4 for xs in g.values())/30;se=math.sqrt(sum(sum((x-sum(xs)/4)**2 for x in xs)/3/4 for xs in g.values())/900)
 return {'mean':mean,'standardError':se,'ci95':[mean-1.96*se,mean+1.96*se]}
def margins(arm):return {(g['opponent'],g['i']):sum(p['margin']-p['baselineMargin'] for p in g['pair'])/2 for g in arm['games']}
def delta(a,b):assert set(a)==set(b);return {k:a[k]-b[k] for k in a}
players=[]
for pid in read(R/'protocol.json')['ids']:
 p=by[pid,'v30'];q=by[pid,'v37'];arms=[]
 for a in p['arms']:
  b=next(r for r in q['arms'] if r['arm']==a['arm']);assert a['minutes']==b['minutes'];av,bv=margins(a),margins(b);fix={}
  for version,new in [('v30',av),('v37',bv)]:
   before=next(r for r in archived[version][pid]['arms'] if r['arm']==a['arm']);assert before['minutes']==a['minutes'];fix[version]=estimate(delta(new,margins(before)))
  stats={}
  for key in a['games'][0]['pair'][0]['playerStats']:
   values=lambda arm:{(g['opponent'],g['i']):sum(p['playerStats'][key] for p in g['pair'])/2 for g in arm['games']}
   x,y=values(a),values(b);within={}
   for version,new in [('v30',x),('v37',y)]:
    before=next(r for r in archived[version][pid]['arms'] if r['arm']==a['arm']);within[version]=estimate(delta(new,values(before)))
   stats[key]={'v30CanonicalPerWorkloadGame':sum(x.values())/120,'v37CanonicalPerWorkloadGame':sum(y.values())/120,'transportChange':estimate(delta(y,x)),'inputCorrectionChanges':within}
  arms.append({'arm':a['arm'],'minutes':a['minutes'],'v30Canonical':estimate(av),'v37Canonical':estimate(bv),'transportChange':estimate(delta(bv,av)),'inputCorrectionChanges':fix,'stats':stats})
 players.append({'playerId':pid,'name':p['name'],'position':p['position'],'arms':arms})
out={'scope':'Exactly shared canonical source roles, attributes, workloads, distinct mean70 profiles and opponents; transport-specific source centering is intentional. Compare canonical v37 vs canonical v30. Input-correction changes versus old archives separately quantified within each transport. Selected10 diagnostic players; no full ranking, adoption or causal NBA claim. Conditional simulation CIs, no multiplicity adjustment or source/model uncertainty.','players':players,'simulatedGames':sum(r['result']['simulatedGames'] for r in state['rows'])}
(R/'summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'players':len(players),'games':out['simulatedGames']}))

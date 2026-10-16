import json,statistics
from pathlib import Path
root=Path(__file__).parent
ps=json.loads((root/'ranking.json').read_text(encoding='utf-8'))['players']
views=[]
for indices in [(0,1),(2,3)]:
 vals={p['playerId']:statistics.mean(statistics.mean(s['values'][i] for i in indices) for s in p['healthy']['strata']) for p in ps}
 rank={pid:i+1 for i,pid in enumerate(sorted(vals,key=lambda k:(-vals[k],k)))};views.append((vals,rank))
a,b=views;topA={i for i,r in a[1].items() if r<=20};topB={i for i,r in b[1].items() if r<=20}
out={'splitDefinition':'seeds 0,1 versus 2,3; both rotation phases, all 30 fixed opponents and two seats retained','postRunDiagnostic':True,'spearman':statistics.correlation([a[1][p['playerId']] for p in ps],[b[1][p['playerId']] for p in ps]),'top20Intersection':len(topA&topB),'top20Jaccard':len(topA&topB)/len(topA|topB),'medianConditional95HalfWidth':statistics.median((p['healthy']['ci95'][1]-p['healthy']['ci95'][0])/2 for p in ps),'focus':[]}
for p in ps:
 if p['rank']<=20 or p['name'] in ['Cade Cunningham','Stephen Curry','Mitchell Robinson','Neemias Queta']:
  out['focus'].append({'name':p['name'],'fullRank':p['rank'],'halfRanks':[a[1][p['playerId']],b[1][p['playerId']]],'contribution':p['healthy']['meanContribution'],'ci95':p['healthy']['ci95']})
(root/'stability.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='focus'},ensure_ascii=True))

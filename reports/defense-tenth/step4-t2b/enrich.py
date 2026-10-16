import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,ast,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime,timezone
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(f,x):(O/f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
P=read(O/'protocol.json');profiles=read(O/'profiles.json');org=read(O/'organizers.json')
counts=read(O/'onoff-game-counts.json');cases=read(O/'cases.json');injuries=read(O/'injury-evidence.json')
# Extra make-production split is explicitly post-hoc. It never supplies a missing assisted-attempt label.
explore={'registeredAt':datetime.now(timezone.utc).isoformat(),'label':'事後探索；已看過分類結果；不作預登記假說驗收','rule':'within paint/mid/three, target FGA times prior-minus-current assisted FGM/FGA and unassisted FGM/FGA; exclude prior-zero-FGA zones, show covered target attempts; this is production, not assisted/unassisted FG%'}
if (O/'exploration-supplement.json').exists():
 old=read(O/'exploration-supplement.json');assert old['rule']==explore['rule'] and old['label']==explore['label'];explore=old
else:save('exploration-supplement.json',explore)
(O/'exploration-supplement.sha256').write_text(hashlib.sha256((O/'exploration-supplement.json').read_bytes()).hexdigest()+'  exploration-supplement.json\n',encoding='utf8')
pbp=read(O/'overall-pbp-counts.json');by=defaultdict(Counter)
for r in pbp:
 for tid in [str(r['team']),'0']:by[r['season'],tid,str(r['player']),r['zone']].update({k:r[k] for k in ['a','m','am']})
for c in cases:
 tid=str(c['organizer']['teamId']);summaries=[]
 for q in c['players']:
  q['injuryEvidence']=[x for x in injuries['sources'] if q['id'] in x['ids'] and x['season'] in [c['season'],c['prior']]]
  specific={('2025-11-16',1630174):'Nesmith 膝傷。',('2025-11-16',1629614):'Nembhard 肩傷。',('2025-11-16',1631097):'Mathurin 腳趾傷。',('2024-01-29',1629634):'Clarke 跟腱術後復健。',('2024-01-29',1631222):'LaRavia 腳踝傷。'}
  q['injuryEvidence']=[{**x,'note':specific.get((x['date'],q['id']),x['note'])} for x in q['injuryEvidence'] if x['date']!='2024-01-29' or q['id'] in [1629634,1631222]]
  q['injury']='官方事件見 injuryEvidence；不能估算命中率影響' if q['injuryEvidence'] else '本次未逐人核實；出賽數不等於傷勢'
  components={'assistedProduction':0.,'unassistedProduction':0.,'coveredTargetFGA':0,'targetFGA':0,'label':explore['label']}
  for zone,value in [('paint',2),('mid',2),('three',3)]:
   a=by[c['prior'],'0',str(q['id']),zone];b=by[c['season'],tid,str(q['id']),zone];components['targetFGA']+=b['a']
   if not a['a'] or not b['a']:continue
   components['coveredTargetFGA']+=b['a']
   for name,mkey in [('assistedProduction','am'),('unassistedProduction','un')]:
    am=a['am'] if mkey=='am' else a['m']-a['am'];bm=b['am'] if mkey=='am' else b['m']-b['am'];components[name]+=value*b['a']*(am/a['a']-bm/b['a'])/82
  q['posthocProductionGap']=components;summaries.append(components)
 c['posthocProductionGap']={k:sum(v[k] for v in summaries) for k in ['assistedProduction','unassistedProduction','coveredTargetFGA','targetFGA']};c['posthocProductionGap']['label']=explore['label']
save('cases.json',cases)
tree=ast.parse((O/'analyze.py').read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['role','onoff']],type_ignores=[]),'fixed-onoff-functions','exec'),globals())
groups=defaultdict(list)
for r in counts:groups[r['season'],r['team'],r['kind'],r['organizer'],r['player']].append(r)
rows=[]
for (s,tid,kind,anchor,pid),rr in groups.items():
 z=onoff(rr)
 if not z['strata']:continue
 rows.append({'season':s,'team':tid,'kind':kind,'organizer':anchor,'player':pid,'name':profiles[s].get(str(tid)+':'+str(pid),{}).get('name'),'role':role(s,tid,pid),**z})
save('onoff-players.json',rows)
print('ENRICH',len(rows),'player contrasts',flush=True)

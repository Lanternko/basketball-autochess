import json
from pathlib import Path
r=Path(__file__).parent
read=lambda f:json.loads(Path(f).read_text(encoding='utf8'))
p=read(r/'protocol.json');real=read('reports/defense-tenth/step4-rebounds-rim-calibration/real.json')['results'];keys=['misses','immediateClock','fgOreb','postOrebClock','clock'];out=[]
for season in p['seasons']:
 rows=[x for x in real[season] if x['half']=='test'];wanted={x['id'] for x in rows};truth={k:sum(x[k] for x in rows) for k in keys};z={k:0 for k in keys}
 for seed in p['fullSeeds']:
  x=read(r/f'runs/{season}-combined-{seed}.json')
  for m,e in zip(x['matches'],x['eventCounts']):
   if m['id'] in wanted:
    for k in keys:z[k]+=e[k]/len(p['fullSeeds'])
 out.append({'season':season,'games':len(rows),'real':truth,'combinedMean':z})
a={'season':'pooled','games':sum(x['games'] for x in out),'real':{k:sum(x['real'][k] for x in out) for k in keys},'combinedMean':{k:sum(x['combinedMean'][k] for x in out) for k in keys}};out.append(a)
for x in out:
 for source in ['real','combinedMean']:
  z=x[source];z['immediateRate']=z['immediateClock']/z['misses'];z['postOrebRate']=z['postOrebClock']/z['fgOreb'];z['clockPerTeamGame']=z['clock']/(2*x['games'])
(r/'events-20seed.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out[-1]))

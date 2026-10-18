import json
from pathlib import Path
import numpy as np
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
p=read(r/'protocol.json');truth=read(r/'timing-real.json');out=[]
def summary(a):
 a=[x for x in a if x['seconds']>=0 and x['periodRemaining']>14]
 return {'n':len(a),'meanSeconds':float(np.mean([x['seconds'] for x in a])) if a else None,'atLeast13Seconds':float(np.mean([x['seconds']>=13 for x in a])) if a else None,'atMost3Seconds':float(np.mean([x['seconds']<=3 for x in a])) if a else None}
for s in p['seasons']+['pooled']:
 seasons=p['seasons'] if s=='pooled' else [s]
 x={'season':s,'real':summary([x for x in truth if x['season'] in seasons])}
 for mode in ['baseline','combined']:
  rows=[]
  for ss in seasons:
   for seed in p['diagnosticSeeds']:
    a=read(r/f'timing/{ss}-{mode}-{seed}.json');b=read(r/f'runs/{ss}-{mode}-{seed}.json');lookup={m['id']:m for m in b['matches']};assert all(m==lookup[m['id']] for m in a['matches']);rows+=a['postClockElapsed']
  x[mode]=summary(rows)
 out.append(x)
(r/'timing-analysis.json').write_text(json.dumps({'note':'descriptive, no parameter refitting; anchor period clock >14 seconds','rows':out},indent=2)+'\n',encoding='utf8')
print(json.dumps(out[-1]))

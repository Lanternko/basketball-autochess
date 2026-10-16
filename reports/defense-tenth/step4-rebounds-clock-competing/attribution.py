import json
from pathlib import Path
import numpy as np
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'));p=read(r/'protocol.json');out=[]
for season in p['seasons']:
 for mode in ['baseline','fresh','post','rimPrior','combined']:
  runs=[]
  for seed in p['diagnosticSeeds']:
   file=Path('reports/defense-tenth/step4-rebounds-rim-calibration/runs')/f'{season}-selected-{seed}.json' if mode=='rimPrior' else r/f'runs/{season}-{mode}-{seed}.json';runs.append(read(file))
  allstats=[t['stats'] for x in runs for t in x['teams']];z={k:sum(t[k] for t in allstats) for k in allstats[0]};g=2*sum(len(x['matches']) for x in runs);poss=z['fga']-z['oreb']+z['tov']+.44*z['fta']
  row={'season':season,'mode':mode,'possProxy':poss/g,'ppg':z['pts']/g,'clock':z['clockTov']/g,'oreb':z['oreb']/g,'dreb':z['dreb']/g,'startedPoss':z['poss']/g,'fga':z['fga']/g}
  for k in ['timeSetup','timePass','timeRelease','timeFlight','timeInbound','timeViolation','timeOther']:row[k]=z[k]/g
  out.append(row)
(r/'attribution.json').write_text(json.dumps({'seeds':p['diagnosticSeeds'],'note':'rimPrior reuses prior fixed-p full-schedule 3-seed outputs; combined interactions not additively attributed','rows':out},indent=2)+'\n',encoding='utf8')
for mode in ['baseline','fresh','post','rimPrior','combined']:
 a=[x for x in out if x['mode']==mode];print(mode,json.dumps({k:float(np.mean([x[k] for x in a])) for k in ['possProxy','ppg','clock','timeViolation','startedPoss','fga']}))

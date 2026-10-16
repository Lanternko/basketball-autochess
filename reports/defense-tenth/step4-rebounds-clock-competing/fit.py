import json,hashlib,datetime
from pathlib import Path
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
p=read(r/'protocol.json');assert hashlib.sha256((r/'protocol.json').read_bytes()).hexdigest()==(r/'protocol.sha256').read_text().strip()
real=read('reports/defense-tenth/step4-rebounds-rim-calibration/real.json')['results'];truth={'games':0,'clock':0,'immediateClock':0,'postOrebClock':0};pilot={'games':0,'fresh':0,'postOreb':0};parity=[]
for s in p['seasons']:
 for row in real[s]:
  if row['half']=='train':
   truth['games']+=1
   for k in ['clock','immediateClock','postOrebClock']:truth[k]+=row[k]
 schedule=read(f'reports/defense-tenth/step4-t0/{s}/bundle.json')['league']['schedule'];idx={g['id']:i for i,g in enumerate(schedule)}
 for seed in p['diagnosticSeeds']:
  x=read(r/f'runs/{s}-pilot-{seed}.json');base=read(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{s}-split-{seed}.json');lookup={m['id']:m for m in base['matches']}
  assert all(m==lookup[m['id']] for m in x['matches']);parity.append({'season':s,'seed':seed,'games':len(x['matches']),'passed':True})
  for m,t in zip(x['matches'],x['clockTrials']):
   if idx[m['id']]<len(schedule)/2:
    pilot['games']+=1
    for k in ['fresh','postOreb']:pilot[k]+=t[k]
other=truth['clock']-truth['immediateClock']-truth['postOrebClock'];assert other>=0
q={'freshClockProbability':(other/truth['games'])/(pilot['fresh']/pilot['games']),'postOrebClockProbability':(truth['postOrebClock']/truth['games'])/(pilot['postOreb']/pilot['games'])}
assert all(0<=v<=1 for v in q.values())
(r/'calibration.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf8')
(r/'calibration-audit.json').write_text(json.dumps({'fittedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parameters':q,'realTrain':truth,'realOther':other,'pilotTrain':pilot,'parity':parity},indent=2)+'\n',encoding='utf8')
print(json.dumps(q))

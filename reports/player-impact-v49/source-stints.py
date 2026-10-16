import json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path('reports/player-impact-v49');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));out=[]
for season in read(R/'protocol.json')['seasons']:
 valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);intervals=defaultdict(list);file=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
 with file.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in valid or st['period']>4 or st['seconds']<=0:continue
   start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds']
   for t in st['teams']:
    for pid in t['players']:intervals[(st['id'],t['teamId'],pid)].append((start,end))
 durations=[]
 for rows in intervals.values():
  start=end=None
  for a,b in sorted(rows):
   if start is not None and abs(a-end)<1e-6:end=b
   else:
    if start is not None:durations.append(end-start)
    start,end=a,b
  if start is not None:durations.append(end-start)
 out.append({'season':season,'sourceSHA256':{file.as_posix():hashlib.sha256(file.read_bytes()).hexdigest()},'count':len(durations),'median':float(np.median(durations)),'p90':float(np.quantile(durations,.9)),'under60Share':float(np.mean(np.array(durations)<60)),'over900Share':float(np.mean(np.array(durations)>900))})
(R/'source-stint-scores.json').write_text(json.dumps({'scope':'Regulation playing-clock continuous occupancy segments; adjacent quarters merge if player never exits. Does not represent wall-clock rest or exertion. Candidate collector stint distributions include simulated overtime and are labeled separately.','cells':out},indent=2),encoding='utf-8');print(json.dumps(out))

"""Expose signed bias, absolute error and low-minute cohorts without discarding players."""
import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
d=read(R/'scores.json');results=[]
for cell in d['cells']:
 for sample in ['primary500','lowMinutes','allPositiveMinutes']:
  for group in ['ALL','G','F','C']:
   keep=lambda p:p['minutes']>0 and (group=='ALL' or p['roleGroup']==group) and (p['minutes']>=500 if sample=='primary500' else p['minutes']<500 if sample=='lowMinutes' else True)
   groups={}
   for field in ['players','onCourtPlayers']:
    ps=[p for p in cell[field] if keep(p)];stats={}
    for k in cell[field][0]['metrics']:
     values=sorted([(abs(p['metrics'][k]['predicted']-p['metrics'][k]['actual']),p['metrics'][k]['predicted']-p['metrics'][k]['actual'],p['minutes']) for p in ps if p['metrics'][k]],key=lambda a:a[0])
     weight=sum(v[2] for v in values)
     if not weight:stats[k]=None;continue
     cum=0;p90=None
     for absolute,signed,w in values:
      cum+=w
      if p90 is None and cum>=.9*weight:p90=absolute
     stats[k]={'players':len(values),'actualMinutes':weight,'mae':sum(v[0]*v[2] for v in values)/weight,'signedBias':sum(v[1]*v[2] for v in values)/weight,'weightedAbsoluteP90':p90}
    groups[field]=stats
   results.append({'season':cell['season'],'version':cell['version'],'sample':sample,'roleGroup':group,**groups})
out={'design':__doc__,'scope':'Each season uses actual-minute weights. Low-minute cohorts have larger source noise; FG attempt thresholds remain the scorer thresholds, with explicit metric player counts. Signed bias is predicted minus actual, not causal role effect. No new fit or runtime coefficient.','rows':results,'hashes':{str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'scores.json',R/'error-strata.py']}}
f=R/'error-strata.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'strata':len(results),'roleGroups':4,'minuteCohorts':3}))

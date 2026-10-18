"""Describe all20 matched arms and frozen mean70 flow; no attribution of net effect to one stat."""
import hashlib,json,math
from pathlib import Path
from statistics import mean,variance
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
new=read(R/'ovr-probe-checkpoint.json');old=read('reports/player-impact-v30/ovr-probe-checkpoint.json');flow=read(R/'flow-audit.json')
before={p['result']['playerId']:p['result'] for p in old['rows']};mf={p['playerId']:next(r for r in p['rows'] if r['playerId']==p['playerId']) for p in flow['mean70']}
rows=[]
for p in [r['result'] for r in new['rows']]:
 for arm in p['arms']:
  prior=next(a for a in before[p['playerId']]['arms'] if a['arm']==arm['arm']);assert arm['minutes']==prior['minutes']
  stats={}
  for k in arm['games'][0]['pair'][0]['playerStats']:
   groups={};oldValues=[];newValues=[]
   for g,h in zip(arm['games'],prior['games']):
    assert (g['opponent'],g['seed'],g['i'],g['phase'])==(h['opponent'],h['seed'],h['i'],h['phase'])
    a=mean(x['playerStats'][k] for x in h['pair']);b=mean(x['playerStats'][k] for x in g['pair']);oldValues.append(a);newValues.append(b);groups.setdefault(g['opponent'],[]).append(b-a)
   change=mean(mean(values) for values in groups.values());se=math.sqrt(sum(variance(v)/len(v) for v in groups.values())/30**2)
   stats[k]={'v30PerWorkloadGame':mean(oldValues),'v36PerWorkloadGame':mean(newValues),'pairedChange':change,'standardError':se,'pointwise95':[change-1.96*se,change+1.96*se]}
  rows.append({'playerId':p['playerId'],'name':p['name'],'arm':arm['arm'],'minutes':arm['minutes'],'mean70FrozenFlow':mf[p['playerId']],'stats':stats})
assert len(rows)==20
files=[R/'ovr-probe-checkpoint.json',Path('reports/player-impact-v30/ovr-probe-checkpoint.json'),R/'flow-audit.json',R/'probe-role-diagnostics.py']
out={'scope':__doc__+' Counts are simulated at fixed workloads, not NBA per-game or OVR. Pointwise intervals across many players/arms/stats are not multiplicity-adjusted; fixed source/model only.','rows':rows,'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
f=R/'probe-role-diagnostics.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(next(r for r in rows if r['playerId']==203999 and r['arm']=='supportedHealthy'),ensure_ascii=False,indent=2))

"""Independently verify all canonical-role probes, paired intervals and counters."""
import hashlib,json,math,statistics
from pathlib import Path
from collections import defaultdict
R=Path('reports/player-impact-v38');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=read(R/'protocol.json');m=read(R/'manifest.json');state=read(R/'checkpoint.json');s=read(R/'summary.json')
for path,h in p['hashes'].items():assert sha(path)==h,path
assert sha(R/'checkpoint.json')==m['checkpointSHA256'] and m['simulatedGames']==19200 and len(state['rows'])==20
assert {(r['job']['id'],r['job']['variant']) for r in state['rows']}=={(pid,v) for pid in p['ids'] for v in p['variants']}
for f in ['input-verification.json','input-audit-verification.json']:
 d=read(R/f);assert d['passed']
 for path,h in d['hashes'].items():assert sha(path)==h,path
data={(r['job']['id'],r['job']['variant']):r['result'] for r in state['rows']};reported={r['playerId']:r for r in s['players']};old={v:{r['result']['playerId']:r['result'] for r in read(f'reports/player-impact-{v}/ovr-probe-checkpoint.json')['rows']} for v in p['variants']}
close=lambda a,b:math.isclose(a,b,abs_tol=1e-8,rel_tol=1e-10)
def verify_est(values,result):
 groups=defaultdict(list)
 for (op,i),x in values.items():groups[op].append(x)
 assert len(groups)==30 and all(len(v)==4 for v in groups.values())
 mean=statistics.mean(statistics.mean(v) for v in groups.values());se=math.sqrt(sum(statistics.variance(v)/len(v) for v in groups.values())/900)
 assert close(result['mean'],mean) and close(result['standardError'],se)
 assert close(result['ci95'][0],mean-1.96*se) and close(result['ci95'][1],mean+1.96*se)
def differences(a,b):assert set(a)==set(b);return {k:a[k]-b[k] for k in a}
for pid in p['ids']:
 pair={v:data[pid,v] for v in p['variants']};r=reported[pid]
 for ai in range(2):
  arms={v:pair[v]['arms'][ai] for v in p['variants']};rep=r['arms'][ai];assert arms['v30']['arm']==arms['v37']['arm']==rep['arm'];assert arms['v30']['minutes']==arms['v37']['minutes']==rep['minutes']
  values={};stats={};prior={};priorStats={}
  for version,a in arms.items():
   assert len(a['games'])==120;before=next(x for x in old[version][pid]['arms'] if x['arm']==a['arm']);values[version]={};prior[version]={};stats[version]=defaultdict(dict);priorStats[version]=defaultdict(dict)
   for g,h in zip(a['games'],before['games']):
    for key in ['opponent','seed','i','phase']:assert g[key]==h[key]
    assert len(g['pair'])==2 and {v['side'] for v in g['pair']}=={0,1};k=(g['opponent'],g['i'])
    assert k not in values[version]
    for x,y in zip(g['pair'],h['pair']):
     assert x['side']==y['side'] and close(x['playerMinutes'],y['playerMinutes']) and close(x['playerMinutes'],a['minutes']);t=x['playerStats'];assert t['pts']==2*t['fgm']+t['fg3m']+t['ftm'];assert 0<=t['fg3m']<=t['fg3a']<=t['fga'] and 0<=t['fgm']<=t['fga']
    values[version][k]=statistics.mean(x['margin']-x['baselineMargin'] for x in g['pair']);prior[version][k]=statistics.mean(x['margin']-x['baselineMargin'] for x in h['pair'])
    for key in rep['stats']:
     stats[version][key][k]=statistics.mean(x['playerStats'][key] for x in g['pair']);priorStats[version][key][k]=statistics.mean(x['playerStats'][key] for x in h['pair'])
   verify_est(values[version],rep[version+'Canonical']);verify_est(differences(values[version],prior[version]),rep['inputCorrectionChanges'][version])
  verify_est(differences(values['v37'],values['v30']),rep['transportChange'])
  for key,info in rep['stats'].items():
   for version in p['variants']:
    assert close(info[version+'CanonicalPerWorkloadGame'],statistics.mean(stats[version][key].values()))
    verify_est(differences(stats[version][key],priorStats[version][key]),info['inputCorrectionChanges'][version])
   verify_est(differences(stats['v37'][key],stats['v30'][key]),info['transportChange'])
assert s['simulatedGames']==19200
files=[R/f for f in ['protocol.json','manifest.json','checkpoint.json','summary.json','input-verification.json','input-audit-verification.json','verify.py']]
out={'passed':True,'players':10,'transports':2,'scenarios':40,'games':19200,'allPairedIntervalsAnd13CountersRecomputed':True,'sourceRoleComparabilityVerified':True,'noFullOvr':True,'hashes':{str(f).replace('\\','/'):sha(f) for f in files}}
(R/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

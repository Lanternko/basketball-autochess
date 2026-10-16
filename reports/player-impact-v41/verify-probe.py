import json,hashlib,statistics,math
from pathlib import Path
from collections import defaultdict
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=read(R/'probe-protocol.json');manifest=read(R/'probe-manifest.json');state=read(R/'probe-checkpoint.json');report=read(R/'probe-summary.json');source=read('reports/player-impact-v29/workload-source.json')
for f,h in p['hashes'].items():assert sha(f)==h,f
assert sha(R/'probe-checkpoint.json')==manifest['checkpointSHA256'];assert manifest['simulatedGames']==19200
assert len(state['rows'])==20 and {(r['job']['id'],r['job']['variant']) for r in state['rows']}=={(pid,v) for pid in p['ids'] for v in p['variants']}
raw={(r['job']['id'],r['job']['variant']):r['result'] for r in state['rows']};by={r['playerId']:r for r in report['players']}
archive={r['result']['playerId']:r['result'] for r in read('reports/player-impact-v38/checkpoint.json')['rows'] if r['job']['variant']=='v30'}
close=lambda a,b:math.isclose(a,b,abs_tol=1e-8,rel_tol=1e-10)
def check_estimate(values,reported):
 groups=defaultdict(list)
 for (op,i),x in values.items():groups[op].append(x)
 assert set(groups)==set(range(30)) and all(len(v)==4 for v in groups.values())
 mean=statistics.mean(statistics.mean(v) for v in groups.values());se=math.sqrt(sum(statistics.variance(v)/4 for v in groups.values())/900)
 assert close(reported['mean'],mean) and close(reported['standardError'],se)
 assert close(reported['ci95'][0],mean-1.96*se) and close(reported['ci95'][1],mean+1.96*se)
def diff(a,b):assert set(a)==set(b);return {k:a[k]-b[k] for k in a}
armChecks=0;seatChecks=0
for pid in p['ids']:
 r=by[pid];margins={v:{} for v in p['variants']}
 for armName in ['fullCapCounterfactual','supportedHealthy']:
  rep=next(a for a in r['arms'] if a['arm']==armName);values={};counts={}
  for version in p['variants']:
   result=raw[pid,version];assert result['playerId']==pid and result['name']==r['name'];a=next(a for a in result['arms'] if a['arm']==armName);assert a['minutes']==rep['minutes'] and len(a['games'])==120
   expectedMinutes=source['capMinutes'] if armName=='fullCapCounterfactual' else source['players'][str(pid)]['supportedMinutes'];assert close(a['minutes'],round(expectedMinutes*600)/600)
   values[version]={};counts[version]=defaultdict(dict)
   prior=next(t for t in archive[pid]['arms'] if t['arm']==armName)
   for g,h in zip(a['games'],prior['games']):
    k=(g['opponent'],g['i']);assert k not in values[version] and g['phase']==g['i']%2
    seed=(p['seed']+((g['opponent']*5+result['slot'])*1000003)+g['i']*7919)&0xffffffff;assert g['seed']==seed
    assert all(g[key]==h[key] for key in ['opponent','i','phase','seed']);assert {x['side'] for x in g['pair']}=={0,1}
    for x,y in zip(g['pair'],h['pair']):
     assert close(x['playerMinutes'],a['minutes']);t=x['playerStats'];assert t['pts']==2*t['fgm']+t['fg3m']+t['ftm'];assert 0<=t['fg3m']<=t['fg3a']<=t['fga'];assert 0<=t['fgm']<=t['fga'];seatChecks+=1
     if version=='v39':
      for key in ['side','margin','baselineMargin','win','baselineWin','playerMinutes']:assert x[key]==y[key]
      assert {k:v for k,v in t.items() if k!='blk'}=={k:v for k,v in y['playerStats'].items() if k!='blk'}
    values[version][k]=statistics.mean(x['margin']-x['baselineMargin'] for x in g['pair'])
    for key in rep['stats']:counts[version][key][k]=statistics.mean(x['playerStats'][key] for x in g['pair'])
   check_estimate(values[version],rep[version]);margins[version][armName]=values[version];armChecks+=1
  check_estimate(diff(values['v41'],values['v39']),rep['change'])
  for key,stats in rep['stats'].items():
   for version in p['variants']:check_estimate(counts[version][key],stats[version+'PerWorkloadGame'])
   check_estimate(diff(counts['v41'][key],counts['v39'][key]),stats['change'])
 for version in p['variants']:
  check_estimate(diff(margins[version]['fullCapCounterfactual'],margins[version]['supportedHealthy']),r['fullCapMinusSupportedContribution'][version])
  history=list(source['players'][str(pid)]['history'].values());rates=sorted((h['documentedInjuryIllnessGames']/h['listedGames'] for h in history if h['historyCoverageAdequate']),reverse=True);persistent=rates[1] if len(rates)>1 else 0
  mean=statistics.mean(margins[version]['supportedHealthy'].values())
  for q,c in zip(r['reliabilitySensitivity'][version],[0,.05,.1]):
   assert q['coefficient']==c and q['persistentRate']==persistent;assert close(q['healthyContribution'],mean);deduction=max(0,mean)*c*persistent;assert close(q['deduction'],deduction) and close(q['adjustedContribution'],mean-deduction)
assert report['simulatedGames']==19200 and armChecks==40 and seatChecks==9600
files=[R/f for f in ['probe-protocol.json','probe-manifest.json','probe-checkpoint.json','probe-summary.json','verify-probe.py','summarize-probe.py','input-verification.json']]
(R/'probe-verification.json').write_text(json.dumps({'passed':True,'players':10,'variants':2,'armChecks':armChecks,'seatChecks':seatChecks,'simulatedGames':19200,'all13CountersAndPairedIntervalsRecomputed':True,'baselineExactlyCanonicalV38ExceptBlockCounts':True,'recurrenceSensitivityIndependentlyRecomputed':True,'scope':'Conditional workload experiment, not full OVR, source/model uncertainty, causal NBA defense or adoption.','hashes':{str(f).replace('\\','/'):sha(f) for f in files}},indent=2),encoding='utf-8');print('Verified19200 games,40 scenarios,all13 counters and paired intervals;canonical baseline parity.')

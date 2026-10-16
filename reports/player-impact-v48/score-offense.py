import json,sys,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
R=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));protocol=read(R/'protocol.json');selected=read(R/'selection.json')['selectedSigma'];variant=sys.argv[1];assert variant in ['baseline','candidate'];seasons=sys.argv[2:] or protocol['seasons'];prefix='' if seasons==protocol['seasons'] else '-'.join(seasons)+'-';zones=['ra','paint','mid'];cells=[];sources={}
for season in seasons:
 source=read(f'reports/player-impact-v45/{season}-fga-data.json');ids=[p['playerId'] for p in source['players']];idx={pid:i for i,pid in enumerate(ids)};minutes=np.zeros(len(ids));actual={z:{key:{arm:sum(np.array(read(R/'fits'/f'{season}-sigma0-fold{f}.json')['models'][zi]['counters'][key][arm]) for f in range(5)) for arm in ['on','off','teammates']} for key in ['actualAttempts','actualMakes','predictedMakes']} for zi,z in enumerate(zones)}
 for gid,fold,ps in source['minutes']:
  for pid,m in ps:minutes[idx[pid]]+=m
 pred=defaultdict(lambda:{arm:Counter() for arm in ['on','off','teammates']});byshooter=defaultdict(lambda:defaultdict(lambda:{'on':Counter(),'off':Counter()}));seedc=[]
 for seed in protocol['seeds']:
  file=R/f'baseline-runs/{season}-{seed}.json' if variant=='baseline' else R/f'runs/{season}-v48-strict-{seed}.json';r=read(file);sources[file.as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest();fine=r['fineOffense']
  if variant=='baseline':assert r['observerOnlyBaselineParityPassed']
  assert fine['freshOnly'] and fine['games']==len(r['matches']);assert fine['total']==r['fineDefense']['total']
  for p in fine['players']:
   for arm in ['on','off','teammates']:pred[p['playerId']][arm].update(p[arm])
   for pid,c in p['byShooter'].items():
    for arm in ['on','off']:byshooter[p['playerId']][pid][arm].update(c[arm])
  cp=next(p for p in fine['players'] if p['playerId']==201939);seedc.append({'seed':seed,**{arm:100*sum(cp[arm][z+'M'] for z in zones)/sum(cp[arm][z+'A'] for z in zones) for arm in ['on','off','teammates']}})
 rows=[]
 for i,p in enumerate(source['players']):
  metrics={};counts={arm:{z:{'a':int(actual[z]['actualAttempts'][arm][i]),'m':int(actual[z]['actualMakes'][arm][i])} for z in zones} for arm in ['on','off','teammates']}
  for arm in ['on','off','teammates']:
   a=sum(c['a'] for c in counts[arm].values());m=sum(c['m'] for c in counts[arm].values());pa=sum(pred[p['playerId']][arm][z+'A'] for z in zones);pm=sum(pred[p['playerId']][arm][z+'M'] for z in zones)
   if not a or not pa:continue
   metrics['two:'+arm]={'actual':100*m/a,'predicted':100*pm/pa,'error':100*pm/pa-100*m/a,'actualAttempts':a,'predictedAttempts':pa/len(protocol['seeds']),'sourceFixedShotExpectation':100*sum(actual[z]['predictedMakes'][arm][i] for z in zones)/a}
   for z in zones:
    ac=counts[arm][z];pc=pred[p['playerId']][arm];n=pc[z+'A'];made=pc[z+'M'];metrics[z+':'+arm+':shareWithinTwo']={'actual':100*ac['a']/a,'predicted':100*n/pa,'error':100*n/pa-100*ac['a']/a,'actualAttempts':a}
    if ac['a'] and n:metrics[z+':'+arm+':FGpct']={'actual':100*ac['m']/ac['a'],'predicted':100*made/n,'error':100*made/n-100*ac['m']/ac['a'],'actualAttempts':ac['a']}
  eligible=minutes[i]>=500 and all(sum(c['a'] for c in counts[a].values())>=100 for a in ['on','off','teammates']);rows.append({**p,'minutes':float(minutes[i]),'primaryEligible':bool(eligible),'metrics':metrics})
 summary={}
 for key in set(k for p in rows for k in p['metrics']):
  rs=[p for p in rows if p['primaryEligible'] and key in p['metrics'] and p['metrics'][key]['actualAttempts']>=100];den=sum(p['minutes'] for p in rs)
  if den:summary[key]={'players':len(rs),'mae':sum(p['minutes']*abs(p['metrics'][key]['error']) for p in rs)/den,'bias':sum(p['minutes']*p['metrics'][key]['error'] for p in rs)/den}
 # By-shooter decomposition of Curry is diagnostic only, never a model input.
 sides=defaultdict(dict);file=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');sources[file.as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest();valid={gid for gid,f,ps in source['minutes']}
 with file.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] in valid:
    for team in st['teams']:
     for pid in team['players']:sides[st['id']][pid]=team['teamId']
 truth=defaultdict(lambda:{'on':Counter(),'off':Counter()})
 for gid,f,zi,shooter,own,ds,n,m,blocked in source['rows']:
  if zi>=3 or 201939 not in sides[gid] or sides[gid][shooter]!=sides[gid][201939]:continue
  arm='on' if 201939 in own else 'off';truth[str(shooter)][arm][zones[zi]+'A']+=n;truth[str(shooter)][arm][zones[zi]+'M']+=m
 decomp={}
 for arm in ['on','off','teammates']:
  armkey='on' if arm=='teammates' else arm;chosen=[pid for pid in set(truth)|set(byshooter[201939]) if arm!='teammates' or int(pid)!=201939];aa=sum(truth[pid][armkey][z+'A'] for pid in chosen for z in zones);pa=sum(byshooter[201939][pid][armkey][z+'A'] for pid in chosen for z in zones);composition=accuracy=0.;unsupported=0;contributions=[]
  for pid in chosen:
   for z in zones:
    a=truth[pid][armkey];p=byshooter[201939][pid][armkey];an=a[z+'A'];pn=p[z+'A'];aw=an/aa;pw=pn/pa;fallback=sum(truth[x][armkey][z+'M'] for x in chosen)/max(1,sum(truth[x][armkey][z+'A'] for x in chosen));ar=a[z+'M']/an if an else fallback;pr=p[z+'M']/pn if pn else ar;comp=100*(pw-aw)*(ar+pr)/2;acc=100*(pr-ar)*(aw+pw)/2;composition+=comp;accuracy+=acc
    if not an:unsupported+=pn
    if an or pn:contributions.append({'playerId':int(pid),'zone':z,'actualAttempts':an,'predictedAttempts':pn/len(protocol['seeds']),'actualShare':100*aw,'predictedShare':100*pw,'actualFGpct':100*ar if an else None,'predictedFGpct':100*pr if pn else None,'compositionContribution_pp':comp,'withinCategoryRateContribution_pp':acc})
  cp=next(p for p in rows if p['playerId']==201939);assert abs(composition+accuracy-cp['metrics']['two:'+arm]['error'])<1e-8
  decomp[arm]={'composition_pp':composition,'withinShooterZoneRate_pp':accuracy,'unsupportedRuntimeAttemptShare_pct':100*unsupported/pa,'contributions':sorted(contributions,key=lambda x:abs(x['compositionContribution_pp'])+abs(x['withinCategoryRateContribution_pp']),reverse=True)}
 cells.append({'season':season,'summary':summary,'players':rows,'curry':next(p for p in rows if p['playerId']==201939),'curryDecomposition':decomp,'currySeedTwoPct':seedc})
 print(json.dumps({'season':season,'variant':variant,'teammateTwoFGMAE':summary['two:teammates']['mae'],'curry':cells[-1]['curry']['metrics'],'curryDecomposition':{arm:{k:v for k,v in d.items() if k!='contributions'} for arm,d in decomp.items()}}),flush=True)
out={'variant':variant,'scope':'Strict fresh FGA only; independent fine observer labels, same random labels as defensive fine observer. Source >=500min and>=100two attempts in on/off/teammates; individual fineFG summary additionally>=100zone attempts. Source-fixed-shot expectation is a different condition, not simulated accuracy. By-shooter/zone symmetric decomposition is descriptive, not causal. Missing actual category rates use source arm-zone pooled average; predicted-zero categories use actual rate, report unsupported runtime mass.','cells':cells,'sourceSHA256':sources};(R/(prefix+variant+'-offense-scores.json')).write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')

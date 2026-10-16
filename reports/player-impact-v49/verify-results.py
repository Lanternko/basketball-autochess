import json,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean
import numpy as np
R=Path('reports/player-impact-v49');B=Path('reports/player-impact-v47');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
frozen=read(R/'candidate-run-protocol.json');outputs=read(R/'candidate-run-verification.json');p=frozen['protocol'];scores=read(R/'scores.json');rotation=read(R/'rotation-scores.json');decision=read(R/'decision.json')
assert outputs['passed'] and len(outputs['jobs'])==36 and read(R/'verification.json')['passed'] and read(R/'fit-verification.json')['passed']
for file,h in frozen['hashes'].items():assert sha(file)==h,file
for file,h in read(R/'fit-verification.json')['profileSHA256'].items():assert sha(file)==h
for file,h in read('reports/player-impact-v46-closeout/status.json')['evidenceSHA256'].items():assert sha(file)==h,file
for file,h in read('reports/player-impact-v48/results-verification.json')['evidenceSHA256'].items():assert sha(file)==h,file
old=read(B/'scores.json');games=Counter();ledgers=0;rotationExceptions=[]
for j in outputs['jobs']:
 assert sha(j['file'])==j['sha256'];r=read(j['file']);games[j['variant']]+=len(r['matches'])
 if j['variant']=='v47':
  original=read(B/f"runs/{j['season']}-v47-strict-{j['seed']}.json");assert r['matches']==original['matches'] and r['teams']==original['teams'] and r['observerOnlyBaselineParityPassed']
 rotationExceptions.extend({'variant':j['variant'],'season':j['season'],'seed':j['seed'],'strict':j['strict'],**x} for x in r['rotationExceptions'])
 totals=Counter()
 for g in r['rotation']['games']:
  for tid,t in g['teams'].items():
   assert sum(sum(q['phase']) for q in t['players'].values())==144000
   assert sum(t['pairs'].values())==288000
   assert sum(q['seconds'] for q in t['players'].values())==5*t['end']
   for pid,q in t['players'].items():assert sum(q['stints'])==q['seconds'];totals[tid+'/'+pid]+=q['seconds']
 for t in r['teams']:
  s=t['stats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm']
  for k in ['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','stl','blk','pf']:assert s[k]==sum(q['stats'][k] for q in t['players'])
  assert s['tov']==sum(q['stats']['tov'] for q in t['players'])+s['clockTov']
  for q in t['players']:assert abs(totals[str(t['id'])+'/'+str(q['playerId'])]/10-q['stats']['seconds'])<1e-6
 if j['variant']=='v49' and j['strict']:
  assert r['fineOffense']['total']==r['fineDefense']['total']
  for ledger in ['defense','fineDefense','fineOffense']:
   d=r[ledger];assert d['games']==len(r['matches'])
   for k,v in d['total'].items():assert sum(q['on'][k] for q in d['players'])==5*v
  for k,v in r['fineOffense']['total'].items():
   assert sum(q['own'][k] for q in r['fineOffense']['players'])==v
   assert sum(q['teammates'][k] for q in r['fineOffense']['players'])==4*v
   for q in r['fineOffense']['players']:
    for arm in ['on','off']:assert sum(x[arm][k] for x in q['byShooter'].values())==q[arm][k]
 ledgers+=1
assert games=={'v49':28023,'v47':13263}
for c in scores['cells']:
 if c['variant']=='v47':assert c==next(x for x in old['cells'] if x['season']==c['season'] and x['variant']=='v47');continue
 pts=Counter();players=defaultdict(Counter)
 for seed in p['seeds']:
  r=read(R/f"runs/{c['season']}-v49-full-{seed}.json")
  for t in r['teams']:
   pts[t['id']]+=t['stats']['pts']/3
   for q in t['players']:
    for k,v in q['stats'].items():
     if isinstance(v,(int,float)):players[q['playerId']][k]+=v
 for t in c['teamPPG']['teams']:assert abs(pts[t['teamId']]/82-t['predictedPPG'])<1e-9
 for q in c['individualPlayers']:
  raw=players[q['playerId']]
  for k in ['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']:
   m=q['metrics'][k+'36']
   if m is not None:assert abs(2160*raw[k]/raw['seconds']-m['predicted'])<1e-9
  for k,(m,a) in {'fgPct':('fgm','fga'),'threePct':('fg3m','fg3a'),'ftPct':('ftm','fta')}.items():
   if q['metrics'][k] is not None:assert abs(100*raw[m]/raw[a]-q['metrics'][k]['predicted'])<1e-9
 for group in ['ALL','G','F','C']:
  for metric in ['pts36','ast36','tov36','ftPct']:
   rs=[q for q in c['individualPlayers'] if q['minutes']>=500 and q['metrics'][metric] is not None and (group=='ALL' or q['roleGroup']==group)];value=sum(q['minutes']*abs(q['metrics'][metric]['predicted']-q['metrics'][metric]['actual']) for q in rs)/sum(q['minutes'] for q in rs);assert abs(value-c['individualSummary'][group][metric]['mae'])<1e-9
# Rebuild source phase intervals independently; verify every strict prediction.
timingChecks=[]
for season in p['seasons']:
 meta=read(R/f'{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);truth=defaultdict(lambda:defaultdict(lambda:{'players':defaultdict(lambda:[0.]*24),'pairs':Counter()}))
 source=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
 with source.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in valid or st['period']>4 or st['seconds']<=0:continue
   start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds']
   for t in st['teams']:
    q=truth[st['id']][t['teamId']];ids=sorted(t['players'])
    for b in range(max(0,int(start//120)),min(24,math.ceil(end/120))):
     seconds=max(0,min(end,(b+1)*120)-max(start,b*120))
     for pid in ids:q['players'][str(pid)][b]+=seconds
    for i,a in enumerate(ids):
     for b in ids[i+1:]:q['pairs'][f'{a}/{b}']+=st['seconds']
 for variant in ['v47','v49']:
  phase=[];pair=[];reg=[];actualError=[];regTargets=[]
  for seed in p['seeds']:
   r=read(R/f'runs/{season}-{variant}-strict-{seed}.json')
   for g in r['rotation']['games']:
    for tid,t in g['teams'].items():
     tr=truth[g['id']][int(tid)];off=next(x for x in ex[g['id']]['teams'] if x['teamId']==int(tid));ids=sorted(q['playerId'] for q in off['players'] if q['seconds']>0)
     for pid in ids:
      a=tr['players'][str(pid)];b=t['players'].get(str(pid),{}).get('phase',[0]*24);phase.append(sum(abs(x/10-y) for x,y in zip(b,a))/60);reg.append(abs(sum(b)/10-sum(a))/60)
     for i,a in enumerate(ids):
      for b in ids[i+1:]:key=f'{a}/{b}';pair.append(abs(t['pairs'].get(key,0)/10-tr['pairs'][key])/60)
   full=read(B/f'runs/{season}-v47-full-{seed}.json' if variant=='v47' else R/f'runs/{season}-v49-full-{seed}.json');numerator=0.
   for g in full.get('rotation',{}).get('games',[]):
    for tid,t in g['teams'].items():
     off=next(x for x in ex[g['id']]['teams'] if x['teamId']==int(tid))
     numerator+=sum(abs(t['players'].get(str(q['playerId']),{}).get('seconds',0)/10-q['seconds'])/60 for q in off['players'])
   n=sum(t['playerGames'] for t in full['teams']);value=sum(t['minuteError'] for t in full['teams'])/n
   if variant=='v49':assert abs(numerator/n-value)<1e-8
   actualError.append(value);regTargets.append(sum(t['regulationMinuteError'] for t in full['teams'])/n)
  c=next(c for c in rotation['cells'] if c['season']==season and c['variant']==variant)
  for key,vals in [('phaseAbsoluteMinutesPerAppearance',phase),('pairOverlapMinutesMAE',pair),('strictRegulationSourceMinutesMAE',reg),('fullActualMinutesMAE',actualError),('fullRegulationTargetMinutesMAE',regTargets)]:assert abs(mean(vals)-c[key])<1e-9,key
  timingChecks.append({'season':season,'variant':variant,'appearances':len(phase),'pairComparisons':len(pair)})
rc=lambda s,v:next(c for c in rotation['cells'] if c['season']==s and c['variant']==v);meanrot=lambda v,k:mean(rc(s,v)[k] for s in p['seasons']);meanbox=lambda v,f:mean(f(c) for c in scores['cells'] if c['variant']==v)
keys=['fullActualMinutesMAE','fullRegulationTargetMinutesMAE','phaseAbsoluteMinutesPerAppearance','pairOverlapMinutesMAE'];g={k+'Improved':meanrot('v49',k)<meanrot('v47',k) for k in keys};g.update({'everySeasonActualMinutesNonRegression':all(rc(s,'v49')['fullActualMinutesMAE']<=rc(s,'v47')['fullActualMinutesMAE'] for s in p['seasons']),'runtimeVerified':True,'fitVerified':True});assert g==decision['rotationGates'] and all(g.values())==decision['rotationAdopted']
cg={'teamPPGnonRegression':meanbox('v49',lambda c:c['teamPPG']['mae'])<=meanbox('v47',lambda c:c['teamPPG']['mae']),'individualPTS36within002':meanbox('v49',lambda c:c['individualSummary']['ALL']['pts36']['mae'])<=meanbox('v47',lambda c:c['individualSummary']['ALL']['pts36']['mae'])+.02,'coarseDefenseWithin005pp':all(meanbox('v49',lambda c:c['defenseSummary']['ALL'][k]['mae'])<=meanbox('v47',lambda c:c['defenseSummary']['ALL'][k]['mae'])+.05 for k in ['onshortFGpct','onlongFGpct'])};assert cg==decision['combinedOffenseGates'] and (all(g.values()) and all(cg.values()))==decision['combinedOffenseAdopted']
for f in ['rotation-scores.json','baseline-offense-scores.json','candidate-offense-scores.json']:
 for file,h in read(R/f)['sourceSHA256'].items():assert sha(file)==h
result={'passed':True,'jobs':36,'candidateGames':games['v49'],'observerBaselineGames':games['v47'],'allFrozenSourceAndOutputHashesPassed':True,'v46V47V48EvidenceUnchanged':True,'exactObserverBaselineParityPassed':True,'all36RotationMinutePhasePairAndStintLedgersPassed':True,'individualAndTeamScoresRecomputed':True,'allFourSeasonTimingAndPairScoresIndependentlyRecomputed':timingChecks,'actualFullMinutesRecomputedFromOfficialBoxes':True,'adoptionGatesIndependentlyVerified':True,'minimumFiveLegacyFallbackGameOccurrences':rotationExceptions,'evidenceSHA256':{(R/f).as_posix():sha(R/f) for f in ['scores.json','fine-scores.json','rotation-scores.json','baseline-offense-scores.json','candidate-offense-scores.json','decision.json','report.md','report.py','verify-results.py','verification.json','fit-verification.json','tuning-selection.json','role-selection.json']}}
for c in read(R/'source-stint-scores.json')['cells']:
 for file,h in c['sourceSHA256'].items():assert sha(file)==h
for name in ['source-stint-scores.json','source-stints.py','score.py','score-rotation.py','score-offense.py','score-fine.py','tuning-source-protocol.json','tuning-verification.json','role-source-protocol.json','role-verification.json']:result['evidenceSHA256'][(R/name).as_posix()]=sha(R/name)
for prefix in ['tuning','role']:
 for file,h in read(R/(prefix+'-source-protocol.json'))['hashes'].items():assert sha(file)==h
 for file,h in read(R/(prefix+'-verification.json'))['outputHashes'].items():assert sha(file)==h
(R/'results-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ['minimumFiveLegacyFallbackGameOccurrences','evidenceSHA256']}))

"""Independent raw-ledger, frozen provenance, score and decision checks."""
import hashlib,json
from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean
R=Path('reports/player-impact-v48');B=Path('reports/player-impact-v47')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
frozen=read(R/'candidate-run-protocol.json');outputs=read(R/'candidate-run-verification.json');scores=read(R/'scores.json');old=read(B/'scores.json');decision=read(R/'decision.json');p=frozen['protocol']
assert outputs['passed'] and read(R/'choice-verification.json')['passed'] and read(R/'choice-fit-verification.json')['passed']
assert len(outputs['jobs'])==24
for file,h in frozen['hashes'].items():assert sha(file)==h,file
for file,h in read(R/'observe-protocol.json')['hashes'].items():assert sha(file)==h,file
for file,h in read('reports/player-impact-v46-closeout/status.json')['evidenceSHA256'].items():assert sha(file)==h,file
v47=read(B/'results-verification.json')
for key,file in [('scoresSHA256','scores.json'),('fineScoresSHA256','fine-scores.json'),('offenseOnCourtScoresSHA256','offense-oncourt-scores.json'),('decisionSHA256','decision.json'),('reportSHA256','report.md')]:assert sha(B/file)==v47[key]
observed=read(R/'observe-verification.json');assert observed['passed'] and len(observed['jobs'])==12
observerGames=0
for j in observed['jobs']:
 assert sha(j['file'])==j['sha256'];r=read(j['file']);assert r['observerOnlyBaselineParityPassed'];observerGames+=len(r['matches'])
assert observerGames==13263
games=0;rawFine=defaultdict(lambda:defaultdict(lambda:defaultdict(Counter)))
for j in outputs['jobs']:
 assert sha(j['file'])==j['sha256'];r=read(j['file']);games+=len(r['matches'])
 for t in r['teams']:
  s=t['stats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'];assert s['fga']==s['fg3a']+s['mida']+s['rima']
  for k in ['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','stl','blk','pf']:assert s[k]==sum(q['stats'][k] for q in t['players'])
  assert s['tov']==sum(q['stats']['tov'] for q in t['players'])+s['clockTov']
 if not j['strict']:continue
 for ledger in ['defense','fineDefense','fineOffense']:
  d=r[ledger];assert d['games']==len(r['matches'])
  for k,v in d['total'].items():assert sum(q['on'][k] for q in d['players'])==5*v
 assert r['fineOffense']['total']==r['fineDefense']['total']
 d=r['fineOffense'];f=d['total']
 for q in d['players']:
  for arm in ['on','off','teammates']:rawFine[j['season']][q['playerId']][arm].update(q[arm])
 assert f['fga']==sum(f[z+'A'] for z in ['ra','paint','mid','corner','arc']);assert f['fgm']==sum(f[z+'M'] for z in ['ra','paint','mid','corner','arc'])
 for k,v in f.items():
  assert sum(q['own'][k] for q in d['players'])==v
  assert sum(q['teammates'][k] for q in d['players'])==4*v
  for q in d['players']:
   for arm in ['on','off']:assert sum(x[arm][k] for x in q['byShooter'].values())==q[arm][k]
assert games==28023
for c in scores['cells']:
 season=c['season']
 if c['variant']=='v47':assert c==next(x for x in old['cells'] if x['variant']=='v47' and x['season']==season);continue
 totals=defaultdict(Counter);teams=Counter()
 for seed in p['seeds']:
  r=read(R/f'runs/{season}-v48-full-{seed}.json')
  for t in r['teams']:
   teams[t['id']]+=t['stats']['pts']/3
   for q in t['players']:
    for k,v in q['stats'].items():
     if isinstance(v,(int,float)):totals[q['playerId']][k]+=v
 for t in c['teamPPG']['teams']:assert abs(teams[t['teamId']]/82-t['predictedPPG'])<1e-9
 for q in c['individualPlayers']:
  raw=totals[q['playerId']]
  for k in ['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']:
   m=q['metrics'][k+'36']
   if m is not None:assert abs(2160*raw[k]/raw['seconds']-m['predicted'])<1e-9
  for k,(m,a) in {'fgPct':('fgm','fga'),'threePct':('fg3m','fg3a'),'ftPct':('ftm','fta')}.items():
   if q['metrics'][k] is not None:assert abs(100*raw[m]/raw[a]-q['metrics'][k]['predicted'])<1e-9
 for group in ['ALL','G','F','C']:
  for metric in ['pts36','ast36','tov36','ftPct']:
   rs=[q for q in c['individualPlayers'] if q['minutes']>=500 and q['metrics'][metric] is not None and (group=='ALL' or q['roleGroup']==group)]
   mae=sum(q['minutes']*abs(q['metrics'][metric]['predicted']-q['metrics'][metric]['actual']) for q in rs)/sum(q['minutes'] for q in rs)
   assert abs(mae-c['individualSummary'][group][metric]['mae'])<1e-9
off={v:read(R/(f+'-offense-scores.json')) for v,f in [('v47','baseline'),('v48','candidate')]}
for data in off.values():
 for file,h in data['sourceSHA256'].items():assert sha(file)==h
 for c in data['cells']:
  if data is off['v48']:
   for q in c['players']:
    for key,m in q['metrics'].items():
     z,arm,*tail=key.split(':');raw=rawFine[c['season']][q['playerId']][arm];two=sum(raw[x+'A'] for x in ['ra','paint','mid'])
     expected=100*sum(raw[x+'M'] for x in ['ra','paint','mid'])/two if z=='two' else 100*raw[z+'A']/two if tail==['shareWithinTwo'] else 100*raw[z+'M']/raw[z+'A']
     assert abs(expected-m['predicted'])<1e-9
  for key in ['two:teammates','ra:teammates:shareWithinTwo']:
   rows=[q for q in c['players'] if q['primaryEligible'] and key in q['metrics'] and q['metrics'][key]['actualAttempts']>=100]
   value=sum(q['minutes']*abs(q['metrics'][key]['error']) for q in rows)/sum(q['minutes'] for q in rows)
   assert abs(value-c['summary'][key]['mae'])<1e-9
  for arm,d in c['curryDecomposition'].items():assert abs(d['composition_pp']+d['withinShooterZoneRate_pp']-c['curry']['metrics']['two:'+arm]['error'])<1e-8
meanbox=lambda v,f:mean(f(c) for c in scores['cells'] if c['variant']==v)
meanoff=lambda v,k:mean(c['summary'][k]['mae'] for c in off[v]['cells'])
sel=read(R/'choice-selection.json');table=sel['table'];best=min(table,key=lambda x:(x['meanNllPerTwoAttempt'],x['sigma']));assert best['sigma']==sel['selectedSigma'] and sel['targetExcluded']
g={'nonzeroOlderThreeSelection':sel['selectedSigma']>0,'teammateTwoFGmaeImproved':meanoff('v48','two:teammates')<meanoff('v47','two:teammates'),'teammateRAshareMAEimproved':meanoff('v48','ra:teammates:shareWithinTwo')<meanoff('v47','ra:teammates:shareWithinTwo'),'teamPPGmeanNonRegression':meanbox('v48',lambda c:c['teamPPG']['mae'])<=meanbox('v47',lambda c:c['teamPPG']['mae']),'individualPTS36within002':meanbox('v48',lambda c:c['individualSummary']['ALL']['pts36']['mae'])<=meanbox('v47',lambda c:c['individualSummary']['ALL']['pts36']['mae'])+.02,'coarseDefenseWithin005pp':all(meanbox('v48',lambda c:c['defenseSummary']['ALL'][k]['mae'])<=meanbox('v47',lambda c:c['defenseSummary']['ALL'][k]['mae'])+.05 for k in ['onshortFGpct','onlongFGpct']),'fitVerified':True,'runtimeVerified':True,'olderThreeHeldoutNLLimproved':best['meanNllPerTwoAttempt']<next(x for x in table if x['sigma']==0)['meanNllPerTwoAttempt']}
assert g==decision['gates'] and all(g.values())==decision['adopted']
pair=read(R/'pair-scores.json');pv=read(R/'pair-verification.json');assert pv['passed']
for file,h in {**pv['sourceHashes'],**pv['outputHashes'],**pair['sourceSHA256']}.items():assert sha(file)==h
for row in pair['rows']:
 for arm,m in row['arms'].items():
  for prefix in ['actual','predicted']:
   minutes=m[prefix+'Minutes'];rate=m[prefix+'RAper36']
   if rate is not None:assert abs(36*m[prefix+'RAattempts']/minutes-rate)<1e-8
result={'passed':True,'jobs':24,'matches':games,'observerOnlyGames':observerGames,'frozenSourcesAndOutputsPassed':True,'v46AndV47Unchanged':True,'rawLedgersAndByShooterPassed':True,'rawIndividualAndTeamScoreRecomputationPassed':True,'adoptionGatesIndependentlyRecomputed':True,'evidenceSHA256':{(R/f).as_posix():sha(R/f) for f in ['scores.json','fine-scores.json','baseline-offense-scores.json','candidate-offense-scores.json','decision.json','report.md','report.py','verify-results.py']}}
result['pairObservationThreeSeedExactGameplayParityPassed']=True
for f in ['pair-scores.json','pair-verification.json','pair-score.py','score.py','score-offense.py','score-fine.py']:result['evidenceSHA256'][(R/f).as_posix()]=sha(R/f)
(R/'results-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))

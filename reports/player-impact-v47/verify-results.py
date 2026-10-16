"""Check frozen provenance, all accounting and scoring against raw simulations."""
import hashlib,json
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
R=Path('reports/player-impact-v47');B=Path('reports/player-impact-v46');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();frozen=read(R/'candidate-run-protocol.json');outputs=read(R/'candidate-run-verification.json');scores=read(R/'scores.json');old=read(B/'scores.json');decision=read(R/'decision.json');p=frozen['protocol']
assert outputs['passed'] and read(R/'verification.json')['passed'] and read(R/'fit-verification.json')['passed'];assert len(outputs['jobs'])==24
for file,h in frozen['hashes'].items():assert sha(file)==h,file
closed=read('reports/player-impact-v46-closeout/status.json')
for file,h in closed['evidenceSHA256'].items():assert sha(file)==h,file
games=0;seedChecks=[]
for job in outputs['jobs']:
 assert sha(job['file'])==job['sha256'];r=read(job['file']);games+=len(r['matches'])
 for t in r['teams']:
  s=t['stats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'];assert s['fga']==s['fg3a']+s['mida']+s['rima']
  for k in ['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','stl','blk','pf']:assert s[k]==sum(q['stats'][k] for q in t['players'])
  assert s['tov']==sum(q['stats']['tov'] for q in t['players'])+s['clockTov']
 if job['strict']:
  assert r['defense']['games']==r['fineDefense']['games']==r['onCourt']['games']==len(r['matches'])
  for ledger in ['defense','fineDefense']:
   for k,v in r[ledger]['total'].items():assert sum(q['on'][k] for q in r[ledger]['players'])==5*v
  for k in ['fga','fgm','fg3a','fg3m']:
   total=sum(t['stats'][k] for t in r['teams']);assert sum(q['own'][k] for q in r['onCourt']['players'])==total;assert sum(q['teammates'][k] for q in r['onCourt']['players'])==4*total
  f=r['fineDefense']['total'];assert f['fga']==sum(f[z+'A'] for z in ['ra','paint','mid','corner','arc']);assert f['fgm']==sum(f[z+'M'] for z in ['ra','paint','mid','corner','arc'])
assert games==28023
for c in scores['cells']:
 season=c['season']
 if c['variant']=='v46':assert c==next(b for b in old['cells'] if b['season']==season and b['variant']=='v46');continue
 totals=defaultdict(Counter);teamTotals=Counter();base=next(b for b in old['cells'] if b['season']==season and b['variant']=='v46')
 for seed in p['seeds']:
  run=read(R/f'runs/{season}-v47-full-{seed}.json');original=read(B/f'runs/{season}-v46-full-{seed}.json');vals=[]
  for variant,data in [('v46',original),('v47',run)]:
   byid=defaultdict(Counter)
   for t in data['teams']:
    for q in t['players']:byid[q['playerId']].update(q['stats'])
   rs=[q for q in base['individualPlayers'] if q['minutes']>=500 and q['metrics']['ftPct'] is not None];den=sum(q['minutes'] for q in rs);mae=sum(q['minutes']*abs(100*byid[q['playerId']]['ftm']/byid[q['playerId']]['fta']-q['metrics']['ftPct']['actual']) for q in rs)/den;vals.append(mae)
  seedChecks.append({'season':season,'seed':seed,'baselineFTmae':vals[0],'candidateFTmae':vals[1],'improved':vals[1]<vals[0]})
  for t in run['teams']:
   teamTotals[t['id']]+=t['stats']['pts']/len(p['seeds'])
   for q in t['players']:
    for k,v in q['stats'].items():
     if isinstance(v,(int,float)):totals[q['playerId']][k]+=v
 expected=sum(teamTotals.values())/2460;assert abs(expected-c['teamMetrics']['ptsPerGame'])<1e-9
 for t in c['teamPPG']['teams']:assert abs(teamTotals[t['teamId']]/82-t['predictedPPG'])<1e-9
 for q in c['individualPlayers']:
  raw=totals[q['playerId']]
  for k in ['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']:
   m=q['metrics'][k+'36']
   if m is not None:assert abs(2160*raw[k]/raw['seconds']-m['predicted'])<1e-9
  for k,(m,a) in {'fgPct':('fgm','fga'),'threePct':('fg3m','fg3a'),'ftPct':('ftm','fta')}.items():
   if q['metrics'][k] is not None:assert abs(100*raw[m]/raw[a]-q['metrics'][k]['predicted'])<1e-9
 for group in ['ALL','G','F','C']:
  rs=[q for q in c['individualPlayers'] if q['minutes']>=500 and q['metrics']['ftPct'] is not None and (group=='ALL' or q['roleGroup']==group)];mae=sum(q['minutes']*abs(q['metrics']['ftPct']['predicted']-q['metrics']['ftPct']['actual']) for q in rs)/sum(q['minutes'] for q in rs);assert abs(mae-c['individualSummary'][group]['ftPct']['mae'])<1e-9
mean=lambda v,f:float(np.mean([f(c) for c in scores['cells'] if c['variant']==v]));gates={'everySeasonFTmaeImproved':all(next(c for c in scores['cells'] if c['season']==s and c['variant']=='v47')['individualSummary']['ALL']['ftPct']['mae']<next(c for c in scores['cells'] if c['season']==s and c['variant']=='v46')['individualSummary']['ALL']['ftPct']['mae'] for s in p['seasons']),'teamPPGmeanNonRegression':mean('v47',lambda c:c['teamPPG']['mae'])<=mean('v46',lambda c:c['teamPPG']['mae']),'coarseDefenseMeanWithinPredeclared005pp':all(mean('v47',lambda c:c['defenseSummary']['ALL'][k]['mae'])<=mean('v46',lambda c:c['defenseSummary']['ALL'][k]['mae'])+.05 for k in ['onshortFGpct','onlongFGpct']),'fitVerified':True,'runtimeVerified':True}
assert gates==decision['gates'] and all(gates.values())==decision['adopted']
result={'passed':True,'jobs':len(outputs['jobs']),'matches':games,'allFrozenSourceOutputHashesPassed':True,'v46CloseoutUnchanged':True,'allTeamPlayerCoarseFineAndObserverLedgersPassed':True,'baselineScoreParityPassed':True,'candidateIndividualAndTeamScoresRecomputedFromRawRuns':True,'adoptionGatesIndependentlyRecomputed':True,'seedFTcomparison':seedChecks,'seedFTmaeImproved':sum(c['improved'] for c in seedChecks),'seedComparisons':len(seedChecks),'scoresSHA256':sha(R/'scores.json'),'fineScoresSHA256':sha(R/'fine-scores.json'),'offenseOnCourtScoresSHA256':sha(R/'offense-oncourt-scores.json'),'decisionSHA256':sha(R/'decision.json'),'reportSHA256':sha(R/'report.md')}
(R/'results-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='seedFTcomparison'}))

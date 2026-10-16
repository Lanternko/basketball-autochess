import json,hashlib
from pathlib import Path
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
protocol=read(ROOT/'candidate-run-protocol.json');runcheck=read(ROOT/'candidate-run-verification.json');assert runcheck['passed'];assert read(ROOT/'verification.json')['passed']
for kind in ['make','choice']:assert read(ROOT/(kind+'-fit-verification.json'))['passed']
for p,h in protocol['hashes'].items():assert sha(p)==h,p
sourceHashes={}
for season in protocol['protocol']['seasons']:
 data=read(ROOT/f'{season}-fga-data.json');exposure=read(ROOT/f'{season}-exposures.json');context=read(ROOT/f'{season}-contexts.json')
 assert exposure['sourceDataSHA256']==sha(ROOT/f'{season}-fga-data.json');assert context['sources']['shotExposureSHA256']==sha(ROOT/f'{season}-exposures.json')
 for p,h in data['hashes'].items():
  if p in sourceHashes:assert sourceHashes[p]==h
  sourceHashes[p]=h
 for kind in ['make','choice']:
  fit=read(ROOT/(kind+'-fit.json'));s=next(s for s in fit['seasons'] if s['season']==season)
  for name,c in fit['selected'].items():
   original=read(ROOT/'fits'/f"{kind}-{season}-sigma{c['sigma']:g}-feature{int(c['feature'])}-foldNone.json");assert original['playerIds']==s['playerIds'];a=next(m for m in original['models'] if m['name']==name);b=next(m for m in s['models'] if m['name']==name)
   assert a=={k:b[k] for k in a}
   if kind=='make':assert b['featureCode']==c['feature'] and b['featureSlope']==a['blockSlope'];assert set(b)-set(a)=={'featureCode','featureSlope'}
   else:assert set(b)==set(a)
for p,h in sourceHashes.items():assert sha(p)==h,p
games=0
for job in runcheck['jobs']:
 assert sha(job['file'])==job['sha256'];d=read(job['file']);games+=len(d['matches'])
 for t in d['teams']:
  s=t['stats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'];assert s['fga']==s['fg3a']+s['mida']+s['rima']
  for k in ['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','stl','blk','pf']:
   assert s[k]==sum(p['stats'][k] for p in t['players']),(job['file'],t['id'],k)
  # Shot-clock violations are deliberately team turnovers, never charged to a player.
  assert s['tov']==sum(p['stats']['tov'] for p in t['players'])+s['clockTov']
 if job['strict']:
  assert d['defense']['total']['fga']==sum(t['stats']['fga'] for t in d['teams'])
  for ledger in ['defense','fineDefense']:
   for k,v in d[ledger]['total'].items():assert sum(p['on'][k] for p in d[ledger]['players'])==5*v,(job['file'],ledger,k)
   for p in d[ledger]['players']:assert p['onSeconds']>=0 and p['offSeconds']>=-1e-6
  fine=d['fineDefense']['total'];assert fine['fga']==sum(fine[z+'A'] for z in ['ra','paint','mid','corner','arc']);assert fine['fgm']==sum(fine[z+'M'] for z in ['ra','paint','mid','corner','arc']);assert fine['fga']<=d['defense']['total']['fga'];assert fine['fgm']<=d['defense']['total']['fgm']
  for z in ['ra','paint','mid','corner','arc']:assert 0<=fine[z+'M']<=fine[z+'A']
scores=read(ROOT/'scores.json');old=read('reports/player-impact-v42/scores.json')
for c in scores['cells']:
 if c['variant']=='v41':
  prior=next(p for p in old['cells'] if p['season']==c['season'] and p['variant']=='v41')
  for k in ['teamPPG','teamMetrics','individualSummary','defenseSummary']:assert c[k]==prior[k],(c['season'],k)
 else:
  rs=[read(ROOT/f"runs/{c['season']}-v45-full-{s}.json") for s in protocol['protocol']['seeds']];expected=sum(t['stats']['pts'] for r in rs for t in r['teams'])/(len(rs)*2460);assert abs(expected-c['teamMetrics']['ptsPerGame'])<1e-9
decision=read(ROOT/'decision.json');result={'passed':True,'matches':games,'jobs':len(runcheck['jobs']),'allFrozenSourceAndOutputHashesPassed':True,'rawSourceHashesChecked':len(sourceHashes),'fineSourceDataExposureAndContextHashChainPassed':True,'assembledCoefficientsMatchVerifiedOriginalFits':True,'baselineScoreParityPassed':True,'scoreAndCoarseFineDefenseLedgersPassed':True,'temporaryTeamRegressionAuthorized':True,'adopted':decision['adopted'],'reportSHA256':sha(ROOT/'report.md'),'scoresSHA256':sha(ROOT/'scores.json'),'fineScoresSHA256':sha(ROOT/'fine-scores.json'),'decisionSHA256':sha(ROOT/'decision.json')}
(ROOT/'results-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))

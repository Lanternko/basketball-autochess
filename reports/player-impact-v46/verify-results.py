import json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-v46');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();protocol=read(ROOT/'candidate-run-protocol.json');runs=read(ROOT/'candidate-run-verification.json');assert runs['passed'] and read(ROOT/'verification.json')['passed'] and read(ROOT/'fit-verification.json')['passed']
for p,h in protocol['hashes'].items():assert sha(p)==h,p
oldcheck=read('reports/player-impact-v45/results-verification.json');assert oldcheck['passed'];assert sha('reports/player-impact-v45/scores.json')==oldcheck['scoresSHA256'];assert sha('reports/player-impact-v45/fine-scores.json')==oldcheck['fineScoresSHA256']
fit=read(ROOT/'make-fit.json');prior=read('reports/player-impact-v45/make-fit.json');a=fit['selected']['commonSigma'];b=fit['selected']['contrastSigma'];selection=read(ROOT/'selection.json');expected=min(selection['table'],key=lambda c:(c['meanPlayerPaintMAE'],c['nll'],c['contrastSigma'],c['commonSigma']));assert (a,b)==(expected['commonSigma'],expected['contrastSigma']);assert all(c['season'] in protocol['protocol']['seasons'][:3] for row in selection['table'] for c in row['cells'])
for row in selection['table']:
 errors=[]
 for c in row['cells']:
  season=c['season'];data=read(f'reports/player-impact-v45/{season}-fga-data.json');ids=[p['playerId'] for p in data['players']];idx={p:i for i,p in enumerate(ids)};minutes=np.zeros(len(ids))
  for gid,fold,ps in data['minutes']:
   for pid,m in ps:minutes[idx[pid]]+=m
  fs=[read(ROOT/'fits'/f"{season}-common{row['commonSigma']:g}-contrast{row['contrastSigma']:g}-fold{f}.json") for f in range(5)];counts=sum(np.array(f['onCounts']) for f in fs);mask=(minutes>=500)&(counts[:,0]>=100);mae=float(minutes[mask]@(100*abs(counts[mask,2]-counts[mask,1])/counts[mask,0])/minutes[mask].sum());assert abs(mae-c['mae'])<1e-9;errors.append(mae)
 assert abs(np.mean(errors)-row['meanPlayerPaintMAE'])<1e-9
for s in fit['seasons']:
 season=s['season'];original=read(ROOT/'fits'/f'{season}-common{a:g}-contrast{b:g}-foldNone.json');assert original['playerIds']==s['playerIds'];assert original['sourceDataSHA256']==sha(f'reports/player-impact-v45/{season}-fga-data.json')
 for model in s['models']:
  source=original if model['name'] in ['ra','paint'] else next(v for v in prior['seasons'] if v['season']==season)
  assert model==next(m for m in source['models'] if m['name']==model['name'])
games=0
for job in runs['jobs']:
 assert sha(job['file'])==job['sha256'];r=read(job['file']);games+=len(r['matches'])
 for t in r['teams']:
  s=t['stats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'];assert s['fga']==s['fg3a']+s['mida']+s['rima']
  for k in ['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','stl','blk','pf']:assert s[k]==sum(p['stats'][k] for p in t['players'])
  assert s['tov']==sum(p['stats']['tov'] for p in t['players'])+s['clockTov']
 if job['strict']:
  assert r['defense']['games']==len(r['matches'])==r['fineDefense']['games'];assert r['defense']['total']['fga']==sum(t['stats']['fga'] for t in r['teams'])
  for ledger in ['defense','fineDefense']:
   for k,v in r[ledger]['total'].items():assert sum(p['on'][k] for p in r[ledger]['players'])==5*v
   assert all(p['onSeconds']>=0 and p['offSeconds']>=-1e-6 for p in r[ledger]['players'])
  f=r['fineDefense']['total'];assert f['fga']==sum(f[z+'A'] for z in ['ra','paint','mid','corner','arc']);assert f['fgm']==sum(f[z+'M'] for z in ['ra','paint','mid','corner','arc']);assert f['fga']<=r['defense']['total']['fga']
scores=read(ROOT/'scores.json');old=read('reports/player-impact-v45/scores.json')
for c in scores['cells']:
 if c['variant']=='v41':
  p=next(p for p in old['cells'] if p['season']==c['season'] and p['variant']=='v41')
  for k in ['teamPPG','teamMetrics','individualSummary','defenseSummary']:assert c[k]==p[k]
 else:
  rs=[read(ROOT/f"runs/{c['season']}-v46-full-{s}.json") for s in protocol['protocol']['seeds']];expected=sum(t['stats']['pts'] for r in rs for t in r['teams'])/(len(rs)*2460);assert abs(expected-c['teamMetrics']['ptsPerGame'])<1e-9
result={'passed':True,'jobs':len(runs['jobs']),'matches':games,'allFrozenSourceAndOutputHashesPassed':True,'selectionTargetExcludedAndMinimumPassed':True,'onlyPaintCoefficientsChangedAndVerified':True,'baselineScoreParityPassed':True,'teamPlayerCoarseFineLedgersPassed':True,'reportSHA256':sha(ROOT/'report.md'),'scoresSHA256':sha(ROOT/'scores.json'),'fineScoresSHA256':sha(ROOT/'fine-scores.json'),'decisionSHA256':sha(ROOT/'decision.json')};(ROOT/'results-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))

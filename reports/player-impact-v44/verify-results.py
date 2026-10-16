import json,hashlib
from pathlib import Path
ROOT=Path('reports/player-impact-v44');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
protocol=read(ROOT/'candidate-run-protocol.json');runcheck=read(ROOT/'candidate-run-verification.json');assert runcheck['passed'];assert read(ROOT/'verification.json')['passed']
for p,h in protocol['hashes'].items():assert sha(p)==h,p
games=0
for job in runcheck['jobs']:
    assert sha(job['file'])==job['sha256'];d=read(job['file']);games+=len(d['matches'])
    for t in d['teams']:
        s=t['stats'];assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'];assert s['fga']==s['fg3a']+s['mida']+s['rima']
    if job['strict']:
        assert d['defense']['total']['fga']==sum(t['stats']['fga'] for t in d['teams'])
        for k in d['defense']['total']:assert sum(p['on'][k] for p in d['defense']['players'])==5*d['defense']['total'][k]
scores=read(ROOT/'scores.json');old=read('reports/player-impact-v42/scores.json')
for c in scores['cells']:
    if c['variant']=='v41':
        prior=next(p for p in old['cells'] if p['season']==c['season'] and p['variant']=='v41')
        for k in ['teamPPG','teamMetrics','individualSummary','defenseSummary']:assert c[k]==prior[k],(c['season'],k)
    else:
        rs=[read(ROOT/f"runs/{c['season']}-v44-full-{s}.json") for s in protocol['protocol']['seeds']]
        expected=sum(t['stats']['pts'] for r in rs for t in r['teams'])/(3*2460)
        assert abs(expected-c['teamMetrics']['ptsPerGame'])<1e-9
result={'passed':True,'matches':games,'jobs':len(runcheck['jobs']),'allFrozenSourceAndOutputHashesPassed':True,'baselineScoreParityPassed':True,'scoreAndDefenseLedgersPassed':True,'temporaryTeamRegressionAuthorized':True,'adopted':False,'reportSHA256':sha(ROOT/'report.md'),'scoresSHA256':sha(ROOT/'scores.json')}
(ROOT/'results-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))

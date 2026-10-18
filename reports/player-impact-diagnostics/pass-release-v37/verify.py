import json,hashlib,math
from pathlib import Path
R=Path('reports/player-impact-diagnostics/pass-release-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();d=read(R/'audit.json')
for p,h in d['hashes'].items():assert sha(p)==h,p
for version in d['versions']:
 v=version['version'];p=next(r['result'] for r in read(f'reports/player-impact-{v}/ovr-probe-checkpoint.json')['rows'] if r['result']['playerId']==203999);arm=next(a for a in p['arms'] if a['arm']=='supportedHealthy');games=[x for g in arm['games'] for x in g['pair']];t=version['totals']
 assert len(games)==t['games']==240 and sum(x['playerStats']['ast'] for x in games)==t['playerAst']==t['creditedAssists']
 assert math.isclose(sum(x['playerMinutes'] for x in games),t['minutes'],abs_tol=1e-7)
 for key in ['passes','creditedAssists']:assert sum(r[key] for r in version['receivers'])==t[key]
 assert sum(r['releases'] for r in version['receivers'])==t['releasePotential'] and sum(r['usesAssist'] for r in version['receivers'])==t['releaseUsesAssist'] and sum(r['rejectsAssist'] for r in version['receivers'])==t['releaseRejectsAssist']
 assert t['releasePotential']==t['releaseUsesAssist']+t['releaseRejectsAssist']
out={'passed':True,'replayedGamesExactlyArchived':480,'originalInputComparisonConfounded':True,'notAnOvrOrAdoption':True,'hashes':{str(p).replace('\\','/'):sha(p) for p in R.iterdir() if p.is_file() and p.name!='verification.json'}}
(R/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'}))

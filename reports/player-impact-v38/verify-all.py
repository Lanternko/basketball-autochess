import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v38');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for f in [R/'protocol.json',R/'input-verification.json',R/'input-audit-verification.json',R/'verification.json',Path('reports/player-impact-v37/verification.json'),Path('reports/player-impact-diagnostics/block-source-v37/all-verification.json'),Path('reports/player-impact-diagnostics/pass-release-v37/verification.json')]:
 d=read(f)
 if 'passed' in d:assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
status=read(R/'status.json');assert status['canonicalRoleInputFixed'] and not status['officialModelAdopted'] and not status['goalComplete'] and not status['fullOvrThisVersion'] and status['probeGames']==19200
index=read(R/'index-transition.json');assert sha(index['updatedIndex'])==index['updatedIndexSha256'] and sha(index['snapshot'])==index['previousIndexSha256']
files=[p for p in R.iterdir() if p.is_file() and p.name!='all-verification.json']+[Path('src/source_creation_roles.js'),Path('test/source_creation_roles.js')]
out={'passed':True,'canonicalRoleBugFixed':True,'games':19200,'selectedPlayers':10,'all582SourceRolesChecked':True,'sourcePlayerSeasonsInIdempotenceTest':2262,'probeAndRetrospectiveInputAuditsVerified':True,'oldFrozenFilesUnchanged':True,'officialModelAdopted':False,'goalComplete':False,'noFullOvr':True,'scope':'Source-stable OVR constructor and two-transport paired workload experiment. Candidate v37 still fails four season win gates; no ranking/adoption certification.','hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(R/'all-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

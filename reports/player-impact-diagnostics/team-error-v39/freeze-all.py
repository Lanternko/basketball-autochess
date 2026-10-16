import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-diagnostics/team-error-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'all-verification.json').exists();hashes={}
for name in ['audit.json','verification.json']:
 d=read(R/name)
 if 'passed' in d:assert d['passed']
 for p,h in d.get('hashes',{}).items():assert sha(p)==h,p;hashes[p]=h
for p in R.iterdir():
 if p.is_file():hashes[str(p).replace('\\','/')]=sha(p)
(R/'all-verification.json').write_text(json.dumps({'passed':True,'scope':'Descriptive exact team scoring-error decomposition; no fitted parameter or runtime change. Projection is not causal or an independent variance decomposition.','hashes':hashes},indent=2),encoding='utf-8');print('Team-error diagnostic frozen.')

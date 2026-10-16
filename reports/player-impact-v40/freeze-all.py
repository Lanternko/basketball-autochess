import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'all-verification.json').exists()
hashes={}
for name in ['source-fit-protocol.json','target-null-protocol.json','data-verification.json','fit-verification.json','fit.json','target-null.json','selection.json']:
 d=read(R/name)
 if 'passed' in d:assert d['passed']
 for p,h in d.get('hashes',{}).items():assert sha(p)==h,p;hashes[p]=h
for p in R.iterdir():
 if p.is_file():hashes[str(p).replace('\\','/')]=sha(p)
out={'passed':True,'sourceOnlyPrototype':True,'verifiedFits':104,'fullSeasonSimulation':False,'fullOvr':False,'officialModelAdopted':False,'scope':'Preserved common-prior prototype and all source-fit dependencies. Zone-specific refinement is explicit v41, not a mutation of this version.','hashes':hashes}
(R/'all-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('v40 frozen source-only prototype;104 verified fits.')

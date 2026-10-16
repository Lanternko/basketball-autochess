import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();hashes={}
for path in ['reports/player-impact-v39/validation-protocol.json','reports/player-impact-v39/all-verification.json','reports/player-impact-v40/data-verification.json']:
 d=read(path)
 for p,h in d['hashes'].items():assert sha(p)==h,p
 hashes.update(d['hashes']);hashes[path]=sha(path)
for name in ['fit-verification.json','model-verification.json','fit-protocol.json','launcher-protocol.json']:
 d=read(R/name)
 for p,h in d['hashes'].items():assert sha(p)==h,p
 hashes.update(d['hashes']);hashes[str(R/name).replace('\\','/')]=sha(R/name)
files=[R/f for f in ['input.mjs','model.mjs','engine.mjs','prepare-contexts.mjs','scaffold.py','freeze-context.py','protocol-source.json']]+[Path(p) for p in ['src/source_fresh_defense.js','test/source_fresh_defense.js']];hashes.update({str(p).replace('\\','/'):sha(p) for p in files});out={'stage':'Freeze selected per-zone descriptor, raw-attribute slopes and centering code before source recomputation. Same FGA/minutes/energy/fresh partition; no sim outcomes or win residual.','hashes':hashes};f=R/'context-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')

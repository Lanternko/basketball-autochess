import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');V=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();s=read(R/'selection.json');hashes={**s['hashes'],**read(V/'source-fit-protocol.json')['hashes']}
for p,h in hashes.items():assert sha(p)==h,p
files=[R/f for f in ['protocol-source.json','select.py','fit.py','freeze-fit.py','selection.json']]+[V/'fit.json',V/'target-null.json'];hashes.update({str(p).replace('\\','/'):sha(p) for p in files});out={'stage':'Explicit zone-prior refinement frozen before new full-source fits and simulation; prior v40 files immutable.','hashes':hashes};f=R/'fit-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')

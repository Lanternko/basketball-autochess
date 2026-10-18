import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();protocol=read(R/'source-fit-protocol.json')
for p,h in protocol['hashes'].items():assert sha(p)==h,p
out={'scope':'Preregister target fivefold sigma0 benchmark before target fitting; does not change older-only sigma selection, selected fits or final runtime. Same frozen objective, prior conversion and folds as all other fits. If selected sigma0, existing files are reused. No source hyperparameter change.','hashes':{**protocol['hashes'],**{str(R/f).replace('\\','/'):sha(R/f) for f in ['fit-target-null.py','freeze-target-null.py','source-fit-protocol.json']}}};f=R/'target-null-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')

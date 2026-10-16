import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v39');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();files=[R/name for name in ['prepare-data.mjs','protocol-source.json','fitlib.py','fit.py','freeze-source.py']]+[R/(s+'-miss-data.json') for s in ['2022-23','2023-24','2024-25','2025-26']]
out={'stage':'Freeze source mechanism, prior selection and unchanged validation gates before fitting.','hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
f=R/'source-fit-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print('Source fit frozen.')

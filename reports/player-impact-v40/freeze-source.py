import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v40');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();files=[R/f for f in ['prepare-data.py','protocol-source.json','fitlib.py','fit.py','freeze-source.py']]+[R/(s+'-fga-data.json') for s in ['2022-23','2023-24','2024-25','2025-26']]
out={'stage':'Frozen source model, prior conversion and older-only whole-game selection before fitting any candidate. No source/model changes to pass numerical validation or rankings.','hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
f=R/'source-fit-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print('v40 source fitting frozen.')

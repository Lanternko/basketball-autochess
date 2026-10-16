import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v37');f=Path('reports/player-impact-v38/input-audit-verification.json');d=json.loads(f.read_text(encoding='utf-8'));assert d['passed']
o={'probeComparisonValid':False,'fullSeasonComparisonsUnaffected':True,'reason':'OVR card assembly repeatedly multiplied conditional-success reference factor; full-season source path applies once. Archived numeric ledgers retained, interpretation withdrawn.','canonicalRerun':'reports/player-impact-v38/protocol.json','hashes':{str(f).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest()}}
(R/'input-integrity-note.json').write_text(json.dumps(o,indent=2),encoding='utf-8')

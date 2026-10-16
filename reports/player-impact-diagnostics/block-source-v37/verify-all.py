import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-diagnostics/block-source-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['audit.json','source-cards.json','verification.json']:
 d=read(R/name)
 for p,h in d['hashes'].items():assert sha(p)==h,p
v=read(R/'verification.json');assert v['passed'] and v['allSourceCountsAndExpectationsIndependentlyRecomputed']
d=read(R/'audit.json');assert len(d['seasons'])==4 and sum(s['games'] for s in d['seasons'])==4421
out={'passed':True,'sourceGames':4421,'sourceFga':sum(s['sourceFga'] for s in d['seasons']),'runtimeChanged':False,'newFittedParameters':False,'goalComplete':False,'hashes':{str(p).replace('\\','/'):sha(p) for p in R.iterdir() if p.is_file() and p.name!='all-verification.json'}}
(R/'all-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'}))

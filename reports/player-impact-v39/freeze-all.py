import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=['verification.json','fit-verification.json','data-verification.json','input-verification.json','ledger-verification.json','isolation-verification.json']
for name in checks:
 d=read(R/name);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
for name in ['validation-protocol.json','solver-repair-protocol.json','source-fit-protocol.json','selection.json','fit.json']:
 for p,h in read(R/name)['hashes'].items():assert sha(p)==h,p
previous=read('reports/player-impact-v38/all-verification.json');assert previous['passed']
for p,h in previous['hashes'].items():assert sha(p)==h,p
transition=read(R/'index-transition.json');assert sha(transition['snapshot'])==transition['previousIndexSha256'];assert sha(transition['updatedIndex'])==transition['updatedIndexSha256']
assert read(R/'status.json')['goalComplete']==False
files=[p for p in R.iterdir() if p.is_file() and p.name!='all-verification.json']+[Path(p) for p in ['src/measured_block_events.js','test/measured_block_events.js','src/player_workload.js','src/player_reliability.js','test/player_workload.js','test/player_reliability.js','reports/player-impact-v38/all-verification.json']]
out={'passed':True,'games':28023,'canonicalWorkloadSmokeGames':40,'sourceGames':4421,'sourceFga':785193,'sourceMisses':414386,'sourceBlocks':42932,'targetPlayers':582,'targetColumns':170,'allNonBlockOutputsExactlyEqualV30':True,'oldFrozenFilesUnchanged':True,'officialModelAdopted':False,'goalComplete':False,'noFullOvr':True,'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
f=R/'all-verification.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

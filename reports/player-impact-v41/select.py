import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');V=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();verification=read(V/'fit-verification.json');assert verification['passed'];grid=[0,.025,.05,.1,.2,.4];zones=['long','mid','short'];scores={};choices={}
for p,h in verification['hashes'].items():assert sha(p)==h,p
for zone in zones:
 table=[]
 for sigma in grid:
  rows=[z for r in verification['foldChecks'] if r['season']!='2025-26' and r['sigma']==sigma for z in r['zones'] if z['zone']==zone];assert len(rows)==15;table.append({'sigma':sigma,'nll':sum(r['nll'] for r in rows),'fga':sum(r['fga'] for r in rows)})
 minimum=min(r['nll']/r['fga'] for r in table);choices[zone]=min(r['sigma'] for r in table if r['nll']/r['fga']<=minimum+1e-10);scores[zone]=table
hashes={str(p).replace('\\','/'):sha(p) for p in [R/'protocol-source.json',R/'select.py',V/'fit-verification.json',V/'fit.py',V/'fitlib.py',V/'source-fit-protocol.json']};hashes.update(read(V/'selection.json')['hashes'])
out={'version':'zone-prior-fresh-fg-defense-41','selectedSigmaByZone':choices,'olderOnlyScores':scores,'scope':'Explicit zone-separable older-only refinement.2025-26 is excluded from selection; not blind because earlier versions have been examined.','hashes':hashes};f=R/'selection.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(choices))

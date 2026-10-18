"""Check archived pass rates against powers of the independently computed factor."""
import hashlib,json,math
from pathlib import Path
from collections import Counter
R=Path('reports/player-impact-v38');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(R/'input-assembly-audit.json');v=read(R/'input-verification.json')
for obj in [d,v]:
 for p,h in obj['hashes'].items():assert sha(p)==h,p
raw=read('reports/player-impact-v6/2025-26-cards.json')['cards'];source=read('reports/player-impact-v17/2025-26-creation-audit.json');rows={p['playerId']:p for p in source['rows']};powers={'v24':0,'v29':1,'v30':2,'v34':3,'v35':3,'v36':3,'v37':3};counts=Counter();maximum=0
for r in d['rows']:
 p=rows[r['playerId']];prob=((p['minutes']*p['conditionalSuccess'] if p['minutes'] else 0)+60*source['conditionalSuccess'])/(p['minutes']+60);factor=p['oldGlobalSuccess']/prob;base=raw[str(r['playerId'])]['passOpportunityRate'];canonical=base*factor;expected=canonical*factor**powers[r['version']]
 assert math.isclose(r['canonicalPassRate'],canonical,abs_tol=1e-12,rel_tol=1e-12)
 error=abs(r['archivedPassRate']-expected);maximum=max(maximum,error);assert error<1e-12
 assert r['otherRoleKeysIdentical'];counts[r['version']]+=1
for version,n in counts.items():assert n==582
assert v['allCanonicalRolesExactlySeasonInput'] and v['allOtherCardFieldsIdenticalAcrossControlledVariants'] and v['actualCardsAndOpponentPrimaries']==732
out={'passed':True,'auditedVersions':dict(counts),'repeatedCorrectionPowersAboveCanonical':powers,'maxAbsoluteDifferenceToIndependentPowerReconstruction':maximum,'scope':'Confirms non-idempotent OVR assembly for v29/v30/v34-v37; v24 source pass roles match canonical. Full-season source assembly is a separate path. No all-model or complete-ranking invalidity assertion.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'input-assembly-audit.json',R/'input-verification.json',R/'verify-inputs.py']}}
(R/'input-audit-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))

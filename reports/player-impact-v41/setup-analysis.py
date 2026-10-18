from pathlib import Path
R=Path('reports/player-impact-v41')
def fork(name):
    s=Path('reports/player-impact-v39',name).read_text(encoding='utf-8')
    return s.replace('player-impact-v39','player-impact-v41').replace('player-impact-v30','player-impact-v39').replace("'v30'","'v39'")
for name in ['validation-score.py','export-players.py','error-strata.py','skill-cohort-errors.py','verify-ledgers.mjs']:
    p=R/name
    assert not p.exists(),p
    text=fork(name)
    if name=='export-players.py':text=text.replace('player-impact-v39/dependence-audit.json','player-impact-v30/dependence-audit.json')
    p.write_text(text,encoding='utf-8')
s=fork('verify-validation.py')
s=s.replace("mechanism=read(root/'solver-repair-protocol.json')","mechanism=read(root/'context-protocol.json')")
s=s.replace("sv=read(root/'data-verification.json');assert sv['passed'] and sv['sourceGames']==4421 and sv['sourceFga']==785193","sv=read(root/'context-verification.json');assert sv['passed'] and sv['uniqueCards']==2262 and sv['totalStates']==270090 and sv['fullIndependentWeightedReconstruction']")
s=s.replace("['fit-verification.json','data-verification.json','isolation-verification.json','ledger-verification.json','input-verification.json']","['fit-verification.json','context-verification.json','model-verification.json','ledger-verification.json','context-structure-verification.json','input-verification.json','probe-verification.json']")
s=s.replace("assert status['countsOnlyRepair'] and status['allNonBlockOutputsExactlyEqualV30']","assert status['sourceFreshDefenseChanged'] and status['sourceRawAttributesPreserved']")
s=s.replace("'previousV30AndControlScoresExactlyReproduced'","'previousV39AndControlScoresExactlyReproduced'")
s=s.replace("Source block/no-block/recipient competing labels; same already determined misses. Every other output equals archived v30. No scoring impact, no full OVR or adoption. Same-season source descriptors are not causal or prospective ability estimates.","Five-defender source fresh-FG associations with zone-specific older-season prior; four-season same-season reconstruction, all individual and on-court errors, not causal or prospective ability estimates. No full OVR or adoption.")
s=s.replace("previous=read('reports/player-impact-v38/all-verification.json')","previous=read('reports/player-impact-v39/all-verification.json')")
assert not (R/'verify-validation.py').exists()
(R/'verify-validation.py').write_text(s,encoding='utf-8')

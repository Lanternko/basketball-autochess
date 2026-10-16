from pathlib import Path
R=Path('reports/player-impact-v39');text=(R/'verify-validation.py').read_text(encoding='utf-8')
text=text.replace("mechanism=read(root/'mechanism-protocol.json')","mechanism=read(root/'solver-repair-protocol.json')")
text=text.replace("sv=read(root/'source-verification.json');assert sv['passed'] and sv['sourceRoleCards']==2262 and sv['sourceContextStates']==270090","sv=read(root/'data-verification.json');assert sv['passed'] and sv['sourceGames']==4421 and sv['sourceFga']==785193")
a=text.index("fa=read(root/'flow-audit.json')");b=text.index('for r in rows:',a);text=text[:a]+text[b:]
a=text.index(" for field,key in [('sourceStrictMeanSelfRoleRate'");b=text.index('strata=read(',a)
text=text[:a]+'''for name in ['fit-verification.json','data-verification.json','isolation-verification.json','ledger-verification.json','input-verification.json']:
 check=read(root/name);assert check['passed']
 for p,h in check['hashes'].items():assert sha(p)==h,p
'''+text[b:]
a=text.index("diagnostic=read(root/'probe-role-diagnostics.json')");b=text.index("cohorts=read(",a);text=text[:a]+text[b:]
a=text.index("note=read(root/'input-integrity-note.json')");b=text.index("failed=[]",a)
text=text[:a]+'''status=read(root/'status.json');assert not status['officialModelAdopted'] and not status['goalComplete'] and not status['fullOvrThisVersion'] and status['latestCompleteOvrVersion']==24
assert status['countsOnlyRepair'] and status['allNonBlockOutputsExactlyEqualV30']
'''+text[b:]
text=text.replace("'scope':'Fixed passer rows and separate own pool with explicit non-strict source-column branch, four-season same-season reconstruction; not causal/predictive/OVR certification. No adoption.'","'scope':'Source block/no-block/recipient competing labels; same already determined misses. Every other output equals archived v30. No scoring impact, no full OVR or adoption. Same-season source descriptors are not causal or prospective ability estimates.'")
# Verify v38's preserved work as an explicit dependency before freezing this run.
anchor="files=[p for p in root.iterdir()"
assert text.count(anchor)==1
text=text.replace(anchor,"previous=read('reports/player-impact-v38/all-verification.json');assert previous['passed']\nfor p,h in previous['hashes'].items():assert sha(p)==h,p\n"+anchor)
(R/'verify-validation.py').write_text(text,encoding='utf-8')

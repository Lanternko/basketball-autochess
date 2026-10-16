from pathlib import Path
R=Path('reports/player-impact-v34');O=Path('reports/player-impact-v31')
s=(O/'verify-validation.py').read_text(encoding='utf-8').replace('reports/player-impact-v31','reports/player-impact-v34')
s=s.replace('sourceStrictMeanSupportedSelf_v31','sourceStrictMeanAssignedSelf_v34').replace("'supportedSelf'","'assignedSelf'")
s=s.replace('sourceStrictMeanRemovedSelf','sourceStrictMeanAddedSelf').replace("'unfilledReceive'","'addedSelf'").replace('mean70SupportedSelf_v31','mean70AssignedSelf_v34')
start=s.index("supplement=read(root/'supplement-verification.json')");end=s.index("for name in ['source-verification.json'",start)
s=s[:start]+s[end:]
s=s.replace("['source-verification.json','equivalence-verification.json','profile-verification.json']","['source-verification.json','equivalence-verification.json','profile-verification.json','probability-verification.json','data-verification.json','source-comparison-verification.json']")
s=s.replace("protocol=read(root/'validation-protocol.json')","protocol=read(root/'validation-protocol.json')\nmechanism=read(root/'mechanism-protocol.json')\nfor p,h in mechanism['hashes'].items():assert sha(p)==h,p")
s=s.replace("'scope':'Four-season same-season reconstruction, not causal/predictive/OVR certification; no adoption.'","'scope':'Fixed source-self floor, four-season same-season reconstruction; not causal/predictive/OVR certification. No adoption.'")
out=R/'verify-validation.py';assert not out.exists();out.write_text(s,encoding='utf-8')
print('Created full-run/582-column and source diagnostic verification.')

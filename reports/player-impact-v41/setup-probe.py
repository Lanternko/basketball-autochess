import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['probe-worker.mjs','probe-run.mjs','probe-protocol.json']:assert not (R/name).exists()
s=Path('reports/player-impact-v38/worker.mjs').read_text(encoding='utf-8')
s=s.replace("import {controlledInput} from './input.mjs';","import {ovrInput as previousInput} from '../player-impact-v39/ovr-input.mjs';\nimport {ovrInput as candidateInput} from './ovr-input.mjs';")
s=s.replace("../player-impact-v30/engine.mjs","../player-impact-v39/engine.mjs").replace("../player-impact-v37/engine.mjs","./engine.mjs")
s=s.replace("const inputs={v30:await controlledInput('v30'),v37:await controlledInput('v37')},runs={v30:await oldEngine('rotation-space',{game:true}),v37:await nextEngine('rotation-space',{game:true})},src=source();","const inputs={v39:await previousInput(),v41:await candidateInput()},runs={v39:await oldEngine('rotation-space',{game:true}),v41:await nextEngine('rotation-space',{game:true})},src=source();")
assert 'controlledInput' not in s
(R/'probe-worker.mjs').write_text(s,encoding='utf-8')
s=Path('reports/player-impact-v38/run.mjs').read_text(encoding='utf-8').replace('player-impact-v38','player-impact-v41')
for name in ['protocol.json','checkpoint.json','manifest.json','worker.mjs']:s=s.replace(name,'probe-'+name)
(R/'probe-run.mjs').write_text(s,encoding='utf-8')
files=[R/f for f in ['setup-probe.py','probe-worker.mjs','probe-run.mjs','ovr-input.mjs','input-verification.json','verify-input.mjs']]
hashes={**read(R/'validation-protocol.json')['hashes'],**read('reports/player-impact-v39/all-verification.json')['hashes'],**{str(p).replace('\\','/'):sha(p) for p in files}}
for p,h in hashes.items():assert sha(p)==h,p
old=read('reports/player-impact-v38/protocol.json')
p={'version':'zone-prior-fresh-defense-workload-probe-41','variants':['v39','v41'],'ids':old['ids'],'samples':4,'seed':old['seed'],'expectedGames':19200,'noFullOvr':True,'noAdoption':True,'purpose':'Diagnostic10, paired source-supported healthy and full-cap counterfactual workload. Canonical source roles; four other-position mean70 teammates; same30 opponents, seeds, seat swaps and phase schedules. v41 adds source five-defender fresh-FG associations and corresponding source shooting centering; same original attributes and event mechanisms.','healthyPolicy':old['healthyPolicy'],'scope':'Not a full ranking or adoption evidence. Conditional Monte Carlo intervals omit model/source uncertainty; source associations are not pure causal defense. No player-name coefficient or ranking target.','hashes':hashes}
(R/'probe-protocol.json').write_text(json.dumps(p,indent=2),encoding='utf-8');print('Frozen two-variant,19200-game diagnostic workload probe.')

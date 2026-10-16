"""Create isolated v47 runners; frozen v46 files are never edited."""
from pathlib import Path
import json
R=Path('reports/player-impact-v47');old=Path('reports/player-impact-v46')
protocol=json.loads((old/'protocol.json').read_text(encoding='utf-8'))
protocol={k:protocol[k] for k in ['seasons','seeds']}|{'version':'measured-ft-accuracy-v47','scope':'Only FT accuracy and technical-FT taker preference change. v46 defense/shot choice/shooting/foul-generation/rebound/creation input preserved. Healthy OVR not recomputed.','selection':'FT Beta count prior selected by older-three-season whole-game heldout NLL per attempt, target2025-26 excluded.','adoptionRule':'All four seasons FT% all-player MAE must improve; four-season team PPG MAE must not increase; four-season mean coarse paint/three defense MAE may fluctuate at most0.05 percentage points each, fine-zone changes and seed results reported. This is a pre-run screen, not a causal or future-prediction guarantee.'}
(R/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
w=(old/'worker.mjs').read_text(encoding='utf-8').replace("from '../player-impact-v45/engine.mjs'","from './engine.mjs'")
w=w.replace('fs.writeFileSync(job.file,JSON.stringify(r));','fs.writeFileSync(job.file+".tmp",JSON.stringify(r));fs.renameSync(job.file+".tmp",job.file);')
(R/'worker.mjs').write_text(w,encoding='utf-8')
s=(old/'run.mjs').read_text(encoding='utf-8').replace("root='reports/player-impact-v46'","root='reports/player-impact-v47'").replace("variant='v46'","variant='v47'")
s=s.replace("const files=['protocol.json','worker.mjs','input.mjs','run.mjs','fit.py','make-fit.json','selection.json','verify.py','verify.mjs'];","const files=['protocol.json','worker.mjs','input.mjs','run.mjs','engine.mjs','model.mjs','ft-model.mjs','fit-ft.py','ft-fit.json','verify.mjs'];")
s=s.replace("...read('reports/player-impact-v45/candidate-run-protocol.json').hashes","...read('reports/player-impact-v46/candidate-run-protocol.json').hashes,...read(root+'/ft-fit.json').sourceSHA256")
(R/'run.mjs').write_text(s,encoding='utf-8')
s=(old/'score-fine.py').read_text(encoding='utf-8').replace("ROOT=Path('reports/player-impact-v46')","ROOT=Path('reports/player-impact-v47')").replace('{season}-v46-strict-','{season}-v47-strict-')
(R/'score-fine.py').write_text(s,encoding='utf-8')
print(json.dumps({'created':['protocol.json','worker.mjs','run.mjs','score-fine.py']}))

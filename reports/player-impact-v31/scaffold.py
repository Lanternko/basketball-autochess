"""Create isolated v31 runners without changing frozen older artifacts."""
from pathlib import Path
R=Path('reports/player-impact-v31');O=Path('reports/player-impact-v30')
def put(name,text):
 p=R/name
 assert not p.exists(),p
 p.write_text(text,encoding='utf-8')
engine=(O/'engine.mjs').read_text(encoding='utf-8')
assert engine.count("url('reports/player-impact-v14/model.mjs')")==1
put('engine.mjs',engine.replace("url('reports/player-impact-v14/model.mjs')","url('reports/player-impact-v31/model.mjs')"))
prepare=(O/'prepare-contexts.mjs').read_text(encoding='utf-8')
prepare=prepare.replace("from './model.mjs'","from './probability.mjs'").replace("from '../player-impact-v11/model.mjs'","from './model.mjs'")
prepare=prepare.replace("root='reports/player-impact-v30'","root='reports/player-impact-v31'")
prepare=prepare.replace("hash('reports/player-impact-v11/model.mjs')","hash(root+'/model.mjs')")
prepare=prepare.replace("hash(root+'/model.mjs'),creationDependenceSHA256","hash(root+'/probability.mjs'),sourceSelfModelSHA256:hash('src/source_self_opportunities.js'),creationDependenceSHA256")
prepare=prepare.replace('Measured existing received/terminal opportunity dependence replaces FTR-derived drive/pass proxy.','Source-self transport: unfilled received terminal demand is not automatically reassigned to self creation; self is capped at source self-role rate and remaining nominal terminal room. Source-role anchors are descriptive, not physiological maxima. No tuned parameter; all source roles remain frozen. v30 received/terminal dependence retained.')
put('prepare-contexts.mjs',prepare)
put('worker.mjs',(O/'worker.mjs').read_text(encoding='utf-8'))
put('verify-ledgers.mjs',(O/'verify-ledgers.mjs').read_text(encoding='utf-8').replace('player-impact-v30','player-impact-v31'))
score=(O/'validation-score.py').read_text(encoding='utf-8').replace('player-impact-v30','player-impact-v31').replace('player-impact-v28','player-impact-v30').replace("'v28'","'v30'")
put('validation-score.py',score)
export=(O/'export-players.py').read_text(encoding='utf-8').replace("root=Path('reports/player-impact-v30')","root=Path('reports/player-impact-v31')").replace("read(root/'dependence-audit.json')","read('reports/player-impact-v30/dependence-audit.json')")
put('export-players.py',export)
print('Created v31 engine, preparation, worker, ledger and export/scoring scripts.')

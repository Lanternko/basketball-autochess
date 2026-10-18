from pathlib import Path
root=Path('reports/player-impact-v7')
s=Path('reports/player-impact-v6/engine.mjs').read_text(encoding='utf-8').replace('player-impact-v6/model.mjs','player-impact-v7/model.mjs').replace("['terminal-flow','terminal-contests']","['space-half','space-full','space-control']").replace("['terminal-contests']","[]").replace('freshZoneProbability','spaceProbability').replace('originalProbability,os[i],putback!==null)','originalProbability,os[i],putback!==null,opt)')
(root/'engine.mjs').write_text(s,encoding='utf-8')
worker=Path('reports/player-impact-v6/worker.mjs').read_text(encoding='utf-8').replace("from './input.mjs'","from '../player-impact-v6/input.mjs'")
worker=worker.replace('if(job.onCourt)b.options.onCourtObserver',"const scale={'space-half':.5,'space-full':1,'space-control':0}[job.version];b.options.contextLongScale=scale;b.options.spaceCenter=scale*JSON.parse(fs.readFileSync(`reports/player-impact-v7/${job.season}-center.json`)).fullCenter;\n if(job.onCourt)b.options.onCourtObserver")
(root/'worker.mjs').write_text(worker,encoding='utf-8')
worker=Path('reports/player-impact-validation/fast-ovr-worker.mjs').read_text(encoding='utf-8').replace("from './fast-engine.mjs'","from './engine.mjs'")
worker="import fs from 'node:fs';\n"+worker
worker=worker.replace("const x=ovrInput();","const x=ovrInput(),center=JSON.parse(fs.readFileSync('reports/player-impact-v7/2025-26-center.json')).fullCenter;const settings=v=>{const scale={'space-half':.5,'space-full':1,'space-control':0}[v];return {...x.options,contextLongScale:scale,spaceCenter:scale*center};};")
worker=worker.replace('...x.options,seed','...settings(job.version),seed')
(root/'ovr-worker.mjs').write_text(worker,encoding='utf-8')
s=Path('reports/player-impact-v6/ovr-run.mjs').read_text(encoding='utf-8').replace('player-impact-v6','player-impact-v7').replace("['terminal-flow','terminal-contests']","['space-half','space-full']").replace('conserved-terminal-natural-role-ovr-6','centered-space-natural-role-ovr-7')
# This folder deliberately reuses frozen input cards and profiles.
s=s.replace("fs.readFileSync(root+'/ovr-input.mjs')","fs.readFileSync('reports/player-impact-v6/ovr-input.mjs')")
(root/'ovr-run.mjs').write_text(s,encoding='utf-8')

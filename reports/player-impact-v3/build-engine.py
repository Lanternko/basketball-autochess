from pathlib import Path
root=Path('reports/player-impact-v3')
s=Path('reports/player-impact-v2/engine.mjs').read_text(encoding='utf-8').replace("['opportunity-flow']","['reference-flow','reference-contests','reference-no-size','reference-both']").replace("reports/player-impact-v2/model.mjs","reports/player-impact-v3/model.mjs").replace('{opportunityPlan}', '{opportunityPlan,contestHelp}')
anchor=' // Keep the already verified'
block=r''' if(['reference-contests','reference-both'].includes(version)){
  replace('ds[i],M.helpDefense(ds),tr(os)','ds[i],contestHelp(ds),tr(os)');
 }
 if(['reference-no-size','reference-both'].includes(version)){
  // Local replacement in the shooting probability path only. Rebound chances,
  // OREB recipients and putback selection retain their adopted model.
  replace('const os=ls[off],ds=ls[1-off];\n      const tr = lineup=>C.weightedTop',
   'const os=ls[off].map(p=>({...p,physique:70})),ds=ls[1-off].map(p=>({...p,physique:70}));\n      const tr = lineup=>C.weightedTop');
 }
'''
assert s.count(anchor)==1
s=s.replace(anchor,block+anchor)
(root/'engine.mjs').write_text(s,encoding='utf-8')
(root/'worker.mjs').write_text(Path('reports/player-impact-v2/worker.mjs').read_text(encoding='utf-8'),encoding='utf-8')
run=Path('reports/player-impact-v2/run.mjs').read_text(encoding='utf-8').replace('player-impact-v2','player-impact-v3').replace('observed-opportunity-flow-2','reference-context-flow-3').replace("variants:['opportunity-flow']","variants:['reference-flow','reference-contests','reference-no-size','reference-both']").replace("s+'-risk.json'","s+'-cards.json'")
run=run.replace("[false,true].map(strict=>","[false].map(strict=>")
run=run.replace("design:'Self make-rate", "design:'FROZEN source-context conversion, NOT counterfactual probability inversion. Self make-rate")
(root/'run.mjs').write_text(run,encoding='utf-8')

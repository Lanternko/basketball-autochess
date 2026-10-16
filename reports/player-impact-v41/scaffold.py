from pathlib import Path
R=Path('reports/player-impact-v41');V=Path('reports/player-impact-v40')
for name in ['model.mjs','engine.mjs','input.mjs','prepare-contexts.mjs','worker.mjs']:
 text=(V/name).read_text(encoding='utf-8').replace('player-impact-v40','player-impact-v41')
 if name=='model.mjs':
  old=" const currentPhys=baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,phys,opts);\n const sourcePhys=baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,sourcePhysique,opts);"
  new=" const currentPhys=phys===sourcePhysique?null:baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,phys,opts);\n const sourcePhys=phys===sourcePhysique?null:baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,sourcePhysique,opts);"
  assert text.count(old)==1;text=text.replace(old,new).replace('currentPhys.make[z]-sourcePhys.make[z]','(currentPhys?currentPhys.make[z]-sourcePhys.make[z]:0)')
 if name=='prepare-contexts.mjs':
  start=text.index(' const out={season,design:');end=text.index(',stints,states:',start)
  text=text[:start]+" const out={season,design:'Five-defender source fresh-FG logit associations, zone-specific older-only prior. Source defense physique baseline neutralized; current-minus-source counterfactual slopes preserved. Same raw attributes, canonical once-corrected roles, actual source rotation energy, fresh FGA weights and recorded-FGA survival. New defense descriptors themselves were fitted to same-season outcomes; this centering step only weights recorded FGA counts and never fits simulation/win/onoff residuals. Frozen60minute source attempt prior, not causal defense or physiology.'"+text[end:]
  text=text.replace('sources:{stints:file',"sources:{freshDefenseFitSHA256:hash(root+'/fit.json'),freshDefenseSelectionSHA256:hash(root+'/selection.json'),sourceInputSHA256:hash(root+'/input.mjs'),stints:file")
 (R/name).write_text(text,encoding='utf-8')
print('v41 model/input/engine/centering fork prepared; equal-anchor physique fast path.')

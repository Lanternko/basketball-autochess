from pathlib import Path
R=Path('reports/player-impact-v39')
source=Path('reports/player-impact-v30/engine.mjs').read_text(encoding='utf-8')
anchor=" const anchor='  const gu=encode(g),s=';"
assert source.count(anchor)==1
extra='''
 replace("if(rng()<bp.conditionalOnMiss){blocker=D.lineup[pickWeighted(measuredRecipientWeights(ls[1-off],'blk'),rng())];record(1-off,blocker,'blk');}","const blockIndex=coupledBlockLabel(ls[1-off],{zone,legacyProbability:bp.conditionalOnMiss},rng);if(blockIndex>=0){blocker=D.lineup[blockIndex];record(1-off,blocker,'blk');}");
 patches.push(`g="import {coupledBlockLabel} from '${url('src/measured_block_events.js')}';\\\\n"+g;`);
'''
source=source.replace(anchor,extra+anchor);(R/'engine.mjs').write_text(source,encoding='utf-8')
(R/'worker.mjs').write_text(Path('reports/player-impact-v30/worker.mjs').read_text(encoding='utf-8'),encoding='utf-8')
for name in ['validation-score.py','verify-ledgers.mjs','error-strata.py','skill-cohort-errors.py','verify-validation.py']:
 text=Path('reports/player-impact-v37',name).read_text(encoding='utf-8').replace('player-impact-v37','player-impact-v39');(R/name).write_text(text,encoding='utf-8')
text=Path('reports/player-impact-v37/export-players.py').read_text(encoding='utf-8').replace('player-impact-v37','player-impact-v39')
a=text.index("flowAudit=read(");b=text.index("for p in cell['players']:",a);text=text[:a]+text[b:]
a=text.index(' sf=sourceFlow.get(pid)');b=text.index(' rows.append(r)',a);text=text[:a]+text[b:];(R/'export-players.py').write_text(text,encoding='utf-8')
print('v39 isolated block-label engine and verification scaffold created.')

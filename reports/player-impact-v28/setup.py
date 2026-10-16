"""Fork frozen source paths; never modify v20/v26/v27 artifacts."""
from pathlib import Path
root=Path('reports/player-impact-v28')
source=Path('reports/player-impact-v27/engine.mjs').read_text(encoding='utf-8')
assert source.count("url('reports/player-impact-v21/model.mjs')")==1
source=source.replace("url('reports/player-impact-v21/model.mjs')","url('reports/player-impact-v28/model.mjs')")
target=root/'engine.mjs';assert not target.exists();target.write_text(source,encoding='utf-8')
source=Path('reports/player-impact-v20/prepare.mjs').read_text(encoding='utf-8')
source=source.replace("from './role-input.mjs'","from '../player-impact-v20/role-input.mjs'")
source=source.replace("const root='reports/player-impact-v20'","const root='reports/player-impact-v28'")
source=source.replace("import {loadInput} from '../player-impact-v20/role-input.mjs';","import {loadInput} from '../player-impact-v20/role-input.mjs';\nimport {attachDefenseAnchors} from './defense-input.mjs';")
anchor="const b=loadInput(season),reference=";assert source.count(anchor)==1
source=source.replace(anchor,"const b=loadInput(season);attachDefenseAnchors(b.league.teams.flatMap(t=>t.roster));const reference=")
source=source.replace("hash(root+'/'+season+'-defense-exposure.json')","hash('reports/player-impact-v20/'+season+'-defense-exposure.json')")
source=source.replace("'Defense percentage effects gated by closest-contest FGA/minute exposure;", "'Direct original 200-attempt-shrunk defense difference plus current-attribute counterfactual delta; no lossy display-cap round trip. Defense percentage effects gated by closest-contest FGA/minute exposure;")
source=source.replace("codeSHA256:hash(root+'/prepare.mjs')","codeSHA256:hash(root+'/prepare-contexts.mjs'),defenseAnchorSHA256:hash(root+'/defense-input.mjs')")
target=root/'prepare-contexts.mjs';assert not target.exists();target.write_text(source,encoding='utf-8')
print('Prepared v28 engine and source-context rebuild paths.')

"""Independent recipient-only correction, frozen before simulation."""
from pathlib import Path
src=Path('reports/player-box-audit/experiment');dst=Path('reports/player-box-audit/allocation')
for f in ['worker.mjs','run.mjs']:
    s=(src/f).read_text(encoding='utf-8')
    if f=='worker.mjs':
      s=s.replace("import {candidateSeason} from './adapter.mjs';","import {candidateSeason} from './adapter.mjs';\nimport {attachBoxAllocationMeasurements} from '../../../src/individual_box_allocation.js';")
      s=s.replace('const run=await candidateSeason(job.version)', 'attachBoxAllocationMeasurements(b.league);\n  const run=await candidateSeason(job.version)')
    else:
      s=s.replace("root='reports/player-box-audit/experiment'","root='reports/player-box-audit/allocation'")
      s=s.replace("['creator-touch','pass-credit','creator-and-credit']","['dreb-allocation','block-allocation','box-allocation']")
      s=s.replace("version:'creator-assist-mechanism-1'","version:'observed-conditional-recipient-allocation-1'")
      s=s.replace("creatorTouch:'Initial handler weight adds observed AST/minute to existing (FGA+.44FTA+TOV)/minute. A creation-opportunity proxy, not measured handle or a positional boost. Receiver weights unchanged.'", "creatorTouch:'Only conditional recipients change: individual DREB and BLK/minute, traded stints merged before rates. Existing 240-minute defensive measurement prior, no player-specific fitted adjustment. Team event probability, shooting, passing, OREB and RNG draw counts untouched.'")
      s=s.replace("passCredit:'Credit final passer on made FG regardless of EV comparison used to choose probability branch. No extra RNG, no gameplay probability change. A diagnostic upper bound: not every pass is a real NBA assist.'", "passCredit:'Original AST accounting untouched. DREB includes final-FT player defensive rebounds. Team rebounds remain team events. BLK only splits pre-existing misses and retains original block-event probability.'")
      s=s.replace("['adapter.mjs','worker.mjs','run.mjs']","['adapter.mjs','worker.mjs','run.mjs','prepare.py']")
      s=s.replace("gates:'No promotion from diagnostic alone.","gates:'Require exact per-game scores, all team statistics and all non-DREB/BLK player statistics; require lower individual DREB/BLK MAE across four seasons. Remaining gates refer only to gameplay-changing mechanisms. No promotion from diagnostic alone.")
    assert not (dst/f).exists(),f
    (dst/f).write_text(s,encoding='utf-8')

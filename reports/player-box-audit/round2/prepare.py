"""Create immutable independent mechanism trial; never overwrite round one."""
from pathlib import Path
src=Path('reports/player-box-audit/experiment');dst=Path('reports/player-box-audit/round2')
for f in ['worker.mjs','run.mjs']:
    s=(src/f).read_text(encoding='utf-8')
    if f=='run.mjs':
      s=s.replace("root='reports/player-box-audit/experiment'","root='reports/player-box-audit/round2'")
      s=s.replace("['creator-touch','pass-credit','creator-and-credit']","['hazard-balance','creator-hazard','creator-only-hazard']")
      s=s.replace("version:'creator-assist-mechanism-1'","version:'observed-receiver-stopping-hazard-1'")
      s=s.replace("creatorTouch:'Initial handler weight adds observed AST/minute to existing (FGA+.44FTA+TOV)/minute. A creation-opportunity proxy, not measured handle or a positional boost. Receiver weights unchanged.'", "creatorTouch:'hazard-balance uses original initial involvement. creator-hazard adds AST/min. creator-only-hazard uses AST/min alone. On receiving, all divide observed FGA/min by the existing probability of shooting at the next pass state. This tests whether measured final FGA was double weighted by finishing EV; it is not a fitted player offset or positional boost.'")
      s=s.replace("passCredit:'Credit final passer on made FG regardless of EV comparison used to choose probability branch. No extra RNG, no gameplay probability change. A diagnostic upper bound: not every pass is a real NBA assist.'", "passCredit:'Original pass/assist accounting untouched. No direct FG, rebound or steal probability edit. Inverse shot willingness only approximates terminal hazard: pass failures, fouls, turnovers, clocks and putbacks still affect realized shots.'")
      s=s.replace("['adapter.mjs','worker.mjs','run.mjs']","['adapter.mjs','worker.mjs','run.mjs','prepare.py']")
    assert not (dst/f).exists(),f
    (dst/f).write_text(s,encoding='utf-8')

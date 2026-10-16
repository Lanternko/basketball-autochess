from pathlib import Path
root=Path('reports/player-impact-v4')
for name in ['input.mjs','worker.mjs','run.mjs']:
 s=Path('reports/player-impact-v3',name).read_text(encoding='utf-8').replace('player-impact-v3','player-impact-v4').replace('reference-context-flow-3','balanced-source-opportunity-4')
 # This version changes flow only; physiology/contest experiments are separate.
 s=s.replace("variants:['reference-flow','reference-contests','reference-no-size','reference-both']","variants:['balanced-flow','balanced-contests']")
 (root/name).write_text(s,encoding='utf-8')
s=Path('reports/player-impact-v3/engine.mjs').read_text(encoding='utf-8').replace('player-impact-v3','player-impact-v4')
s=s.replace("['reference-flow','reference-contests','reference-no-size','reference-both']","['balanced-flow','balanced-contests']").replace("['reference-contests','reference-both']","['balanced-contests']")
start=s.index(" if(['reference-no-size'");end=s.index(' // Keep the already verified',start)
s=s[:start]+s[end:]
(root/'engine.mjs').write_text(s,encoding='utf-8')
score=Path('reports/player-impact-v3/score.py').read_text(encoding='utf-8').replace("ROOT=Path('reports/player-impact-v3')","ROOT=Path('reports/player-impact-v4')")
(root/'score.py').write_text(score,encoding='utf-8')

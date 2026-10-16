import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v36')
files=[R/'model.mjs',R/'prepare-marked.py',R/'prepare-marked.mjs',R/'fit-marked.py',R/'pre-register.py',Path('reports/player-impact-v35/verification.json'),Path('reports/player-impact-v30/verification.json')]
p=R/'marked-protocol.json';assert not p.exists()
out={'previousGoalTurn':'progress: v35 completed and independently verified full/strict 28,023 games, workload 9,600 games; two win gates fail and high-creator AST regresses; rejected, not adopted.',
 'mechanism':'Positive source self/pass prior; preserve finisher columns, remove joint creator row constraints. One positive diagonal self scale. All pair cells positive, diagonal not an assist. No per-player/position/name or rank coefficient.',
 'trainingSeasons':['2022-23','2023-24','2024-25'],'checkSeason':'2025-26',
 'criterion':'Equal-season mean exact conditional multinomial NLL per actual fresh FGA; categories unassisted make, assisted make by each other player, miss. Probabilities use frozen v30 centered source contexts, mean-stint fatigue and exact selected own/caught branch with recorded-FGA survival. No probability floor. If an observed event has zero support, report and stop instead of conceal.',
 'fit':'One log(selfScale), unbounded scalar bracket search; all fitting restricted to older seasons. Five whole-game folds for stability and older out-of-game fit predictions; source descriptors remain full-season, not a blind cross-fit. 2025-26 not used to select scale or prior.',
 'limits':'Scale is descriptive conditional mark calibration, not physiological capacity or pure skill. Recentered final mechanism must be rescored, source inputs contain made outcomes; no causal/predictive claim.',
 'adoptionGate':'Unchanged each-season archived official winsMAE +0.5 and all individual/position/on-court/workload review. No ranking-driven fit or relaxed gate.',
 'hashes':{str(f).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('Preregistered source mark calibration')

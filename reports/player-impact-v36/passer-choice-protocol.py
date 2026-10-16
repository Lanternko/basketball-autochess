import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v36');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[R/'passer-choice-inputs.json',R/'passer-choice-diagnostic.py',R/'passer-choice-protocol.py',*[R/f'{s}-marked-data.json' for s in ['2022-23','2023-24','2024-25','2025-26']]]
p=R/'passer-choice-protocol.json';assert not p.exists()
out={'scope':'Exploratory source diagnostic of the previous frozen beta; not a change to v36 runtime, not a fitted OVR bonus. Prepared before viewing this conditional identity fit.',
 'trainingSeasons':['2022-23','2023-24','2024-25'],'checkSeason':'2025-26',
 'criterion':'Equal-season conditional assister-choice multinomial NLL per assisted FGM, receiver/stint and made result fixed. Known exact v30-centered source probabilities. A beta change multiplies each passer prior by originalPassRate**(beta-oldBeta); common elastic pass normalization cancels in this conditional choice.',
 'fit':'One unbounded scalar beta, analytic convex score root. Five whole-game leave-fold-out fits; fixed full-season descriptors mean not blind crossfit. Check season not used for selection.',
 'limits':'Conditioning on assisted FGM estimates who receives assist credit, not total creation volume, pure pass skill, causal teammate effect or OVR. Engine and source-centering review still required for any future candidate.',
 'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
p.write_text(json.dumps(out,indent=2),encoding='utf-8');print('Preregistered conditional assister-choice diagnostic')

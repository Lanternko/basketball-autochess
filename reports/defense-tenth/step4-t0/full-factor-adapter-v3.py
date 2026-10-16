"""Full-season validation adapter: traded players can play >82 games.
No change to design, labels, folds, prior, regularization or estimation.
"""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
config=json.loads((R/sys.argv[1]).read_text(encoding='utf-8'))
assert config['k']==82
# Execute the existing parameterized wrapper, replacing only its GP assertion
# and stale fixed strict-count metadata in its generated program.
source=(R/'scripts/estimate_defense_seventh_factors.py').read_text(encoding='utf-8')
needle="exec(compile(s,'calendar-factor-estimator','exec')"
replacement="""s=s.replace("assert t['GP']<=config['teamGP'][str(src['teamId'])]", "assert t['GP']<=logged_gp[t['CLOSE_DEF_PERSON_ID']]")
s=s.replace("tracking={}", "tracking={}; from collections import Counter; logged_gp=Counter(b['PLAYER_ID'] for b in boxes)")
s=s.replace("'strictGames':1188", "'strictGames':len(strict)")
exec(compile(s,'calendar-factor-estimator','exec')"""
assert source.count(needle)==1
source=source.replace(needle,replacement)
sys.argv=[str(R/'scripts/estimate_defense_seventh_factors.py'),sys.argv[1],'random']
exec(compile(source,'registered-full-factor-validation-adapter','exec'),dict(__file__=str(R/'scripts/estimate_defense_seventh_factors.py'),__name__='__main__'))



"""Thin only training labels/exposure, with frozen B1 estimator and folds."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/estimate_defense_seventh_factors.py').read_text(encoding='utf-8')
needle="exec(compile(s,'calendar-factor-estimator','exec'),"
assert needle in s
extra='''s=s.replace("train_games={g for g in strict if game_map[g]['date']<=config['date']}","train_games=set(config['trainGames']);assert train_games<=strict")
s=s[:s.index('# Normalize three separately modeled shot shares')]
s+="\\n(out/'offline-coefficients.json').write_text(json.dumps({'players':pids,'coefficients':coeff,'engineIntegrated':False},ensure_ascii=False)+'\\\\n',encoding='utf-8')\\n"
'''
s=s.replace(needle,extra+needle)
exec(compile(s,'coverage-factor-export','exec'),{'__file__':str(R/'scripts/estimate_defense_seventh_factors.py'),'__name__':'__main__'})

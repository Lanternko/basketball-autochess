"""Training-only export for the previous full season, after blind tests finish.
Uses exactly the frozen calendar factor estimator up to its engine export.
No fabricated empty holdout evaluation.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/estimate_defense_seventh_factors.py').read_text(encoding='utf-8')
needle="exec(compile(s,'calendar-factor-estimator','exec'),"
assert needle in s
extra='''s=s[:s.index('# Normalize three separately modeled shot shares')]
s+="\\n(out/'offline-coefficients.json').write_text(json.dumps({'players':pids,'coefficients':coeff,'engineIntegrated':False},ensure_ascii=False)+'\\\\n',encoding='utf-8')\\n"
'''
s=s.replace(needle,extra+needle)
exec(compile(s,'previous-full-factor-export','exec'),{'__file__':str(R/'scripts/estimate_defense_seventh_factors.py'),'__name__':'__main__'})

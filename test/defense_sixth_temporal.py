"""Perturb future outcomes; actual training feature/fit code must stay equal."""
import sys,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from defense_sixth_data import *
for k in [25,41,55]:
 d=Data(k);source=ast.parse((R/'scripts/estimate_defense_sixth.py').read_text(encoding='utf-8'));fn=ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['features','prior_fit']],type_ignores=[]);ns=dict(d=d,P=d.P,np=np,sparse=sparse,minimize=minimize);exec(compile(fn,'actual_estimator_functions','exec'),ns)
 a,fo,fd,stats=ns['features'](d.trainids,True);beta,_=ns['prior_fit'](a,d.train);offset=a@beta;b,_=fit_count(d,d.train,300,offset)
 for row in d.box:
  if d.order[row['GAME_ID'],row['TEAM_ID']]>k:
   for field in ['MIN','PTS','FGA','FG3A','FTA','AST','TOV','OREB','DREB','STL','BLK','PF']:row[field]=1234567.
 d.y[~d.train]=999999.;d.n[~d.train]=999999.
 aa,ff,gg,ss=ns['features'](d.trainids,True);np.testing.assert_array_equal(a,aa);np.testing.assert_array_equal(fo,ff);np.testing.assert_array_equal(fd,gg);np.testing.assert_array_equal(stats,ss)
 bb,_=ns['prior_fit'](aa,d.train);np.testing.assert_array_equal(beta,bb);rr,_=fit_count(d,d.train,300,aa@bb);np.testing.assert_array_equal(b,rr)
 print('Temporal invariance',k,'PASS',flush=True)

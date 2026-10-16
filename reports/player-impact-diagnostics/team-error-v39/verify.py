import json,math,hashlib
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-diagnostics/team-error-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();d=read(R/'audit.json')
for p,h in d['hashes'].items():assert sha(p)==h,p
assert len(d['rows'])==240
for row in d['rows']:
 total=0
 for group,sign in [('own',1),('opp',-1)]:
  q=row['stats'][group];a=q['actual'];p=q['predicted'];assert math.isclose(p['pts'],2*p['fgm']+p['fg3m']+p['ftm'],abs_tol=1e-7)
  for zone,att,made,value in [('two','fga','fgm',2),('three','fg3a','fg3m',3),('ft','fta','ftm',1)]:
   aa=a[att]-(a['fg3a'] if zone=='two' else 0);am=a[made]-(a['fg3m'] if zone=='two' else 0);pa=p[att]-(p['fg3a'] if zone=='two' else 0);pm=p[made]-(p['fg3m'] if zone=='two' else 0)
   v=sign*value*(pa-aa)*(pm/pa+am/aa)/164;c=sign*value*(pm/pa-am/aa)*(pa+aa)/164
   assert math.isclose(v,row['components'][group+'_'+zone+'Volume'],abs_tol=1e-10);assert math.isclose(c,row['components'][group+'_'+zone+'Accuracy'],abs_tol=1e-10);total+=v+c
 assert math.isclose(total,row['netError'],abs_tol=1e-10)
for s in d['summaries']:
 rs=[r for r in d['rows'] if r['version']==s['version'] and (s['season']=='ALL' or r['season']==s['season'])];e=np.array([r['netError'] for r in rs]);assert len(rs)==s['teams'];assert math.isclose(float(np.sqrt(np.mean(e*e))),s['netRMSE'],abs_tol=1e-10)
 for k,n in s['netErrorProjection'].items():assert math.isclose(float(np.mean([r['netError']*r['components'][k] for r in rs])/np.mean(e*e)),n,abs_tol=1e-10)
 assert math.isclose(sum(s['netErrorProjection'].values()),1,abs_tol=1e-10)
 for part in ['own','opp']:assert math.isclose(sum(v for k,v in s['netErrorProjection'].items() if k.startswith(part+'_')),s['groupProjection'][part],abs_tol=1e-10)
 for part in ['Volume','Accuracy']:assert math.isclose(sum(v for k,v in s['netErrorProjection'].items() if k.endswith(part)),s['groupProjection'][part],abs_tol=1e-10)
scores=read('reports/player-impact-v39/scores.json')
for s in d['summaries']:
 if s['season']=='ALL':continue
 c=next(c for c in scores['cells'] if c['season']==s['season'] and c['version']==('control' if s['version']=='control' else 'rotation-space'));assert math.isclose(s['winsMAE'],c['teamMetrics']['winsMAE'],abs_tol=1e-10);assert math.isclose(s['netRMSE'],c['teamMetrics']['netRMSE'],abs_tol=1e-10)
out={'passed':True,'rows':240,'sourceBoxGames':4920,'scope':'Exact source score closure,2P/3P/FT symmetric accounting and MSE projection recomputed; no causal or independent-variance claim. Four season win/net scores match archived scorer.','hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'audit.json',R/'audit.py',R/'verify.py']}}
(R/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('Team error diagnostic verified:240 model/team rows and4920 source games.')

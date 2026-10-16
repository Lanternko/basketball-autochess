"""Freeze an own-pool candidate before source preparation or simulation scores."""
import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v37');O=Path('reports/player-impact-v35');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
design='Preserve old successful passer rows and terminal columns; project a separate positive own row whose total is old residual supply onto source own-rate shape. Strict feasibility: ownPool>1e-10*max(1,total) and each passer row below all other terminal columns by that tolerance. Only non-strict inputs use unfitted source self/pass prior projected to terminal columns (diagonal scale exactly1), explicitly relaxing passer rows. Numerical nonconvergence throws, never selects fallback. No new fitted coefficients, unchanged frozen elastic exponents, raw attributes, source roles and v30 probabilities. Recenter on identical source FGA/energy. Four seasons,3seeds,full/strict; archived official winsMAE+0.5 per season and broad individual/role/on-court/workload review. Same-season descriptors contain outcomes, not blind/causal. No ranking/name/onoff/wins residual fit.'
runtime=['input.mjs','engine.mjs','probability.mjs','worker.mjs','prepare-contexts.mjs','run.mjs','validation-score.py','verify-ledgers.mjs','ovr-input.mjs']
checks=['prepare-data.mjs','verify-data.py','verify-probability.mjs','verify-profiles.mjs','verify-equivalence.mjs','export-players.py','compare-source.py','verify-source-comparison.py','error-strata.py','ovr-worker.mjs','ovr-probe.mjs','summarize-probe.py','verify-supplement.py','probe-role-diagnostics.py']
for name in runtime+checks:
 text=(O/name).read_text(encoding='utf-8').replace('v35','v37').replace('joint_creator_transport','own_pool_transport')
 if name=='run.mjs':
  text=text.replace('joint-creator-terminal-35','fixed-pass-own-pool-37')
 if name in ['run.mjs','prepare-contexts.mjs','ovr-probe.mjs']:
  start=text.index("design:'");end=text.index("',",start);text=text[:start]+"design:'"+design+text[end:]
 if name=='prepare-data.mjs':
  text=text.replace('jointFlow','sourceFlow')
  start=text.index("design:'");end=text.index("',",start);text=text[:start]+"design:'"+design+" Fixed conditional predictions; all slope columns zero."+text[end:]
  text=text.replace('done=0;','done=0;const flowBranches={};')
  text=text.replace('const supported=flow.self,unused=flow.self.map(()=>0);','flowBranches[flow.branch]=(flowBranches[flow.branch]??0)+1;\n    const supported=flow.self,unused=flow.self.map(()=>0);')
  text=text.replace('gameMetadata,rows,hashes','flowBranches,gameMetadata,rows,hashes')
 if name=='verify-equivalence.mjs':text=text.replace('Both new joint and old residual transport identical','Both new own-pool and old residual transport identical')
 f=R/name;assert not f.exists();f.write_text(text,encoding='utf-8')
for name in ['verify-validation.py','skill-cohort-errors.py']:
 text=(Path('reports/player-impact-v36')/name).read_text(encoding='utf-8').replace('v36','v37')
 if name=='verify-validation.py':
  text=text.replace(",'marked-data-verification.json','marked-fit-verification.json','passer-choice-verification.json'",'')
  text=text.replace('Terminal-column source-prior projection','Fixed passer rows with separate own-pool projection')
 (R/name).write_text(text,encoding='utf-8')
protocol={'hypothesis':design,'fittedParameter':False,'fallbackSelfScale':1,'frozenElasticSource':'reports/player-impact-v8/model.mjs','injuryPolicy':'Healthy contribution primary, one injured season no penalty; recurrent injury is mild reliability deduction, bench load constrained by observed played-game workload. Existing v29 workload and reliability unchanged.','previousTurn':'v36 rejected: nine of14 individual MAEs worse and two failed win gates. Separate own-pool prototype independently solved on every strict source lineup and all582 mean70 subjects;850 of891 impossible own makes restored with passer rows unchanged,41 require relaxed infeasible margins.','hashes':{str(R/name).replace('\\','/'):sha(R/name) for name in runtime+['model.mjs','scaffold.py']}|{'test/own_pool_transport.js':sha('test/own_pool_transport.js')}}
(R/'mechanism-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
print('Frozen own-pool experiment; no scores inspected.')

"""Reuse frozen controls, ledgers and source readers with explicit hypothesis changes."""
from pathlib import Path
R=Path('reports/player-impact-v36');O=Path('reports/player-impact-v35')
files=['prepare-data.mjs','verify-data.py','verify-probability.mjs','verify-profiles.mjs','verify-equivalence.mjs','export-players.py','compare-source.py','verify-source-comparison.py','error-strata.py','ovr-worker.mjs','ovr-probe.mjs','summarize-probe.py','verify-supplement.py','probe-role-diagnostics.py','verify-validation.py','audit-flow.mjs']
for name in files:
 s=(O/name).read_text(encoding='utf-8').replace('v35','v36').replace('joint_creator_transport','terminal_prior_transport')
 if name=='prepare-data.mjs':
  # prepare-data.mjs already holds the byte-identical source extraction alias;
  # retain it, and place recentered final conditional data in a new script.
  s=s.replace("import {jointFlow} from './model.mjs';","import {priorFlow} from './model.mjs';\nconst selfScale=JSON.parse(fs.readFileSync('reports/player-impact-v36/marked-fit.json')).selfScale;\nconst jointFlow=ls=>priorFlow(ls,selfScale);")
  s=s.replace("[`${root}/prepare-data.mjs`]:hash(`${root}/prepare-data.mjs`)","[`${root}/prepare-final-data.mjs`]:hash(`${root}/prepare-final-data.mjs`)")
  s=s.replace('Joint creator/finisher flow v36: positive source self/pass prior balanced to normalized creator rows and terminal columns.', 'Terminal-column projected source prior v36 with older-season fitted diagonal scale. Creator row constraints removed.')
  name='prepare-final-data.mjs'
 if name=='verify-probability.mjs':s=s.replace("root+'/prepare-data.mjs'","root+'/prepare-final-data.mjs'")
 if name=='audit-flow.mjs':
  s=s.replace("import {jointFlow} from './model.mjs';","import {priorFlow} from './model.mjs';")
  a="const seasons=[],inputs=[],transportSamples=[];"
  s=s.replace(a,"const selfScale=read(root+'/marked-fit.json').selfScale;\nconst jointFlow=ls=>priorFlow(ls,selfScale);\n"+a)
  s=s.replace('  assert.ok(Math.abs(flow.self[i]+flow.rows[i]-flow.creator[i])<1e-8);\n','')
  s=s.replace('creator:flow.creator,terminal:flow.terminal,normalization:flow.normalization','terminal:flow.terminal,selfScale')
  s=s.replace('sourceCreator:flow.rawCreator[i],assignedCreator:flow.creator[i],creatorNormalization:flow.normalization','sourceCreator:p.opportunityMeasurement.selfOpportunityRate+p.opportunityMeasurement.passOpportunityRate,assignedCreator:flow.self[i]+flow.rows[i]')
  s=s.replace('Joint creator and terminal marginals with positive source self/pass prior. No hard source role boundary;', 'Positive source self/pass kernel projected to terminal columns, older-only fitted global self scale, no fixed creator-row budget;')
  s=s.replace('creatorMarginalsConserved:true','creatorRowBudgetConstrained:false')
  s=s.replace("root+'/input.mjs',root+'/audit-flow.mjs'","root+'/input.mjs',root+'/marked-fit.json',root+'/audit-flow.mjs'")
 if name=='verify-equivalence.mjs':
  s=s.replace("const x=structuredClone(await ovrInput()),cap=source().capMinutes;","const x=structuredClone(await ovrInput()),cap=source().capMinutes,selfScale=JSON.parse(fs.readFileSync('reports/player-impact-v36/marked-fit.json')).selfScale;")
  s=s.replace('passOpportunityRate:.8,passStolenPerMinute:.02','passOpportunityRate:1-.2*selfScale,passStolenPerMinute:.02')
  s=s.replace('Controlled symmetric self/pass roles give already feasible joint prior: own0.2, pass0.8, terminal1. Both new joint and old residual transport identical;', 'Controlled symmetric roles: source self0.2, pass1-0.2*selfScale, terminal1. Candidate scaled diagonal and off-diagonals already sum to terminal1; old residual transport identical;')
 if name=='ovr-probe.mjs':s=s.replace('Joint creator/finisher flow','Terminal-projected positive-prior flow')
 if name=='verify-validation.py':
  s=s.replace("'transport-verification.json']","'transport-verification.json','marked-data-verification.json','marked-fit-verification.json']")
  s=s.replace('Joint creator/terminal transport, four-season same-season reconstruction','Terminal prior with older-only mark calibration, four-season same-season reconstruction')
 f=R/name;assert not f.exists(),name;f.write_text(s,encoding='utf-8')
print('Prepared full statistics, workload and source checks')

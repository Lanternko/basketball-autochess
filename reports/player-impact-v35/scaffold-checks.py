"""Reuse audited ledgers and controls, changing only isolated hypothesis paths."""
from pathlib import Path
R=Path('reports/player-impact-v35');O=Path('reports/player-impact-v34')
files=['prepare-data.mjs','verify-data.py','verify-probability.mjs','verify-profiles.mjs','verify-equivalence.mjs','export-players.py','compare-source.py','verify-source-comparison.py','error-strata.py','ovr-worker.mjs','ovr-probe.mjs','summarize-probe.py','verify-supplement.py','probe-role-diagnostics.py','verify-validation.py','audit-flow.mjs']
for name in files:
 text=(O/name).read_text(encoding='utf-8').replace('v34','v35').replace('joint_source_opportunities','joint_creator_transport')
 if name=='prepare-data.mjs':
  text=text.replace('anchoredFlow','jointFlow')
  start=text.index("design:'");end=text.index("',\n coverage",start)
  text=text[:start]+"design:'Joint creator/finisher flow v35: positive source self/pass prior balanced to normalized creator rows and terminal columns. attemptBase/selfMakeBase/assistedMakeExpected are fixed predictions; all slope columns zero. New source centering on identical source counts and mean-stint energy. Source full-season descriptors contain outcomes, not blind/causal. No fitted parameter or rank/name/wins coefficient."+text[end:]
 if name=='compare-source.py':text=text.replace("baseline=read('reports/player-impact-v33/compensation-fit.json')","baseline=read('reports/player-impact-v33/compensation-fit.json')")
 if name=='audit-flow.mjs':
  text=text.replace('anchoredFlow','jointFlow')
  text=text.replace('assert.ok(flow.self[i]+1e-8>=m.selfOpportunityRate);','assert.ok(flow.self[i]>0);\n  assert.ok(Math.abs(flow.self[i]+flow.rows[i]-flow.creator[i])<1e-8);')
  text=text.replace('  assert.ok(flow.rows[i]<=m.passOpportunityRate+1e-8);\n','')
  text=text.replace(' assert.ok(flow.rows.reduce((s,v)=>s+v,0)<=old.rows.reduce((s,v)=>s+v,0)+1e-8);\n','')
  text=text.replace('assignedPass:flow.rows[i]','assignedPass:flow.rows[i],sourceCreator:flow.rawCreator[i],assignedCreator:flow.creator[i],creatorNormalization:flow.normalization')
  text=text.replace('Fixed source-self floor, changing passer/receiver marginals while conserving terminal demand. Descriptive role constraint, not validated physiology; same frozen attributes, roles, exposures and energy.','Joint creator and terminal marginals with positive source self/pass prior. No hard source role boundary; same frozen attributes, roles, exposures and energy.')
  text=text.replace('sourceSelfFloorReserved:true','positiveSelfSupport:true,creatorMarginalsConserved:true')
 if name=='verify-equivalence.mjs':
  text=text.replace('receiveOpportunityRate:m.terminalOpportunityRate,selfOpportunityRate:0','terminalOpportunityRate:1,receiveOpportunityRate:.8,selfOpportunityRate:.2,passOpportunityRate:.8,passStolenPerMinute:.02')
  text=text.replace('Controlled zero source-self anchors make receiver capacity equal to original terminal capacity; old and new transport are identical with passing active.','Controlled symmetric self/pass roles give already feasible joint prior: own0.2, pass0.8, terminal1. Both new joint and old residual transport identical; original distinct shooting skills remain.')
 if name=='ovr-probe.mjs':
  text=text.replace('Joint source-self floor vs frozen v30.','Joint creator/finisher flow vs frozen v30.').replace('Source self-role floor flow applies to actual cards and synthetic profiles, new v35 source contexts;','Joint creator/finisher flow applies to actual cards and synthetic profiles, new v35 source contexts;')
 if name=='verify-validation.py':text=text.replace('Fixed source-self floor, four-season same-season reconstruction','Joint creator/terminal transport, four-season same-season reconstruction')
 f=R/name;assert not f.exists();f.write_text(text,encoding='utf-8')
print('Created fixed-control source, basic/on-court, workload and independent checks.')

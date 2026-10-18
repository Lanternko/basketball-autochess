"""Create an isolated fixed source-self-floor experiment; preserve previous artifacts."""
import hashlib,json
from pathlib import Path
ROOT=Path('reports/player-impact-v34');OLD=Path('reports/player-impact-v31')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=['input.mjs','engine.mjs','probability.mjs','worker.mjs','prepare-contexts.mjs','run.mjs','validation-score.py','verify-ledgers.mjs','ovr-input.mjs']
for f in files:
 out=ROOT/f;assert not out.exists(),out
 text=(OLD/f).read_text(encoding='utf-8').replace('reports/player-impact-v31','reports/player-impact-v34')
 if f=='prepare-contexts.mjs':
  start=text.index("design:'");end=text.index("',stints",start)
  text=text[:start]+"design:'Fixed source-self-floor hypothesis: incoming receiver capacity=terminal minus source self role. Scale pass supply only when required for feasible receiver capacity with zero self-assists; residual terminal demand remains self, so terminal volume is conserved. Source role floor is a descriptive assumption, not proven ability. Probability, source attributes, FGA/exposure/energy support and v30 creation dependence unchanged. Same-season reconstruction; full-season source descriptors contain aggregate outcomes, not a blind or causal estimate."+text[end:]
  text=text.replace("sourceSelfModelSHA256:hash('src/source_self_opportunities.js'),",'')
 if f=='run.mjs':
  text=text.replace(",['src/source_self_opportunities.js','test/source_self_opportunities.js']",",['test/joint_source_opportunities.js']")
  text=text.replace("version:'source-self-supported-flow-31'","version:'joint-source-self-floor-34'")
  start=text.index("design:'");end=text.index("',hashes",start)
  text=text[:start]+"design:'Predeclared fixed source-self-floor experiment, reserve=1; no fit or rank-based coefficient. Receive capacities leave each actor at least its descriptive elastic source-self rate; pass supply reduced only to make capacities feasible, all terminal demand remains conserved. No source attributes/roles or probabilities changed, contexts recomputed on identical FGA/stamina exposure. Compare archived official control and v30, full and strict four seasons, three seeds each. Every season must retain official winsMAE+0.5 adoption gate; report all individual, role-group and on-court errors, not just favorable outcomes. No adoption based only on source allocation score or named-player ranks. Same-season reconstruction, not blind/causal."+text[end:]
 text=text.replace('Only the opportunity transport changes in v31','Only the opportunity transport changes in v34')
 out.write_text(text,encoding='utf-8')
protocol={'stage':'predeclared-fixed-mechanism','priorTurn':'progress: v33 source/fit verified; no adoption','reserve':1,'fit':False,'hypothesis':'Source self role anchors should not be erased by receiving transport. This floor can be wrong and is tested rather than adopted. Full terminal volume is conserved while passer supply and receiver transport jointly adapt.','controls':['archived official model','v30 full residual self'],'adoptionGate':'Each of four seasons official control winsMAE+0.5, with complete individual/on-court and role-group review. No threshold relaxed and no rank/name-based tuning.','seasons':['2022-23','2023-24','2024-25','2025-26'],'seeds':[20261012,20261013,20261014],'uncertainty':'Same-season reconstruction, fixed source descriptors with aggregate made outcomes. Not blind/causal; source-self floor is not physiology.','hashes':{str(ROOT/f).replace('\\','/'):sha(ROOT/f) for f in files+['model.mjs','scaffold.py']}}
(ROOT/'mechanism-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
print(json.dumps({'created':len(files),'fixedReserve':1,'adopted':False}))

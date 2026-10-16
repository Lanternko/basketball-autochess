"""Freeze the prospective runtime comparison after older-season mark calibration."""
import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v36');O=Path('reports/player-impact-v35');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fit=json.loads((R/'marked-fit.json').read_text(encoding='utf-8'));assert fit['trainingSeasons']==['2022-23','2023-24','2024-25']
files=['input.mjs','engine.mjs','probability.mjs','worker.mjs','prepare-contexts.mjs','run.mjs','validation-score.py','verify-ledgers.mjs','ovr-input.mjs']
design='Terminal-column projection of positive source self/pass prior; creator row budgets removed. One positive self scale estimated on 2022-25 conditional FGA marks only using frozen v30 source probabilities, never rank/wins/ONOFF; 2025-26 separate check. No source self cap/floor, no self-assists. Same raw source roles/attributes and v30 probability mechanism, source contexts recomputed on identical FGA/energy support. Four same-season reconstructions,3seeds,full/strict; official per-season winsMAE+0.5 unchanged. Individual/position/on-court and matched workload review required. Not blind/causal or a physiological capacity estimate.'
for name in files:
 s=(O/name).read_text(encoding='utf-8').replace('reports/player-impact-v35','reports/player-impact-v36').replace('test/joint_creator_transport.js','test/terminal_prior_transport.js')
 if name=='run.mjs':
  s=s.replace("version:'joint-creator-terminal-35'","version:'terminal-prior-marked-36'")
  a=s.index("design:'");b=s.index("',hashes",a);s=s[:a]+"design:'"+design+s[b:]
  # The inherited runtime source list includes the new model and this fit.
  s=s.replace("const root='reports/player-impact-v36'","const root='reports/player-impact-v36'")
 if name=='prepare-contexts.mjs':
  a=s.index("design:'");b=s.index("',stints",a);s=s[:a]+"design:'"+design+s[b:]
 f=R/name;assert not f.exists();f.write_text(s,encoding='utf-8')
protocol={'hypothesis':design,'selfScale':fit['selfScale'],'trainingSeasons':fit['trainingSeasons'],'fittedParameters':['one global logSelfScale'],'rawAttributesUnchanged':True,'adoptionGate':'Each season archived official winsMAE+0.5, plus complete individual/position/on-court/workload review; never relaxed or rank fitted.',
 'hashes':{str(R/n).replace('\\','/'):sha(R/n) for n in [*files,'model.mjs','marked-fit.json','marked-protocol.json','scaffold-runtime.py']}|{'test/terminal_prior_transport.js':sha('test/terminal_prior_transport.js')}}
(R/'mechanism-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8');print('Frozen terminal-prior runtime experiment')

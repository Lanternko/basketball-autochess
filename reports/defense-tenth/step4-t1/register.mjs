import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const root='reports/defense-tenth/step4-t1';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const walk=p=>fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(p,e.name)):[path.join(p,e.name).replaceAll('\\','/')]);
if(fs.existsSync(root+'/protocol.json'))throw Error('Protocol already registered; never overwrite');
const protectedFiles=[...walk('reports/defense-tenth/step3-a'),...walk('reports/defense-tenth/step3-a2'),...walk('src')].sort();
const protectedHashes=Object.fromEntries(protectedFiles.map(p=>[p,hash(p)]));
fs.writeFileSync(root+'/protected-before.json',JSON.stringify(protectedHashes,null,2)+'\n');
const protocol={version:'tenth-t1-rescore-v1',registeredAt:new Date().toISOString(),scope:'T1 only. Existing outputs, no simulations, no new seasons, no engine/card changes. All four seasons already observed.',
  protectedManifestSHA:hash(root+'/protected-before.json'),
  inputHashes:Object.fromEntries(['reports/defense-tenth/step3-a2/analysis.json','reports/defense-seventh/full-comparison.json','reports/defense-tenth/step2/season-analysis.json','reports/defense-fourth/v1-seeds.json','reports/defense-fourth/final-normalized-seeds.json'].map(p=>[p,hash(p)])),
  seasons:['2022-23','2023-24','2024-25','2025-26'],seeds:Array.from({length:20},(_,i)=>20261012+i),
  eligibility:{task1:'Full-season same-season cards and full-season schedule only. Calendar holdouts never substituted for full-season. Historical simple has no full-season prediction; do not manufacture answer-copy predictions.',task2:'Reuse A2 L1/L2. L2 is answer-side newcomer diagnostic, not independent portability test. Known future exposure/soft minute targets, pre-opening schedule remain disclosed.'},
  ranking:{axes:['net','wins'],primary:'net',actualTop5:'descending actual metric ranks <=5',actualBottom5:'descending actual metric ranks >=26',topFailure:'predicted rank >10',bottomFailure:'predicted rank <=20',ties:'average tied rank, no jitter',prediction:'mean of existing 20 seeds before ranking',pass:'zero failures; explanations do not waive a failure. Combined pass requires both axes. Missing is unevaluated, never pass.'},
  errors:{offense:'O = predicted PPG - actual PPG, separately league-centered',defense:'D = actual opponent PPG - predicted opponent PPG, separately league-centered',identity:'centered net error = O + D; retain raw values',direction:'absolute error <=0.25 point/game is near zero; positive overestimates strength; negative underestimates'},
  attribution:{principle:'Observational abnormality alone is not causal attribution. Counterfactual must remove failure on its own axis and reduce absolute error >=50%, with sign agreement. Otherwise unexplained, with anomaly flags reported separately. Never coach/tactics attribution.',
    clutch:{definition:'Fourth quarter and overtime clock <=300 seconds, pre-event absolute lead <=5. Score increments and elapsed time use prior-event scoreboard; only exact final-score/event-score reconciliation games accepted.',minimumCoverage:0.85,minimumMinutes:40,minimumRateDifferencePer48:10,minimumImpactPerGame:0.75,impact:'(clutch net - nonclutch net/minute * clutch minutes)/all season games; coverage >=85%, incomplete game impact extrapolated by GP/validGP. No simulations adjusted.',counterfactual:'actual net minus impact; rank all 30 again. Only net-axis explanation; wins attribution requires unavailable simulated clutch traces, so never inferred.'},
    luck:{close:'final absolute margin <=5',minimumCloseGames:15,closeWinRateDeviation:0.15,expectedWins:'GP * PF^14/(PF^14+PA^14), fixed exponent 14 diagnostic convention, not fitted to answers',minimumWinExcess:3,counterfactual:'actual wins replaced by net-based expected wins, rank all 30 again; only wins-axis eligible. This is win conversion anomaly, not proof of random luck and cannot explain net error.'},
    missingPrior:{eligible:'L1 only',minimumActualMinuteShare:0.10,effect:'L2-L1 same season, same seed existing outputs; must remove rank failure, reduce absolute corresponding error >=50%, and move prediction toward truth. L2 changes only no-prior cards. Supports this model-input explanation; not biological causal claim.'},
    unresolved:'No qualifying explanation => 無法解釋. Partial contributions and flags not promoted to explained.'},
  metrics:['centered net RMSE','Spearman net ranking','win MAE','win RMSE','calibration slope','SD ratio','failure counts on both axes'],
  uncertainty:'Reuse existing A2 joint franchise+seed intervals where applicable; no seed-only significance claims. Rank threshold audit is deterministic 20-seed mean, not causal inference.',
  outputs:['analysis.json','coverage.json','real-diagnostics.json','failures.md','team-errors.md','report.md','completion-audit.json'],
  freeze:'Rules not modified after scoring. Finish T1 then stop; T2/T3/T4 not started.'};
fs.writeFileSync(root+'/protocol.json',JSON.stringify(protocol,null,2)+'\n');
fs.writeFileSync(root+'/protocol.sha256',hash(root+'/protocol.json')+'  protocol.json\n');
console.log(JSON.stringify({registeredAt:protocol.registeredAt,sha256:hash(root+'/protocol.json'),protectedFiles:protectedFiles.length}));

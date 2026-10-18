import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='reports/player-impact-v24',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),groups={};
for(const f of [root+'/validation-protocol.json','reports/player-box-audit/source-hashes.json','reports/player-impact-v14/validation-protocol.json',...['19','20','21','22','23'].flatMap(v=>['validation','ovr'].map(n=>`reports/player-impact-v${v}/${n}-protocol.json`))]){
 const source=read(f),hashes=source.hashes??source;for(const[path,h]of Object.entries(hashes))assert.equal(hash(path),h,`Frozen source drift: ${path}`);groups[f]=Object.keys(hashes).length;
}
const manifest=read(root+'/validation-manifest.json');assert.equal(manifest.jobs.length,24);for(const job of manifest.jobs)assert.equal(hash(job.file),job.sha256);
const ledger=read(root+'/ledger-verification.json');assert.ok(ledger.passed);assert.equal(ledger.files,24);
const parity=read(root+'/season-parity.json');for(const k of ['allMatchesAndTeamStatsExact','onCourtFgLedgersExact','putbackAuditExact','allPersonalNonDrebCountersExact'])assert.equal(parity[k],true);assert.equal(parity.games,ledger.games);
const probe=read(root+'/counterfactual-parity.json');for(const k of ['allNonDrebCountersExact','cacheExactParity','previousInputUnchanged','syntheticAttributesUnchanged'])assert.equal(probe[k],true);assert.equal(probe.games,96);
assert.equal(read(root+'/free-throw-audit.json').passiveExactMatchAndTeamParity,true);
const status=read(root+'/status.json');assert.equal(status.officialModelAdopted,false);assert.equal(status.goalComplete,false);assert.equal(status.targetPlayers,582);
for(const file of ['counterfactual-parity.json','free-throw-audit.json','season-parity.json'])for(const[f,h]of Object.entries(read(root+'/'+file).hashes))assert.equal(hash(f),h);
const artifacts=['report.md','report.py','status.json','2025-26-player-validation.csv','scores.json','all-players.csv','all-players-on-court.csv','ledger-verification.json','season-parity.json','counterfactual-parity.json','free-throw-audit.json','old-source-allocation-audit.json','audit-old-allocation.py','audit-free-throws.mjs','audit-engine.mjs','ovr-input.mjs','verify-counterfactual-parity.mjs','verify-season-parity.mjs','export-players.py','validation-score.py','verify-ledgers.mjs','verify.mjs','../../test/conditional_dreb_recipient.js'];
const output={groups,resultFiles:manifest.jobs.length,games:ledger.games,artifacts:Object.fromEntries(artifacts.map(f=>[root+'/'+f,hash(root+'/'+f)])),status:'Frozen source/run hashes, 24 season ledgers and exact non-DREB parity passed. Conditional DREB recipient reconstruction only; no new OVR ranking. Candidate remains experimental, not adopted.'};
fs.writeFileSync(root+'/verification.json',JSON.stringify(output,null,2));console.log(JSON.stringify({groups,resultFiles:manifest.jobs.length,games:ledger.games,status:output.status},null,2));

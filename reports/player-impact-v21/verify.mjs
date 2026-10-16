import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='reports/player-impact-v21',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const groups={};
for(const name of ['validation-protocol','ovr-protocol']){
 const source=read(root+'/'+name+'.json');for(const[f,h]of Object.entries(source.hashes))assert.equal(hash(f),h,`Frozen source drift: ${f}`);groups[name]=Object.keys(source.hashes).length;
}
for(const f of ['reports/player-box-audit/source-hashes.json','reports/player-impact-v14/validation-protocol.json','reports/player-impact-v19/validation-protocol.json','reports/player-impact-v19/ovr-protocol.json','reports/player-impact-v20/validation-protocol.json','reports/player-impact-v20/ovr-protocol.json']){
 const source=read(f),hashes=source.hashes??source;for(const[path,h]of Object.entries(hashes))assert.equal(hash(path),h,`Archived source drift: ${path}`);groups[f]=Object.keys(hashes).length;
}
const manifest=read(root+'/validation-manifest.json');for(const job of manifest.jobs)assert.equal(hash(job.file),job.sha256);
const benchmark=read(root+'/ovr-checkpoint.json');assert.equal(benchmark.rows.length,36);assert.equal(benchmark.fingerprint,read(root+'/ovr-protocol.json').fingerprint);
const ledger=read(root+'/ledger-verification.json');assert.ok(ledger.passed);assert.equal(ledger.files,24);
assert.equal(read(root+'/ovr-cache-verification.json').exactGameAndIndividualCounterParity,true);
assert.equal(read(root+'/input-isolation-verification.json').isolated.previousInputUnchanged,true);
const artifacts=['report.md','status.json','2025-26-player-validation.csv','scores.json','all-players.csv','all-players-on-court.csv','team-impact-audit.json','team-impact-audit.csv','ovr-checkpoint.json','ledger-verification.json','ovr-cache-verification.json','input-isolation-verification.json','ovr-input-isolated.mjs','verify-input-isolation.mjs','report.py','validation-score.py','verify-ledgers.mjs','verify.mjs','team-impact-audit.py','../../test/measured_terminal_risk.js'];
const output={groups,resultFiles:manifest.jobs.length,ovrRows:benchmark.rows.length,artifacts:Object.fromEntries(artifacts.map(f=>[root+'/'+f,hash(root+'/'+f)])),status:'All archived and candidate source hashes, full/strict run hashes and required ledgers passed. Candidate remains experimental, not adopted.'};
fs.writeFileSync(root+'/verification.json',JSON.stringify(output,null,2));console.log(JSON.stringify({groups,resultFiles:manifest.jobs.length,ovrRows:benchmark.rows.length,status:output.status},null,2));

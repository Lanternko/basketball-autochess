import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='reports/player-impact-v22',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const groups={};
for(const f of [root+'/validation-protocol.json',root+'/ovr-protocol.json','reports/player-box-audit/source-hashes.json','reports/player-impact-v14/validation-protocol.json',...['19','20','21'].flatMap(v=>['validation','ovr'].map(n=>`reports/player-impact-v${v}/${n}-protocol.json`))]){
 const source=read(f),hashes=source.hashes??source;for(const[path,h]of Object.entries(hashes))assert.equal(hash(path),h,`Frozen source drift: ${path}`);groups[f]=Object.keys(hashes).length;
}
const manifest=read(root+'/validation-manifest.json');for(const job of manifest.jobs)assert.equal(hash(job.file),job.sha256);
assert.equal(manifest.jobs.length,24);
const benchmark=read(root+'/ovr-checkpoint.json');assert.equal(benchmark.rows.length,36);assert.equal(benchmark.fingerprint,read(root+'/ovr-protocol.json').fingerprint);
const ledger=read(root+'/ledger-verification.json');assert.ok(ledger.passed);assert.equal(ledger.files,24);
assert.equal(read(root+'/ovr-cache-verification.json').exactGameAndIndividualCounterParity,true);
const artifacts=['report.md','status.json','2025-26-player-validation.csv','scores.json','all-players.csv','all-players-on-court.csv','ovr-checkpoint.json','ledger-verification.json','ovr-cache-verification.json','allocation-audit.json','allocation-audit.py','allocation-players.csv','allocation-teams.csv','putback-runtime-audit.json','putback-runtime-strict-audit.json','audit-engine.mjs','putback-runtime-audit.mjs','putback-runtime-strict-audit.mjs','report.py','export-players.py','validation-score.py','verify-ledgers.mjs','verify-ovr-cache.mjs','verify.mjs','../../test/measured_putback.js'];
const output={groups,resultFiles:manifest.jobs.length,ovrRows:benchmark.rows.length,artifacts:Object.fromEntries(artifacts.map(f=>[root+'/'+f,hash(root+'/'+f)])),status:'Archived and candidate source hashes, 24 full/strict run hashes, 36 OVR sample rows and required ledgers passed. Candidate remains experimental, not adopted.'};
fs.writeFileSync(root+'/verification.json',JSON.stringify(output,null,2));console.log(JSON.stringify({groups,resultFiles:manifest.jobs.length,ovrRows:benchmark.rows.length,status:output.status},null,2));

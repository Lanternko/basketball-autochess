import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='reports/player-impact-v23',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),groups={};
for(const f of [root+'/validation-protocol.json',root+'/ovr-protocol.json','reports/player-box-audit/source-hashes.json','reports/player-impact-v14/validation-protocol.json',...['19','20','21','22'].flatMap(v=>['validation','ovr'].map(n=>`reports/player-impact-v${v}/${n}-protocol.json`))]){
 const source=read(f),hashes=source.hashes??source;for(const[path,h]of Object.entries(hashes))assert.equal(hash(path),h,`Frozen source drift: ${path}`);groups[f]=Object.keys(hashes).length;
}
const manifest=read(root+'/validation-manifest.json');assert.equal(manifest.jobs.length,24);for(const job of manifest.jobs)assert.equal(hash(job.file),job.sha256);
const checkpoint=read(root+'/ovr-checkpoint.json');assert.equal(checkpoint.rows.length,36);assert.equal(checkpoint.fingerprint,read(root+'/ovr-protocol.json').fingerprint);
const ledger=read(root+'/ledger-verification.json');assert.ok(ledger.passed);assert.equal(ledger.files,24);assert.equal(read(root+'/ovr-cache-verification.json').exactGameAndIndividualCounterParity,true);
for(const s of Object.values(read(root+'/source-score-audit.json')))assert.equal(s.invalid.length,0);
const status=read(root+'/status.json');assert.equal(status.officialModelAdopted,false);assert.equal(status.goalComplete,false);assert.equal(status.targetPlayers,582);
const artifacts=['report.md','report.py','status.json','2025-26-player-validation.csv','scores.json','all-players.csv','all-players-on-court.csv','ovr-checkpoint.json','ledger-verification.json','ovr-cache-verification.json','source-score-audit.json','audit-source-scores.py','putback-fit-audit.json','audit-putback-fit.py','export-players.py','validation-score.py','verify-ledgers.mjs','verify-ovr-cache.mjs','verify.mjs','../../test/measured_putback_choice.js','../../test/measured_putback_choice_profiles.js'];
const output={groups,resultFiles:manifest.jobs.length,ovrRows:checkpoint.rows.length,games:ledger.games,artifacts:Object.fromEntries(artifacts.map(f=>[root+'/'+f,hash(root+'/'+f)])),status:'Frozen archived and candidate sources, all 24 run hashes and required ledgers passed. 31-player OVR diagnostic only. All four win gates fail; experimental, not adopted.'};
fs.writeFileSync(root+'/verification.json',JSON.stringify(output,null,2));console.log(JSON.stringify({groups,resultFiles:manifest.jobs.length,ovrRows:checkpoint.rows.length,games:ledger.games,status:output.status},null,2));

import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='reports/player-impact-v26',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),groups={};
for(const f of [root+'/validation-protocol.json','reports/player-box-audit/source-hashes.json','reports/player-impact-v14/validation-protocol.json',...['19','20','21','22','23'].flatMap(v=>['validation','ovr'].map(n=>`reports/player-impact-v${v}/${n}-protocol.json`)), 'reports/player-impact-v24/validation-protocol.json','reports/player-impact-v25/validation-protocol.json']){
 const source=read(f),hashes=source.hashes??source;for(const[path,h]of Object.entries(hashes))assert.equal(hash(path),h,`Frozen source drift: ${path}`);groups[f]=Object.keys(hashes).length;
}
const manifest=read(root+'/validation-manifest.json');assert.equal(manifest.jobs.length,24);for(const job of manifest.jobs)assert.equal(hash(job.file),job.sha256);
const ledger=read(root+'/ledger-verification.json');assert.ok(ledger.passed);assert.equal(ledger.files,24);
const probe=read(root+'/counterfactual-verification.json');for(const k of ['cacheExactParity','disabledIntensityExactPreviousParity','previousInputUnchanged','syntheticAttributesUnchanged'])assert.equal(probe[k],true);assert.equal(probe.games,96);
assert.equal(read(root+'/contact-opportunity-audit.json').passiveExactMatchAndTeamParity,true);
for(const file of ['counterfactual-verification.json','contact-opportunity-audit.json'])for(const[f,h]of Object.entries(read(root+'/'+file).hashes))assert.equal(hash(f),h);
const status=read(root+'/status.json');assert.equal(status.officialModelAdopted,false);assert.equal(status.goalComplete,false);assert.equal(status.targetPlayers,582);
const scores=read(root+'/scores.json');assert.equal(scores.cells.length,12);for(const c of scores.cells)assert.equal(c.onCourtPlayers.length,c.players.length);
const failed=read(root+'/validation-protocol.json').seasons.filter(season=>{
 const c=Object.fromEntries(scores.cells.filter(c=>c.season===season).map(c=>[c.version,c]));
 return c['rotation-space'].teamMetrics.winsMAE>c.control.teamMetrics.winsMAE+.5;
});assert.deepEqual(status.teamWinGatesFailed,failed);
for(const[f,h]of Object.entries(read(root+'/source-verification.json').hashes))assert.equal(hash(f),h);
const artifacts=['report.md','report.py','status.json','2025-26-player-validation.csv','scores.json','all-players.csv','all-players-on-court.csv','ledger-verification.json','counterfactual-verification.json','contact-opportunity-audit.json','audit-contact-opportunities.mjs','audit-engine.mjs','ovr-input.mjs','verify-counterfactual.mjs','export-players.py','validation-score.py','verify-ledgers.mjs','verify.mjs','verify-source.py','source-verification.json','contact-intensity-prior.json','pilot-report.md','pilot-verification.json'];
const output={groups,resultFiles:manifest.jobs.length,games:ledger.games,artifacts:Object.fromEntries(artifacts.map(f=>[root+'/'+f,hash(root+'/'+f)])),status:'Frozen source/run hashes, 24 season ledgers including FT identities/categories, 96 source-intensity counterfactual probes and passive contact opportunity audit passed. Experimental; not adopted; no v26 OVR ranking.'};
fs.writeFileSync(root+'/verification.json',JSON.stringify(output,null,2));console.log(JSON.stringify({resultFiles:output.resultFiles,games:output.games,status:output.status},null,2));

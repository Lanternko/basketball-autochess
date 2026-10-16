import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {Worker,isMainThread,parentPort,workerData} from 'node:worker_threads';
import {ovrInput as previousInput} from '../player-impact-v20/ovr-input.mjs';
const fingerprint=x=>crypto.createHash('sha256').update(JSON.stringify(x,(_,v)=>v instanceof Map?[...v]:v)).digest('hex');
if(!isMainThread){
 const before=await previousInput('2025-26'),original=fingerprint(before);
 const {ovrInput}=await import(workerData.isolated?'./ovr-input-isolated.mjs':'./ovr-input.mjs');
 const next=await ovrInput('2025-26');
 parentPort.postMessage({inputHash:fingerprint(next),previousInputUnchanged:original===fingerprint(before)});
}else{
 const run=isolated=>new Promise((resolve,reject)=>{const w=new Worker(new URL(import.meta.url),{workerData:{isolated}});w.once('error',reject);w.once('message',resolve);});
 const [legacy,isolated]=await Promise.all([run(false),run(true)]);
 assert.equal(legacy.inputHash,isolated.inputHash,'Single-version worker inputs must be exactly identical');
 assert.equal(isolated.previousInputUnchanged,true,'Cross-version cached inputs must remain unchanged');
 const out={legacy,isolated,interpretation:'Frozen original OVR worker is valid in its dedicated process: its complete candidate input equals isolated input. Its previous-version cache is mutated in that process, so do not import both versions for a mixed comparison there. Use ovr-input-isolated.mjs for future same-process comparisons. Existing sample outputs remain valid; original frozen sources unchanged.'};
 fs.writeFileSync('reports/player-impact-v21/input-isolation-verification.json',JSON.stringify(out,null,2));console.log(out);
}

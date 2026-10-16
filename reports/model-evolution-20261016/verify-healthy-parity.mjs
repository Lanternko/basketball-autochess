import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/model-evolution-20261016',sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const manifest=JSON.parse(fs.readFileSync('reports/player-impact-v41/probe-manifest.json'));
assert.equal(sha('reports/player-impact-v41/probe-checkpoint.json'),manifest.checkpointSHA256);
const old=JSON.parse(fs.readFileSync('reports/player-impact-v41/probe-checkpoint.json')).rows.filter(r=>r.job.variant==='v41'&&[1628983,203999,1629011].includes(r.job.id));
assert.equal(old.length,3);
const rows=[],workers=[],started=Date.now();
try{await Promise.all(old.map(previous=>new Promise((resolve,reject)=>{
 const w=new Worker(new URL('./healthy-ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{
  try{if(m.error)throw Error(m.error);const expected=previous.result.arms.find(a=>a.arm==='supportedHealthy');assert.deepEqual(m.result.arms,[expected]);assert.equal(m.result.simulatedGames,480);
   rows.push({name:m.result.name,playerId:m.result.playerId,pairedObservations:expected.games.length,allScoresBaselinesPlayerStatsAndMinutesExactlyEqual:true,originalGames:previous.result.simulatedGames,optimizedGames:m.result.simulatedGames});console.log(JSON.stringify(rows.at(-1)));resolve();
  }catch(e){reject(e);}
 });w.postMessage(previous.job);
})));}finally{await Promise.all(workers.map(w=>w.terminate()));}
fs.writeFileSync(root+'/healthy-parity.json',JSON.stringify({passed:true,workerSHA256:sha(root+'/healthy-ovr-worker.mjs'),frozenCheckpointSHA256:manifest.checkpointSHA256,comparison:'deepStrictEqual on complete supportedHealthy arm; only fullCap arm omitted',elapsedSeconds:(Date.now()-started)/1000,rows},null,2));

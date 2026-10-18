// Step 2b (local only): extra seed draws for the v47 board so stability and shrinkage can be
// validated on independent halves. Needs the full local research inputs.
//   node reports/ovr-v47-2025-26/resample-run.mjs [--start 4] [--samples 20] [--workers 6] [--ids 1628983,201939]
// Resumable: finished players are kept in resample-checkpoint.jsonl and skipped on restart.
import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {ovrInput} from './input.mjs';
const root='reports/ovr-v47-2025-26',arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i<0?d:process.argv[i+1];};
const start=+arg('start',4),samples=+arg('samples',20),workers=+arg('workers',6),seed=20261016;
const x=await ovrInput(),only=arg('ids',null)?.split(',').map(Number);
const ids=x.players.map(p=>p.playerId).filter(id=>!only||only.includes(id)).sort((a,b)=>a-b);
const cf=root+'/resample-checkpoint.jsonl',pf=root+'/resample-protocol.json';
const protocol={engine:'v47',seed,start,samples,note:'Same paired design as run.mjs; seed indices continue after the original 0..3.'};
if(fs.existsSync(pf)){const old=JSON.parse(fs.readFileSync(pf));if(old.seed!==seed||old.start!==start||old.samples!==samples)throw Error('Checkpoint protocol differs; move resample-checkpoint.jsonl away first');}
else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
const done=new Set(fs.existsSync(cf)?fs.readFileSync(cf,'utf8').trim().split('\n').filter(Boolean).map(l=>JSON.parse(l).playerId):[]);
const jobs=ids.filter(id=>!done.has(id)).map(id=>({id,seed,start,samples}));
console.log(JSON.stringify({total:ids.length,remaining:jobs.length,gamesPerPlayer:30*samples*4,workers}));
let next=0,finished=0;const pool=[],t0=Date.now();
await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();
 const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let k=0;k<Math.min(workers,jobs.length);k++){
  const w=new Worker(new URL('./resample-worker.mjs',import.meta.url));pool.push(w);w.on('error',reject);
  w.on('message',m=>{
   if(m.error)return reject(Error(m.error));
   fs.appendFileSync(cf,JSON.stringify(m.result)+'\n');finished++;
   if(finished%10===0||finished===jobs.length){const s=(Date.now()-t0)/1000;console.log(JSON.stringify({finished,remaining:jobs.length-finished,etaMinutes:Math.round(s/finished*(jobs.length-finished)/60)}));}
   if(finished===jobs.length)resolve();else dispatch(w);
  });dispatch(w);
 }
}).finally(()=>Promise.all(pool.map(w=>w.terminate())));
console.log('done; next: python3 '+root+'/resample-analyze.py');

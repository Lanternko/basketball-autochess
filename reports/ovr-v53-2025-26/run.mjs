// v53 OVR board (local only).
//   node reports/player-impact-v53/calibrate-spread.mjs            # once, writes spread.json
//   node reports/ovr-v53-2025-26/run.mjs --variant control --ids 1628983,201939,1627936   # parity smoke test
//   node reports/ovr-v53-2025-26/run.mjs --variant both            # all 582 players, about 72 minutes
//   python3 reports/ovr-v53-2025-26/analyze.py
// Resumable through checkpoint-<variant>.jsonl.
import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {ovrInput} from '../ovr-v47-2025-26/input.mjs';
const root='reports/ovr-v53-2025-26',arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i<0?d:process.argv[i+1];};
const variant=arg('variant','both'),workers=+arg('workers',6),seed=20261016,samples=4;
const x=await ovrInput(),only=arg('ids',null)?.split(',').map(Number);
const ids=x.players.map(p=>p.playerId).filter(id=>!only||only.includes(id)).sort((a,b)=>a-b);
const cf=`${root}/checkpoint-${variant}.jsonl`;
const done=new Set(fs.existsSync(cf)?fs.readFileSync(cf,'utf8').trim().split('\n').filter(Boolean).map(l=>JSON.parse(l).playerId):[]);
const jobs=ids.filter(id=>!done.has(id)).map(id=>({id,variant,seed,samples}));
console.log(JSON.stringify({variant,total:ids.length,remaining:jobs.length,workers}));
let next=0,finished=0;const pool=[],t0=Date.now();
await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();
 const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let n=0;n<Math.min(workers,jobs.length);n++){
  const w=new Worker(new URL('./worker.mjs',import.meta.url));pool.push(w);w.on('error',reject);
  w.on('message',m=>{
   if(m.error)return reject(Error(m.error));
   fs.appendFileSync(cf,JSON.stringify(m.result)+'\n');finished++;
   if(finished%20===0||finished===jobs.length){const s=(Date.now()-t0)/1000;console.log(JSON.stringify({finished,remaining:jobs.length-finished,etaMinutes:Math.round(s/finished*(jobs.length-finished)/60)}));}
   if(finished===jobs.length)resolve();else dispatch(w);
  });dispatch(w);
 }
}).finally(()=>Promise.all(pool.map(w=>w.terminate())));
console.log('done');

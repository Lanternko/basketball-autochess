import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v29',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
// Explicit diagnostic selection: prior user-named comparisons plus one large-
// minute reserve and a repeatedly unavailable high-minute star. No rank fitting.
const ids=[1629011,1641705,1630595,1628983,1629029,203999,1629674,201939,1630202,203954];
const src=read(root+'/workload-source.json'),samples=4,seed=20261016;
const files=[root+'/build-workload.py',root+'/workload-source.json',root+'/workload-game-rows.jsonl',root+'/benchmark.mjs',root+'/ovr-input.mjs',root+'/worker.mjs',root+'/run.mjs','src/player_workload.js','test/player_workload.js'];
const hashes={...read('reports/player-impact-v28/validation-protocol.json').hashes,...src.hashes,
 ...read('reports/player-impact-v24/all-2025-26/protocol.json').hashes,
 ...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Frozen workload source drift: '+f);};verify();
const protocol={version:'workload-availability-29',season:'2025-26',ids,samples,seed,capMinutes:src.capMinutes,
 design:'Diagnostic only: 10 selected players, natural position, four distinct mean70 teammates; 30 fixed primary opponent fives, each with mean70 positional relief. Full 48-minute fixed regulation, sourcePeriods4, foulOut99, fatigue on, matched same-slot average70 baseline at exactly the same minutes/rotation/seed; both seats paired, 2 standardized rotation phases balanced within four seeds per opponent. Four arms: cap extrapolation, actual clipped per-played-game supported load, and provisional recurrent-injury coefficients 0.05/0.10. Minutes affect replacement/rotation and fatigue, never skill attributes. No wins/ONOFF/ranks used to choose cap or coefficients. Not a complete OVR or medical/causal validation; source-opponent selection bias and source-efficiency portability remain uncorrected.',hashes};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex');
const pf=root+'/protocol.json',cf=root+'/checkpoint.json';
if(fs.existsSync(pf)){if(JSON.stringify(read(pf))!==JSON.stringify({...protocol,fingerprint}))throw Error('Protocol drift');}else fs.writeFileSync(pf,JSON.stringify({...protocol,fingerprint},null,2));
let state=fs.existsSync(cf)?read(cf):{fingerprint,rows:[]};if(state.fingerprint!==fingerprint)throw Error('Checkpoint drift');
const jobs=ids.filter(id=>!state.rows.some(r=>r.job.id===id)).map(id=>({id,samples,seed}));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{
   if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(cf,JSON.stringify(state));done++;
   console.log(JSON.stringify({done,total:jobs.length,name:m.result.name,simulatedGames:m.result.simulatedGames}));
   if(done===jobs.length)resolve();else dispatch(w);
  });dispatch(w);
 }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}
verify();if(state.rows.length!==ids.length)throw Error('Incomplete pilot');
fs.writeFileSync(root+'/manifest.json',JSON.stringify({fingerprint,players:state.rows.length,simulatedGames:state.rows.reduce((s,r)=>s+r.result.simulatedGames,0),checkpointSHA256:hash(cf)},null,2));

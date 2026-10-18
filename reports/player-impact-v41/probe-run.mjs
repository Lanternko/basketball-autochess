import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v41',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),protocol=read(root+'/probe-protocol.json');
const verify=()=>{for(const[p,h]of Object.entries(protocol.hashes))if(sha(p)!==h)throw Error('Frozen source drift: '+p);};verify();
let state=fs.existsSync(root+'/probe-checkpoint.json')?read(root+'/probe-checkpoint.json'):{rows:[]};
const all=protocol.ids.flatMap(id=>protocol.variants.map(variant=>({id,variant,samples:protocol.samples,seed:protocol.seed}))),jobs=all.filter(j=>!state.rows.some(r=>r.job.id===j.id&&r.job.variant===j.variant));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('./probe-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(root+'/probe-checkpoint.json',JSON.stringify(state));console.log(JSON.stringify({done:++done,total:jobs.length,variant:m.result.variant,name:m.result.name,games:m.result.simulatedGames}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
 }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/probe-manifest.json',JSON.stringify({jobs:all.length,simulatedGames:state.rows.reduce((s,r)=>s+r.result.simulatedGames,0),checkpointSHA256:sha(root+'/probe-checkpoint.json')},null,2));

import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v20',protocol=JSON.parse(fs.readFileSync(root+'/ovr-protocol.json'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const hashes={...protocol.hashes,[root+'/physique-worker.mjs']:hash(root+'/physique-worker.mjs')};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Source drift: '+f);};verify();
const ids=[1628983,1629029,203999,201939,1629674,1641705];
const jobs=ids.map(id=>({id,kind:'player',ablation:'physique70',season:protocol.season,samples:protocol.samples,seed:protocol.seed,version:protocol.versionEngine}));
let next=0,done=0;const rows=[],workers=[];
try{await new Promise((resolve,reject)=>{
 const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<2;i++){
  const w=new Worker(new URL('./physique-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);
  w.on('message',m=>{if(m.error)return reject(Error(m.error));rows.push(m);console.log(JSON.stringify({name:m.result.name,winRate:m.result.winRate}));if(++done===jobs.length)resolve();else dispatch(w);});dispatch(w);
 }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
const original=JSON.parse(fs.readFileSync(root+'/ovr-checkpoint.json')).rows;
fs.writeFileSync(root+'/physique-audit.json',JSON.stringify({design:'Mechanism ablation only: change the candidate physique attribute to70, holding source centers, role, skill, measured box rates, teammates, opponents and seeds fixed. Team shot/rebound physique paths remain active and respond to the altered value. Not a causal estimate of real height/weight, not a calibration choice; marginal CIs are not paired-difference CIs.',hashes,rows:rows.map(r=>({...r,original:original.find(p=>p.job.id===r.job.id).result}))},null,2));

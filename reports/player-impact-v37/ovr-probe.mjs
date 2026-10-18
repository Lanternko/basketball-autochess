import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v37',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const ids=read('reports/player-impact-v29/protocol.json').ids,samples=4,seed=20261016;
const files=[root+'/ovr-input.mjs',root+'/ovr-probe.mjs',root+'/ovr-worker.mjs'];
const hashes={...read('reports/player-impact-v30/ovr-probe-protocol.json').hashes,...read(root+'/validation-protocol.json').hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Frozen OVR probe source drift: '+f);};verify();
const protocol={ids,samples,seed,design:'Preserve old successful passer rows and terminal columns; project a separate positive own row whose total is old residual supply onto source own-rate shape. Strict feasibility: ownPool>1e-10*max(1,total) and each passer row below all other terminal columns by that tolerance. Only non-strict inputs use unfitted source self/pass prior projected to terminal columns (diagonal scale exactly1), explicitly relaxing passer rows. Numerical nonconvergence throws, never selects fallback. No new fitted coefficients, unchanged frozen elastic exponents, raw attributes, source roles and v30 probabilities. Recenter on identical source FGA/energy. Four seasons,3seeds,full/strict; archived official winsMAE+0.5 per season and broad individual/role/on-court/workload review. Same-season descriptors contain outcomes, not blind/causal. No ranking/name/onoff/wins residual fit.',hashes};
const pf=root+'/ovr-probe-protocol.json',cf=root+'/ovr-probe-checkpoint.json';
if(fs.existsSync(pf)){if(JSON.stringify(read(pf))!==JSON.stringify(protocol))throw Error('Probe protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
let state=fs.existsSync(cf)?read(cf):{rows:[]};const jobs=ids.filter(id=>!state.rows.some(r=>r.job.id===id)).map(id=>({id,samples,seed}));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('./ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{
   if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(cf,JSON.stringify(state));done++;
   console.log(JSON.stringify({done,total:jobs.length,name:m.result.name,simulatedGames:m.result.simulatedGames}));if(done===jobs.length)resolve();else dispatch(w);
  });dispatch(w);
 }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/ovr-probe-manifest.json',JSON.stringify({players:state.rows.length,simulatedGames:state.rows.reduce((s,r)=>s+r.result.simulatedGames,0),checkpointSHA256:hash(cf)},null,2));

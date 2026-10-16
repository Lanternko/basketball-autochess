import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v34',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const ids=read('reports/player-impact-v29/protocol.json').ids,samples=4,seed=20261016;
const files=[root+'/ovr-input.mjs',root+'/ovr-probe.mjs',root+'/ovr-worker.mjs'];
const hashes={...read('reports/player-impact-v30/ovr-probe-protocol.json').hashes,...read(root+'/validation-protocol.json').hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Frozen OVR probe source drift: '+f);};verify();
const protocol={ids,samples,seed,design:'Joint source-self floor vs frozen v30. Same 10 diagnostic players, 30 opponents, two phases, two seats, four seeds, cap and supported-healthy load as frozen v29. Full48 fatigue-on, matched same-role average70 baseline at identical minutes and schedule. Source self-role floor flow applies to actual cards and synthetic profiles, new v34 source contexts; source roles/attributes and workload unchanged. No passing pair quality bonus. Compare to exactly matching archived v30 cap/healthy arms, not raw rankings. No new all-player OVR or adoption.',hashes};
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

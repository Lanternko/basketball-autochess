import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {representativeIds} from '../ovr-2025-26-positional/protocol.mjs';
const root='reports/player-impact-v7',samples=40,seed=20261015;
const protocol={version:'centered-space-natural-role-ovr-7',samples,seed,ids:representativeIds,variants:['space-half','space-full'],
 design:'Equal 14.4-minute exposure, no fatigue/substitutions, one supported natural position, four distinct mean70 positional teammates, 30 opponents, both seating orders. Same role and auxiliary profile policy as prior positional test. Measured role priors added by minute-weighted position pools; no name-specific adjustments.',
 scope:'20-player mechanism screen, cannot establish all-player Top50 or completion of goal.'};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)+fs.readFileSync(root+'/engine.mjs')+fs.readFileSync('reports/player-impact-v6/ovr-input.mjs')+fs.readFileSync(root+'/ovr-worker.mjs')).digest('hex');
const file=root+'/ovr-checkpoint.json';let state={fingerprint,rows:[]};if(fs.existsSync(file)){state=JSON.parse(fs.readFileSync(file));if(state.fingerprint!==fingerprint)throw Error('OVR checkpoint drift');}
fs.writeFileSync(root+'/ovr-protocol.json',JSON.stringify({...protocol,fingerprint},null,2));
let jobs=protocol.variants.flatMap(version=>[...representativeIds.map(id=>({key:version+'-'+id,version,id,kind:'player'})),...[0,1,2,3,4].map(slot=>({key:version+'-base-'+slot,version,kind:'baseline',slot}))]).filter(j=>!state.rows.some(r=>r.job.key===j.key)).map(j=>({...j,samples,seed}));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<4;i++){
 const w=new Worker(new URL('./ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(file,JSON.stringify(state));console.log(JSON.stringify({done:++done,total:jobs.length,name:m.result.name,version:m.job.version,winRate:m.result.winRate}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}

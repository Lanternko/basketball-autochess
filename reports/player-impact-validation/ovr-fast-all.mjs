import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {ovrInput} from '../player-impact-v6/ovr-input.mjs';
const root='reports/player-impact-validation',x=ovrInput(),samples=10,seed=20261015,version='terminal-flow';
const protocol={version:'terminal-flow-all-player-screen-6',engine:version,season:'2025-26',samples,seed,players:x.players.length,
 design:'All 582 players, one natural role, four different positional mean70 teammates, 30 opponents, both seating orders, fixed 14.4 minutes no fatigue/substitutions. Provisional screening; refine ranking contenders before a final Top50. Same ten seed strata across players within each position.',
 roleAudit:x.roleAudit,sourceHashes:Object.fromEntries(['reports/player-impact-v6/engine.mjs','reports/player-impact-v6/model.mjs','reports/player-impact-v6/ovr-input.mjs','reports/player-impact-v6/ovr-worker.mjs'].map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')]))};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex'),file=root+'/ovr-all-checkpoint.json';let state={fingerprint,rows:[]};
if(fs.existsSync(file)){state=JSON.parse(fs.readFileSync(file));if(state.fingerprint!==fingerprint)throw Error('OVR source drift');}
fs.writeFileSync(root+'/ovr-all-protocol.json',JSON.stringify({...protocol,fingerprint},null,2));
const jobs=[...x.players.map(p=>({id:p.playerId,key:String(p.playerId),kind:'player'})),...[0,1,2,3,4].map(slot=>({slot,key:'base-'+slot,kind:'baseline'}))].filter(j=>!state.rows.some(r=>r.job.key===j.key)).map(j=>({...j,version,samples,seed}));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./fast-ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(file,JSON.stringify(state));if(++done%25===0||done===jobs.length)console.log(JSON.stringify({done,total:jobs.length}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}

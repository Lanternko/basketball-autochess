import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {positionalOvrInput} from '../player-impact-validation/positional-input.mjs';
const season=process.argv[2]??'2025-26',samples=10,seed=20261015,version='rotation-space',x=await positionalOvrInput(season),root=`reports/player-impact-v14/all-${season}`;
fs.mkdirSync(root,{recursive:true});
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const old=JSON.parse(fs.readFileSync('reports/player-impact-v14/validation-protocol.json')).hashes;
const files=['src/measured_creation_context.js','src/opportunity_transport.js','reports/player-impact-v14/engine.mjs','reports/player-impact-v14/model.mjs','reports/player-impact-v14/input.mjs',`reports/player-impact-v14/${season}-contexts.json`,`reports/player-impact-v14/${season}-synthetic-center.json`,'reports/player-impact-validation/positional-input.mjs','reports/player-impact-v14/season-ovr-worker.mjs'];
const hashes={...old,...Object.fromEntries(files.map(f=>[f,hash(f)]))},verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('All-player source drift: '+f);};verify();
const protocol={version:'observed-rotation-all-player-screen-14',engine:version,season,samples,seed,players:x.players.length,
 design:'Every player, one natural position, four different mean70 positional teammates, 30 opponents and both seating orders. Equal 14.4 minutes, no fatigue/substitution. Provisional mechanism screen; input uncertainty not propagated and ranking contenders require refinement. No player-name adjustment or minutes multiplier.',roleAudit:x.roleAudit,hashes};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex'),file=root+'/checkpoint.json';let state={fingerprint,rows:[]};
if(fs.existsSync(file)){state=JSON.parse(fs.readFileSync(file));if(state.fingerprint!==fingerprint)throw Error('All-player checkpoint drift');}
fs.writeFileSync(root+'/protocol.json',JSON.stringify({...protocol,fingerprint},null,2));
const jobs=[...x.players.map(p=>({id:p.playerId,key:String(p.playerId),kind:'player'})),...[0,1,2,3,4].map(slot=>({slot,key:'base-'+slot,kind:'baseline'}))].filter(j=>!state.rows.some(r=>r.job.key===j.key)).map(j=>({...j,season,version,samples,seed}));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./season-ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(file,JSON.stringify(state));if(++done%25===0||done===jobs.length)console.log(JSON.stringify({season,done,total:jobs.length}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();

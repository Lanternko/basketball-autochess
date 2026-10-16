import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {ovrInput} from './ovr-input.mjs';
const season='2025-26',samples=40,seed=20261015,version='rotation-space',root=`reports/player-impact-v24/all-${season}`,x=await ovrInput(season);
fs.mkdirSync(root,{recursive:true});
const read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const files=['reports/player-impact-v24/ovr-input.mjs','reports/player-impact-v24/season-ovr-worker.mjs','reports/player-impact-v24/all-ovr.mjs','reports/ovr-2025-26-positional/protocol.mjs','src/strength_benchmark.js'];
const hashes={...read('reports/player-impact-v23/ovr-protocol.json').hashes,...read('reports/player-impact-v24/validation-protocol.json').hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Full OVR frozen source drift: '+f);};verify();
const protocol={version:'conditional-dreb-all-player-24',season,samples,seed,engine:version,players:x.players.length,baselines:5,design:'Every source player, one natural position, four distinct mean70 positional teammates, 30 fixed opponents and both seating orders. 40 independent seed pairs per opponent, 2400 short games per player. All players including low minutes; no name/rank offsets, no minimum-minute filtering. Raw benchmark win probability, conditional simulation CI and marginal rank-overlap diagnostics only; input/model uncertainty not propagated. All four season win-adoption gates still fail, experimental ranking only. DREB-recipient change itself does not alter team wins.',roleAudit:x.roleAudit,hashes};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex'),pf=root+'/protocol.json',cf=root+'/checkpoint.json';
if(fs.existsSync(pf)){if(JSON.stringify(read(pf))!==JSON.stringify({...protocol,fingerprint}))throw Error('Full OVR protocol drift');}else fs.writeFileSync(pf,JSON.stringify({...protocol,fingerprint},null,2));
let state={fingerprint,rows:[]};if(fs.existsSync(cf)){state=read(cf);if(state.fingerprint!==fingerprint)throw Error('Full OVR checkpoint drift');}
const all=[...x.players.map(p=>({id:p.playerId,key:String(p.playerId),kind:'player'})),...[0,1,2,3,4].map(slot=>({slot,key:'base-'+slot,kind:'baseline'}))].map(j=>({...j,season,samples,seed,version}));
const jobs=all.filter(j=>!state.rows.some(r=>r.job.key===j.key));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./season-ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(cf,JSON.stringify(state));done++;if(done%10===0||done===jobs.length)console.log(JSON.stringify({done,total:jobs.length,completedRows:state.rows.length,totalRows:all.length}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
if(state.rows.length!==all.length)throw Error('Incomplete full OVR result');
fs.writeFileSync(root+'/manifest.json',JSON.stringify({rows:state.rows.length,players:protocol.players,baselines:protocol.baselines,fingerprint,checkpointSHA256:hash(cf)},null,2));

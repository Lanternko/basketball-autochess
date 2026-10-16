import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {representativeIds} from '../ovr-2025-26-positional/protocol.mjs';
const season=process.argv[2]??'2024-25',version=process.argv[3]??'centered-space';const root=`reports/player-impact-v12/ovr-${season}-${version}`,samples=40,seed=20261015;fs.mkdirSync(root,{recursive:true});
const protocol={version:'source-context-centered-natural-role-ovr-12',samples,seed,ids:representativeIds,season,variants:[version],
 design:'Equal 14.4-minute exposure, no fatigue/substitutions, one supported natural position, four distinct mean70 positional teammates, 30 opponents, both seating orders. Same role and auxiliary profile policy as prior positional test. Measured role priors added by minute-weighted position pools; no name-specific adjustments.',
 scope:'20-player mechanism screen, cannot establish all-player Top50 or completion of goal.'};
const files=['reports/player-impact-v12/engine.mjs','reports/player-impact-v12/model.mjs','reports/player-impact-v12/input.mjs',`reports/player-impact-v12/${season}-contexts.json`,'reports/player-impact-validation/positional-input.mjs','reports/player-impact-validation/season-ovr-worker.mjs'];const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)+files.map(f=>fs.readFileSync(f)).join('')).digest('hex');
const file=root+'/ovr-checkpoint.json';let state={fingerprint,rows:[]};if(fs.existsSync(file)){state=JSON.parse(fs.readFileSync(file));if(state.fingerprint!==fingerprint)throw Error('OVR checkpoint drift');}
fs.writeFileSync(root+'/ovr-protocol.json',JSON.stringify({...protocol,fingerprint},null,2));
let jobs=protocol.variants.flatMap(version=>[...representativeIds.map(id=>({key:version+'-'+id,version,id,kind:'player'})),...[0,1,2,3,4].map(slot=>({key:version+'-base-'+slot,version,kind:'baseline',slot}))]).filter(j=>!state.rows.some(r=>r.job.key===j.key)).map(j=>({...j,season,samples,seed}));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<4;i++){
 const w=new Worker(new URL('./season-ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(file,JSON.stringify(state));console.log(JSON.stringify({done:++done,total:jobs.length,name:m.result.name,version:m.job.version,winRate:m.result.winRate}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}

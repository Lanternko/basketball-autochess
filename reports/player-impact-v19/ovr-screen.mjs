import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {representativeIds} from '../ovr-2025-26-positional/protocol.mjs';
const root='reports/player-impact-v19',season='2025-26',samples=40,seed=20261015,version='rotation-space';
const low=JSON.parse(fs.readFileSync('reports/player-impact-v14/low-minute-top50-audit.json')).players.map(p=>p.playerId),ids=[...new Set([...representativeIds,...low])];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const hashes={...JSON.parse(fs.readFileSync(root+'/validation-protocol.json')).hashes,...Object.fromEntries([root+'/season-ovr-worker.mjs',root+'/ovr-input.mjs',root+'/synthetic-center.mjs',root+'/2025-26-synthetic-center.json','reports/player-impact-validation/positional-input.mjs'].map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('OVR source drift: '+f);};verify();
const protocol={version:'source-ft-categories-ovr-screen-19',season,samples,seed,ids,versionEngine:version,scope:'Exploratory mechanism sample: original20 representatives plus11 low-minute v14Top50 players. Not an all-player ranking or a final Top50. Equal natural-position exposure and same four mean70 positional teammates; no name-specific parameter. Strict shooting-only FT prior and measured defensive-personal-contact rate for all sides; positional synthetic pools use pooled shooting-only counts and corrected creator supply. Attributes still arithmetic mean70; all four unknowns unchanged.',hashes};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex'),file=root+'/ovr-checkpoint.json';let state={fingerprint,rows:[]};
if(fs.existsSync(file)){state=JSON.parse(fs.readFileSync(file));if(state.fingerprint!==fingerprint)throw Error('OVR fingerprint drift');}
fs.writeFileSync(root+'/ovr-protocol.json',JSON.stringify({...protocol,fingerprint},null,2));
const jobs=[...ids.map(id=>({id,key:String(id),kind:'player'})),...[0,1,2,3,4].map(slot=>({slot,key:'base-'+slot,kind:'baseline'}))].filter(j=>!state.rows.some(r=>r.job.key===j.key)).map(j=>({...j,season,samples,seed,version}));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./season-ovr-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);fs.writeFileSync(file,JSON.stringify(state));console.log(JSON.stringify({done:++done,total:jobs.length,name:m.result.name,winRate:m.result.winRate}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();

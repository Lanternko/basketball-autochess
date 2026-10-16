import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v20',old=JSON.parse(fs.readFileSync('reports/player-impact-v19/validation-protocol.json'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=old.seasons;
const files=['model.mjs','engine.mjs','input.mjs','worker.mjs','prepare.mjs','role-input.mjs','build-defense-exposure.mjs'].map(f=>root+'/'+f).concat(seasons.flatMap(s=>[root+'/'+s+'-contexts.json',root+'/'+s+'-defense-exposure.json']));
const hashes={...old.hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('FTR prior source drift: '+f);};verify();
const protocol={version:'measured-contest-exposure-pilot-20',seasons,seeds:[20261012,20261013,20261014],variants:['rotation-space'],design:'Closest-defender conditional FG differences weighted by tracked defended FGA per player-minute, divided by measured team-zone FGA per team-minute. Rim tracking is six-foot scope, full short denominator includes other paint shots. Retains source defensive attribute curves and shrinkage, explicit midpoint proxy and separate physique prior. Source FGA-weighted centers recomputed. No player names, rankings, simulation residuals or on/off targets fit. Descriptive tracking association, not causal identification.',hashes};
const pf=root+'/validation-protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Pilot protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=protocol.seasons.flatMap(season=>protocol.seeds.flatMap(seed=>[false,true].map(strict=>({season,seed,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-${seed}.json`}))));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,strict:m.job.strict}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/validation-manifest.json',JSON.stringify({jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

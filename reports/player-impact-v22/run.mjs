import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v22',pilot=process.argv.includes('--pilot'),seasons=process.argv.filter(a=>/^202\d-\d\d$/.test(a));
if(!seasons.length)seasons.push(...(pilot?['2025-26']:['2022-23','2023-24','2024-25','2025-26']));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const inherited=JSON.parse(fs.readFileSync('reports/player-impact-v21/validation-protocol.json')).hashes;
const files=['model.mjs','input.mjs','engine.mjs','worker.mjs','build-putback-source.py','fit-putback-prior.py','prepare-putback-context.mjs','putback-prior.json'].map(f=>root+'/'+f).concat(seasons.flatMap(s=>[root+'/'+s+'-putback-events.json',root+'/'+s+'-putback-rates.json',root+'/'+s+'-putback-contexts.json']));
const hashes={...inherited,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
for(const s of seasons){Object.assign(hashes,JSON.parse(fs.readFileSync(root+'/'+s+'-putback-events.json')).hashes);Object.assign(hashes,JSON.parse(fs.readFileSync(root+'/'+s+'-putback-contexts.json')).hashes);}
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Frozen source drift: '+f);};verify();
const protocol={version:'measured-putback-success-22',seasons,seeds:pilot?[20261012]:[20261012,20261013,20261014],variants:['rotation-space'],design:'Recorded putback FG estimated separately from fresh FG: same-player short FGA within 0-3 seconds after a missed-FG offensive rebound. Beta count prior fitted on 2022-25 whole-game folds. PB-only source context removes retained generic physique/context boost; counterfactual changes remain. OREB opportunity/recipient, putback selection, all fresh shots, FT and turnover branches unchanged. Legacy fresh partition includes 69-135 FT-rebound proxy FGAs excluded from this PB target; retained as known minor scope mismatch. No player-name, rank, on/off or win residual fit. Experimental, not adopted.',hashes};
const pf=root+(pilot?'/pilot-protocol-'+seasons.join('_')+'.json':'/validation-protocol.json');
if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=seasons.flatMap(season=>protocol.seeds.flatMap(seed=>[false,true].map(strict=>({season,seed,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-${seed}.json`}))));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(pilot?2:4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,strict:m.job.strict,seed:m.job.seed}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+(pilot?'/pilot-manifest-'+seasons.join('_')+'.json':'/validation-manifest.json'),JSON.stringify({jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

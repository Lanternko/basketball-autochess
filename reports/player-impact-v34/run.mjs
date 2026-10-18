import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v34',read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const seasons=['2022-23','2023-24','2024-25','2025-26'],seeds=[20261012,20261013,20261014];
const files=['model.mjs','probability.mjs','input.mjs','engine.mjs','worker.mjs','run.mjs','prepare-contexts.mjs'].map(f=>root+'/'+f)
 .concat(seasons.map(s=>root+'/'+s+'-contexts.json'),['test/joint_source_opportunities.js']);
const hashes={...read('reports/player-impact-v30/validation-protocol.json').hashes,...Object.fromEntries(files.map(p=>[p,hash(p)]))};
const verify=()=>{for(const[p,h]of Object.entries(hashes))if(hash(p)!==h)throw Error('Frozen source drift: '+p);};verify();
const protocol={version:'joint-source-self-floor-34',seasons,seeds,variants:['rotation-space'],
 design:'Predeclared fixed source-self-floor experiment, reserve=1; no fit or rank-based coefficient. Receive capacities leave each actor at least its descriptive elastic source-self rate; pass supply reduced only to make capacities feasible, all terminal demand remains conserved. No source attributes/roles or probabilities changed, contexts recomputed on identical FGA/stamina exposure. Compare archived official control and v30, full and strict four seasons, three seeds each. Every season must retain official winsMAE+0.5 adoption gate; report all individual, role-group and on-court errors, not just favorable outcomes. No adoption based only on source allocation score or named-player ranks. Same-season reconstruction, not blind/causal.',hashes};
const pf=root+'/validation-protocol.json';
if(fs.existsSync(pf)){if(JSON.stringify(read(pf))!==JSON.stringify(protocol))throw Error('Protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=seasons.flatMap(season=>seeds.flatMap(seed=>[false,true].map(strict=>({season,seed,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-${seed}.json`}))));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);
  w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,seed:m.job.seed,strict:m.job.strict}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
 }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/validation-manifest.json',JSON.stringify({jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

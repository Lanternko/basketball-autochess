import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v16',old=JSON.parse(fs.readFileSync('reports/player-impact-v14/validation-protocol.json'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const files=['src/free_throw_profile_prior.js',root+'/input.mjs',root+'/worker.mjs',root+'/ftr-prior.json',root+'/fit-ftr.py'];
const hashes={...old.hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('FTR prior source drift: '+f);};verify();
const protocol={version:'source-ftr-prior-pilot-16',seasons:old.seasons,seeds:[20261012],variants:['rotation-space'],design:'Only source FT/FGA is sample-size corrected with one prior estimated from five game folds in2022-25. Already-seen2025-26 check improves. v14 engine, frozen make/rotation centers and roles unchanged; drive attribute unchanged. Synthetic mean70 profiles retain their positional pool policy. Four full seasons plus latest-season strict on-court pilot. No names or ranking target used to fit.',hashes};
const pf=root+'/protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Pilot protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=protocol.seasons.flatMap(season=>(season==='2025-26'?[false,true]:[false]).map(strict=>({season,seed:20261012,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-20261012.json`})));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,strict:m.job.strict}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/pilot-manifest.json',JSON.stringify({jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

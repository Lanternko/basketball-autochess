import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v19',old=JSON.parse(fs.readFileSync('reports/player-impact-v14/validation-protocol.json'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=process.argv.slice(2).length?process.argv.slice(2):['2025-26'];
const files=[root+'/input.mjs',root+'/worker.mjs',root+'/prepare.mjs',root+'/role-input.mjs','src/free_throw_profile_prior.js',root+'/ftr-prior.json',root+'/fit-ftr.py',root+'/ft-kinds.py',root+'/foul-contact-audit.py','reports/player-impact-v18/role-input.mjs','reports/player-impact-v18/creation-reference.mjs','reports/player-impact-v17/source-creation-audit.mjs',...seasons.flatMap(s=>[root+'/'+s+'-contexts.json',root+'/'+s+'-ft-kinds.json',root+'/'+s+'-foul-contact-audit.json','reports/player-impact-v17/'+s+'-shot-exposures.json','reports/player-impact-v17/'+s+'-creation-audit.json'])];
const hashes={...old.hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('FTR prior source drift: '+f);};verify();
const protocol={version:'source-ft-categories-pilot-19',seasons,seeds:[20261012],variants:['rotation-space'],design:'Isolate source FT category correction over v18: shooting-only FTA/FGA with33.0602-FGA prior estimated by source game folds; nonshooting defensive-personal-contact probability from source event counts with and-one overlap removed and conservative multi-FGA linkage bound. Technical/unresolved FT excluded from shooting profile, technical process not yet separately rebuilt. Recompute source centers. No simulation residuals, names, ranks or on/off targets fit. v18 creator reference retained as an approximation pending new survival audit.',hashes};
const pf=root+'/protocol-'+seasons.join('_')+'.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Pilot protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=protocol.seasons.flatMap(season=>(season==='2025-26'?[false,true]:[false]).map(strict=>({season,seed:20261012,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-20261012.json`})));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,strict:m.job.strict}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/pilot-manifest-'+seasons.join('_')+'.json',JSON.stringify({jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

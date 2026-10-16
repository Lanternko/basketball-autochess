import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v18',old=JSON.parse(fs.readFileSync('reports/player-impact-v14/validation-protocol.json'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=process.argv.slice(2).length?process.argv.slice(2):['2025-26'];
const files=[root+'/input.mjs',root+'/worker.mjs',root+'/prepare.mjs',root+'/role-input.mjs',root+'/creation-reference.mjs','reports/player-impact-v17/source-creation-audit.mjs',...seasons.flatMap(s=>[root+'/'+s+'-contexts.json','reports/player-impact-v17/'+s+'-shot-exposures.json','reports/player-impact-v17/'+s+'-creation-audit.json'])];
const hashes={...old.hashes,...Object.fromEntries(files.map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('FTR prior source drift: '+f);};verify();
const protocol={version:'source-creation-reference-pilot-18',seasons,seeds:[20261012],variants:['rotation-space'],design:'Replace obsolete global creator success denominator with source-lineup conditional receiver success, with60-minute league-success prior; recompute FGA-weighted shooting centers and production-context reference after role change. Same v14 engine, attributes and FTR. No on/off, simulation residuals, names or rank targets used. Source audit assumes approximate terminal per-minute clock. Single-pass reference update, historically seen reconstruction.',hashes};
const pf=root+'/protocol-'+seasons.join('_')+'.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Pilot protocol drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=protocol.seasons.flatMap(season=>(season==='2025-26'?[false,true]:[false]).map(strict=>({season,seed:20261012,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-20261012.json`})));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,strict:m.job.strict}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}verify();
fs.writeFileSync(root+'/pilot-manifest-'+seasons.join('_')+'.json',JSON.stringify({jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

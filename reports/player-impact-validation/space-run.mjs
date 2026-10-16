import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-validation',variants=['space-control','space-half','space-full'];
const files=['reports/player-impact-v7/engine.mjs','reports/player-impact-v7/model.mjs','reports/player-impact-v7/worker.mjs','reports/player-impact-v7/2025-26-center.json'];
const protocol={version:'centered-spacing-2025-diagnostic-7',season:'2025-26',seed:20261012,variants,
 design:'Enable half/full existing long context term, centered against source-lineup predicted context. Frozen terminal-flow inputs. Compare each with exact same implementation at context=0. No name/ranking adjustment. Single-seed mechanism check, not adoption.',
 hashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')]))};
const pf=root+'/space-protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Space source drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/space',{recursive:true});
const jobs=variants.flatMap(version=>[false,true].map(strict=>({season:'2025-26',seed:20261012,version,strict,onCourt:strict,file:`${root}/space/${version}-${strict?'strict':'full'}.json`}))).filter(j=>!fs.existsSync(j.file));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('../player-impact-v7/worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,...m.job}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}

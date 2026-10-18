import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v12',files=['engine.mjs','model.mjs','input.mjs','ovr-input.mjs','2025-26-contexts.json','../../src/opportunity_transport.js','worker.mjs','../player-impact-v8/usage-fit.json','../player-impact-v8/assist-fit.json'];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const protocol={version:'source-context-centered-12',season:'2025-26',seed:20261012,variants:['centered-flow','centered-creation','centered-space'],
 design:'Observed zone FG is source-context centered before reapplying new context; source contexts come from actual lineup exposures and frozen model predictions, not fitted individual residuals. Successful creation supply is conserved subject to terminal capacity and zero self-assist. Receiving propensity is a soft allocation prior rather than a cap on team creation. Global alpha from 2022-25 fresh-FGA actor choices; global beta from assisted-make passer choices conditional on receiver. Source lineup total demand conserved. No target player names, OVR/on-off ranking fit or positional bonus. Third variant enables source-centered long context. Diagnostic single seed, not adoption.',
 hashes:Object.fromEntries(files.map(f=>[root+'/'+f,hash(root+'/'+f)]))};
const pf=root+'/protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Elastic model source drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const jobs=protocol.variants.flatMap(version=>[false,true].map(strict=>({season:'2025-26',seed:20261012,version,strict,onCourt:strict,file:`${root}/runs/2025-26-${version}-${strict?'strict':'full'}-20261012.json`}))).filter(j=>!fs.existsSync(j.file));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,...m.job}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const[f,h]of Object.entries(protocol.hashes))if(hash(f)!==h)throw Error('Elastic source drift');

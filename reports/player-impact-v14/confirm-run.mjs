import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v14',base=JSON.parse(fs.readFileSync('reports/player-impact-v14/validation-protocol.json'));
for(const [f,h]of Object.entries(base.hashes))if(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')!==h)throw Error('Frozen candidate source drift: '+f);
const protocol={version:'rotation-space-confirmation-20',seasons:base.seasons,seeds:Array.from({length:20},(_,i)=>20261012+i),engine:'rotation-space',
 reason:'Four-season three-seed individual and on-court FG improved, but 2022-23 and 2023-24 wins MAE rose beyond0.5. Confirm all four seasons against the fixed20 archived seeds; do not hide season failures in the aggregate. On-court remains three seeds.',
 sourceValidationSHA:crypto.createHash('sha256').update(fs.readFileSync('reports/player-impact-v14/validation-protocol.json')).digest('hex')};
const pf=root+'/confirmation-protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Confirmation drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
const jobs=protocol.seasons.flatMap(season=>protocol.seeds.map(seed=>({season,seed,version:'rotation-space',strict:false,onCourt:false,file:`reports/player-impact-v14/runs/${season}-rotation-space-full-${seed}.json`}))).filter(j=>!fs.existsSync(j.file));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,seed:m.job.seed}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
fs.writeFileSync(root+'/confirmation-manifest.json',JSON.stringify({newGames:jobs.length*1230,totalGames:80*1230,jobs:protocol.seasons.flatMap(season=>protocol.seeds.map(seed=>{const file=`reports/player-impact-v14/runs/${season}-rotation-space-full-${seed}.json`;return {season,seed,file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')};}))},null,2));

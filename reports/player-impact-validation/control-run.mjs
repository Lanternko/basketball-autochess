import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-validation';fs.mkdirSync(root+'/control',{recursive:true});
const jobs=['2022-23','2023-24','2024-25','2025-26'].flatMap(season=>[20261012,20261013,20261014].map(seed=>({season,seed,version:'control',strict:true,onCourt:true,file:`${root}/control/${season}-${seed}.json`}))).filter(j=>!fs.existsSync(j.file));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(2,jobs.length);i++){
 const w=new Worker(new URL('../player-impact-v1/worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,seed:m.job.seed}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}

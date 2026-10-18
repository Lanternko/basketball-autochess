import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from './defense_io.js';
const label=process.argv[2]??'combined',options=label==='combined-grid'?read('reports/defense-third/calibration-grid.json').selected:{};
const jobs=Array.from({length:20},(_,i)=>({preset:'combined',seed:20261012+i,options})),results=[],pool=[];let next=0,done=0;
try{await new Promise((resolve,reject)=>{
  const dispatch=w=>{if(next<jobs.length){const index=next++;w.postMessage({index,job:jobs[index]});}};
  for(let i=0;i<4;i++){const w=new Worker(new URL('./defense_third_audit_worker.js',import.meta.url));pool.push(w);w.on('error',reject);w.on('message',m=>{if(m.error){reject(Error(m.error));return;}results[m.index]=m.result;done++;if(done%4===0)console.log('possession audits',done+'/20');if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);}
});}finally{await Promise.all(pool.map(w=>w.terminate()));}
fs.writeFileSync('reports/defense-third/'+label+'-possession-audits-20.json',JSON.stringify({seeds:jobs.map(j=>j.seed),optionsOverride:options,results,provenance:Object.fromEntries(['src/defense_third_game.js','src/defense_third_jobs.js','reports/defense-third/calibration.json','scripts/defense_third_audit_worker.js',...(label==='combined-grid'?['reports/defense-third/calibration-grid.json']:[])].map(f=>[f,hash(f)]))},null,2)+'\n');

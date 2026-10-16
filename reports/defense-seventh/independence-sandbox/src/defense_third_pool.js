import {Worker} from 'node:worker_threads';
import {availableParallelism} from 'node:os';
export async function runThirdJobs(jobs,{workers=Math.min(4,availableParallelism()),onProgress=()=>{}}={}){
  if(!Number.isInteger(workers)||workers<1||workers>32)throw Error('Invalid workers');
  if(!jobs.length)return [];const results=new Array(jobs.length),pool=[];let next=0,completed=0;
  try{await new Promise((resolve,reject)=>{
    const dispatch=w=>{if(next<jobs.length){const index=next++;w.postMessage({index,job:jobs[index]});}};
    for(let i=0;i<Math.min(workers,jobs.length);i++){const w=new Worker(new URL('../scripts/defense_third_worker.js',import.meta.url));pool.push(w);w.on('error',reject);w.on('exit',code=>{if(code&&completed<jobs.length)reject(Error('Worker exit '+code));});w.on('message',m=>{if(m.error){reject(Error(m.error));return;}results[m.index]=m.result;completed++;onProgress(completed,jobs.length);if(completed===jobs.length)resolve();else dispatch(w);});dispatch(w);}
  });}finally{await Promise.all(pool.map(w=>w.terminate()));}return results;
}

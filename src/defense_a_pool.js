import {Worker} from 'node:worker_threads';
import {availableParallelism} from 'node:os';
export const DEFAULT_WORKERS=Math.min(4,availableParallelism());
export async function runJobs(jobs,{workers=DEFAULT_WORKERS,onProgress=()=>{}}={}){
  if(!Number.isInteger(workers)||workers<1||workers>32)throw new Error('Invalid worker count');
  if(!jobs.length)return [];
  const results=new Array(jobs.length);let next=0,completed=0;
  const pool=[];
  try{
    await new Promise((resolve,reject)=>{
      const dispatch=w=>{if(next<jobs.length){const index=next++;w.postMessage({index,job:jobs[index]});}};
      for(let i=0;i<Math.min(workers,jobs.length);i++){
        const w=new Worker(new URL('../scripts/defense_a_worker.js',import.meta.url));pool.push(w);
        w.on('error',reject);w.on('exit',code=>{if(code&&completed<jobs.length)reject(new Error('Worker exited '+code));});
        w.on('message',message=>{
          if(message.error){reject(new Error(message.error));return;}
          results[message.index]=message.result;completed++;onProgress(completed,jobs.length);
          if(completed===jobs.length)resolve();else dispatch(w);
        });dispatch(w);
      }
    });
  }finally{await Promise.all(pool.map(w=>w.terminate()));}
  return results;
}

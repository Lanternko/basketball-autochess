import {parentPort} from 'node:worker_threads';
import {executeJob} from '../src/defense_a_jobs.js';
parentPort.on('message',({index,job})=>{
  try{parentPort.postMessage({index,result:executeJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}
});

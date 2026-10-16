import {parentPort} from 'node:worker_threads';
import {executeSeventhJob} from '../src/defense_seventh_jobs.js';
parentPort.on('message',({index,job})=>{try{parentPort.postMessage({index,result:executeSeventhJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}});

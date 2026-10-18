import {parentPort} from 'node:worker_threads';
import {executeThirdJob} from '../src/defense_third_jobs.js';
parentPort.on('message',({index,job})=>{try{parentPort.postMessage({index,result:executeThirdJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}});

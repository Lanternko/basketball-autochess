import {parentPort} from 'node:worker_threads';
import {executeFifthJob} from '../src/defense_fifth_jobs.js';
parentPort.on('message',({index,job})=>{try{parentPort.postMessage({index,result:executeFifthJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}});

import {parentPort} from 'node:worker_threads';
import {executeClockJob} from '../src/defense_clock_jobs.js';
parentPort.on('message',({index,job})=>{try{parentPort.postMessage({index,result:executeClockJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}});

import {parentPort} from 'node:worker_threads';
import {executeFourthJob} from '../src/defense_fourth_jobs.js';
parentPort.on('message',({index,job})=>{try{parentPort.postMessage({index,result:executeFourthJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}});

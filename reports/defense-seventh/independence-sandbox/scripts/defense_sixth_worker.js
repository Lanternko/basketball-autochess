import {parentPort} from 'node:worker_threads';
import {executeSixthJob} from '../src/defense_sixth_jobs.js';
parentPort.on('message',({index,job})=>{try{parentPort.postMessage({index,result:executeSixthJob(job)});}catch(e){parentPort.postMessage({index,error:e.stack});}});

import {parentPort,workerData} from 'node:worker_threads';
import {executeNormalizationJob} from '../src/defense_fourth_normalization.js';
try{parentPort.postMessage({result:executeNormalizationJob(workerData)});}catch(e){parentPort.postMessage({error:e.stack});}

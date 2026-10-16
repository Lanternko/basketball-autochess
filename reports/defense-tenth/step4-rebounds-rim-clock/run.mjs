import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from '../../../scripts/defense_io.js';
import {job} from '../step4-rebounds-turnover-time/run.mjs';
const root='reports/defense-tenth/step4-rebounds-rim-clock',p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').trim())throw Error('Protocol changed');
fs.mkdirSync(root+'/runs',{recursive:true});
const jobs=['2022-23','2023-24','2024-25','2025-26'].flatMap(season=>['baseline','off','allRim','noRim'].map(mode=>({...job(season,'split',20261012,read(`reports/defense-tenth/step4-rebounds-oreb/${season}/calibration-oreb.json`).selected),clockCalibration:read(`reports/defense-tenth/step4-rebounds-turnover-time/${season}/calibration.json`).selected,indices:Array.from({length:12},(_,i)=>i),baseline:mode==='baseline',rimMode:mode,file:`${root}/runs/${season}-${mode}.json`}))).filter(j=>!fs.existsSync(j.file));
const ws=[];let next=0,done=0;
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();for(let i=0;i<Math.min(4,jobs.length);i++){const w=new Worker(new URL('./worker.mjs',import.meta.url));ws.push(w);const dispatch=()=>{if(next<jobs.length)w.postMessage(jobs[next++]);};w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(++done+'/'+jobs.length,m.job.season,m.job.rimMode);if(done===jobs.length)resolve();else dispatch();});dispatch();}});}finally{await Promise.all(ws.map(w=>w.terminate()));}

import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from '../../../scripts/defense_io.js';
import {job} from '../step4-rebounds-turnover-time/run.mjs';
const root='reports/defense-tenth/step4-rebounds-clock-competing',p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').trim())throw Error('Protocol changed');
const pilot=process.argv.includes('--pilot'),full=process.argv.includes('--full');
const c=pilot?{}:read(root+'/calibration.json');
const modes=['baseline','combined'];
fs.mkdirSync(root+'/timing',{recursive:true});
const jobs=p.seasons.flatMap(season=>modes.flatMap(mode=>(full?p.fullSeeds:p.diagnosticSeeds).map(seed=>{
 const n=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`).league.schedule.length;
 const indices=true?Array.from({length:256},(_,i)=>Math.floor((i+.5)*n/256)):null;
 return {...job(season,'split',seed,read(`reports/defense-tenth/step4-rebounds-oreb/${season}/calibration-oreb.json`).selected),clockCalibration:read(`reports/defense-tenth/step4-rebounds-turnover-time/${season}/calibration.json`).selected,pEffective:p.pEffective,mode,indices,...c,file:`${root}/timing/${season}-${mode}-${seed}.json`};
}))).filter(j=>!fs.existsSync(j.file));
const ws=[];let next=0,done=0,start=Date.now();
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();for(let i=0;i<Math.min(6,jobs.length);i++){
 const w=new Worker(new URL('./timing-worker.mjs',import.meta.url));ws.push(w);const dispatch=()=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(++done+'/'+jobs.length,m.job.season,m.job.mode,Math.round((Date.now()-start)/1000)+'s');if(done===jobs.length)resolve();else dispatch();});dispatch();
}});}finally{await Promise.all(ws.map(w=>w.terminate()));}

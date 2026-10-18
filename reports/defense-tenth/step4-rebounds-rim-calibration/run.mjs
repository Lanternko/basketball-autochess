import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from '../../../scripts/defense_io.js';
import {job} from '../step4-rebounds-turnover-time/run.mjs';
const root='reports/defense-tenth/step4-rebounds-rim-calibration',p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').trim())throw Error('Protocol changed');
const selected=process.argv.includes('--selected');
const probs=selected?[read(root+'/selection.json').pEffective]:p.grid;
fs.mkdirSync(root+'/runs',{recursive:true});
const jobs=p.seasons.flatMap(season=>probs.flatMap(prob=>p.seeds.map(seed=>{
 const n=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`).league.schedule.length;
 const indices=selected?null:Array.from({length:p.gridGamesPerSeason},(_,i)=>Math.floor((i+.5)*n/p.gridGamesPerSeason));
 return {...job(season,'split',seed,read(`reports/defense-tenth/step4-rebounds-oreb/${season}/calibration-oreb.json`).selected),clockCalibration:read(`reports/defense-tenth/step4-rebounds-turnover-time/${season}/calibration.json`).selected,pEffective:prob,indices,file:`${root}/runs/${season}-${selected?'selected':prob}-${seed}.json`};
}))).filter(j=>!fs.existsSync(j.file));
const ws=[];let next=0,done=0;const start=Date.now();
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();for(let i=0;i<Math.min(6,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));ws.push(w);
 const dispatch=()=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(++done+'/'+jobs.length,m.job.season,m.job.pEffective,Math.round((Date.now()-start)/1000)+'s');if(done===jobs.length)resolve();else dispatch();});dispatch();
}});}finally{await Promise.all(ws.map(w=>w.terminate()));}

import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from '../../../scripts/defense_io.js';
export const root='reports/defense-tenth/step4-rebounds-turnover-time';
export function verify(){if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').trim().split(' ')[0])throw Error('Protocol changed');}
export function job(season,version,seed,calibration=null){return{season,version,seed,bundle:`reports/defense-tenth/step4-t0/${season}/bundle.json`,baseCalibration:season==='2025-26'?null:read(`reports/defense-tenth/step4-t0/${season}/calibration-v3.json`).selected,calibration};}
export async function pool(jobs,{workers=8,quiet=false}={}){
 const ws=[],results=[],start=Date.now();let next=0,done=0;
 try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(workers,jobs.length);i++){const w=new Worker(new URL('./worker.mjs',import.meta.url));ws.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));results.push(m);done++;if(!quiet)console.log('RUN',done+'/'+jobs.length,m.job.season,m.job.version,m.job.seed,Math.round((Date.now()-start)/1000)+'s');if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);}});}finally{await Promise.all(ws.map(w=>w.terminate()));}return results;
}
if(process.argv[1]?.replaceAll('\\','/').endsWith('/step4-rebounds-turnover-time/run.mjs')){
 verify();const p=read(root+'/protocol.json');fs.mkdirSync(root+'/runs',{recursive:true});
 const jobs=p.seasons.flatMap(s=>['split'].flatMap(v=>p.seeds.map(seed=>({...job(s,v,seed,read(`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`).selected),clockCalibration:read(`${root}/${s}/calibration.json`).selected,diagnostic:p.diagnosticSeeds.includes(seed),file:`${root}/runs/${s}-${v}-${seed}.json`}))));
 await pool(jobs.filter(j=>!fs.existsSync(j.file)));
 fs.writeFileSync(root+'/run-manifest.json',JSON.stringify({finishedAt:new Date().toISOString(),files:jobs.map(j=>({...j,sha256:hash(j.file)}))},null,2)+'\n');
}

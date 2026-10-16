import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from '../../../scripts/defense_io.js';
const d='reports/defense-tenth/step4-t0';
export async function pool(jobs,{workers=6,quiet=false}={}){
 const ws=[],results=[],start=Date.now();let next=0,done=0;
 try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(workers,jobs.length);i++){const w=new Worker(new URL('./worker.mjs',import.meta.url));ws.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));results.push(m);if(m.job.file)fs.writeFileSync(m.job.file,JSON.stringify(m.result)+'\n');done++;if(!quiet)console.log('RUN',done+'/'+jobs.length,m.job.season,m.job.version,m.job.seed,Math.round((Date.now()-start)/1000)+'s');if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);}});}finally{await Promise.all(ws.map(w=>w.terminate()));}return results;
}
if(process.argv[1]?.replaceAll('\\','/').endsWith('/step4-t0/run.mjs')){
 const p=read(d+'/protocol.json');if(hash(d+'/protocol.json')!==fs.readFileSync(d+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol changed');
 const original=read('reports/defense-fourth/final-normalized-seeds.json');
 const parity=(await pool([{season:'2025-26',version:'v3',seed:p.seeds[0],bundle:d+'/2025-26/bundle.json'}],{workers:1}))[0].result,old=read(original.files[0].file);
 const mismatches=parity.matches.filter((g,i)=>['id','homeId','awayId','scoreA','scoreB','overtimes'].some(k=>g[k]!==old.matches[i][k]));
 fs.writeFileSync(d+'/parity.json',JSON.stringify({seed:p.seeds[0],source:original.files[0],games:parity.matches.length,mismatches},null,2)+'\n');if(mismatches.length)throw Error('Frozen v3 parity failed: '+mismatches.length);
 const jobs=p.seasons.flatMap(season=>['pure','v3'].flatMap(version=>p.seeds.map(seed=>({season,version,seed,bundle:d+'/'+season+'/bundle.json',calibration:season==='2025-26'?null:read(d+'/'+season+'/calibration-v3.json').selected,file:`${d}/runs/${season}-${version}-${seed}.json`}))));fs.mkdirSync(d+'/runs',{recursive:true});
 for(const j of jobs.filter(j=>j.season==='2025-26'&&j.version==='v3')){const src=original.files.find(f=>f.seed===j.seed);fs.copyFileSync(src.file,j.file);j.reusedFrom=src.file;}
 await pool(jobs.filter(j=>!fs.existsSync(j.file)),{workers:8});
 fs.writeFileSync(d+'/run-manifest.json',JSON.stringify({finishedAt:new Date().toISOString(),protocolSHA:hash(d+'/protocol.json'),files:jobs.map(j=>({...j,calibration:undefined,sha256:hash(j.file)}))},null,2)+'\n');
}

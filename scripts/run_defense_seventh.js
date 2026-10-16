import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from './defense_io.js';
const root='reports/defense-seventh';
export const loadSeventh=label=>read(root+'/'+label+'-seeds.json').files.map(f=>read(f.file));
export async function runSeventh(label,extra={},seeds=Array.from({length:20},(_,i)=>20261012+i)){
 const jobs=seeds.map(seed=>({label,seed,...extra})),results=new Array(jobs.length),pool=[];let next=0,completed=0;const start=Date.now();console.log('START',label);
 try{await new Promise((resolve,reject)=>{const dispatch=w=>{if(next<jobs.length){const index=next++;w.postMessage({index,job:jobs[index]});}};for(let i=0;i<Math.min(6,jobs.length);i++){const w=new Worker(new URL('./defense_seventh_worker.js',import.meta.url));pool.push(w);w.on('error',reject);w.on('exit',code=>{if(code&&completed<jobs.length)reject(Error('Worker exit '+code));});w.on('message',m=>{if(m.error)return reject(Error(m.error));results[m.index]=m.result;completed++;if(completed%5===0)console.log(label,completed+'/'+jobs.length);if(completed===jobs.length)resolve();else dispatch(w);});dispatch(w);}});}finally{await Promise.all(pool.map(w=>w.terminate()));}
 const files=results.map(r=>{const file=`${root}/runs/${label}-seed${r.seed}.json`;fs.writeFileSync(file,JSON.stringify(r)+'\n');return {seed:r.seed,file,sha256:hash(file)};});
 fs.writeFileSync(root+'/'+label+'-seeds.json',JSON.stringify({label,extra,files,seconds:(Date.now()-start)/1000,sources:Object.fromEntries(['src/defense_fifth_game.js','src/defense_sixth_season.js','src/defense_seventh_jobs.js','scripts/run_defense_seventh.js',...(extra.cardFile?[extra.cardFile]:[])].map(f=>[f,hash(f)]))},null,2)+'\n');console.log('DONE',label);return results;
}
if(process.argv[1]?.endsWith('run_defense_seventh.js'))await runSeventh(process.argv[2],JSON.parse(process.argv[3]??'{}'));

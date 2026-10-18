import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {runFifthJobs} from '../src/defense_fifth_pool.js';
const root='reports/defense-fifth';
export function loadFifth(label){const m=read(root+'/'+label+'-seeds.json');return m.files.map(f=>read(f.file));}
export async function runFifth(label,extra={}){
 const jobs=Array.from({length:20},(_,i)=>({label,seed:20261012+i,...extra}));console.log('START',label);const start=Date.now();
 const runs=await runFifthJobs(jobs,{workers:6,onProgress:(n)=>{if(n%5===0)console.log(label,n+'/20');}});
 const files=runs.map(r=>{const file=root+'/runs/'+label+'-seed'+r.seed+'.json';fs.writeFileSync(file,JSON.stringify(r)+'\n');return {seed:r.seed,file,sha256:hash(file)};});
 fs.writeFileSync(root+'/'+label+'-seeds.json',JSON.stringify({label,extra,files,seconds:(Date.now()-start)/1000,code:Object.fromEntries(['src/defense_fifth_game.js','src/defense_fifth_season.js','src/defense_fifth_jobs.js','src/defense_fifth_presets.js','src/defense_fourth_effects.js'].map(f=>[f,hash(f)]))},null,2)+'\n');
 console.log('DONE',label);return runs;
}
if(process.argv[1]?.endsWith('run_defense_fifth.js'))await runFifth(process.argv[2],{cutoff:Number(process.argv[3]??0),options:JSON.parse(process.argv[4]??'{}')});

import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {runSixthJobs} from '../src/defense_sixth_pool.js';
const root='reports/defense-sixth';
export function loadSixth(label){return read(root+'/'+label+'-seeds.json').files.map(f=>read(f.file));}
export async function runSixth(label,extra={}){
 const jobs=Array.from({length:20},(_,i)=>({label,seed:20261012+i,...extra})),start=Date.now();console.log('START',label);
 const runs=await runSixthJobs(jobs,{workers:6,onProgress:n=>{if(n%5===0)console.log(label,n+'/20');}});
 const files=runs.map(r=>{const file=root+'/runs/'+label+'-seed'+r.seed+'.json';fs.writeFileSync(file,JSON.stringify(r)+'\n');return {seed:r.seed,file,sha256:hash(file)};});
 const sources=['src/defense_fifth_game.js','src/defense_sixth_season.js','src/defense_sixth_jobs.js','src/defense_sixth_pool.js','src/defense_fourth_effects.js'];
 if(extra.cardVersion)sources.push(`${root}/pre${extra.cutoff}-${extra.cardVersion}-league.json`);
 fs.writeFileSync(root+'/'+label+'-seeds.json',JSON.stringify({label,extra,files,seconds:(Date.now()-start)/1000,code:Object.fromEntries(sources.map(f=>[f,hash(f)]))},null,2)+'\n');console.log('DONE',label);
 return runs;
}
if(process.argv[1]?.endsWith('run_defense_sixth.js'))await runSixth(process.argv[2],JSON.parse(process.argv[3]??'{}'));

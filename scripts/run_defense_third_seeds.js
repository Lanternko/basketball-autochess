import fs from 'node:fs';
import {runThirdJobs} from '../src/defense_third_pool.js';
import {hash,read} from './defense_io.js';
const presets=process.argv.slice(2);if(!presets.length)throw Error('Supply presets');
const root='reports/defense-third',dir=root+'/runs';fs.mkdirSync(dir,{recursive:true});
for(const label of presets){
  const preset=label==='season-minutes'?'v1':label==='combined-grid'?'combined':label,options=label==='season-minutes'?{seasonMinuteTargets:true}:label==='combined-grid'?read('reports/defense-third/calibration-grid.json').selected:{};
  const jobs=Array.from({length:20},(_,i)=>({preset,label,seed:20261012+i,options}));
  const start=Date.now(),runs=await runThirdJobs(jobs,{onProgress:(n,total)=>{if(n%4===0)console.log(label,n+'/'+total);}});
  const files=runs.map(r=>{const file=dir+'/'+label+'-seed'+r.seed+'.json';fs.writeFileSync(file,JSON.stringify(r)+'\n');return {seed:r.seed,file,sha256:hash(file)};});
  const code=Object.fromEntries(['src/defense_third_game.js','src/defense_third_season.js','src/defense_third_jobs.js','src/defense_third_minutes.js','reports/defense-third/foul-audit.json','reports/defense-third/calibration.json',...(label==='combined-grid'?['reports/defense-third/calibration-grid.json']:[])].map(f=>[f,hash(f)]));
  fs.writeFileSync(root+'/'+label+'-seeds.json',JSON.stringify({preset:label,seeds:jobs.map(j=>j.seed),files,seconds:(Date.now()-start)/1000,code},null,2)+'\n');
}

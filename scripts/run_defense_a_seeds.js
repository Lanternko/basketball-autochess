import fs from 'node:fs';
import {performance} from 'node:perf_hooks';
import {runJobs,DEFAULT_WORKERS} from '../src/defense_a_pool.js';
import {hash,codeFiles} from './defense_io.js';
const args=process.argv.slice(2),arg=(name,fallback)=>{const i=args.indexOf('--'+name);return i<0?fallback:args[i+1];};
const mode=arg('mode','fast'),preset=arg('preset','v1'),workers=Number(arg('workers',DEFAULT_WORKERS));
const seeds=arg('seeds','')?arg('seeds','').split(',').map(Number):Array.from({length:mode==='full'?20:2},(_,i)=>20261012+i);
if(!['fast','full'].includes(mode)||seeds.some(s=>!Number.isInteger(s)||s<0||s>0xffffffff))throw new Error('Invalid mode/seeds');
const start=performance.now();
const runs=await runJobs(seeds.map(seed=>({kind:'season',preset,seed})),{workers,onProgress:(n,total)=>console.log(preset+' '+n+'/'+total)});
fs.mkdirSync(new URL('../reports/defense-a/runs/',import.meta.url),{recursive:true});
const files=[];
for(const run of runs){const file='reports/defense-a/runs/'+preset+'-seed'+run.seed+'.json';fs.writeFileSync(new URL('../'+file,import.meta.url),JSON.stringify(run)+'\n');files.push({file,sha256:hash(file)});}
const result={preset,mode,workers,seeds,elapsedSeconds:(performance.now()-start)/1000,files,
  provenance:{sources:Object.fromEntries(['data/season-league.json','data/defense-source/game-exposure.json',
    ...(preset.startsWith('a-')?['reports/defense-a/rebound-audit.json']:[]),...(preset.endsWith('-clock')?['reports/defense-a/clock-calibration.json']:[])].map(f=>[f,hash(f)])),
  code:Object.fromEntries([...new Set([...codeFiles,'src/timed_game.js','src/season_simulation.js','src/defense_a_game.js','src/defense_a_season.js','src/defense_a_jobs.js','src/defense_a_presets.js',
    'src/defense_a_pool.js','scripts/defense_a_worker.js','scripts/run_defense_a_seeds.js'])].map(f=>[f,hash(f)]))}};
fs.writeFileSync(new URL('../reports/defense-a/'+preset+'-seeds.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));

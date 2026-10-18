import fs from 'node:fs';
import {runFourthJobs} from '../src/defense_fourth_pool.js';
import {prepareRuns,summarize,comparison} from '../src/defense_fourth_scoreboard.js';
import {read,hash} from './defense_io.js';
const root='reports/defense-fourth';
export function loadRuns(label){const m=read(root+'/'+label+'-seeds.json');return m.files.map(f=>read(f.file));}
export async function runLabel(label,options={},extra={}){
  const jobs=Array.from({length:20},(_,i)=>({label,seed:20261012+i,options,...extra}));
  const {defenseSignals,timingCDF,...brief}=options;
  console.log('START',label,JSON.stringify({...brief,...(defenseSignals?{signalPlayers:Object.keys(defenseSignals.values).length,signalCenters:defenseSignals.centers}:{}),...(timingCDF?{timingStates:Object.keys(timingCDF)}:{})}));const started=Date.now();
  const runs=await runFourthJobs(jobs,{workers:6,onProgress:(n,total)=>{if(n%4===0)console.log(label,n+'/'+total);}});
  const files=runs.map(r=>{const file=root+'/runs/'+label+'-seed'+r.seed+'.json';fs.writeFileSync(file,JSON.stringify(r)+'\n');return {seed:r.seed,file,sha256:hash(file)};});
  const manifest={label,seeds:jobs.map(j=>j.seed),options,extra,files,seconds:(Date.now()-started)/1000,code:Object.fromEntries(['src/defense_fourth_game.js','src/defense_fourth_season.js','src/defense_fourth_jobs.js','src/defense_fourth_effects.js','reports/defense-fourth/v2-calibration.json','reports/defense-fourth/model-'+(extra.post41?'pre41':'full')+'/engine-signals.json'].filter(f=>fs.existsSync(f)).map(f=>[f,hash(f)]))};
  fs.writeFileSync(root+'/'+label+'-seeds.json',JSON.stringify(manifest,null,2)+'\n');
  prepareRuns(runs);const board=summarize(runs,extra.post41),paired={};
  if(!extra.post41)for(const base of ['v1','v2'])if(base!==label&&fs.existsSync(root+'/'+base+'-seeds.json'))paired[base]=comparison(runs,loadRuns(base));
  fs.writeFileSync(root+'/scoreboard-'+label+'.json',JSON.stringify({...board,label,seeds:manifest.seeds,paired},null,2)+'\n');console.log('DONE',label,JSON.stringify(board.metrics));return runs;
}
if(process.argv[1]?.endsWith('run_defense_fourth.js'))for(const label of process.argv.slice(2))await runLabel(label);

import fs from 'node:fs';
import {read} from './defense_io.js';
import {runFifthJobs} from '../src/defense_fifth_pool.js';
import {teamDefenseMetrics} from '../src/defense_fifth_season.js';
import {mean} from '../src/statistical_summary.js';
const root='reports/defense-fifth';
for(const k of [25,41,55]){
 const target=read(root+'/pace-forecast-pre'+k+'.json'),history=[];let pace=read('reports/defense-fourth/normalization-pre41.json').selected.pace;
 // Three measured common-clock corrections, fixed before any score comparison.
 // The future roster is already a conditional input; no future result is read.
 for(let i=0;i<3;i++){
  const runs=await runFifthJobs([20261010,20261011].map(seed=>({label:'clock-calibration',seed,cutoff:k,audit:false,options:{pace}})),{workers:2});
  const ps=runs.map(r=>{const all=Object.fromEntries(Object.keys(r.teams[0].stats).map(key=>[key,r.teams.reduce((s,t)=>s+t.stats[key],0)])),op=Object.fromEntries(Object.keys(r.teams[0].stats).map(key=>[key,r.teams.reduce((s,t)=>s+t.opponent[key],0)]));return teamDefenseMetrics(all,op,r.teams.reduce((s,t)=>s+t.games,0)).possessionsProxy;});
  history.push({iteration:i,pace,simulatedPace:mean(ps),target:target.predictedPace});console.log(k,JSON.stringify(history.at(-1)));pace*=target.predictedPace/mean(ps);
 }
 const last=history.at(-1);fs.writeFileSync(root+'/clock-calibration-pre'+k+'.json',JSON.stringify({cutoff:k,seeds:[20261010,20261011],target,history,selected:{pace:last.pace},switch:'forecastClock',method:'Only common pace; player effects unchanged. Last of3 measured points, no accuracy objective. Calibration forecasts from pre-cutoff league box counts and unlabeled remaining active-roster schedule, never post-cutoff true pace/results.'},null,2)+'\n');
}

import fs from 'node:fs';
import {runFourthJobs} from '../src/defense_fourth_pool.js';
import {globalDefenseMetrics} from '../src/defense_fourth_season.js';
import {loadDefenseInputs,read} from './defense_io.js';
const target=loadDefenseInputs().target,history=[];let selected={pace:.90,foulScale:1};
for(let iteration=0;iteration<4;iteration++){
  const runs=await runFourthJobs([20261010,20261011].map(seed=>({label:'calibration',seed,audit:false,options:selected})),{workers:2});
  const merged={matches:runs.flatMap(r=>r.matches),teams:runs.flatMap(r=>r.teams)},metrics=globalDefenseMetrics(merged);
  history.push({iteration,selected:{...selected},metrics});console.log(JSON.stringify(history.at(-1)));
  if(Math.abs(metrics.possessionsProxy-target.possessionsProxy)<.15&&Math.abs(metrics.opponentFTR-target.opponentFTR)<.0015)break;
  selected={pace:selected.pace*target.possessionsProxy/metrics.possessionsProxy,foulScale:selected.foulScale*target.opponentFTR/metrics.opponentFTR};
}
// The final measured point, never an unmeasured extrapolation.
selected=history.at(-1).selected;
fs.writeFileSync('reports/defense-fourth/v2-calibration.json',JSON.stringify({selected,history,target,seeds:[20261010,20261011],method:'Full1230-game seasons, league FTR and possession proxy only. No team/win/net-accuracy objective; fixed maximum4 iterations. Continuous timing jitter uniform within +/-0.5s empirical bins, truncated conditionally.'},null,2)+'\n');

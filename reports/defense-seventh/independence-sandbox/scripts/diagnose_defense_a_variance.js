import fs from 'node:fs';
import {runJobs} from '../src/defense_a_pool.js';
import {VARIANCE_CONFIGS} from '../src/defense_a_variance.js';
import {mean,sd} from '../src/statistical_summary.js';
import {hash} from './defense_io.js';
const variants=Object.keys(VARIANCE_CONFIGS),games=2000;
const runs=await runJobs(variants.map(variant=>({kind:'variance',variant,games})),{onProgress:(n,total)=>console.log('Variance '+n+'/'+total)});
const baseline=runs.find(r=>r.variant==='baseline');
for(const run of runs){
  const deltas=run.results.map((r,i)=>baseline.results[i].margin**2-r.margin**2);
  run.varianceReductionVsBaseline=baseline.finalSD**2-run.finalSD**2;
  const se=sd(deltas)/Math.sqrt(games);
  run.pairedSquaredMarginReduction95=[mean(deltas)-1.96*se,mean(deltas)+1.96*se];
  run.sdReductionVsBaseline=baseline.finalSD-run.finalSD;
}
const report={scope:'A4 diagnosis only. Same roster on both sides; 2000 shared seeds per intervention; no variance correction adopted.',
  notes:['One-factor effects are non-additive; allFourOff and fixedFive are combined probes.',
    'Independent theory uses regulation possession outcomes; final SD additionally includes overtime/tie rules.',
    'Paired intervals concern squared margin, approximately variance for identical teams; starter exposure is descriptive, not causal.'],
  runs,provenance:{code:Object.fromEntries(['src/defense_a_game.js','src/defense_a_variance.js','src/statistical_summary.js','src/defense_a_pool.js','src/defense_a_jobs.js','scripts/defense_a_worker.js','scripts/diagnose_defense_a_variance.js'].map(f=>[f,hash(f)])),
    sources:{'data/season-league.json':hash('data/season-league.json'),'data/defense-source/game-exposure.json':hash('data/defense-source/game-exposure.json')}}};
fs.writeFileSync(new URL('../reports/defense-a/variance.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(runs.map(({results,...r})=>r),null,2));

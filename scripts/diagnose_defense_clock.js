import fs from 'node:fs';
import {runClockJobs} from '../src/defense_clock_pool.js';
import {hash} from './defense_io.js';
const presets=['v1-instrumented','a-instrumented','c-independent','c-time-only','c-empirical'];
const results=await runClockJobs(presets.map(preset=>({kind:'replay',preset,seed:20261012})),{onProgress:(n,t)=>console.log('clock diagnosis '+n+'/'+t)});
for(const r of results)fs.writeFileSync('reports/defense-b1/'+r.preset+'-diagnosis.json',JSON.stringify({...r,provenance:{normalizedReplay:hash(r.file),code:Object.fromEntries(['src/defense_clock_game.js','src/defense_clock_jobs.js','src/defense_pbp_analysis.js','scripts/diagnose_defense_clock.js'].map(f=>[f,hash(f)]))}},null,2)+'\n');
console.log(results.map(r=>({preset:r.preset,tov:r.totals.tov/2460,clock:r.totals.clockTov/2460,stl:r.totals.stl/2460,suppressedTouch:r.totals.clockExpectedTouch/2460,suppressedSteals:r.totals.clockExpectedLive/2460,residual:r.analysis.marginResidualSD,iid:r.analysis.independentSD})));

import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read} from './defense_io.js';
import {normalizationTarget,signalOptions} from '../src/defense_fourth_normalization.js';
import {logit} from '../src/defense_fourth_effects.js';
import {teamDefenseMetrics} from '../src/defense_fourth_season.js';
const root='reports/defense-fourth',selection=read(root+'/final-selection.json'),v2={...read('reports/defense-third/calibration-grid.json').selected,...read(root+'/v2-calibration.json').selected};
const run=data=>new Promise((resolve,reject)=>{const w=new Worker(new URL('./defense_fourth_normalization_worker.js',import.meta.url),{workerData:data});w.on('error',reject);w.on('message',m=>{w.terminate();m.error?reject(Error(m.error)):resolve(m.result);});});
for(const mode of ['full','pre41']){
  const target=normalizationTarget(mode),history=[],shifts={};let constants={...v2};
  for(let iteration=0;iteration<4;iteration++){
    const options={...selection.finalOptions,...constants,defenseSignals:signalOptions(mode,shifts)};
    const runs=await Promise.all([20261010,20261011].map(seed=>run({mode,seed,options})));
    const pooled=Object.fromEntries(Object.keys(runs[0].counts).map(k=>[k,runs.reduce((s,r)=>s+r.counts[k],0)]));
    const metrics=teamDefenseMetrics(pooled,pooled,runs.reduce((s,r)=>s+2*r.matches,0));
    const shortFG=runs.reduce((s,r)=>s+r.counts.rimm,0)/runs.reduce((s,r)=>s+r.counts.rima,0);
    history.push({iteration,constants:{...constants},shifts:{...shifts},metrics,shortFG});console.log(mode,JSON.stringify(history.at(-1)));
    if(selection.finalOptions.reboundSignal)shifts.DREB=(shifts.DREB??0)+logit(metrics.defensiveReboundPct/100)-logit(target.defensiveReboundPct/100);
    if(selection.finalOptions.rimSignal)shifts.shortFG=(shifts.shortFG??0)+logit(shortFG)-logit(target.shortFG);
    if(selection.finalOptions.liveSignal)shifts.liveTOV=(shifts.liveTOV??0)+Math.log(metrics.steals/target.steals);
    constants={...constants,pace:constants.pace*target.possessionsProxy/metrics.possessionsProxy,foulScale:constants.foulScale*target.opponentFTR/metrics.opponentFTR,clockViolationProbability:constants.clockViolationProbability*target.clockTurnovers/metrics.clockTurnovers};
  }
  const measured=history.at(-1);const selected={...measured.constants,defenseSignals:signalOptions(mode,measured.shifts)};
  fs.writeFileSync(root+'/normalization-'+mode+'.json',JSON.stringify({mode,target,selected,shifts:measured.shifts,history,seeds:[20261010,20261011],method:'Only common league intercepts: DREB, paint FG, live TOV plus common pace/foul/clock constants. Four measured iterations fixed in advance; never net margins or wins, never player/team coefficients. Full uses complete1230 fixtures; heldout calibration uses only574 strict first41 training fixtures and pre41 cards. Last measured point retained, not extrapolation.'},null,2)+'\n');
}

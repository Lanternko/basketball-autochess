import assert from 'node:assert/strict';
import {read,table,hash} from '../scripts/defense_io.js';
import {executeFifthJob} from '../src/defense_fifth_jobs.js';
import {executeFourthJob} from '../src/defense_fourth_jobs.js';
import {runFifthJobs} from '../src/defense_fifth_pool.js';
import {NBA_DEFENSE_V3,NBA_DEFENSE_V3_NAME} from '../src/defense_fifth_presets.js';
import {forecastClockOptions,fifthFinalOptions} from '../src/defense_fifth_clock.js';
import {summarizeFifth,compareFifth,actualFifth} from '../src/defense_fifth_scoreboard.js';
const root='reports/defense-fifth',frozen=read(root+'/v3-frozen.json');
assert.equal(NBA_DEFENSE_V3_NAME,'nba-defense-v3');for(const [file,h] of Object.entries(frozen.sources))assert.equal(hash(file),h,'frozen v3 '+file);
const indices=[0,1,2],seed=20261012;
assert.deepEqual(executeFifthJob({label:'v3',seed,indices,audit:false}).matches,executeFourthJob({label:'final',seed,indices,audit:false,options:NBA_DEFENSE_V3}).matches);
const jobs=[{label:'v3',seed,indices:[0],cutoff:0,audit:false},{label:'v3',seed:seed+1,indices:[1],cutoff:0,audit:false}],parallel=await runFifthJobs(jobs,{workers:2});for(let i=0;i<2;i++)assert.deepEqual(parallel[i],executeFifthJob(jobs[i]));
assert.deepEqual(forecastClockOptions(false,41),{});assert.deepEqual(fifthFinalOptions(0),{});assert.ok(forecastClockOptions(true,41).pace>0);
const league=read('data/season-league.json'),order=actualFifth(41).order;
for(const k of [25,55]){
 const model=read(root+'/model-pre'+k+'/engine-signals.json'),cards=read(root+'/pre'+k+'-league.json');
 assert.deepEqual(new Set(model.trainGames),new Set(cards.fifthProvenance.trainingGames));
 for(const id of model.trainGames){const g=league.schedule.find(g=>g.id===id);assert.ok(order[g.id+'/'+g.homeId]<=k&&order[g.id+'/'+g.awayId]<=k);}
 const manifest=read('data/defense-fifth-source/pre'+k+'/manifest.json');assert.equal(manifest.sources.length,60);assert.equal(manifest.failures.length,0);
 for(const s of manifest.sources){assert.equal(hash(s.file),s.sha256);assert.ok(table(s.file).every(r=>r.GP<=k));const g=league.schedule.find(g=>[g.homeId,g.awayId].includes(s.teamId)&&order[g.id+'/'+s.teamId]===k);assert.equal(s.date,g.date);}
}
if(process.argv.includes('--artifacts')){
 const labels=['v3-diagnostic','grid-00','grid-11','neutral-41','clock-41','v1-25','v3-25','clock-25','v1-55','v3-55','clock-55'];
 for(const label of labels){const m=read(root+'/'+label+'-seeds.json');assert.equal(m.files.length,20);assert.deepEqual(m.files.map(f=>f.seed),Array.from({length:20},(_,i)=>20261012+i));for(const [file,h] of Object.entries(m.code))assert.equal(hash(file),h,label+': '+file);for(const f of m.files){assert.equal(hash(f.file),f.sha256);const r=read(f.file);assert.ok(r.teams.every(t=>t.games===82-(m.extra.cutoff??0)));assert.ok(r.diagnosticGames.length>350);}}
 const m=read(root+'/v3-diagnostic-seeds.json'),p=read('reports/defense-fourth/final-normalized-seeds.json');for(let i=0;i<20;i++)assert.deepEqual(read(m.files[i].file).matches,read(p.files[i].file).matches);
 const runs=m.files.map(f=>read(f.file)),shuffled=runs.map(r=>({...r,teams:r.teams.slice().reverse()}));assert.deepEqual(summarizeFifth(runs).metrics,summarizeFifth(shuffled).metrics);for(const d of Object.values(compareFifth(runs,shuffled,0,100)))assert.equal(d.estimate,0);
 const report=read(root+'/closeout.json');for(const [file,h] of Object.entries(report.sources))assert.equal(hash(file),h,'report '+file);
 assert.equal(report.variance.implemented2c,false);assert.ok(report.variance.varianceGate['holdout-normalized'].MAEGainVersusActualEngine<.3);
 assert.ok(report.heldout.vsV3.winMAE.ci95[1]<0);assert.ok(report.heldout.vsV3.netRMSE.ci95[0]<=0);assert.ok(report.heldout.vsV3.calibrationError.ci95[0]<=0);
 assert.equal(report.candidates['neutral-41'].accepted,false);assert.ok(report.candidates['neutral-41'].paired.calibrationError.ci95[0]>0);
 for(const v of Object.values(report.variance.summary))assert.ok(Number.isFinite(v.real)&&Number.isFinite(v.v3));
 const simple=read(root+'/simple-baselines.json').splits['41'];assert.ok(simple.shrinkage>=0&&simple.shrinkage<=1);assert.ok(simple.pythagoreanExponent>0);assert.ok(simple.metrics.first_net_and_pythagorean.netRMSE<report.heldout.final.metrics.netRMSE);assert.ok(simple.metrics.first_net_and_pythagorean.winMAE<report.heldout.final.metrics.winMAE);
 assert.ok(Math.abs(report.clockDiagnosis.originalBias-(report.clockDiagnosis.trainingCalibrationError+report.clockDiagnosis.inputTransferShift+report.clockDiagnosis.actualSeasonPaceChange))<1e-10);
 assert.deepEqual(report.full.final.metrics,report.full.v3.metrics);
}
console.log('Fifth: frozen v3 parity, worker equality, clock switch, rolling cutoff provenance and artifacts PASS');

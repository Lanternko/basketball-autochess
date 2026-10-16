import assert from 'node:assert/strict';
import {executeThirdJob,thirdOptions} from '../src/defense_third_jobs.js';
import {executeClockJob} from '../src/defense_clock_jobs.js';
import {runThirdJobs} from '../src/defense_third_pool.js';
import {thirdLineup} from '../src/defense_third_minutes.js';
import {clockInputs} from '../src/defense_clock_jobs.js';
import {attemptMakeProbability} from '../src/defense_probability.js';
import {makeRng} from '../src/rng.js';
import {read,hash} from '../scripts/defense_io.js';
const indices=Array.from({length:12},(_,i)=>i),job={preset:'v1',seed:20261012,indices};
const old=executeClockJob({...job,preset:'v1-instrumented'}),now=executeThirdJob(job);assert.deepEqual(now.matches,old.matches);
const combined={preset:'combined',seed:20261012,indices:[0,1,2]},parallel=await runThirdJobs([combined,{...combined,seed:20261013}],{workers:2});
assert.deepEqual(parallel[0],executeThirdJob(combined));assert.deepEqual(parallel[1],executeThirdJob({...combined,seed:20261013}));
for(const run of parallel)for(const t of run.teams){const s=t.stats;assert.equal(s.deadTov-s.clockTov,s.offensiveFoulTov+s.otherViolationTov+s.passOutTov+s.handlingOutTov+s.unmappedDeadTov);}
for(const flag of ['reboundAccounting','empiricalTiming','independentClock','foulOutcomes','turnoverCategories'])assert.equal(thirdOptions('combined',{[flag]:false})[flag],false);
// Recorded FG inverse remains exact with unequal P(foul|made) and P(foul|miss).
const rng=makeRng(19),m=.57,qMiss=.28,qMake=.08,r=attemptMakeProbability(m,qMiss);let fga=0,fgm=0,fta=0;
for(let i=0;i<200000;i++){const made=rng()<r,foul=rng()<(made?qMake:qMiss);if(made||!foul){fga++;fgm+=made;}if(foul)fta+=made?1:2;}
assert.ok(Math.abs(fgm/fga-m)<.004);assert.ok(Math.abs(fta/200000-(r*qMake+2*(1-r)*qMiss))<.005);
const {inputs}=clockInputs(),g=inputs.league.schedule[0],t=inputs.league.teams.find(t=>t.id===g.homeId),e=inputs.exposure.games[0].teams.find(t=>t.teamId===g.homeId);
const actual=thirdLineup(t,g.homePlayerIds,e),season=thirdLineup(t,g.homePlayerIds,e,true);
assert.deepEqual(actual.roster.map(p=>p.playerId),season.roster.map(p=>p.playerId));assert.ok(Math.abs(season.roster.reduce((s,p)=>s+p.targetMinutes,0)-240)<1e-8);assert.ok(season.roster.every(p=>p.targetMinutes>=0&&p.targetMinutes<=48));
const model=read('reports/defense-third/offline-model.json');assert.equal(model.strictGames,1188);for(const d of Object.values(model.fitDiagnostics))assert.ok(d.residual.success&&d.prior.success&&d.current.success);
if(process.argv.includes('--artifacts')){
  for(const label of ['combined','combined-grid','accounting','independent','empirical','fouls','season-minutes']){const manifest=read('reports/defense-third/'+label+'-seeds.json');assert.equal(manifest.files.length,20);for(const [file,h] of Object.entries(manifest.code))assert.equal(hash(file),h);for(const f of manifest.files){assert.equal(hash(f.file),f.sha256);const r=read(f.file);assert.equal(r.matches.length,1230);assert.ok(r.teams.every(t=>t.games===82));}}
  for(const [file,h] of Object.entries(model.sources))assert.equal(hash(file),h);
  const tracking=read('data/defense-third-source/manifest.json');assert.equal(tracking.sources.length,60);assert.equal(tracking.failures.length,0);for(const s of tracking.sources)assert.equal(hash(s.file),s.sha256);
  const audits=read('reports/defense-third/combined-grid-possession-audits-20.json');assert.equal(audits.results.length,20);for(const [file,h] of Object.entries(audits.provenance))assert.equal(hash(file),h);
  const report=read('reports/defense-third/closeout.json');assert.equal(report.adopted,false);assert.equal(report.baseline,'nba-defense-v1');assert.ok(report.gates.some(g=>!g.pass));
  for(const [file,h] of Object.entries(report.sources))assert.equal(hash(file),h);
  assert.equal(model.fitDiagnostics.FTA.zeroExposureDroppedY,0);assert.equal(model.fitDiagnostics.FTA.testZeroExposureY,0);
}
console.log('third-batch tests passed: frozen parity, worker equality, ledgers, foul inverse, independent flags, minute targets, model convergence');

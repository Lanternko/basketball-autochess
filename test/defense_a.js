import assert from 'node:assert/strict';
import {read,hash,loadDefenseInputs} from '../scripts/defense_io.js';
import {simulateDefenseGame} from '../src/defense_game.js';
import {simulateDefenseAGame} from '../src/defense_a_game.js';
import {observedLineup} from '../src/minute_budget.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {checkDefenseAccounting} from '../src/defense_validation.js';
import {replayAccounting} from '../src/replay_accounting.js';
import {compareMetrics,scoreboard} from '../src/defense_scoreboard.js';
import {runJobs} from '../src/defense_a_pool.js';
import {executeJob} from '../src/defense_a_jobs.js';
const inputs=loadDefenseInputs(),fixture=inputs.league.schedule[0],exposure=inputs.exposure.games.find(g=>g.id===fixture.id);
const pair=[fixture.homeId,fixture.awayId].map((id,i)=>observedLineup(inputs.league.teams.find(t=>t.id===id),
  fixture[i?'awayPlayerIds':'homePlayerIds'],exposure.teams.find(t=>t.teamId===id)));
const before=JSON.stringify(pair),rates=read('reports/defense-a/rebound-audit.json').rates;
let teamRebounds=0;
for(let seed=1;seed<=24;seed++){
  const options={...NBA_DEFENSE_V1,stealPriorRate:inputs.priorRate,seed,replay:true};
  const old=simulateDefenseGame(...pair,options),unchanged=simulateDefenseAGame(...pair,options);
  assert.deepEqual(unchanged.events,old.events,'A switches off must preserve every v1 replay event');
  assert.equal(unchanged.scoreA,old.scoreA);assert.equal(unchanged.scoreB,old.scoreB);
  for(const k of Object.keys(old.statA))assert.equal(unchanged.statA[k],old.statA[k]);
  for(const k of Object.keys(old.statB))assert.equal(unchanged.statB[k],old.statB[k]);
  const candidate=simulateDefenseAGame(...pair,{...options,reboundAccounting:true,reboundRates:rates});
  checkDefenseAccounting(candidate);replayAccounting(candidate,pair);
  for(const side of ['A','B']){
    const own=candidate['stat'+side],op=candidate['stat'+(side==='A'?'B':'A')];
    assert.equal(own.reboundChances,own.oreb+op.dreb+own.teamOreb+op.teamDreb);
    teamRebounds+=own.teamOreb+own.teamDreb;
    for(const key of ['teamOreb','teamDreb','deadFtReb','reboundChances','periodMiss'])assert.equal(candidate['players'+side].reduce((n,p)=>n+p[key],0),0,'Team-only count must not be awarded to a player');
  }
}
assert.ok(teamRebounds>0);assert.equal(JSON.stringify(pair),before);
assert.throws(()=>simulateDefenseAGame(...pair,{reboundAccounting:true}));
const shifted=compareMetrics([1,2,3],[11,12,13]);
assert.equal(shifted.centeredMAE,0);assert.equal(shifted.centeredRMSE,0);assert.ok(Math.abs(shifted.correlation-1)<1e-12);assert.equal(shifted.sdRatio,1);assert.equal(shifted.slope,1);
assert.equal(compareMetrics([1,2],[5,5]).correlation,null);
assert.throws(()=>scoreboard([],[],{},[]));
const indices=Array.from({length:40},(_,i)=>i*30);
const jobs=[{kind:'season',preset:'legacy',seed:20261013,indices},{kind:'season',preset:'v1',seed:20261014,indices},
  {kind:'season',preset:'a-accounting-clock',seed:20261015,indices}];
const parallel=await runJobs(jobs,{workers:3});
for(let i=0;i<jobs.length;i++)assert.deepEqual(parallel[i],executeJob(jobs[i]),'Parallel/sequential full returned accounting differs');
const base=read('reports/nba-season-2025-26-seed20261012.json'),legacy=read('reports/defense-a/runs/legacy-seed20261012.json');
assert.deepEqual(legacy.matches.map(g=>[g.scoreA,g.scoreB]),base.matches.map(g=>[g.homeScore,g.awayScore]));
for(const seed of [20261012,20261013]){
  const p=read('reports/defense-a/runs/v1-seed'+seed+'.json'),saved=read('reports/nba-defense-v1-seed'+seed+'.json');
  assert.deepEqual(p.matches,saved.matches,'All 1230 parallel v1 scores must equal frozen sequential baseline');
  assert.deepEqual(p.teams.map(t=>t.stats),saved.accounting.map(t=>t.stats));
}
for(const file of ['reports/defense-a/scoreboard-legacy.json','reports/defense-a/scoreboard-nba-defense-v1.json','reports/defense-a/rebound-audit.json',
  'reports/defense-a/clock-calibration.json','reports/defense-a/variance.json']){
  const r=read(file);for(const entries of Object.values(r.provenance))for(const [f,h] of Object.entries(entries))assert.equal(hash(f),h,'Stale '+f);
}
const full=read('reports/defense-a/a-accounting-clock-seeds.json');assert.equal(full.mode,'full');assert.equal(full.seeds.length,20);
for(const [file,expected] of Object.entries(full.provenance.code))assert.equal(hash(file),expected);
for(const [file,expected] of Object.entries(full.provenance.sources))assert.equal(hash(file),expected);
for(const artifact of full.files){assert.equal(hash(artifact.file),artifact.sha256);const run=read(artifact.file);
  assert.equal(run.matches.length,1230);assert.equal(run.teams.length,30);assert.ok(run.teams.every(t=>t.games===82));
  assert.equal(run.teams.reduce((n,t)=>n+t.wins,0),1230);
}
console.log('PASS frozen v1 event parity, audited rebound/team accounting, player/score/minute/PM conservation, scoreboard centering and parallel/sequential deterministic outcomes');

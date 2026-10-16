import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash,loadDefenseInputs} from '../scripts/defense_io.js';
import {simulateDefenseGame} from '../src/defense_game.js';
import {simulateDefenseClockGame} from '../src/defense_clock_game.js';
import {observedLineup} from '../src/minute_budget.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {checkDefenseAccounting} from '../src/defense_clock_season.js';
import {normalizeRealGame,reconstructLineups} from '../src/defense_pbp_analysis.js';
import {executeClockJob,clockOptions} from '../src/defense_clock_jobs.js';
import {runClockJobs} from '../src/defense_clock_pool.js';
import {varianceAnalysis as trueScoreVariance} from '../src/defense_variance_sources.js';
const inputs=loadDefenseInputs(),fixture=inputs.league.schedule[0],exposure=inputs.exposure.games.find(g=>g.id===fixture.id),pair=[fixture.homeId,fixture.awayId].map((id,i)=>observedLineup(inputs.league.teams.find(t=>t.id===id),fixture[i?'awayPlayerIds':'homePlayerIds'],exposure.teams.find(t=>t.teamId===id)));
for(let seed=1;seed<=12;seed++){
  const opt={...NBA_DEFENSE_V1,stealPriorRate:inputs.priorRate,seed,replay:true},old=simulateDefenseGame(...pair,opt),instrument=simulateDefenseClockGame(...pair,opt);
  assert.deepEqual(instrument.events,old.events,'Clock switches off preserve frozen v1 events');
  for(const side of ['A','B'])for(const k of Object.keys(old['stat'+side]))assert.equal(instrument['stat'+side][k],old['stat'+side][k]);
  const empirical=simulateDefenseClockGame(...pair,{...clockOptions('c-empirical',{pace:.84}),seed,replay:true});checkDefenseAccounting(empirical);
  assert.ok(empirical.events.every(e=>e.clock>=0&&e.shotClock>=0));
  assert.ok(empirical.events.filter(e=>e.type==='SHOT_CLOCK').every(e=>e.independent===true),'No duration-generated shot-clock violation');
  const noViolation=simulateDefenseClockGame(...pair,{...clockOptions('c-empirical'),clockViolationProbability:0,seed,replay:true});assert.equal(noViolation.statA.clockTov+noViolation.statB.clockTov,0);
}
const pbp=read('data/defense-a-source/pbp/0022500123.json').data.game.actions,box=inputs.exposure.games.find(g=>g.id==='0022500123');
const lineup=reconstructLineups(pbp,box);assert.equal(lineup.valid,true,'Same-clock enter/leave sequence must be replayed in event order');
assert.ok(lineup.minuteChecks.every(p=>Math.abs(p.errorSeconds)<=1.1));
const silent=reconstructLineups(read('data/defense-a-source/pbp/0022500458.json').data.game.actions,inputs.exposure.games.find(g=>g.id==='0022500458'));
assert.equal(silent.valid,false);assert.ok(silent.errors.some(e=>e.reason==='ambiguous-period-start'),'Never infer silent overtime player from box minute fit');
const event=(type,sub,side,clock,score,extra={})=>({actionType:type,subType:sub,teamId:side,period:1,clock:'PT00M'+clock+'S',scoreHome:String(score[0]),scoreAway:String(score[1]),...extra});
const mini=[{...event('period','start',0,60,[0,0]),clock:'PT12M00.00S'},event('2pt','Layup',1,50,[2,0],{isFieldGoal:1,shotResult:'Made',area:'Restricted Area'}),event('freethrow','1 of 1',1,50,[3,0],{shotResult:'Made'}),event('turnover','shot clock',2,26,[3,0]),event('2pt','Layup',1,20,[3,0],{isFieldGoal:1,shotResult:'Missed',actionNumber:5}),event('rebound','offensive',1,18,[3,0],{shotActionNumber:5}),event('3pt','Jump Shot',1,10,[6,0],{isFieldGoal:1,shotResult:'Made'}),event('period','end',0,0,[6,0])];
const normalized=normalizeRealGame(mini,{id:'test',homeId:1,awayId:2});assert.equal(normalized.pointsValid,true);assert.deepEqual(normalized.possessions.map(p=>p.points),[3,0,3,0]);assert.ok(normalized.segments.some(s=>s.state==='retained'));
const technical=structuredClone(normalized);technical.id='technical';technical.possessions[0].opponentPoints=1;technical.possessions[0].signedPoints=2;technical.possessions.push({...technical.possessions[1],points:2,signedPoints:2});
const third=structuredClone(normalized);third.id='third';third.possessions[0].points=4;third.possessions[0].signedPoints=4;
const trueScores=trueScoreVariance([normalized,technical,third]);assert.deepEqual(trueScores.records.find(r=>r.id==='technical').S,[6,3],'Score covariance must use actual team points, not signed offensive-possession scores');
const jobs=[{preset:'v1-instrumented',seed:20261012,indices:[0,200,400]},{preset:'c-empirical',seed:20261013,indices:[1,201,401],options:{pace:.84}}],parallel=await runClockJobs(jobs,{workers:2});
for(let i=0;i<jobs.length;i++)assert.deepEqual(parallel[i],executeClockJob(jobs[i]),'New clock parallel/sequential parity');
const prep=read('reports/defense-b1/preparation.json');assert.equal(prep.sourceGames,1227);assert.equal(prep.validLineupGames+prep.failedLineupGames,1227);assert.equal(prep.stintCountChecks.length,0);assert.equal(prep.individualPlayers.length,582);
for(const group of Object.values(prep.provenance))for(const [file,expected] of Object.entries(group))assert.equal(hash(file),expected,'Stale preparation '+file);
const actual=read('reports/defense-b1/real-variance.json'),d=actual.decomposition;
assert.ok(Math.abs(d.iidVariance+d.individualPaceVariance+d.paceCovarianceReduction+d.remainingCovarianceReduction+d.withinTeamSerialAndHeterogeneityVariance-d.total)<1e-8);
assert.ok(Math.abs(actual.strengthAdjustedScoreVariance*2-2*actual.scoreCovariance-d.total)<1e-8);
assert.ok(Math.abs(Object.values(actual.pointsDistribution).reduce((n,v)=>n+v.share,0)-1)<1e-10);
const accurate=read('reports/defense-b1/variance-sources.json');for(const r of [accurate.real,accurate.simulation]){
  const d=r.decomposition;assert.ok(Math.abs(d.iidVariance+d.individualPaceVariance+d.paceCovarianceReduction+d.remainingCovarianceReduction+d.withinTeamSerialAndHeterogeneityVariance-d.total)<1e-8);
  assert.ok(Math.abs(r.strengthAdjustedScoreVariance*2-2*r.scoreCovariance-d.total)<1e-8);
  assert.ok(Math.abs(r.withinTeamScoreVariance-r.perTeam.reduce((n,t)=>n+t.games*t.scoreVariance,0)/r.perTeam.reduce((n,t)=>n+t.games,0))<1e-8);
}
const stints=fs.readFileSync('reports/defense-b1/stints.jsonl','utf8').trim().split('\n').map(JSON.parse);assert.equal(stints.length,prep.stintCount);assert.ok(stints.every(s=>s.lineups.every(a=>a.length===5&&new Set(a).size===5)));
const sample=read('reports/defense-b1/defensive-samples.json'),bad=new Set([...sample.uncertainPossessionGames.map(g=>g.id),...sample.counterMismatchGames]);
const usable=new Set(stints.filter(s=>!bad.has(s.id)).map(s=>s.id));const realGames=fs.readFileSync('reports/defense-b1/real-games.jsonl','utf8').trim().split('\n').map(JSON.parse);
const credited=sample.strict.individualPlayers.reduce((n,p)=>n+p.defensivePossessions,0),expected=5*realGames.filter(g=>usable.has(g.id)).reduce((n,g)=>n+g.possessions.length,0);
assert.ok(Math.abs(credited-expected)<1e-6,'Five defensive players must receive exactly one possession total per opposing possession');
const frozen=read('reports/defense-a/runs/v1-seed20261012.json'),matches=new Map(frozen.matches.map(g=>[g.id,g]));
for(const g of fs.readFileSync('reports/defense-b1/v1-instrumented-replay-seed20261012.jsonl','utf8').trim().split('\n').map(JSON.parse))assert.deepEqual(g.score,[matches.get(g.id).scoreA,matches.get(g.id).scoreB],'All 1230 instrumented scores match frozen v1');
for(const manifest of ['reports/defense-a/v1-seeds.json','reports/defense-b1/c-empirical-seeds.json']){
  const m=read(manifest);assert.equal(m.seeds.length,20);for(const group of Object.values(m.provenance))for(const [file,expected] of Object.entries(group))assert.equal(hash(file),expected,'Stale season input '+file);
  for(const s of m.files){assert.equal(hash(s.file),s.sha256);const run=read(s.file);assert.equal(run.matches.length,1230);assert.equal(run.teams.reduce((n,t)=>n+t.wins,0),1230);assert.ok(run.teams.every(t=>t.games===82));}
}
for(const preset of ['v1','a-accounting-clock','c-empirical']){const b=read('reports/defense-b1/scoreboard-'+preset+'-20.json');assert.equal(b.seeds.length,20);assert.equal(hash(b.provenance.manifest.file),b.provenance.manifest.sha256);for(const group of [b.provenance.sources,b.provenance.code])for(const [file,h] of Object.entries(group))assert.equal(hash(file),h);assert.equal(b.adoption.reportedOnly.includes('winMAE'),true);assert.ok(b.uncertainty.metrics['net.centeredRMSE'].standardError>0);}
const zones=read('reports/defense-b1/stint-schema.json');assert.equal(zones.stints,prep.stintCount);assert.equal(hash('reports/defense-b1/stint-zones.jsonl'),zones.provenance.output);
for(const file of ['reports/defense-b1/variance-sources.json','reports/defense-b1/closeout.json']){
  const p=read(file);for(const [source,expected] of Object.entries(p.provenance.sources))assert.equal(hash(source),expected,'Stale report '+source);
  if(typeof p.provenance.code==='string')assert.equal(hash('scripts/report_defense_b1.js'),p.provenance.code);else for(const [file,h] of Object.entries(p.provenance.code))assert.equal(hash(file),h);
}
console.log('PASS baseline replay parity, independent timing/violation switches, replay clock/accounting, real and-one/OREB possessions, lineup minutes and same-clock substitutions, ambiguity quarantine, parallel parity, stint factor conservation, variance identity');

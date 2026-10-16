import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {runDefenseSeason,defensiveMeasurements,teamDefenseMetrics,realCountStats,boxPossessions} from '../src/defense_validation.js';
const read=f=>JSON.parse(fs.readFileSync(new URL('../'+f,import.meta.url)));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+f,import.meta.url))).digest('hex');
const table=f=>{const s=read(f).data.resultSets[0];return s.rowSet.map(r=>Object.fromEntries(s.headers.map((k,i)=>[k,r[i]])));};
const raw=read('data/season-league.json'),exposure=read('data/defense-source/game-exposure.json');
assert.equal(exposure.games.length,1230);assert.equal(exposure.sources.length,1231);
for(const source of exposure.sources)assert.equal(hash('data/'+source.file),source.sha256);
const games=new Map(exposure.games.map(g=>[g.id,g]));
for(const f of raw.schedule)for(const side of ['home','away']){
  const observed=games.get(f.id).teams.find(t=>t.teamId===f[side+'Id']);
  assert.equal(observed.players.filter(p=>p.starter).length,5);
  assert.equal(observed.players.reduce((n,p)=>n+p.points,0),f.observed[side+'Score']);
  assert.ok(f[side+'PlayerIds'].every(id=>observed.players.some(p=>p.playerId===id)));
}
const {league,priorRate}=defensiveMeasurements(raw,table('data/benchmark-source/base.json'));
const baseline=read('reports/nba-season-2025-26-seed20261012.json');
const indices=[0,raw.schedule.findIndex(g=>g.neutral),baseline.matches.findIndex(g=>g.overtimes>0)];
runDefenseSeason(league,exposure,{seed:20261012,options:{stealPriorRate:priorRate},indices,baseline});
const options={minuteMode:'budget',foulOut:99,stealPriorRate:priorRate,turnoverMode:'pressure',foulConditioning:true,shotSelection:'volume'};
const controlled=runDefenseSeason(league,exposure,{seed:20261012,options,indices,replay:true});
assert.equal(controlled.matches.length,3);
assert.ok(controlled.teams.every(t=>t.regulationMinuteError<1e-5));
for(const t of controlled.teams){
  assert.equal(t.players.reduce((n,p)=>n+p.plusMinus,0),5*(t.stats.pts-t.opponent.pts));
  assert.ok(t.stats.touchSteals+t.stats.passSteals===t.stats.stl);
}
assert.equal(boxPossessions({fga:90,oreb:10,tov:14,fta:25}),105);
const actual=realCountStats(table('data/benchmark-source/teams.json')[0]);assert.ok(actual.fga>0&&actual.pts>0);
const reportPath=new URL('../reports/defense-validation.json',import.meta.url);
if(fs.existsSync(reportPath)){
  const report=read('reports/defense-validation.json');
  for(const [f,h] of Object.entries(report.provenance.sources))assert.equal(hash(f),h);
  for(const [f,h] of Object.entries(report.provenance.code))assert.equal(hash(f),h);
  assert.equal(report.variants.length,8);
  assert.ok(Number.isFinite(report.target.fg)&&report.target.fg>40&&report.target.fg<55);
  for(const v of report.variants){
    assert.equal(hash(v.file),v.sha256);
    const run=read(v.file);assert.equal(run.matches.length,1230);assert.equal(run.teams.length,30);
    assert.equal(run.teams.reduce((n,t)=>n+t.wins,0),1230);assert.ok(run.teams.every(t=>t.games===82));
    assert.ok(v.teams.every(t=>Number.isFinite(t.defensiveRatingProxy)&&Number.isFinite(t.observed.defensiveRatingProxy)));
    if(v.options.minuteMode==='budget')assert.ok(v.meanRegulationTargetMAE<1e-5);
  }
  const legacy=read(report.variants.find(v=>v.id==='legacy').file),minutes=read(report.variants.find(v=>v.id==='minutes').file),split=read(report.variants.find(v=>v.id==='split').file);
  assert.deepEqual(legacy.matches.map(g=>[g.scoreA,g.scoreB]),baseline.matches.map(g=>[g.homeScore,g.awayScore]));
  assert.deepEqual(minutes.matches,split.matches,'split accounting must not change scores, clock or overtime');
  assert.equal(minutes.teams.reduce((n,t)=>n+t.stats.tov,0),split.teams.reduce((n,t)=>n+t.stats.tov,0));
  console.log('PASS eight complete season artifacts, independent split accounting, regulation exposure, original baseline parity and all fingerprints');
}
console.log('PASS 1230 official boxes, original/neutral/OT fixture accounting, volume/pressure/foul interventions and complete source manifests');

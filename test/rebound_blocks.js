import assert from 'node:assert/strict';
import { opportunityReboundWeights, blockProfile, REBOUND_RULES } from '../src/rebound_block_model.js';
import { simulateGame } from '../src/simulation_engine.js';
import { BASELINE, TEAMS } from '../src/teams.js';
import { percentileAttribute, percentileTeam } from '../src/benchmark_teams.js';
import * as M from '../src/probability_model.js';
import * as C from '../src/constants.js';

let passed=0;
function test(name,fn){fn();console.log(`PASS ${name}`);passed++;}
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`);

test('Landing luck floors, bounded skill, normalization and guard long rebounds',()=>{
  const l=BASELINE.roster;
  for(const side of ['offense','defense'])for(const zone of ['short','mid','long']) {
    const w=opportunityReboundWeights(l,{side,zone});
    close(w.reduce((a,b)=>a+b),1);
    assert.ok(w.every(x=>x>=REBOUND_RULES.luckShare/5));
    assert.ok(w[4]>w[0] || zone==='long');
  }
  const rim=opportunityReboundWeights(l,{zone:'short'}),long=opportunityReboundWeights(l,{zone:'long'});
  assert.ok(long[0]>rim[0]);
  for(const v of [0,40,70,99,999]) {
    const w=opportunityReboundWeights(l.map((p,i)=>({...p,rebound:i===0?v:70})),{zone:'mid'});
    assert.ok(w.every(Number.isFinite));
    if(v>0)assert.ok(w[0]>opportunityReboundWeights(l.map((p,i)=>({...p,rebound:i===0?v-1:70})),{zone:'mid'})[0] || v>150);
  }
});
test('Offensive role and shooter location limit long-range self-rebounding',()=>{
  const l=TEAMS.GSW.roster;
  const legacy=M.reboundWeights(l);
  const updated=opportunityReboundWeights(l,{side:'offense',zone:'long',shooterIndex:2});
  assert.ok(updated[2]<legacy[2]/2,'KD should not monopolize long-shot rebounds');
  assert.ok(updated[0]>legacy[0],'Curry has baseline opportunities');
  const shootingInside=opportunityReboundWeights(l,{side:'offense',zone:'short',shooterIndex:2});
  assert.ok(shootingInside[2]>updated[2]);
  const center=l.map((p,i)=>i===3?{...p,courtPosition:'C'}:p);
  const original=opportunityReboundWeights(l,{side:'offense',zone:'short'});
  assert.ok(opportunityReboundWeights(center,{side:'offense',zone:'short'})[3]>original[3]);
});
test('Blocks scale with shot location, rim protection and assigned interior role',()=>{
  const l=BASELINE.roster;
  const rim=blockProfile(l,{zone:'short'}),mid=blockProfile(l,{zone:'mid'}),long=blockProfile(l,{zone:'long'});
  assert.ok(rim.perAttempt>mid.perAttempt && mid.perAttempt>long.perAttempt);
  const low=l.map(p=>({...p,help:40})),high=l.map(p=>({...p,help:99}));
  assert.ok(blockProfile(high).perAttempt>blockProfile(low).perAttempt);
  const candidate=l.map((p,i)=>i===2?{...p,courtPosition:'C'}:p);
  assert.ok(blockProfile(candidate).weights[2]>rim.weights[2]);
  assert.ok(long.weights[0]>rim.weights[0],'Perimeter blocks mostly by direct defender');
  for(const makeProbability of [0,0.5,0.99,1]) {
    const profile=blockProfile(high,{makeProbability});
    assert.ok(profile.perAttempt<=1-makeProbability);
    assert.ok(profile.conditionalOnMiss>=0 && profile.conditionalOnMiss<=1);
    close(profile.weights.reduce((a,b)=>a+b),1);
  }
  assert.equal(blockProfile(l,{makeProbability:1}).conditionalOnMiss,0);
});
test('Block tags match credits, missed FGAs, rebound conservation; no fake TOV',()=>{
  let blocks=0;
  for(let seed=1;seed<=16;seed++) {
    const g=simulateGame(TEAMS.OKC,TEAMS.GSW,{seed,possessions:75,fatigue:false});
    const tags=g.log.filter(e=>e.blocker);
    assert.equal(tags.length,g.statA.blk+g.statB.blk);
    for(const e of tags){assert.ok(['FG3X','MIDX','RIMX'].includes(e.ev));assert.ok(e.blocker);}
    for(const [s,d,players]of[[g.statA,g.statB,g.playersA],[g.statB,g.statA,g.playersB]]) {
      assert.equal(s.blk,d.blka);assert.ok(s.blka<=s.fga-s.fgm);
      assert.equal(s.oreb+d.dreb,s.fga-s.fgm);
      assert.equal(players.reduce((a,p)=>a+p.blk,0),s.blk);
    }
    blocks+=tags.length;
  }
  assert.ok(blocks>0);
});
test('Block classification adds no second FG penalty and leaves all FT draws intact',()=>{
  for(const team of Object.values(TEAMS))for(const seed of [1,20260908]) {
    const opts={possessions:75,fatigue:false,seed};
    const on=simulateGame(team,BASELINE,{...opts,blocks:true});
    const off=simulateGame(team,BASELINE,{...opts,blocks:false});
    assert.equal(on.scoreA,off.scoreA);assert.equal(on.scoreB,off.scoreB);
    assert.deepEqual(on.log.map(({blocker,...e})=>e),off.log);
    for(const side of ['statA','statB'])for(const k of ['fga','fgm','fta','ftm','oreb','dreb','tov'])assert.equal(on[side][k],off[side][k]);
  }
  // Golden FT mapping is intentionally unchanged by the rebound/block work.
  assert.deepEqual(C.CURVE_FT,[[0,0.450],[40,0.560],[55,0.700],[70,0.7935],[85,0.850],[99,0.900],[120,0.925],[150,0.940]]);
});
test('PR90 uses card percentile scale, not raw attribute 90',()=>{
  assert.equal(percentileAttribute(50),70);assert.equal(percentileAttribute(90),94);
  assert.equal(percentileAttribute(99),99);
  const high=percentileTeam(90);
  assert.equal(high.roster.length,5);
  assert.ok(high.roster.every(p=>p.onBall===94&&p.help===94&&p.ft===94));
  assert.throws(()=>percentileTeam(100));
});
console.log(`\n${passed} rebound/block checks passed`);

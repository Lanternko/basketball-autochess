import assert from 'node:assert/strict';
import {simulateGame} from '../src/simulation_engine.js';
import {simulateDefenseGame} from '../src/defense_game.js';
import {BASELINE} from '../src/teams.js';
import {minuteBudgetSchedule,observedLineup} from '../src/minute_budget.js';
import {pressureSignal,stealRate,attemptMakeProbability,defenseProbabilities} from '../src/defense_probability.js';
import * as M from '../src/probability_model.js';
import {replayAccounting} from '../src/replay_accounting.js';
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-5,`${a} != ${b}`);
const legacyKeys=['pts','fgm','fga','fg3m','fg3a','fta','ftm','oreb','dreb','ast','blk','tov','pf','seconds','poss','passes'];
const team={...BASELINE,roster:Array.from({length:11},(_,i)=>({...BASELINE.roster[i%5],playerId:i+1,
  name:'Controlled '+i,targetMinutes:[36,35,34,33,32,20,18,16,10,6,0][i],defenseMeasurement:{minutes:1000,steals:20+i*4}}))};
const before=JSON.stringify(team);
for(const m of [.2,.5,.8,1])for(const q of [0,.05,.2,.5]){
  const raw=attemptMakeProbability(m,q);near(raw/(1-q*(1-raw)),m);
}
assert.throws(()=>attemptMakeProbability(.5,1));
const handler={...team.roster[0],shotProfile:{threeRate:.4,freeThrowsPerAttempt:.3}},context=M.teammateContext(team.roster.slice(0,5),0);
for(const coefficient of [0,1]){
  const options={contextLongScale:coefficient,contextShortScale:coefficient};
  const separate=defenseProbabilities(handler,context,team.roster[1],70,70,70,70,options);
  const shared=M.possessionProbabilities(handler,context,team.roster[1],70,70,70,70,{contextScale:coefficient});
  for(const z of ['long','mid','short']){near(separate.make[z],shared.make[z]);near(separate.zone[z],shared.zone[z]);}
  near(separate.ev,shared.ev);
}
const pressureOpts={turnoverMode:'pressure',pressureAttribute:70,contextLongScale:0,contextShortScale:.5};
const low=defenseProbabilities(handler,context,{...team.roster[1],onBall:40},70,70,70,70,pressureOpts);
const high=defenseProbabilities(handler,context,{...team.roster[1],onBall:99},70,70,70,70,pressureOpts);
near(low.pTovTouch,high.pTovTouch);assert.ok(high.make.long<low.make.long);
const schedule=minuteBudgetSchedule(team.roster),actual=team.roster.map(()=>0);
for(const s of schedule){assert.equal(new Set(s.lineup).size,5);s.lineup.forEach(i=>actual[i]+=s.end-s.start);}
actual.forEach((seconds,i)=>near(seconds,team.roster[i].targetMinutes*60));
assert.deepEqual(schedule[0].lineup,[0,1,2,3,4]);
assert.throws(()=>minuteBudgetSchedule(team.roster.map(p=>({...p,targetMinutes:49}))));
assert.throws(()=>minuteBudgetSchedule(team.roster.map(p=>({...p,targetMinutes:1}))));
let touches=0,passes=0,overtime=false;
for(let seed=1;seed<=16;seed++){
  const old=simulateGame(team,team,{mode:'timed',seed}),original=simulateDefenseGame(team,team,{seed,replay:true});
  const split=simulateDefenseGame(team,team,{seed,turnoverMode:'split',replay:true});
  assert.equal(original.scoreA,old.scoreA);assert.equal(original.scoreB,old.scoreB);
  assert.equal(split.scoreA,original.scoreA);assert.equal(split.scoreB,original.scoreB);
  assert.equal(split.gameSeconds,original.gameSeconds);
  for(const side of ['A','B']){
    for(const k of legacyKeys){near(original['stat'+side][k],old['stat'+side][k]);near(split['stat'+side][k],original['stat'+side][k]);}
    const stats=split['stat'+side],opposite=split['stat'+(side==='A'?'B':'A')];
    assert.equal(stats.liveTov+stats.deadTov,stats.tov);assert.equal(stats.liveTov,opposite.stl);
    assert.equal(stats.passSteals+stats.touchSteals,stats.stl);assert.equal(stats.fga,stats.fg3a+stats.mida+stats.rima);
    assert.equal(stats.fgm,stats.fg3m+stats.midm+stats.rimm);assert.ok(stats.xfgm>=0&&stats.xfgm<=stats.fga);
    touches+=stats.touchSteals;passes+=stats.passSteals;
  }
  replayAccounting(split,[team,team]);
  const controlled=simulateDefenseGame(team,team,{seed,minuteMode:'budget',foulOut:99,turnoverMode:'pressure',replay:true});
  for(const side of ['A','B']){
    controlled['players'+side].forEach((p,i)=>near(p.regulationSeconds,team.roster[i].targetMinutes*60));
    assert.equal(controlled['players'+side][10].seconds,0);
    near(controlled['stat'+side].seconds,controlled.gameSeconds*5);
    for(const event of controlled.events.filter(e=>['FGM','FGX','FTM','FTX','STEAL','TOV','PASS'].includes(e.type)))assert.ok(event.lineups[event.off].includes(event.player),'off-court event attribution');
  }
  overtime ||= controlled.overtimes>0;
  replayAccounting(controlled,[team,team]);
  const {events,...plain}=controlled;
  assert.deepEqual(simulateDefenseGame(team,team,{seed,minuteMode:'budget',foulOut:99,turnoverMode:'pressure'}),plain);
}
assert.ok(touches>0&&passes>0);
for(let seed=17;seed<=160&&!overtime;seed++){
  const g=simulateDefenseGame(team,team,{seed,minuteMode:'budget',foulOut:99,replay:true});
  if(g.overtimes){overtime=true;replayAccounting(g,[team,team]);g.playersA.forEach((p,i)=>near(p.regulationSeconds,team.roster[i].targetMinutes*60));assert.equal(g.playersA[10].seconds,0);}
}
assert.ok(overtime,'Overtime must preserve regulation budgets');
assert.equal(JSON.stringify(team),before);
assert.equal(pressureSignal(team.roster,.035).relative,pressureSignal(team.roster.map(p=>({...p,onBall:150})),.035).relative,'pressure independent of 3P contest');
assert.ok(stealRate({...team.roster[0],defenseMeasurement:{minutes:1000,steals:90}},.035)>stealRate(team.roster[0],.035));
assert.throws(()=>simulateDefenseGame(team,team,{minuteMode:'budget'}));
assert.throws(()=>simulateDefenseGame(team,team,{turnoverMode:'invalid'}));
assert.throws(()=>simulateDefenseGame(team,team,{stealPriorRate:0}));
const exposure={players:team.roster.map((p,i)=>({playerId:p.playerId,seconds:p.targetMinutes*60,starter:i<5,position:i<2?'G':i<4?'F':i===4?'C':''}))};
const observed=observedLineup({...team,roster:team.roster.map(p=>({...p,heightInches:72+p.playerId,seasonMinutesPerGame:p.targetMinutes||.01}))},team.roster.map(p=>p.playerId),exposure);
near(observed.roster.reduce((n,p)=>n+p.targetMinutes,0),240);assert.equal(observed.roster.at(-1).targetMinutes,0);
assert.equal(observed.roster.filter(p=>p.officialStarter).length,5);
console.log(`PASS legacy outcome parity, split-only TOV/score/minute parity, live/dead/STL identities, exact regulation budgets, zero-minute exclusion, replay attribution and independent pressure; OT observed=${overtime}`);

import assert from 'node:assert/strict';
import { simulateGame } from '../src/simulation_engine.js';
import { TEAMS } from '../src/teams.js';
for (const seed of [1,42,20260908]) {
 const opts={seed,possessions:50};
 const plain=simulateGame(TEAMS.GSW,TEAMS.CLE,opts);
 const {events,...result}=simulateGame(TEAMS.GSW,TEAMS.CLE,{...opts,replay:true});
 assert.deepEqual(result,plain,'Replay recording must not change the model');
 assert.deepEqual(events.at(-1).score,[plain.scoreA,plain.scoreB]);
 for(const e of events) for(let s=0;s<2;s++) {
  assert.equal(e.players[s].reduce((n,p)=>n+p.pts,0),e.score[s]);
  for(const p of e.players[s]) {
   assert.equal(p.pts,3*p.fg3m+2*(p.midm+p.rimm)+p.ftm);
   assert.ok(p.fgm<=p.fga); assert.ok(p.fg3m<=p.fg3a);
  }
 }
 for(const [s,rows] of [plain.playersA,plain.playersB].entries()) rows.forEach((p,i)=>{
  for(const key of ['pts','reb','stl','blk','tov','fgm','fga','fg3m','fg3a','ftm','fta','pf']) assert.equal(events.at(-1).players[s][i][key],p[key]);
 });
 assert.ok(events.some(e=>e.type==='PASS'));
}
console.log('Replay: deterministic parity, per-event scoring, final player totals passed (3 seeds).');

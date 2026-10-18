import assert from 'node:assert/strict';
import {SEASON_COUNT_KEYS} from './season_simulation.js';
// Team shot-clock violations have no player actor in the cached official PBP.
// Preserve every original accounting identity, with an explicit team-only TOV.
export function checkTeamClockAccounting(game){
 assert(game.complete&&game.winnerA!==null&&game.scoreA!==game.scoreB,'Unfinished game; refusing to assign a winner');
 assert.equal(game.gameSeconds,2880+game.overtimes*300,'Incorrect game duration');
 for(const side of ['A','B']){
  const stat=game['stat'+side],players=game['players'+side];
  assert.equal(stat.pts,game['score'+side],'Score does not match points');
  assert.equal(stat.pts,2*stat.fgm+stat.fg3m+stat.ftm,'Scoring identity failed');
  assert.equal(game.periodScores[side==='A'?0:1].reduce((s,x)=>s+x,0),stat.pts,'Period scores do not sum');
  for(const key of SEASON_COUNT_KEYS.filter(k=>k!=='poss')){
   const playerTotal=players.reduce((s,p)=>s+p[key],0),teamOnly=key==='tov'?stat.clockTov:0;
   assert.ok(Math.abs(playerTotal+teamOnly-stat[key])<.11,'Player/team accounting mismatch: '+key);
  }
  assert.ok(Math.abs(stat.seconds-5*game.gameSeconds)<.11,'Five-player minute budget failed');
  assert.equal(players.reduce((s,p)=>s+p.clockTov,0),0,'Team clock violations must not be assigned to a player');
  assert.equal(players.reduce((s,p)=>s+p.deadTov,0)+stat.clockTov,stat.deadTov,'Team-only dead turnover partition failed');
 }
}

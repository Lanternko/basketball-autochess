import assert from 'node:assert/strict';
import {loadInput} from '../reports/player-impact-v26/input.mjs';
import {attachDefenseAnchors} from '../reports/player-impact-v28/defense-input.mjs';
import {contestDeltas} from '../reports/player-impact-v28/model.mjs';
import {contestDeltas as previousDeltas} from '../reports/player-impact-v20/model.mjs';
import {interpolate} from '../src/probability_model.js';
import * as C from '../src/constants.js';
let cards=0,restored=0,checks=0;
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-12,`${a} != ${b}`);
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),players=[...new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])).values()];
 const original=structuredClone(players);
 for(const p of original){const five=Array.from({length:5},()=>p);assert.deepEqual(contestDeltas(five),previousDeltas(five));}
 attachDefenseAnchors(players);
 for(let i=0;i<players.length;i++){
  const p=players[i],five=Array.from({length:5},()=>p),actual=contestDeltas(five);cards++;
  for(const[z,k,curve]of [['long','onBall',C.CURVE_DEF_3PT],['short','help',C.CURVE_DEF_RIM]]){
   const m=p.defenseExposureMeasurement[z],reference=m.attempts>0&&!m.sourceMissing&&Number.isFinite(m.rawDifference)?m.rawDifference*m.attempts/(m.attempts+200):interpolate(p[k],curve);
   close(actual[z],5*m.rate*(reference-interpolate(70,curve))/p.defenseExposureMeasurement.leagueAttemptsPerTeamMinute[z]);checks++;
   if(Math.abs(reference-interpolate(p[k],curve))>1e-8)restored++;
   const changed=structuredClone(p);changed[k]=70;
   const expectedChange=5*m.rate*(interpolate(70,curve)-interpolate(p[k],curve))/p.defenseExposureMeasurement.leagueAttemptsPerTeamMinute[z];
   close(contestDeltas(Array.from({length:5},()=>changed))[z]-actual[z],expectedChange);checks++;
  }
 }
}
assert.equal(cards,2262);assert.equal(restored,12);
console.log({cards,sourceAndCounterfactualChecks:checks,restoredSourceZoneCards:restored,withoutAnchorsExactOldDeltas:true});

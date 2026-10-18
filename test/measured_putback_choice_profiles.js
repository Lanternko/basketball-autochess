import assert from 'node:assert/strict';
import {ovrInput as previousInput} from '../reports/player-impact-v22/ovr-input.mjs';
import {ovrInput} from '../reports/player-impact-v23/ovr-input.mjs';
import {ATTRIBUTES} from '../src/strength_benchmark.js';
import {measuredPutbackChoice} from '../reports/player-impact-v23/model.mjs';
let cards=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const previous=await previousInput(season),before=structuredClone(previous),x=await ovrInput(season);
 assert.deepEqual(previous,before,'New input must not mutate previous cached model');
 for(let slot=0;slot<5;slot++){
  const p=x.profiles[slot];assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/ATTRIBUTES.length-70)<1e-10);
  for(const k of ATTRIBUTES)assert.equal(p[k],previous.profiles[slot][k]);
  assert.ok(p.putbackChoiceMeasurement.rebounds>0);assert.ok(measuredPutbackChoice(p)>0&&measuredPutbackChoice(p)<1);cards++;
 }
 for(const p of [...x.players,...x.opponents.flatMap(t=>t.roster)]){assert.ok(measuredPutbackChoice(p)>0&&measuredPutbackChoice(p)<1);cards++;}
}
console.log(JSON.stringify({cards,syntheticMean70:true,previousInputUnchanged:true}));

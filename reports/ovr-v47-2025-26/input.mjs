import assert from 'node:assert/strict';
import {ovrInput as previousInput} from '../player-impact-v41/ovr-input.mjs';
import {loadInput} from '../player-impact-v47/input.mjs';
export async function ovrInput(season='2025-26'){
 const x=structuredClone(await previousInput(season)),y=await loadInput(season);
 const fields=['shootingMeasurement','freshDefenseMeasurement','defensiveChoiceMeasurement','fineDefenseMeasurement','freeThrowAccuracyMeasurement'];
 const map=new Map();
 for(const t of y.league.teams)for(const p of t.roster){
  if(map.has(p.playerId))for(const k of fields)assert.deepEqual(map.get(p.playerId)[k],p[k]);
  map.set(p.playerId,p);
 }
 for(const p of [...x.players,...x.opponents.flatMap(t=>t.roster)]){
  const q=map.get(p.playerId);assert.ok(q,'Missing actual source '+p.playerId);
  for(const k of fields){assert.ok(q[k],k);p[k]=structuredClone(q[k]);}
 }
 const zones=['ra','paint','mid','corner','arc'],branches=['three','paintGivenTwo','raGivenPaint','cornerGivenThree'];
 for(let slot=0;slot<5;slot++){
  const p=x.profiles[slot],pool=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence);
  const total=pool.reduce((s,q)=>s+q.observed.MIN,0);assert.ok(total>0);
  const avg=fn=>pool.reduce((s,q)=>s+q.observed.MIN*fn(q),0)/total;
  const collect=(key,keys)=>Object.fromEntries(keys.map(z=>[z,avg(q=>q.fineDefenseMeasurement[key][z])]));
  p.freshDefenseMeasurement.logits={long:0,mid:0,short:0};
  p.fineDefenseMeasurement={makeShooter:collect('makeShooter',zones),makeDefender:collect('makeDefender',zones),choiceShooter:collect('choiceShooter',branches),choiceDefender:collect('choiceDefender',branches),contexts:{'rotation-space':Object.fromEntries(zones.map(z=>[z,avg(q=>q.fineDefenseMeasurement.contexts['rotation-space'][z])]))}};
  delete p.freeThrowAccuracyMeasurement;
 }
 assert.equal(x.players.length,582);assert.equal(x.opponents.length,30);
 return x;
}

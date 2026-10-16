import {controlledInput} from '../player-impact-v38/input.mjs';
import {attachBlockMeasurements} from './input.mjs';
export async function ovrInput(season='2025-26'){
 const x=await controlledInput('v30',season);attachBlockMeasurements([...x.players,...x.opponents.flatMap(t=>t.roster)],season);
 for(let slot=0;slot<5;slot++){
  const p=x.profiles[slot],pool=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),minutes=pool.reduce((s,q)=>s+q.observed.MIN,0);
  if(!(minutes>0))throw Error('Missing natural-position source pool');
  const hazard=pool.reduce((s,q)=>s+q.observed.MIN*Math.exp(q.blockEventMeasurement.logHazard),0)/minutes;
  p.blockEventMeasurement={logHazard:Math.log(hazard),zoneLogBase:structuredClone(pool[0].blockEventMeasurement.zoneLogBase),sourceOnBall:p.onBall,sourceHelp:p.help,sourcePhysique:p.physique,source:'Minute-weighted arithmetic hazard pool, confident natural position. Source descriptor only; attributes and mean70 unchanged.'};
 }
 return x;
}

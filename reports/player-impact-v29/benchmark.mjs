import fs from 'node:fs';
import {workloadRotation} from '../../src/player_workload.js';
const read=f=>JSON.parse(fs.readFileSync(f));
export const source=()=>read('reports/player-impact-v29/workload-source.json');
export function workloadTeam(x, player, slot, minutes, cap, phase=0){
 const loads=x.profiles.map(()=>cap);loads[slot]=minutes;
 const team={name:'工作負荷測試隊',season:'2025-26',roster:[
  ...x.profiles.map((p,i)=>({...structuredClone(i===slot?player:p),pos:p.pos,courtPosition:p.pos,targetMinutes:loads[i],injured:false})),
  ...x.profiles.map((p,i)=>({...structuredClone(p),playerId:-2000-i,targetMinutes:48-loads[i],injured:false}))
 ]};
 return {team,schedule:workloadRotation(loads,phase)};
}
export function opponentTeam(x, opponent, cap, phase=0){
 const loads=x.profiles.map(()=>cap);
 return {team:{...opponent,roster:[...opponent.roster.map(p=>({...p,targetMinutes:cap,injured:false})),
  ...x.profiles.map((p,i)=>({...structuredClone(p),playerId:-3000-i,targetMinutes:48-cap,injured:false}))]},
  schedule:workloadRotation(loads,phase)};
}
export function options(x, seed, schedules){
 return {...x.options,quarterSeconds:720,sourcePeriods:4,maxOvertimes:0,substitutions:true,
  minuteMode:'budget',foulOut:99,sourceRotations:schedules,seed,creationPolicy:'rotation-space',contextLongScale:1,
  spaceCenter:read('reports/player-impact-v20/2025-26-synthetic-center.json').fullCenter};
}

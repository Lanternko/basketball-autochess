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
// sim 0.1.2 (R-094, E-140/F-096): defender shooting-foul beta (E-116 2025-26 fit, as in E-120) is on by default,
// with the league foul base and pace recalibrated so league fouls, possessions and points match the beta-off engine.
let foulBeta=null;
const defenderFoulBeta=()=>foulBeta??=(f=>Object.fromEntries(f.playerIds.map((id,i)=>[id,f.defenderEffects[i]])))(read('reports/E116-fouls-matchup/fullfit-f-2025-26.json'));
export function options(x, seed, schedules){
 return {...x.options,pace:(x.options?.pace??1)*0.99875,defenderFoulBeta:defenderFoulBeta(),foulBaseShift:-0.03125,
  quarterSeconds:720,sourcePeriods:4,maxOvertimes:0,substitutions:true,
  minuteMode:'budget',foulOut:99,sourceRotations:schedules,seed,creationPolicy:'rotation-space',contextLongScale:1,
  spaceCenter:read('reports/player-impact-v20/2025-26-synthetic-center.json').fullCenter};
}

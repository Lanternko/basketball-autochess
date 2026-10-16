import {ovrInput as previousInput} from '../player-impact-v25/ovr-input.mjs';
import {attachIntensity,contactOptions} from './input.mjs';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=structuredClone(await previousInput(season));attachIntensity(x.players,season);for(const t of x.opponents)attachIntensity(t.roster,season);
 Object.assign(x.options,contactOptions(season));
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),M=ps.reduce((s,q)=>s+q.contactIntensityMeasurement.sourceMinutes,0);
  if(!M)throw Error('Missing positional intensity exposure');
  const mean=key=>ps.reduce((s,q)=>s+q.contactIntensityMeasurement.sourceMinutes*q.contactIntensityMeasurement[key],0)/M;
  return {...p,contactIntensityMeasurement:{sourceMinutes:M,contactRate:mean('contactRate'),terminalRate:mean('terminalRate'),source:'Confident natural-position source-minute weighted mean token intensities. Attribute arithmetic mean70 unchanged; source production/style only.'}};
 });cache.set(season,x);return x;
}

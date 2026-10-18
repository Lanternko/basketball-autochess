import {ovrInput as previousInput} from '../player-impact-v24/ovr-input.mjs';
import {attachContact,ordinaryContactReference} from './input.mjs';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=structuredClone(await previousInput(season));attachContact(x.players,season);for(const t of x.opponents)attachContact(t.roster,season);
 x.options.nonShootingFoulRate=ordinaryContactReference(season).rate;
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),n=ps.reduce((s,q)=>s+q.contactRecipientMeasurement.sourceContactOpportunities,0);
  if(!n)throw Error('Missing positional contact-victim source opportunities');
  const logStrength=ps.reduce((s,q)=>s+q.contactRecipientMeasurement.sourceContactOpportunities*q.contactRecipientMeasurement.logStrength,0)/n;
  return {...p,contactRecipientMeasurement:{sourceContactOpportunities:n,logStrength,strength:Math.exp(logStrength),source:'Confident natural-position source-opportunity weighted geometric strength, same prior/gauge. Attributes stay arithmetic mean70; only conditional contact recipient style.'}};
 });cache.set(season,x);return x;
}

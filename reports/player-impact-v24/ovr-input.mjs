import {ovrInput as previousInput} from '../player-impact-v23/ovr-input.mjs';
import {attachDreb} from './input.mjs';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=structuredClone(await previousInput(season));attachDreb(x.players,season);for(const t of x.opponents)attachDreb(t.roster,season);
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),n=ps.reduce((s,q)=>s+q.drebRecipientMeasurement.sourceTeamWonOpportunities,0);
  if(!n)throw Error('Missing positional DREB source pool');
  const logStrength=ps.reduce((s,q)=>s+q.drebRecipientMeasurement.sourceTeamWonOpportunities*q.drebRecipientMeasurement.logStrength,0)/n;
  return {...p,drebRecipientMeasurement:{sourceTeamWonOpportunities:n,logStrength,strength:Math.exp(logStrength),source:'Confident natural-position, source-opportunity weighted geometric strength; same prior-selected gauge as actual cards. Recipient allocation only; no team winning probability or mean70 attribute change.'}};
 });
 cache.set(season,x);return x;
}

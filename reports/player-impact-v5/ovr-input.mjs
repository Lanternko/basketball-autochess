import fs from 'node:fs';
import {positionalInputs} from '../ovr-2025-26-positional/protocol.mjs';
import {loadInput} from './input.mjs';
export function ovrInput(){
 const x=positionalInputs(),b=loadInput('2025-26'),cards=new Map();
 for(const t of b.league.teams)for(const p of t.roster)cards.set(p.playerId,p);
 const extra=p=>({...p,shotProfile:cards.get(p.playerId).shotProfile,shotCreationMeasurement:cards.get(p.playerId).shotCreationMeasurement,boxAllocationMeasurement:cards.get(p.playerId).boxAllocationMeasurement,opportunityMeasurement:cards.get(p.playerId).opportunityMeasurement});
 x.players=x.players.map(extra);x.opponents=x.opponents.map(t=>({...t,roster:t.roster.map(extra)}));
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),minutes=ps.reduce((a,p)=>a+p.observed.MIN,0);
  const avg=(field,key)=>ps.reduce((a,p)=>a+p.observed.MIN*p[field][key],0)/minutes;
  const priorRates=ps[0].boxAllocationMeasurement.priorRates;
  return {...p,shotCreationMeasurement:Object.fromEntries(['selfMakesPerMinute','assistedMakesPerMinute','assistsPerMinute'].map(k=>[k,avg('shotCreationMeasurement',k)])),
   opportunityMeasurement:{...Object.fromEntries(["selfOpportunityRate","receiveOpportunityRate","passOpportunityRate","passStolenPerMinute","contestExposurePerMinute"].map(k=>[k,avg("opportunityMeasurement",k)])),freshZone:Object.fromEntries(["long","mid","short"].map(z=>[z,ps.reduce((a,q)=>a+q.observed.MIN*q.opportunityMeasurement.freshZone[z],0)/minutes]))},boxAllocationMeasurement:{minutes:1e9,dreb:1e9*avg('boxAllocationMeasurement','dreb')/avg('boxAllocationMeasurement','minutes'),blk:1e9*avg('boxAllocationMeasurement','blk')/avg('boxAllocationMeasurement','minutes'),priorRates}};
 });
 return x;
}

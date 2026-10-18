import {ovrInput as previousInput} from '../player-impact-v20/ovr-input.mjs';
import {attachTerminalRisk,riskSource} from './input.mjs';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=await previousInput(season),source=riskSource(season),ref=source.reference;
 attachTerminalRisk(x.players,season);for(const t of x.opponents)attachTerminalRisk(t.roster,season);
 x.options.measuredTouchTurnovers=true;
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence);
  const totals=ps.reduce((s,q)=>{for(const k of Object.keys(s))s[k]+=q.terminalRiskMeasurement[k];return s;},{opportunities:0,dead:0,live:0,pressureWeightedOpportunities:0});
  return {...p,terminalRiskMeasurement:{...totals,deadProbability:(totals.dead+ref.kappaEvents*ref.deadProbability)/(totals.opportunities+ref.kappaEvents),neutralLiveProbability:(totals.live+ref.kappaEvents*ref.neutralLiveProbability)/(totals.pressureWeightedOpportunities+ref.kappaEvents),source:'Confident natural-position pooled terminal event counts with same common prior; synthetic attributes remain arithmetic mean70.'}};
 });
 cache.set(season,x);return x;
}

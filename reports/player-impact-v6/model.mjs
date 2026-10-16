import {balancedReceivers} from '../player-impact-v4/model.mjs';
export {balancedReceivers};
export {contestHelp} from '../player-impact-v3/model.mjs';
export {freshZoneProbability,observedFoulInputs} from '../player-impact-v5/model.mjs';
const cache=new Map();
export function opportunityPlan(lineup,probability,pressure=1){
 const key=lineup.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');
 let plan=cache.get(key);
 if(!plan){
  const ms=lineup.map(p=>p.opportunityMeasurement),demand=ms.map(m=>m.receiveOpportunityRate),rs=demand.reduce((s,v)=>s+v,0),supply=ms.reduce((s,m)=>s+m.passOpportunityRate,0),scale=supply?Math.min(1,rs/supply):0;
  const matrix=balancedReceivers(ms.map(m=>m.passOpportunityRate*scale),demand),incoming=ms.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
  plan=ms.map((m,i)=>({receivers:matrix[i],pass:matrix[i].reduce((s,v)=>s+v,0),self:Math.max(0,m.terminalOpportunityRate-incoming[i])}));
  if(cache.size>4096)cache.clear();cache.set(key,plan);
 }
 const rows=plan.map((p,i)=>{const lost=lineup[i].opportunityMeasurement.passStolenPerMinute*pressure,pass=p.pass+lost,weight=p.self+pass;
  return {weight,shoot:weight?p.self/weight:1,intercept:pass?Math.min(.95,lost/pass):0,receivers:p.receivers};});
 return {weights:rows.map(r=>Math.max(.0001,r.weight)),rows};
}

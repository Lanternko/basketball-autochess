import {balancedReceivers} from '../player-impact-v4/model.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {spaceProbability} from '../player-impact-v7/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
export function cappedAllocation(weights,caps,total){
 if(total<0||caps.some(x=>!Number.isFinite(x)||x<0)||weights.some(x=>!Number.isFinite(x)||x<0)||caps.reduce((s,x)=>s+x,0)+1e-9<total)throw Error('Infeasible creation allocation');
 let remaining=total;const out=weights.map(()=>0),active=new Set(weights.map((_,i)=>i));
 while(remaining>1e-12&&active.size){
  const den=[...active].reduce((s,i)=>s+weights[i],0),saturated=[];
  for(const i of active){const q=remaining*(den?weights[i]/den:1/active.size);if(q>caps[i]-out[i]+1e-12)saturated.push(i);}
  if(!saturated.length){for(const i of active)out[i]+=remaining*(den?weights[i]/den:1/active.size);remaining=0;break;}
  for(const i of saturated){const v=caps[i]-out[i];out[i]+=v;remaining-=v;active.delete(i);}
 }
 if(remaining>1e-8)throw Error('Creation capacity left unallocated');return out;
}
export function supplyFlow(lineup){
 const ms=lineup.map(p=>p.opportunityMeasurement),terminal=ms.map(m=>m.terminalOpportunityRate),total=terminal.reduce((s,x)=>s+x,0);
 if(!(total>0)||ms.some(m=>['terminalOpportunityRate','receiveOpportunityRate','passOpportunityRate','passStolenPerMinute'].some(k=>!Number.isFinite(m[k])||m[k]<0)))throw Error('Invalid source role measurement');
 // Successful creation supply is no longer silently scaled down to the old
 // assisted-make share. Receivers retain their measured relative propensity,
 // with hard terminal caps and a zero diagonal. No extra FGA can be invented.
 let rows=ms.map((m,i)=>Math.min(m.passOpportunityRate,total-terminal[i]));
 const raw=rows.reduce((s,x)=>s+x,0),scale=raw>total?total/raw:1;rows=rows.map(x=>x*scale);
 const supply=rows.reduce((s,x)=>s+x,0),caps=terminal.map((x,i)=>Math.min(x,Math.max(0,supply-rows[i])));
 const cols=cappedAllocation(ms.map(m=>m.receiveOpportunityRate),caps,supply),matrix=balancedReceivers(rows,cols);
 const actualRows=matrix.map(r=>r.reduce((s,x)=>s+x,0)),incoming=ms.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
 for(let i=0;i<ms.length;i++)if(Math.abs(actualRows[i]-rows[i])>1e-6||incoming[i]>terminal[i]+1e-6)throw Error('Creation flow failed conservation');
 return {matrix,rows:actualRows,incoming,self:terminal.map((x,i)=>Math.max(0,x-incoming[i])),terminal};
}
const cache=new Map();
export function opportunityPlan(lineup,probability,pressure=1,policy='supply-creation'){
 const ls=policy==='supply-flow'?lineup:elasticLineup(lineup,'elastic-creation');
 const key=ls.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');let flow=cache.get(key);
 if(!flow){flow=supplyFlow(ls);if(cache.size>4096)cache.clear();cache.set(key,flow);}
 const rows=ls.map((p,i)=>{const lost=p.opportunityMeasurement.passStolenPerMinute*pressure,pass=flow.rows[i]+lost,weight=flow.self[i]+pass;
  return {weight,shoot:weight?flow.self[i]/weight:1,intercept:pass?Math.min(.95,lost/pass):0,receivers:flow.matrix[i]};});
 return {weights:rows.map(r=>Math.max(.0001,r.weight)),rows};
}

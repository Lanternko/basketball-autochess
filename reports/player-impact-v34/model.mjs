// Hypothesis: receive allocation may not consume a frozen source-self anchor.
// This is a descriptive role constraint, not a validated physical lower bound.
import {creationTransport} from '../../src/opportunity_transport.js';
import {cappedAllocation,supplyFlow} from '../player-impact-v11/model.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';

export function anchoredFlow(lineup,reserve=1){
 if(!Number.isFinite(reserve)||reserve<0||reserve>1)throw Error('Invalid source-self reserve');
 if(reserve===0)return supplyFlow(lineup);
 const ms=lineup.map(p=>p.opportunityMeasurement),terminal=ms.map(m=>m.terminalOpportunityRate);
 for(const m of ms)if(['terminalOpportunityRate','selfOpportunityRate','receiveOpportunityRate','passOpportunityRate','passStolenPerMinute'].some(k=>!Number.isFinite(m[k])||m[k]<0)||Math.abs(m.selfOpportunityRate+m.receiveOpportunityRate-m.terminalOpportunityRate)>1e-8)throw Error('Invalid source role accounting');
 const floor=ms.map(m=>reserve*m.selfOpportunityRate),capacity=terminal.map((t,i)=>Math.max(0,t-floor[i])),totalCapacity=capacity.reduce((s,v)=>s+v,0);
 // Each passer can only feed the other four receivers. If collective supply
 // exceeds their remaining capacity, reduce pass supply proportionally.
 let rows=ms.map((m,i)=>Math.min(m.passOpportunityRate,Math.max(0,totalCapacity-capacity[i])));
 const raw=rows.reduce((s,v)=>s+v,0),scale=raw>totalCapacity?totalCapacity/raw:1;rows=rows.map(v=>v*scale);
 const supply=rows.reduce((s,v)=>s+v,0),caps=capacity.map((v,i)=>Math.min(v,Math.max(0,supply-rows[i])));
 const cols=cappedAllocation(ms.map(m=>m.receiveOpportunityRate),caps,supply),matrix=creationTransport(rows,cols);
 const actualRows=matrix.map(r=>r.reduce((s,v)=>s+v,0)),incoming=ms.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
 const self=terminal.map((v,i)=>Math.max(0,v-incoming[i]));
 for(let i=0;i<ms.length;i++)if(Math.abs(actualRows[i]-rows[i])>1e-8||self[i]+1e-8<floor[i]||incoming[i]>capacity[i]+1e-8)throw Error('Source self/receive flow failed conservation');
 return {matrix,rows:actualRows,incoming,self,terminal,floor};
}
const cache=new Map();
export function opportunityPlan(lineup,probability,pressure=1,policy='rotation-space'){
 if(!['rotation-space','supply-creation'].includes(policy))throw Error('Unknown joint-source policy');
 const ls=elasticLineup(lineup,'elastic-creation');
 const key=ls.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');let flow=cache.get(key);
 if(!flow){flow=anchoredFlow(ls);if(cache.size>4096)cache.clear();cache.set(key,flow);}
 const rows=ls.map((p,i)=>{
  const lost=p.opportunityMeasurement.passStolenPerMinute*pressure,pass=flow.rows[i]+lost,weight=flow.self[i]+pass;
  return {weight,shoot:weight?flow.self[i]/weight:1,intercept:pass?Math.min(.95,lost/pass):0,receivers:flow.matrix[i]};
 });
 if(!rows.some(r=>r.weight>0))throw Error('Source lineup has no opportunities');
 return {weights:rows.map(r=>r.weight),rows};
}

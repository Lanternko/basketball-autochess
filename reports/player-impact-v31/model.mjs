import {supplyFlow} from '../player-impact-v11/model.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
import {sourceSupportedSelf} from '../../src/source_self_opportunities.js';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
const cache=new Map();
export function supportedFlow(lineup){
 const old=supplyFlow(lineup),self=sourceSupportedSelf(old,lineup.map(p=>p.opportunityMeasurement));
 return {...old,self,nominalSelf:old.self,unusedTerminal:old.self.map((v,i)=>v-self[i])};
}
export function opportunityPlan(lineup,probability,pressure=1,policy='rotation-space'){
 if(!['rotation-space','supply-creation'].includes(policy))throw Error('Unknown source-self policy');
 const ls=elasticLineup(lineup,'elastic-creation');
 const key=ls.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');
 let flow=cache.get(key);
 if(!flow){flow=supportedFlow(ls);if(cache.size>4096)cache.clear();cache.set(key,flow);}
 const rows=ls.map((p,i)=>{
  const lost=p.opportunityMeasurement.passStolenPerMinute*pressure,pass=flow.rows[i]+lost,weight=flow.self[i]+pass;
  return {weight,shoot:weight?flow.self[i]/weight:1,intercept:pass?Math.min(.95,lost/pass):0,receivers:flow.matrix[i]};
 });
 if(!rows.some(r=>r.weight>0))throw Error('Source lineup has no supported self/pass opportunities');
 return {weights:rows.map(r=>r.weight),rows};
}

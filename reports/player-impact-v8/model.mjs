import fs from 'node:fs';
import {opportunityPlan as previousPlan} from '../player-impact-v6/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {spaceProbability} from '../player-impact-v7/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
export const alpha=JSON.parse(fs.readFileSync('reports/player-impact-v8/usage-fit.json')).alpha;
export const beta=JSON.parse(fs.readFileSync('reports/player-impact-v8/assist-fit.json')).beta;
export function elasticLineup(lineup,policy){
 const keys=['terminalOpportunityRate','receiveOpportunityRate','passOpportunityRate','passStolenPerMinute'];
 for(const p of lineup)for(const k of keys)if(!Number.isFinite(p.opportunityMeasurement?.[k])||p.opportunityMeasurement[k]<0)throw Error('Missing finite role input: '+k);
 const ms=lineup.map(p=>p.opportunityMeasurement),term=ms.map(m=>m.terminalOpportunityRate),pass=ms.map(m=>m.passOpportunityRate),b=policy==='elastic-flow'?1:beta;
 const total=term.reduce((s,v)=>s+v,0),pt=pass.reduce((s,v)=>s+v,0),tp=term.map(v=>v**alpha),pp=pass.map(v=>v**b),td=tp.reduce((s,v)=>s+v,0),pd=pp.reduce((s,v)=>s+v,0);
 if(!td||!pd)throw Error('Missing positive lineup demand');
 return lineup.map((p,i)=>{const m=ms[i],t=tp[i]/td*total,receive=m.terminalOpportunityRate?m.receiveOpportunityRate/m.terminalOpportunityRate*t:0;
  return {...p,opportunityMeasurement:{...m,terminalOpportunityRate:t,selfOpportunityRate:t-receive,receiveOpportunityRate:receive,passOpportunityRate:pp[i]/pd*pt}};});
}
export function opportunityPlan(lineup,probability,pressure=1,policy='elastic-creation'){
 return previousPlan(elasticLineup(lineup,policy),probability,pressure);
}

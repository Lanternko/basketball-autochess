import assert from 'node:assert/strict';
import {elasticLineup,opportunityPlan,alpha,beta} from '../reports/player-impact-v8/model.mjs';
const lineup=[.8,.5,.4,.3,.2].map((v,i)=>({playerId:i,opportunityMeasurement:{terminalOpportunityRate:v,selfOpportunityRate:v*.4,receiveOpportunityRate:v*.6,passOpportunityRate:.1*(5-i),passStolenPerMinute:.02}})),before=structuredClone(lineup),changed=elasticLineup(lineup,'elastic-creation'),plan=opportunityPlan(lineup,null,1,'elastic-creation');
assert.deepEqual(lineup,before);
assert.ok(Math.abs(changed.reduce((s,p)=>s+p.opportunityMeasurement.terminalOpportunityRate,0)-2.2)<1e-12);
assert.ok(changed[0].opportunityMeasurement.terminalOpportunityRate>.8);
assert.ok(changed[4].opportunityMeasurement.terminalOpportunityRate<.2);
for(let j=0;j<5;j++){
 let expected=plan.rows[j].weight*plan.rows[j].shoot;
 for(let i=0;i<5;i++){const r=plan.rows[i],total=r.receivers.reduce((s,v)=>s+v,0);expected+=total?r.weight*(1-r.shoot)*(1-r.intercept)*r.receivers[j]/total:0;}
 assert.ok(Math.abs(expected-changed[j].opportunityMeasurement.terminalOpportunityRate)<1e-8,'Observed terminal demand must survive the creator/receiver process');
}
assert.throws(()=>opportunityPlan([{playerId:1}],null),/Missing finite/);
console.log(JSON.stringify({alpha,beta,terminalDemandConserved:true,inputsUnchanged:true}));

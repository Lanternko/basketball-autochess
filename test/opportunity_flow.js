import assert from 'node:assert/strict';
import {balancedReceivers,opportunityPlan} from '../reports/player-impact-v4/model.mjs';
const rows=[8,3,2,1,2],cols=[3,4,5,2,2],matrix=balancedReceivers(rows,cols);
for(let i=0;i<5;i++){
 assert.equal(matrix[i][i],0);
 assert.ok(Math.abs(matrix[i].reduce((s,v)=>s+v,0)-rows[i])<1e-6);
 assert.ok(Math.abs(matrix.reduce((s,r)=>s+r[i],0)-cols[i])<1e-6);
}
const lineup=rows.map((v,i)=>({playerId:i,opportunityMeasurement:{selfOpportunityRate:1+i,passOpportunityRate:v,receiveOpportunityRate:cols[i],passStolenPerMinute:.1}}));
// Changing counterfactual shooting ability cannot silently cancel its benefit
// by inversely changing source-context usage weights.
assert.deepEqual(opportunityPlan(lineup,()=>.1),opportunityPlan(lineup,()=>.9));
const plan=opportunityPlan(lineup,()=>.5);
for(let i=0;i<5;i++)assert.ok(Math.abs(plan.rows[i].weight*(1-plan.rows[i].shoot)*(1-plan.rows[i].intercept)-rows[i])<1e-8);
console.log('opportunity flow: passed balanced demands, no self-pass, fixed source usage, loss decomposition');

import assert from 'node:assert/strict';
import {sourceSupportedSelf} from '../src/source_self_opportunities.js';
import {supplyFlow} from '../reports/player-impact-v11/model.mjs';
import {supportedFlow,opportunityPlan} from '../reports/player-impact-v31/model.mjs';
import {ovrInput} from '../reports/player-impact-v30/ovr-input.mjs';
import {elasticLineup} from '../reports/player-impact-v8/model.mjs';
const m={terminalOpportunityRate:1,receiveOpportunityRate:.8,selfOpportunityRate:.2};
assert.deepEqual(sourceSupportedSelf({self:[.8],incoming:[.2]},[m]),[.2]);
assert.ok(Math.abs(sourceSupportedSelf({self:[.1],incoming:[.9]},[m])[0]-.1)<1e-12);
assert.equal(sourceSupportedSelf({self:[1],incoming:[0]},[{...m,selfOpportunityRate:0,receiveOpportunityRate:1}])[0],0);
assert.throws(()=>sourceSupportedSelf({self:[1],incoming:[0]},[{...m,selfOpportunityRate:-1}]));
const x=await ovrInput();let checked=0;
for(const p of x.players){
 const slot=x.roleMap.get(p.playerId).slot,ls=elasticLineup(x.profiles.map((q,i)=>i===slot?p:q),'elastic-creation');
 const frozen=JSON.stringify(ls),old=supplyFlow(ls),next=supportedFlow(ls),plan=opportunityPlan(x.profiles.map((q,i)=>i===slot?p:q),null,1);
 assert.equal(JSON.stringify(ls),frozen);
 assert.deepEqual(next.matrix,old.matrix);assert.deepEqual(next.rows,old.rows);assert.deepEqual(next.incoming,old.incoming);
 for(let i=0;i<5;i++){
  assert.ok(next.self[i]<=old.self[i]+1e-9);
  assert.ok(next.self[i]<=ls[i].opportunityMeasurement.selfOpportunityRate+1e-9);
  assert.ok(next.self[i]+next.incoming[i]<=next.terminal[i]+1e-8);
  assert.ok(Math.abs(plan.rows[i].weight*plan.rows[i].shoot-next.self[i])<1e-8);
 }
 checked++;
}
console.log(JSON.stringify({passed:true,playerLineups:checked,noManufacturedSelfRole:true,passTransportUnchanged:true}));

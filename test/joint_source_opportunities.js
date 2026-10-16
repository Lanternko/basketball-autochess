import assert from 'node:assert/strict';
import {anchoredFlow,opportunityPlan} from '../reports/player-impact-v34/model.mjs';
import {supplyFlow} from '../reports/player-impact-v11/model.mjs';
import {elasticLineup} from '../reports/player-impact-v8/model.mjs';
import {ovrInput} from '../reports/player-impact-v30/ovr-input.mjs';
const card=(id,terminal,self,pass)=>({playerId:id,opportunityMeasurement:{terminalOpportunityRate:terminal,selfOpportunityRate:self,receiveOpportunityRate:terminal-self,passOpportunityRate:pass,passStolenPerMinute:.02}});
function check(ls,reserve=1){
 const before=JSON.stringify(ls),flow=anchoredFlow(ls,reserve);assert.equal(JSON.stringify(ls),before);
 for(let i=0;i<ls.length;i++){
  const m=ls[i].opportunityMeasurement;
  assert.ok(Math.abs(flow.self[i]+flow.incoming[i]-m.terminalOpportunityRate)<1e-8);
  assert.ok(flow.self[i]>=reserve*m.selfOpportunityRate-1e-8);
  assert.equal(flow.matrix[i][i],0);
  assert.ok(Math.abs(flow.rows[i]-flow.matrix[i].reduce((s,v)=>s+v,0))<1e-8);
  assert.ok(flow.rows[i]<=m.passOpportunityRate+1e-8);
 }
 return flow;
}
// Heavy supply formerly erases own opportunities; asymmetric capacities and a
// single active passer exercise the diagonal feasibility constraints.
for(const ls of [Array.from({length:5},(_,i)=>card(i,1,.2,8)),[card(0,1,.8,20),...Array.from({length:4},(_,i)=>card(i+1,.1,.08,0))],Array.from({length:5},(_,i)=>card(i,1,1,3)),Array.from({length:5},(_,i)=>card(i,1,.2,0))])check(ls);
assert.throws(()=>anchoredFlow([card(0,1,2,1)]));assert.throws(()=>anchoredFlow([card(0,1,.2,1)],-1));
const x=await ovrInput();let lineups=0;
for(const p of x.players){
 const slot=x.roleMap.get(p.playerId).slot,raw=x.profiles.map((q,i)=>i===slot?p:q),ls=elasticLineup(raw,'elastic-creation');
 assert.deepEqual(anchoredFlow(ls,0),supplyFlow(ls));
 for(const r of [.25,.5,.75,1])check(ls,r);
 const f=check(ls),plan=opportunityPlan(raw,null,1);
 for(let i=0;i<5;i++)assert.ok(Math.abs(plan.rows[i].weight*plan.rows[i].shoot-f.self[i])<1e-8);
 lineups++;
}
console.log(JSON.stringify({passed:true,naturalPositionMean70Lineups:lineups,nonMutation:true,terminalConserved:true,sourceSelfReserved:true,noSelfAssist:true,zeroReserveExactlyV11:true}));

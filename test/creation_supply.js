import assert from 'node:assert/strict';
import {supplyFlow,cappedAllocation} from '../reports/player-impact-v11/model.mjs';
const ls=Array.from({length:5},(_,i)=>({playerId:i,opportunityMeasurement:{terminalOpportunityRate:.5,receiveOpportunityRate:.25,passOpportunityRate:.2,passStolenPerMinute:.01}}));
const a=supplyFlow(ls),better=structuredClone(ls);better[0].opportunityMeasurement.passOpportunityRate=.7;const b=supplyFlow(better);
assert.ok(b.rows.reduce((s,x)=>s+x,0)>a.rows.reduce((s,x)=>s+x,0),'Better creation must increase completed creation, not only redistribute credit');
for(const q of [a,b])for(let i=0;i<5;i++){assert.equal(q.matrix[i][i],0);assert.ok(Math.abs(q.self[i]+q.incoming[i]-.5)<1e-6);}
assert.deepEqual(cappedAllocation([1,1,1],[.1,.5,.5],1),[.1,.45,.45]);
for(let seed=0;seed<4000;seed++){
 const random=(()=>{let s=seed+1;return()=>((s=Math.imul(s,1664525)+1013904223>>>0)/2**32);})();
 const team=ls.map((p,i)=>({...p,opportunityMeasurement:{...p.opportunityMeasurement,terminalOpportunityRate:.01+random(),receiveOpportunityRate:random(),passOpportunityRate:random()*2}}));
 const q=supplyFlow(team);for(let i=0;i<5;i++){assert.equal(q.matrix[i][i],0);assert.ok(Math.abs(q.self[i]+q.incoming[i]-q.terminal[i])<1e-6);}
}
assert.equal(ls[0].opportunityMeasurement.passOpportunityRate,.2);console.log('creation supply increases opportunities, terminal conservation, no self assists and 4000 heterogeneous lineups passed');

import assert from 'node:assert/strict';
import fs from 'node:fs';
import {priorFlow} from '../reports/player-impact-v36/model.mjs';
import {elasticLineup} from '../reports/player-impact-v8/model.mjs';
import {ovrInput} from '../reports/player-impact-v30/ovr-input.mjs';
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-8*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
const x=await ovrInput();let checked=0;
for(const p of x.players){
 const slot=x.roleMap.get(p.playerId).slot,raw=x.profiles.map((q,i)=>i===slot?p:q),before=JSON.stringify(raw),ls=elasticLineup(raw,'elastic-creation');
 for(const k of [.01,1,100]){
  const f=priorFlow(ls,k),perm=[4,1,3,0,2],g=priorFlow(perm.map(i=>ls[i]),k);
  const scaled=priorFlow(ls.map(p=>({...p,opportunityMeasurement:Object.fromEntries(Object.entries(p.opportunityMeasurement).map(([a,b])=>[a,typeof b==='number'?b*7:b]))})),k);
  for(let i=0;i<5;i++){
   assert.ok(f.self[i]>0&&f.self[i]<f.terminal[i]);assert.equal(f.matrix[i][i],0);
   near(f.self[i]+f.incoming[i],f.terminal[i]);near(f.rows[i],f.matrix[i].reduce((s,v)=>s+v,0));
   for(let j=0;j<5;j++){assert.ok(f.joint[i][j]>0);near(g.joint[i][j],f.joint[perm[i]][perm[j]]);near(scaled.joint[i][j],7*f.joint[i][j]);}
  }
  checked++;
 }
 const low=priorFlow(ls,.01),high=priorFlow(ls,100);
 for(let i=0;i<5;i++)assert.ok(high.self[i]>low.self[i]);
 assert.equal(JSON.stringify(raw),before);
}
const simple=Array.from({length:5},(_,playerId)=>({playerId,opportunityMeasurement:{terminalOpportunityRate:1,selfOpportunityRate:.2,receiveOpportunityRate:.8,passOpportunityRate:.8,passStolenPerMinute:0}}));
const f=priorFlow(simple);
for(let i=0;i<5;i++)for(let j=0;j<5;j++)near(f.joint[i][j],.2);
console.log(JSON.stringify({passed:true,naturalPositionPlayers:x.players.length,checkedLineups:checked,positiveSelfAndPass:true,terminalConservation:true,scaleAndPermutationEquivariance:true,sourceCardsUnmutated:true}));

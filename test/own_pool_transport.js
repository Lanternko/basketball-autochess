import assert from 'node:assert/strict';
import {sourceFlow,opportunityPlan} from '../reports/player-impact-v37/model.mjs';
import {elasticLineup} from '../reports/player-impact-v8/model.mjs';
import {ownPoolFlow} from '../reports/player-impact-diagnostics/pass-row-feasibility-v36/prototype.mjs';
import {priorFlow} from '../reports/player-impact-v36/model.mjs';
import {ovrInput} from '../reports/player-impact-v30/ovr-input.mjs';
const card=(id,t,s,pass)=>({playerId:id,opportunityMeasurement:{terminalOpportunityRate:t,selfOpportunityRate:s,receiveOpportunityRate:t-s,passOpportunityRate:pass,passStolenPerMinute:.02}});
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
function check(ls){
 const before=JSON.stringify(ls),f=sourceFlow(ls);assert.equal(JSON.stringify(ls),before);
 const ref=f.branch==='fixed-pass-rows'?ownPoolFlow(ls):priorFlow(ls,1);
 for(let i=0;i<5;i++){
  assert.ok(f.self[i]>0&&f.rows[i]>0);assert.equal(f.matrix[i][i],0);
  close(f.self[i]+f.incoming[i],f.terminal[i]);close(f.self[i],ref.self[i]);
  for(let j=0;j<5;j++)close(f.matrix[i][j],ref.matrix[i][j]);
  if(f.branch==='fixed-pass-rows')close(f.rows[i],f.old.rows[i]);
 }
 const permutation=[4,2,0,3,1],g=sourceFlow(permutation.map(i=>ls[i]));assert.equal(g.branch,f.branch);
 const scaled=sourceFlow(ls.map(p=>({...p,opportunityMeasurement:Object.fromEntries(Object.entries(p.opportunityMeasurement).map(([k,v])=>[k,v*3]))})));
 for(let i=0;i<5;i++){close(scaled.self[i],3*f.self[i]);close(g.self[i],f.self[permutation[i]]);for(let j=0;j<5;j++)close(g.matrix[i][j],f.matrix[permutation[i]][permutation[j]]);}
 return f;
}
const symmetric=Array.from({length:5},(_,i)=>card(i,1,.2,.8)),a=check(symmetric);
assert.equal(a.branch,'fixed-pass-rows');for(let i=0;i<5;i++){close(a.self[i],.2);close(a.rows[i],.8);}
const saturated=check(symmetric.map(p=>({...p,opportunityMeasurement:{...p.opportunityMeasurement,passOpportunityRate:2}})));
assert.equal(saturated.branch,'relaxed-source-columns');assert.ok(saturated.rows.some((v,i)=>Math.abs(v-saturated.old.rows[i])>1e-5));
assert.throws(()=>sourceFlow(symmetric.slice(1)));assert.throws(()=>sourceFlow([card(0,1,1,.8),...symmetric.slice(1)]));
const x=await ovrInput();let count=0;
for(const p of x.players){const slot=x.roleMap.get(p.playerId).slot,raw=x.profiles.map((q,i)=>i===slot?p:q),f=check(elasticLineup(raw,'elastic-creation')),plan=opportunityPlan(raw,null,1);assert.equal(f.branch,'fixed-pass-rows');for(let i=0;i<5;i++)close(plan.rows[i].weight*plan.rows[i].shoot,f.self[i]);count++;}
console.log(JSON.stringify({passed:true,naturalPositionMean70Lineups:count,bothBranches:true,strictRowsConserved:true,terminalConserved:true,positiveOwnSupport:true,noSelfAssist:true,permutation:true,homogeneity:true,noMutation:true}));

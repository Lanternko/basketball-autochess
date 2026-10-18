import assert from 'node:assert/strict';
import {balanceKernel,jointFlow,opportunityPlan} from '../reports/player-impact-v35/model.mjs';
import {elasticLineup} from '../reports/player-impact-v8/model.mjs';
import {ovrInput} from '../reports/player-impact-v30/ovr-input.mjs';
const card=(id,t,s,pass)=>({playerId:id,opportunityMeasurement:{terminalOpportunityRate:t,selfOpportunityRate:s,receiveOpportunityRate:t-s,passOpportunityRate:pass,passStolenPerMinute:.02}});
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
function check(ls){
 const before=JSON.stringify(ls),f=jointFlow(ls);assert.equal(JSON.stringify(ls),before);
 for(let i=0;i<5;i++){
  assert.ok(f.self[i]>0&&f.rows[i]>0&&f.incoming[i]>0);assert.equal(f.matrix[i][i],0);
  close(f.self[i]+f.incoming[i],f.terminal[i]);close(f.self[i]+f.rows[i],f.creator[i]);
  close(f.rows[i],f.matrix[i].reduce((s,v)=>s+v,0));
 }
 // Multiplicative row/column balancing preserves all 2x2 cross-ratios of prior.
 for(let i=0;i<4;i++)for(let j=0;j<4;j++){
  const odds=a=>Math.log(a[i][j])+Math.log(a[i+1][j+1])-Math.log(a[i][j+1])-Math.log(a[i+1][j]);
  close(odds(f.joint),odds(f.kernel));
 }
 return f;
}
const symmetric=Array.from({length:5},(_,i)=>card(i,1,.2,.8)),f=check(symmetric);
for(let i=0;i<5;i++){close(f.self[i],.2);close(f.rows[i],.8);for(let j=0;j<5;j++)close(f.joint[i][j],.2);}
assert.throws(()=>balanceKernel([[0]],[1],[1]));assert.throws(()=>jointFlow([card(1,1,1,.8),...symmetric.slice(1)]));
const x=await ovrInput();let lineups=0,below=0,above=0;
for(const p of x.players){
 const slot=x.roleMap.get(p.playerId).slot,raw=x.profiles.map((q,i)=>i===slot?p:q),ls=elasticLineup(raw,'elastic-creation'),f=check(ls),plan=opportunityPlan(raw,null,1);
 const permutation=[4,2,0,3,1],g=jointFlow(permutation.map(i=>ls[i]));
 const scaled=jointFlow(ls.map(p=>({...p,opportunityMeasurement:Object.fromEntries(Object.entries(p.opportunityMeasurement).map(([k,v])=>[k,['terminalOpportunityRate','selfOpportunityRate','receiveOpportunityRate','passOpportunityRate','passStolenPerMinute'].includes(k)?v*3:v]))})));
 for(let i=0;i<5;i++){
  close(plan.rows[i].weight*plan.rows[i].shoot,f.self[i]);close(scaled.self[i],3*f.self[i]);
  for(let j=0;j<5;j++)close(g.joint[i][j],f.joint[permutation[i]][permutation[j]]);
  below+=f.self[i]<ls[i].opportunityMeasurement.selfOpportunityRate-1e-8;
  above+=f.self[i]>ls[i].opportunityMeasurement.selfOpportunityRate+1e-8;
 }
 lineups++;
}
assert.ok(below>0&&above>0);
console.log(JSON.stringify({passed:true,naturalPositionMean70Lineups:lineups,nonMutation:true,terminalAndCreatorConserved:true,positiveOwnSupport:true,noSelfAssist:true,permutationEquivariance:true,homogeneity:true,priorCrossRatiosPreserved:true,selfBelowSourceCases:below,selfAboveSourceCases:above}));

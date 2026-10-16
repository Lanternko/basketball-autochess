import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {ownPoolFlow} from './prototype.mjs';
import {elasticLineup} from '../../player-impact-v8/model.mjs';
import {ovrInput} from '../../player-impact-v30/ovr-input.mjs';
const root='reports/player-impact-diagnostics/pass-row-feasibility-v36',sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const x=await ovrInput(),samples=[];let maxIterations=0,maxRowDifference=0;
for(const [index,p]of x.players.entries()){
 const raw=x.profiles.map((q,i)=>i===x.roleMap.get(p.playerId).slot?p:q),before=JSON.stringify(raw),ls=elasticLineup(raw,'elastic-creation'),f=ownPoolFlow(ls),perm=[4,1,3,0,2],g=ownPoolFlow(perm.map(i=>ls[i]));
 for(let i=0;i<5;i++){
  assert.ok(f.self[i]>0);assert.equal(f.matrix[i][i],0);assert.ok(Math.abs(f.self[i]+f.incoming[i]-f.terminal[i])<1e-8);
  maxRowDifference=Math.max(maxRowDifference,Math.abs(f.rows[i]-f.old.rows[i]));
  for(let j=0;j<5;j++)assert.ok(Math.abs(g.matrix[i][j]-f.matrix[perm[i]][perm[j]])<1e-8);
  assert.ok(Math.abs(g.self[i]-f.self[perm[i]])<1e-8);
 }
 assert.equal(JSON.stringify(raw),before);maxIterations=Math.max(maxIterations,f.iterations);
 if(index%17===0)samples.push({playerId:p.playerId,prior:f.prior,joint:f.joint,rows:[...f.old.rows,f.ownPool],columns:f.terminal});
}
const m={terminalOpportunityRate:1,selfOpportunityRate:.2,receiveOpportunityRate:.8,passOpportunityRate:2,passStolenPerMinute:0},impossible=Array.from({length:5},()=>({opportunityMeasurement:m}));
assert.throws(()=>ownPoolFlow(impossible),RangeError);
const out={passed:true,mean70Players:x.players.length,positiveSelfAndUnchangedPasserRows:true,maxPasserRowAbsoluteDifference:maxRowDifference,maxIterations,nonStrictInputsExplicitlyRejected:true,runtimeChanged:false,
 scope:'Prototype allocation only, not a candidate engine, source count calibration, skill measurement, OVR or adoption. Fixed legacy passer rows, terminal columns, separate own pool; KL prior retains old pass matrix and source own shape. Non-strict source cases remain unimplemented.',samples,
 hashes:Object.fromEntries([root+'/prototype.mjs',root+'/test-prototype.mjs','reports/player-impact-v30/ovr-input.mjs'].map(f=>[f,sha(f)]))};
fs.writeFileSync(root+'/prototype-verification.json',JSON.stringify(out,null,2));console.log(JSON.stringify({...out,samples:out.samples.length,hashes:undefined}));

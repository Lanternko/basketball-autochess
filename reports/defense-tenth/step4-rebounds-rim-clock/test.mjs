import assert from 'node:assert/strict';
import fs from 'node:fs';
import {offensiveReboundClock as rule,resolveContact} from './rule.mjs';
import {experimentalGame} from './adapter.mjs';
const root='reports/defense-tenth/step4-rebounds-rim-clock',results=[];
for(const remainingTicks of [0,1,60,139,200,240]) {
  const reset=rule({remainingTicks,periodTicks:600,rimContact:true});
  assert.equal(reset.clockTicks,140);assert.equal(reset.violation,false);
  const carry=rule({remainingTicks,periodTicks:600,rimContact:false});
  assert.equal(carry.clockTicks,remainingTicks);assert.equal(carry.violation,remainingTicks===0);
  results.push({remainingTicks,reset,carry});
}
assert.equal(rule({remainingTicks:0,periodTicks:0,rimContact:false}).periodEnded,true);
assert.equal(rule({remainingTicks:0,periodTicks:0,rimContact:false}).violation,false);
assert.equal(rule({remainingTicks:20,periodTicks:600,freeThrow:true}).clockTicks,140);
assert.throws(()=>rule({remainingTicks:20,periodTicks:600,rimContact:null}),/explicit/);
assert.throws(()=>rule({remainingTicks:-1,periodTicks:600,rimContact:true}),/Invalid/);
assert.throws(()=>resolveContact(()=>null,{},()=>.5),/explicit/);
assert.equal(resolveContact(()=>false,{blocked:false},()=>.5),false);
assert.equal(resolveContact(()=>true,{blocked:true},()=>.5),true);
const game=await experimentalGame();
assert.throws(()=>game(null,null,{rimContactClock:true}),/resolver required/i);
fs.writeFileSync(root+'/unit-tests.json',JSON.stringify({cases:results,periodEndPriority:true,liveFinalFT14:true,unknownRejected:true,invalidClockRejected:true,missingResolverRejected:true,blockNotDeterministicContact:true},null,2));
console.log('Rule cases and adapter compilation passed');

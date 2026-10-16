import assert from 'node:assert/strict';
import {measuredRecipientWeights,attachBoxAllocationMeasurements} from '../src/individual_box_allocation.js';
const p=(id,MIN,DREB,BLK)=>({playerId:id,observed:{MIN,DREB,BLK}});
const league={teams:[{roster:[p(1,100,40,10),p(2,200,80,0)]},{roster:[p(1,300,60,10),p(3,0,0,0)]}]};
const info=attachBoxAllocationMeasurements(league);
assert.equal(info.uniquePlayers,3);
assert.deepEqual(league.teams[0].roster[0].boxAllocationMeasurement,league.teams[1].roster[0].boxAllocationMeasurement);
assert.equal(league.teams[0].roster[0].boxAllocationMeasurement.minutes,400);
assert.equal(league.teams[0].roster[0].boxAllocationMeasurement.blk,20);
const ls=league.teams[0].roster;
for(const key of ['dreb','blk']){
 const w=measuredRecipientWeights(ls,key),reverse=measuredRecipientWeights([...ls].reverse(),key).reverse();
 assert(Math.abs(w.reduce((a,b)=>a+b,0)-1)<1e-12);
 w.forEach((x,i)=>{assert(x>0&&x<1);assert.equal(x,reverse[i]);});
}
assert(measuredRecipientWeights(ls,'blk')[0]>measuredRecipientWeights(ls,'blk')[1]);
assert.deepEqual(measuredRecipientWeights([league.teams[1].roster[1]],'dreb'),[1]);
assert.throws(()=>measuredRecipientWeights([{boxAllocationMeasurement:{minutes:100,dreb:NaN}}],'dreb'));
assert.throws(()=>measuredRecipientWeights([], 'blk'));
assert.throws(()=>attachBoxAllocationMeasurements({teams:[{roster:[p(1,100,undefined,2)]}]}));
console.log('individual box allocation: merged stints, valid shrinkage, permutation invariance, zero exposure, invalid measurements passed');

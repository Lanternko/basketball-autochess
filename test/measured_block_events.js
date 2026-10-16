import assert from 'node:assert/strict';
import {measuredBlockProbabilities,drawMeasuredBlock,coupledBlockLabel} from '../src/measured_block_events.js';
const five=Array.from({length:5},(_,i)=>({onBall:70,help:70,physique:70,blockEventMeasurement:{logHazard:Math.log(i+1),zoneLogBase:{long:-4,mid:-3,short:-2},sourceOnBall:70,sourceHelp:70,sourcePhysique:70}}));
for(const zone of ['long','mid','short']){
 const p=measuredBlockProbabilities(five,zone),base=Math.exp(five[0].blockEventMeasurement.zoneLogBase[zone]);
 for(let i=0;i<5;i++)assert.ok(Math.abs(p.probabilities[i]-(i+1)*base/(1+15*base))<1e-14);
 assert.ok(Math.abs(p.noneProbability+ p.conditionalOnMiss-1)<1e-14);
 let left=0;for(let i=0;i<5;i++){assert.equal(drawMeasuredBlock(five,zone,left+p.probabilities[i]/2),i);left+=p.probabilities[i];}
 assert.equal(drawMeasuredBlock(five,zone,(left+1)/2),-1);
 assert.deepEqual(measuredBlockProbabilities([...five].reverse(),zone).probabilities,p.probabilities.toReversed());
 const stronger=structuredClone(five);stronger[0].help=150;stronger[0].onBall=150;
 assert.ok(measuredBlockProbabilities(stronger,zone).probabilities[0]>p.probabilities[0]);
 const shifted=structuredClone(five);for(const c of shifted){c.help=c.blockEventMeasurement.sourceHelp=130;c.onBall=c.blockEventMeasurement.sourceOnBall=130;}
 assert.deepEqual(measuredBlockProbabilities(shifted,zone),p);
}
for(const u of [0,.1,.5,.999999])for(const legacyProbability of [0,.2,1]){
 let draws=0;const i=coupledBlockLabel(five,{zone:'short',legacyProbability},()=>{draws++;return u;});
 assert.equal(draws,u<legacyProbability?2:1);assert.equal(i,drawMeasuredBlock(five,'short',u));
}
assert.throws(()=>drawMeasuredBlock(five,'short',1));assert.throws(()=>measuredBlockProbabilities(five.slice(1)));assert.throws(()=>measuredBlockProbabilities(five,'oops'));
const incomplete=structuredClone(five);delete incomplete[0].blockEventMeasurement.sourceHelp;assert.throws(()=>measuredBlockProbabilities(incomplete));
console.log('Measured block probabilities, categorical cells, anchor invariance and legacy RNG schedule verified.');

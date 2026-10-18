import assert from 'node:assert/strict';
import {sourceFreshDefense,shiftMakeLogit} from '../src/source_fresh_defense.js';
const five=Array.from({length:5},(_,i)=>({onBall:70,help:70,physique:70,defenseExposureMeasurement:{long:{rate:.2},short:{rate:.3},leagueAttemptsPerTeamMinute:{long:1,short:1.5}},freshDefenseMeasurement:{logits:{long:-.01*i,mid:.02*i,short:-.03*i},sourceOnBall:70,sourceHelp:70,sourcePhysique:70}}));
const a=sourceFreshDefense(five);assert.ok(Math.abs(a.logits.long+.1)<1e-14);assert.equal(a.sourcePhysique,70);assert.equal(a.attributeDelta.long,0);assert.equal(a.attributeDelta.mid,0);assert.equal(a.attributeDelta.short,0);assert.deepEqual(sourceFreshDefense([...five].reverse()).attributeDelta,a.attributeDelta);
const improved=structuredClone(five);improved[0].onBall=100;improved[0].help=100;const b=sourceFreshDefense(improved);assert.ok(b.attributeDelta.long<0&&b.attributeDelta.short<0);assert.deepEqual(a.logits,b.logits);
for(const p of [0,.01,.3,.5,.8,.999,1]){
 assert.equal(shiftMakeLogit(p,0),p);
 if(p>0&&p<1){assert.ok(shiftMakeLogit(p,.1)>p&&shiftMakeLogit(p,-.1)<p);assert.ok(Math.abs(shiftMakeLogit(shiftMakeLogit(p,.1),-.1)-p)<1e-14);}
 for(const shift of [-1000,1000])assert.ok(shiftMakeLogit(p,shift)>=0&&shiftMakeLogit(p,shift)<=1);
}
assert.throws(()=>shiftMakeLogit(NaN,0));assert.throws(()=>sourceFreshDefense(five.slice(1)));const partial=structuredClone(five);delete partial[0].freshDefenseMeasurement;assert.throws(()=>sourceFreshDefense(partial));
console.log('Source fresh FG defense: source-anchor zero slope, attribute direction, logistic direction/extremes and five-card validation passed.');

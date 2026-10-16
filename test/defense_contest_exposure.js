import assert from 'node:assert/strict';
import {contestDeltas,exposureDefenseProbabilities} from '../reports/player-impact-v20/model.mjs';
import {defenseProbabilities} from '../src/defense_probability.js';
import {ovrInput} from '../reports/player-impact-v20/ovr-input.mjs';

const measurement=rate=>({long:{rate},short:{rate},leagueAttemptsPerTeamMinute:{long:1,short:1}});
const card=(skill=70,rate=.2)=>({onBall:skill,help:skill,defenseExposureMeasurement:measurement(rate)});
const neutral=Array.from({length:5},()=>card());
assert.deepEqual(contestDeltas(neutral),{long:0,short:0,mid:0});
const strong=[card(90),...neutral.slice(1)],twice=[card(90,.4),...neutral.slice(1)];
for(const z of ['long','short','mid']){
 assert.ok(contestDeltas(strong)[z]<0);
 assert.ok(Math.abs(contestDeltas(twice)[z]-2*contestDeltas(strong)[z])<1e-14);
 assert.ok(Math.abs(contestDeltas(strong)[z]-contestDeltas(strong.toReversed())[z])<1e-14);
 const halfDen=structuredClone(strong);for(const p of halfDen)p.defenseExposureMeasurement.leagueAttemptsPerTeamMinute={long:.5,short:.5};
 assert.ok(Math.abs(contestDeltas(halfDen)[z]-2*contestDeltas(strong)[z])<1e-14);
}
assert.throws(()=>contestDeltas([{},...neutral.slice(1)]),/Missing/);
const invalid=structuredClone(neutral);invalid[0].defenseExposureMeasurement.long.rate=NaN;
assert.throws(()=>contestDeltas(invalid),/Invalid/);

const x=await ovrInput('2025-26'),handler=x.profiles[0],ctx={spacing:70,screen:70,offBall:70,pass:70},opts={contextScale:0,turnoverMode:'pressure',pressureAttribute:70};
const q=exposureDefenseProbabilities(handler,ctx,card(95),100,70,70,70,opts,neutral);
const base=defenseProbabilities(handler,ctx,card(),70,70,70,70,opts);
assert.deepEqual(q,base,'Neutral contest abilities must preserve the existing noncontest event tree exactly');
const changed=exposureDefenseProbabilities(handler,ctx,card(95),100,70,70,70,opts,strong);
for(const key of ['TOV','FOUL','pTovTouch','pFoul','ftPct'])assert.equal(changed[key],q[key]);
assert.deepEqual(changed.zone,q.zone);
for(const z of ['long','mid','short'])assert.ok(changed.make[z]<q.make[z]);
assert.ok(Math.abs(['TOV','FOUL','FG3M','FG3X','MIDM','MIDX','RIMM','RIMX'].reduce((s,k)=>s+changed[k],0)-1)<1e-12);
for(const p of x.profiles){
 assert.ok(p.defenseExposureMeasurement.long.rate>0);
 assert.ok(p.defenseExposureMeasurement.short.rate>0);
}
console.log('Contest activity scaling, unit checks, permutation invariance, neutral parity and unchanged non-FG hazards passed');

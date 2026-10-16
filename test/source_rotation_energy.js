import assert from 'node:assert/strict';
import {rotationEnergyStep,periodEnergyRecovery} from '../src/source_rotation_energy.js';
const a=rotationEnergyStep(1,360,true,70);assert.ok(a.end<1);assert.equal(a.mean,(1+a.end)/2);
const split=rotationEnergyStep(rotationEnergyStep(1,180,true,70).end,180,true,70);assert.ok(Math.abs(a.end-split.end)<1e-12);
const rested=rotationEnergyStep(.5,900,false,70);assert.equal(rested.end,1);assert.equal(rested.mean,.875);
const exhausted=rotationEnergyStep(.1,3600,true,70);assert.equal(exhausted.end,0);assert.ok(exhausted.mean>0&&exhausted.mean<.05);
assert.equal(periodEnergyRecovery(.6,2),.84);assert.equal(periodEnergyRecovery(.95),1);
assert.throws(()=>rotationEnergyStep(-.1,60,true,70),/Invalid/);
console.log('Continuous rotation energy, recovery boundaries and subdivision invariance passed');

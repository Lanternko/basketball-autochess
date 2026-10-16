import assert from 'node:assert/strict';
import * as M from '../src/probability_model.js';
import {defenseProbabilities} from '../src/defense_probability.js';
import {spaceProbability} from '../reports/player-impact-v7/model.mjs';
const player=i=>({playerId:i,long:70,mid:70,short:70,drive:70,tovSkill:70,pass:70,ft:70,rebound:70,onBall:70,help:70,stamina:70,physique:70,offBall:70,screen:70,handle:70,breakDbl:70,
 shotProfile:{threeRate:.4,freeThrowsPerAttempt:.25},opportunityMeasurement:{freshZone:{long:.4,mid:.1,short:.5}}});
const poor=Array.from({length:5},(_,i)=>player(i)),spacing=structuredClone(poor);
spacing[1].long=95;poor[1].long=40;
const evaluate=(ls,scale)=>{
 const p=defenseProbabilities(ls[0],M.teammateContext(ls,0),player(6),70,70,70,70,{contextLongScale:scale,contextShortScale:.5,contextScale:1});
 return spaceProbability(p,ls[0],false,{spaceCenter:.025*scale});
};
const a=evaluate(poor,1),b=evaluate(spacing,1);
assert.ok(b.make.long>a.make.long,'Teammate shooting threat must improve perimeter shot quality');
assert.ok(b.make.short>a.make.short,'One inside player must benefit when outside shooting deters help');
assert.deepEqual(a.zone,b.zone,'Measured source attempt profile must not be silently reweighted by EV a second time');
console.log(JSON.stringify({perimeterMakeChange:b.make.long-a.make.long,rimMakeChange:b.make.short-a.make.short,sourceZoneConserved:true}));

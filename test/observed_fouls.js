import assert from 'node:assert/strict';
import {observedFoulInputs} from '../reports/player-impact-v5/model.mjs';
import {attemptMakeProbability} from '../src/defense_probability.js';
const opt={foulRates:{long:{foulGivenMiss:.02,foulGivenMake:.01},mid:{foulGivenMiss:.1,foulGivenMake:.03},short:{foulGivenMiss:.2,foulGivenMake:.07}}};
for(const zone of [{long:.8,mid:.1,short:.1},{long:0,mid:.1,short:.9}])for(const target of [0,.1,.28,.55]){
 const p={zone,make:{long:.38,mid:.47,short:.65}},x=observedFoulInputs(p,{shotProfile:{freeThrowsPerAttempt:target}},opt,attemptMakeProbability);
 const ratio=Object.entries(x).reduce((s,[z,q])=>s+zone[z]*(q.raw*q.qMake+(1-q.raw)*q.qMiss*(z==='long'?3:2))/q.recorded,0);
 assert.ok(Math.abs(ratio-target)<1e-8,[zone,target,ratio]);
 for(const [z,q]of Object.entries(x))assert.ok(Math.abs(q.raw/q.recorded-p.make[z])<1e-12,'Recorded FG% must survive foul-miss exclusion');
}
console.log('observed shooting fouls: passed FT/FGA and recorded FG% for perimeter and interior profiles');

import assert from 'node:assert/strict';
import {loadInput} from '../reports/player-impact-v26/input.mjs';
import {impactEngine} from '../reports/player-impact-v27/engine.mjs';
import {elasticLineup} from '../reports/player-impact-v8/model.mjs';
const b=loadInput('2025-26'),run=await impactEngine('rotation-space',{game:true});
const pair=b.league.teams.slice(0,2).map(t=>({...t,roster:t.roster.slice(0,10).map(p=>({...p,injured:false,targetMinutes:24}))}));
const cards=new Map(pair.flatMap(t=>t.roster).map(p=>[p.playerId,p]));
const segments=[{start:0,end:330,lineup:[0,1,2,3,4]},{start:330,end:1770,lineup:[5,6,7,8,9]},{start:1770,end:2880,lineup:[0,1,2,3,4]}];
let checks=0;const fives=new Set();
for(const observed of [false,true]){
const before=checks;
const g=run(...pair,{...b.options,seed:20261015,creationPolicy:'rotation-space',contextLongScale:1,minuteMode:'budget',foulOut:99,sourcePeriods:4,sourceRotations:[segments,segments],sourcePlanObserver:e=>{
 if(e.putback){assert.equal(e.plan,null);return;}
 const expected=elasticLineup(e.lineup.map(id=>cards.get(id)),'elastic-creation').map(p=>p.opportunityMeasurement.terminalOpportunityRate);
 const observed=e.plan.rows.map((row,j)=>row.weight*row.shoot+e.plan.rows.reduce((s,r)=>s+r.receivers[j],0));
 observed.forEach((n,i)=>assert.ok(Math.abs(n-expected[i])<1e-6,'Current player must receive current-five terminal transport after every live-clock refresh'));
 checks++;fives.add(e.lineup.join(','));
},...(!observed?{sourceRotations:undefined}:{})});
assert.ok(checks-before>100);assert.ok(fives.size>=4,'Both distinct fives of both teams must be exercised');
for(const tag of ['A','B'])for(const p of g['players'+tag])assert.ok(Math.abs(p.seconds-1440)<.011);
}
console.log({checks,distinctFives:fives.size,currentFiveTransportConserved:true,individualMinutesExact:true});

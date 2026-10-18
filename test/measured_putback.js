import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as C from '../src/constants.js';
import {measuredPutbackMake,spaceProbability} from '../reports/player-impact-v22/model.mjs';
import {spaceProbability as previousSpace} from '../reports/player-impact-v14/model.mjs';
import {terminalDefenseProbabilities} from '../reports/player-impact-v21/model.mjs';
import {measuredContext} from '../src/measured_creation_context.js';
import {loadInput} from '../reports/player-impact-v22/input.mjs';
import {ovrInput} from '../reports/player-impact-v22/ovr-input.mjs';
import {ATTRIBUTES} from '../src/strength_benchmark.js';
const m={rate:.55,sourceBase:.65,context:.05};
assert.ok(Math.abs(measuredPutbackMake(.70,m)-.55)<1e-14);
assert.ok(Math.abs(measuredPutbackMake(.72,m)-.57)<1e-14,'Preserve counterfactual context/skill effects');
assert.equal(measuredPutbackMake(1,m),.85);assert.equal(measuredPutbackMake(0,m),C.CLAMP.makeShort[0]);
assert.throws(()=>measuredPutbackMake(.6,null),/Missing/);
let cases=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),src=JSON.parse(fs.readFileSync(`reports/player-impact-v22/${season}-putback-events.json`)),ctx=JSON.parse(fs.readFileSync(`reports/player-impact-v22/${season}-putback-contexts.json`));
 assert.equal(ctx.attempts,src.totals.fieldGoalAttempts);assert.equal(src.totals.fieldGoalAttempts,Object.values(src.cards).reduce((s,p)=>s+p.attempts,0));
 const options={...b.options,creationPolicy:'rotation-space',contextLongScale:1,contextShortScale:.5};
 for(let t=0;t<b.league.teams.length;t++){
  const own=b.league.teams[t].roster.slice(0,5),def=b.league.teams[(t+1)%b.league.teams.length].roster.slice(0,5);
  for(let i=0;i<5;i++){
   const p=own[i],q=terminalDefenseProbabilities(p,measuredContext(own,i),def[i],70,70,70,70,{turnoverMode:'pressure',pressureAttribute:70,contextLongScale:1,contextShortScale:.5,putback:true},def,options);
   assert.deepEqual(spaceProbability(q,p,false,options),previousSpace(q,p,false,options),'Every fresh-shot field unchanged');
   const result=spaceProbability(q,p,true,options);
   assert.equal(result.pTovTouch,q.pTovTouch);assert.equal(result.pFoul,q.pFoul);assert.equal(result.ftPct,q.ftPct);assert.equal(result.measuredTouchLiveShare,q.measuredTouchLiveShare);
   assert.deepEqual(result.zone,{long:0,mid:0,short:1});assert.ok(Math.abs(['TOV','FOUL','FG3M','FG3X','MIDM','MIDX','RIMM','RIMX'].reduce((s,k)=>s+result[k],0)-1)<1e-12);cases++;
  }
 }
}
const x=await ovrInput('2025-26');for(const p of x.profiles){assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/ATTRIBUTES.length-70)<1e-10);assert.ok(p.putbackMeasurement.rate>0&&p.putbackMeasurement.rate<1);}
console.log(JSON.stringify({cases,freshShotParity:true,conditionalHazardParity:true,syntheticMean70Preserved:true}));

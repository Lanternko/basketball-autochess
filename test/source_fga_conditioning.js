import assert from 'node:assert/strict';
import fs from 'node:fs';
import {centeredMake} from '../reports/player-impact-v14/model.mjs';

// A player takes 90 shots in an easy lineup and 10 in a difficult one,
// despite equal floor time. Reconstruct the observed conditional FG rate.
const states=[{shots:90,p:.65},{shots:10,p:.35}];
const target=.55,base=.5;
const shotCenter=states.reduce((s,x)=>s+x.shots*(x.p-base),0)/100;
const timeCenter=states.reduce((s,x)=>s+x.p-base,0)/2;
function reconstruction(center){
 return states.reduce((s,x)=>s+x.shots*centeredMake(
  {make:{long:x.p,mid:x.p,short:x.p}},
  {long:70,mid:70,short:70,shootingMeasurement:{
   rates:{long:target,mid:target,short:target},
   sourceBase:{long:base,mid:base,short:base},
   contexts:{test:{long:center,mid:center,short:center}}
  }},'test').mid,0)/100;
}
assert.ok(Math.abs(reconstruction(shotCenter)-target)<1e-12);
assert.ok(Math.abs(reconstruction(timeCenter)-target)>.1);

// Enumerate a terminal event tree: self and assisted opportunities differ
// in turnover/foul survival. The FG denominator counts recorded FGA only.
const branches=[{weight:2,tov:.1,recorded:.8,make:.4},{weight:1,tov:.2,recorded:.5,make:.7}];
let fga=0,fgm=0;
for(const b of branches){
 const events=[{p:b.tov,a:0,m:0},{p:(1-b.tov)*(1-b.recorded),a:0,m:0},
  {p:(1-b.tov)*b.recorded*b.make,a:1,m:1},
  {p:(1-b.tov)*b.recorded*(1-b.make),a:1,m:0}];
 assert.ok(Math.abs(events.reduce((s,e)=>s+e.p,0)-1)<1e-12);
 for(const e of events){fga+=b.weight*e.p*e.a;fgm+=b.weight*e.p*e.m;}
}
const conditioned=branches.reduce((s,b)=>s+b.weight*(1-b.tov)*b.recorded*b.make,0)/
 branches.reduce((s,b)=>s+b.weight*(1-b.tov)*b.recorded,0);
const unconditioned=branches.reduce((s,b)=>s+b.weight*b.make,0)/3;
assert.ok(Math.abs(fgm/fga-conditioned)<1e-12);
assert.ok(Math.abs(unconditioned-fgm/fga)>.03);

for(const version of ['v17','v18','v19','v20'])for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const path=`reports/player-impact-${version}/${season}-contexts.json`;
 if(!fs.existsSync(path))continue;
 const data=JSON.parse(fs.readFileSync(path));
 const exposure=JSON.parse(fs.readFileSync(`reports/player-impact-v17/${season}-shot-exposures.json`));
 for(const z of ['long','mid','short']){
  const count=Object.values(data.cards).reduce((s,c)=>s+c.sourceZoneAttempts[z],0);
  assert.equal(count,exposure.totals[z]);
  assert.ok(Math.abs(data.priorAttempts['rotation-space'][z]-60*count/data.strictMinutes)<1e-12);
  for(const c of Object.values(data.cards)){
   assert.ok(Number.isFinite(c.contexts['rotation-space'][z]));
   if(!c.sourceZoneAttempts[z])assert.ok(Math.abs(c.contexts['rotation-space'][z]-data.priors['rotation-space'][z])<1e-12);
  }
 }
}
console.log('FG denominator event tree, shot-exposure reconstruction, strict FGA coverage and empty-zone priors passed');

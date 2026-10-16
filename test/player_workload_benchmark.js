import assert from 'node:assert/strict';
import {workloadTeam,opponentTeam,options,source} from '../reports/player-impact-v29/benchmark.mjs';
import {ovrInput} from '../reports/player-impact-v29/ovr-input.mjs';
import {impactEngine} from '../reports/player-impact-v28/engine.mjs';
const x=await ovrInput(),src=source(),run=await impactEngine('rotation-space',{game:true}),cap=src.capMinutes;
let games=0;
for(const phase of [0,1])for(const minutes of [0,12,cap]){
 const slot=4,p=x.players.find(p=>p.playerId===1629011),own=workloadTeam(x,p,slot,minutes,cap,phase),
  baseline=workloadTeam(x,x.profiles[slot],slot,minutes,cap,phase),op=opponentTeam(x,x.opponents[0],cap,phase),seed=20261018+phase;
 const original=JSON.stringify([x.profiles,p]);
 const a=run(own.team,op.team,options(x,seed,[own.schedule,op.schedule]));
 const b=run(baseline.team,op.team,options(x,seed,[baseline.schedule,op.schedule]));games+=2;
 assert.equal(a.gameSeconds,2880);assert.equal(b.gameSeconds,2880);
 assert.ok(Math.abs(a.playersA[slot].seconds-Math.round(minutes*600)/10)<.011);
 if(minutes===0){
  assert.equal(a.playersA[slot].pts,0);assert.equal(a.playersA[slot].fga,0);
  assert.deepEqual(a.statA,b.statA);assert.deepEqual(a.statB,b.statB);
 }
 assert.equal(JSON.stringify([x.profiles,p]),original,'Benchmark mutates source skill profiles');
 const same=workloadTeam(x,x.profiles[slot],slot,minutes,cap,phase);
 const c=run(same.team,op.team,options(x,seed,[same.schedule,op.schedule]));games++;
 assert.deepEqual(c,b,'Identical player at identical workload gets a spurious contribution');
}
console.log(JSON.stringify({passed:true,games,zeroLoadContributesExactlyZero:true,identicalProfilesExactlyMatch:true}));

import assert from 'node:assert/strict';
import { TEAMS } from '../src/teams.js';
import { simulateGame } from '../src/simulation_engine.js';
import { planScene, sampleScene, replayRemaining } from '../src/court-scene.js';
const teams=[TEAMS.GSW,TEAMS.CLE];
const targets=[[[57,50],[69,24],[69,76],[82,34],[85,67]],[[63,55],[75,20],[75,82],[88,30],[91,72]]];
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
const kinds=new Set();
for(const seed of [1,42,20260908]){
  const {events}=simulateGame(...teams,{seed,possessions:50,replay:true});
  let previous=sampleScene(planScene(null,null,targets,teams),1);
  for(let i=0;i<events.length;i++){
    const scene=planScene(events[i],previous,targets,teams,events[i+1]);kinds.add(scene.kind);
    const first=sampleScene(scene,0);
    assert.deepEqual(first.positions,previous.positions,'Every player starts at the preceding endpoint');
    assert.ok(distance(first.ball,previous.ball)<1e-8,'Ball must not teleport between events');
    for(const phase of [.12,.2,.3,.35,.4,.52,.53,.55,.57,.62,.68,.73]) {
      const left=sampleScene(scene,phase-1e-7),right=sampleScene(scene,phase+1e-7);
      assert.ok(distance(left.ball,right.ball)<.01,`${scene.kind}: discontinuous ball at ${phase}: ${distance(left.ball,right.ball)}`);
    }
    for(let f=0;f<=50;f++){
      const frame=sampleScene(scene,f/50);
      for(const n of [...frame.ball,...frame.positions.flat(2)])assert.ok(Number.isFinite(n));
      assert.ok(frame.ball[2]>=-1e-8,'Ball cannot travel below the floor');
    }
    const last=sampleScene(scene,1);
    assert.deepEqual(sampleScene(scene,.47),sampleScene(scene,.47),'Paused frames are deterministic');
    if(scene.kind==='rebound')assert.ok(distance(last.positions[events[i].off][events[i].player],previous.landing.slice(0,2))<1e-8);
    previous=last;
  }
}
for(const kind of ['shot','layup','dunk','rebound','steal','block','freeThrow','pass','handle'])assert.ok(kinds.has(kind));
assert.equal(replayRemaining([1000,2000],0),3000);
assert.equal(replayRemaining([1000,2000],1,.5),2500);
assert.equal(replayRemaining([1000,2000],2,1),0);
console.log('Scene: all event boundaries, ball phases, rebound destinations, deterministic scrubbing, clock endpoints passed (3 seeds).');


import assert from 'node:assert/strict';
import { simulateGame } from '../src/simulation_engine.js';
import { TEAMS } from '../src/teams.js';
import { motionKind, arcPoint, motionDuration, impactPoint } from '../src/motion-model.js';
const teams=[TEAMS.GSW,TEAMS.CLE];
for (const seed of [1,42,20260908]) {
 const {events,...result}=simulateGame(...teams,{seed,possessions:50,replay:true});
 assert.deepEqual(result,simulateGame(...teams,{seed,possessions:50}), 'Animation replay must not change simulation outcomes');
 let fouls=0;
 events.forEach((event,i)=>{
  const previous=events[i-1];
  if(event.type==='FOUL') {
   fouls++;
   assert.deepEqual(event.score,previous?.score??[0,0]);
   assert.equal(event.players[1-event.off][event.defender].pf-(previous?.players[1-event.off][event.defender].pf??0),1);
   for(let n=1;n<=event.attempts;n++) {
    const ft=events[i+n];
    assert.ok(['FTM','FTX'].includes(ft.type));
    assert.equal(ft.player,event.player);assert.equal(ft.off,event.off);
    assert.equal(ft.attempt,n);assert.equal(ft.attempts,event.attempts);
    assert.equal(ft.players[ft.off][ft.player].fta-events[i+n-1].players[ft.off][ft.player].fta,1);
    assert.equal(ft.score[ft.off]-events[i+n-1].score[ft.off],ft.type==='FTM'?1:0);
   }
  }
  const kind=motionKind(event,teams);
  assert.ok(motionDuration(kind)>0);assert.ok(impactPoint(kind)>0&&impactPoint(kind)<1);
  if(kind==='dunk') assert.equal(event.type,'RIMM');
 });
 assert.equal(fouls,result.statA.pf+result.statB.pf);
}
for (const [start,end] of [[[66,78],[91.2,50]],[[34,20],[8.8,50]],[[78,50],[91.2,50]]]) {
 assert.deepEqual(arcPoint(start,end,0),start);assert.deepEqual(arcPoint(start,end,1),end);
 assert.ok(arcPoint(start,end,.5)[1]<(start[1]+end[1])/2,'Shot must rise above its straight-line path');
 for(let n=0;n<=100;n++) for(const v of arcPoint(start,end,n/100)) assert.ok(Number.isFinite(v)&&v>=0&&v<=100);
}
console.log('Motion: replay simulation parity, foul attribution, individual 1-point free throws and bounded shot arcs passed.');
const {events}=simulateGame(...teams,{seed:20260908,possessions:50,replay:true});
console.log('QA events:',Object.fromEntries(['shot','dunk','rebound','block','steal','foul','freeThrow'].map(k=>[k,events.findIndex(e=>motionKind(e,teams)===k)+1])));

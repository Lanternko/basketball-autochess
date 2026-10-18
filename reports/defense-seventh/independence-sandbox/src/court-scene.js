import { motionKind, motionDuration, impactPoint, clamp, mix, ease, spacePositions } from './motion-model.js';

export const hoopFor = side => [side === 0 ? 91.2 : 8.8, 50, 10];
export const handAt = (p, side, raised = 0) => [p[0] + (side ? -1.5 : 1.5), p[1], 6 + raised];
const flight = (a,b,t,height) => {
  const p=mix(a,b,clamp(t)); p[2]+=Math.sin(Math.PI*clamp(t))*height; return p;
};
const clone = p => p.map(row=>row.map(v=>[...v]));

// Coordinates are court x/y plus height. The next scene always starts at the
// preceding scene's exact final state, including a loose or bouncing ball.
export function planScene(event, previousFrame, targets, teams, nextEvent) {
  const kind=motionKind(event,teams), off=event?.off??0;
  const start=previousFrame ? clone(previousFrame.positions) : clone(targets);
  let end=clone(targets);
  // A possession change runs the full floor. Within a possession, preserve
  // spacing and move only the participants instead of resetting ten positions.
  if (event && event.type!=='POSSESSION' && previousFrame) {
    end=clone(start);
    if (['shot','layup','dunk','freeThrow','foul','block'].includes(kind)) {
      end[off][event.player]=[...targets[off][event.player]];
      const defender=event.defender??event.player;
      end[1-off][defender]=[...targets[1-off][defender]];
    }
  }
  let actor=[off,event?.player??0];
  if(['steal','foul'].includes(kind)) actor=[1-off,event.defender];
  if(kind==='block') actor=[1-off,teams[1-off].roster.findIndex(p=>p.name===event.blocker)];
  const hoop=hoopFor(off);
  if(kind==='rebound' && previousFrame) {
    // The rebounder travels to the same landing zone the missed shot chose.
    end[off][event.player]=previousFrame.landing?.slice(0,2)??[previousFrame.ball[0],previousFrame.ball[1]];
  }
  if(kind==='steal') {
    const p=start[off][event.player];end[1-off][event.defender]=[p[0]+(off? -3:3),p[1]+2];
  }
  if(kind==='block' && actor[1]>=0) end[actor[0]][actor[1]]=[end[off][event.player][0]+(off?-3:3),end[off][event.player][1]-1];
  end=spacePositions(end,actor,5.5).map(row=>row.map(([x,y])=>[x,Math.max(21,Math.min(86,y))]));
  const reboundNext=nextEvent && ['OREB','DREB'].includes(nextEvent.type);
  const landing=reboundNext ? [hoop[0]+(off?-1:1)*( -7-(nextEvent.player%3)*2),44+(nextEvent.player%3)*7,0] : [hoop[0]+(off?8:-8),59,0];
  return {event,kind,off,start,end,actor,hoop,landing,teams,duration:motionDuration(kind),
    initialBall:previousFrame?.ball??handAt(start[off][event?.player??0],off)};
}
export function sampleScene(scene,t) {
  const {event:e,kind:k,off,start,end,actor,hoop,landing}=scene;
  const moveEnd=k==='handle'?.82:k==='rebound'?.48:['layup','dunk'].includes(k)?.54:.3;
  const positions=start.map((row,s)=>row.map((p,i)=>mix(p,end[s][i],ease(t/moveEnd))));
  const jump=Array.from({length:2},()=>Array(5).fill(0));
  if(e && ['shot','layup','dunk','block','rebound'].includes(k)) {
    const apex=k==='rebound'?.53:k==='block'?.57:k==='dunk'?.68:.3;
    const rise=clamp((t-(apex-.18))/.18),fall=clamp((t-apex)/.22);
    if(actor[1]>=0) jump[actor[0]][actor[1]]=Math.sin((t<apex?rise:1-fall)*Math.PI/2)*(k==='shot'?2:k==='rebound'?3:5);
    if(k==='block') jump[off][e.player]=Math.sin(Math.PI*clamp((t-.18)/.55))*2;
  }
  const held=(s,i,raised=0)=>handAt(positions[s][i],s,jump[s][i]+raised);
  let ball=[...scene.initialBall];
  if(e) {
    const release=handAt(end[off][e.player],off,k==='freeThrow'?3:5);
    if(['shot','layup','freeThrow'].includes(k)) {
      if(t<.3) ball=mix(scene.initialBall,release,ease(t/.3));
      else if(t<.73) ball=flight(release,hoop,(t-.3)/.43,k==='layup'?7:17);
      else if(e.type.endsWith('M')) ball=mix(hoop,[hoop[0],hoop[1]+1,0],clamp((t-.73)/.27));
      else ball=flight(hoop,[landing[0],landing[1],16],(t-.73)/.27,6);
    } else if(k==='dunk') {
      const grip=held(off,e.player,3*clamp((t-.3)/.2));
      const takeoff=handAt(end[off][e.player],off,3+5*Math.sin(Math.PI/2*((.55-.5)/.18)));
      ball=t<.12?mix(scene.initialBall,grip,ease(t/.12)):t<.55?grip:t<.68?mix(takeoff,hoop,(t-.55)/.13):mix(hoop,[hoop[0],hoop[1]+1,0],clamp((t-.68)/.32));
    } else if(k==='rebound') {
      const catchPoint=handAt(end[off][e.player],off,8);
      ball=t<.53?flight(scene.initialBall,catchPoint,t/.53,.4):mix(catchPoint,held(off,e.player),ease((t-.53)/.24));
    } else if(k==='pass') {
      const dest=handAt(end[off][e.player],off);
      ball=t<.12?scene.initialBall:t<.62?flight(scene.initialBall,dest,(t-.12)/.5,3):held(off,e.player);
    } else if(k==='block') {
      const meet=handAt(end[actor[0]][actor[1]],actor[0],14);
      ball=t<.2?mix(scene.initialBall,release,ease(t/.2)):t<.57?flight(release,meet,(t-.2)/.37,6):flight(meet,[landing[0],landing[1],16],(t-.57)/.43,2);
    } else if(k==='steal') {
      const catchPoint=handAt(end[1-off][e.defender],1-off);
      ball=t<.52?flight(scene.initialBall,catchPoint,ease(t/.52),1):held(1-off,e.defender);
    } else if(k==='turnover') {
      ball=flight(scene.initialBall,[end[off][e.player][0]+(off?5:-5),end[off][e.player][1]+7,0],ease(t),2);
    } else {
      ball=mix(scene.initialBall,held(off,e.player),ease(t/.35));
      if(k==='handle' && t>.35) ball[2]=6-5.4*Math.abs(Math.sin((t-.35)/.65*Math.PI*3));
    }
  }
  return {positions,ball,jump,landing,actor,kind:k,progress:t};
}
export function replayRemaining(durations,index,progress=0) {
  return durations.slice(index).reduce((a,b)=>a+b,0)+(index>0?durations[index-1]*(1-progress):0);
}

import { motionKind, motionDuration, impactPoint, clamp } from './motion-model.js';
import { planScene, sampleScene } from './court-scene.js';
import { drawPlayer } from './player-figure.js';
const $=id=>document.getElementById(id);
export class CourtMotion {
  constructor() {
    this.reduced=matchMedia('(prefers-reduced-motion: reduce)');
    this.reduced.addEventListener('change',()=>{if(this.reduced.matches&&!this.finished){this.elapsed=this.duration;this.draw(1);this.resolve();this.finish();}});
    this.speed=1;this.generation=0;this.finished=true;this.progress=1;
  }
  start({event,positions,teams,animate,onImpact,onComplete,onFrame,nextEvent,frame}) {
    this.cancel();this.event=event;this.teams=teams;this.onImpact=onImpact;this.onComplete=onComplete;this.onFrame=onFrame;
    this.kind=motionKind(event,teams);this.duration=motionDuration(this.kind);
    this.scene=planScene(event,frame??null,positions,teams,nextEvent);
    this.elapsed=animate?0:this.duration;this.fired=!animate;this.finished=!animate;
    this.draw(animate?0:1);
    if(animate){ if(this.reduced.matches){this.draw(1);this.resolve();this.finish();}else this.resume(); }
  }
  cancel(){cancelAnimationFrame(this.raf);this.running=false;this.generation++;}
  pause(){cancelAnimationFrame(this.raf);this.running=false;}
  resume(){if(this.finished||this.running)return;this.running=true;this.last=performance.now();this.raf=requestAnimationFrame(time=>this.tick(time));}
  setSpeed(speed){this.speed=speed;}
  tick(time){
    if(!this.running)return;const generation=this.generation;
    this.elapsed+=Math.max(0,time-this.last)*this.speed;this.last=time;
    const t=clamp(this.elapsed/this.duration);this.draw(t);
    if(t>=impactPoint(this.kind))this.resolve();
    if(generation!==this.generation)return;
    if(t>=1){this.finish();return;}
    this.raf=requestAnimationFrame(next=>this.tick(next));
  }
  resolve(){if(!this.fired){this.fired=true;this.onImpact?.();}}
  finish(){cancelAnimationFrame(this.raf);this.running=false;this.finished=true;this.onComplete?.();}
  resize(){if(this.scene)this.draw(this.progress);}
  draw(t){
    this.progress=t;const frame=sampleScene(this.scene,t);this.frame=frame;
    const court=$('court'),w=court.clientWidth,h=court.clientHeight,e=this.event,k=this.kind;
    court.dataset.motion=k;court.dataset.motionProgress=t.toFixed(3);
    for(const token of $('tokens').children){
      const s=+token.dataset.side,i=+token.dataset.player,p=frame.positions[s][i];
      const moving=Math.hypot(p[0]-this.scene.end[s][i][0],p[1]-this.scene.end[s][i][1])>.3;
      const active=frame.actor[0]===s&&frame.actor[1]===i;
      const defending=e && s!==(e.type==='DREB'?1-e.off:e.off);
      const dir=moving?Math.sign(this.scene.end[s][i][0]-this.scene.start[s][i][0])||1:e?(e.type==='DREB'?1-e.off:e.off)===0?1:-1:1;
      token.style.transform=`translate(${p[0]*w/100}px,${p[1]*h/100}px)`;
      token.style.zIndex=String(20+Math.round(p[1]));
      token.classList.toggle('motion-active',active);
      token.classList.toggle('has-ball',e? (k==='steal'&&t>=.52?s===1-e.off&&i===e.defender:s===e.off&&i===e.player&&(!['shot','layup','dunk','freeThrow','block'].includes(k)||t<.3)):false);
      const pose=active?k:k==='block'&&s===e.off&&i===e.player?'shot':'idle';
      drawPlayer(token,pose,t,{moving,defending,phase:t*this.duration/90+i*1.3,direction:dir,jump:frame.jump[s][i]*h/100});
      const cue=token.querySelector('.stat-pop');if(cue)cue.style.animationPlayState=this.running?'running':'paused';
    }
    const ball=$('ball'),b=frame.ball;
    ball.style.transform=`translate(${b[0]*w/100}px,${(b[1]-b[2])*h/100}px) translate(-50%,-50%) rotate(${t*540}deg)`;
    ball.style.zIndex=String(23+Math.round(b[1]));
    const shadow=$('ball-shadow');shadow.style.transform=`translate(${b[0]*w/100}px,${b[1]*h/100}px) translate(-50%,-50%) scale(${1+b[2]/20})`;shadow.style.opacity=String(.35-b[2]/110);
    const made=e?.type.endsWith('M')&&['shot','layup','dunk','freeThrow'].includes(k);
    for(const net of court.querySelectorAll('.basket')){
      const hit=made&&+net.dataset.side===e.off&&t>=impactPoint(k);
      net.style.setProperty('--net-stretch',hit?1+Math.sin(clamp((t-impactPoint(k))/.22)*Math.PI)*.65:1);
      net.classList.toggle('scored',hit);
    }
    this.onFrame?.(t);
  }
}

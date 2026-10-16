import { clamp, mix } from './motion-model.js';
const NS='http://www.w3.org/2000/svg';
const svgNode=(tag,attrs={})=>{const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs)) n.setAttribute(k,v);return n;};
// Joint positions create solid, articulated silhouettes rather than moving a still image.
// Coordinates: shoulder, hip, elbows, wrists, knees, ankles. Head follows the shoulder.
const poses = {
  ready: {s:[0,0],h:[0,43],le:[-18,20],lw:[-4,26],re:[19,18],rw:[28,10],lk:[-14,66],la:[-22,88],rk:[15,66],ra:[25,88]},
  crouch:{s:[7,12],h:[0,47],le:[-12,31],lw:[17,27],re:[23,30],rw:[29,20],lk:[-19,68],la:[-30,88],rk:[23,68],ra:[32,88]},
  set:{s:[0,-9],h:[-1,36],le:[-12,-12],lw:[12,-27],re:[23,-10],rw:[19,-32],lk:[-11,60],la:[-16,88],rk:[11,60],ra:[15,88]},
  release:{s:[0,-20],h:[-2,26],le:[-9,-45],lw:[16,-65],re:[21,-47],rw:[29,-70],lk:[-8,56],la:[-13,80],rk:[9,55],ra:[19,79]},
  follow:{s:[0,-10],h:[-2,34],le:[-10,-28],lw:[13,-42],re:[24,-36],rw:[39,-51],lk:[-12,61],la:[-18,88],rk:[11,62],ra:[19,88]},
  reach:{s:[0,-24],h:[-2,20],le:[-25,-50],lw:[-9,-77],re:[26,-51],rw:[15,-77],lk:[-19,46],la:[-31,65],rk:[23,42],ra:[35,63]},
  clutch:{s:[0,-7],h:[0,37],le:[-21,7],lw:[-4,17],re:[23,7],rw:[9,17],lk:[-18,64],la:[-28,88],rk:[20,64],ra:[29,88]},
  run:{s:[15,5],h:[0,44],le:[-16,18],lw:[-33,3],re:[40,1],rw:[49,-16],lk:[24,54],la:[48,65],rk:[-20,65],ra:[-38,87]},
  windup:{s:[9,-19],h:[-2,21],le:[-13,1],lw:[-32,-6],re:[-5,-52],rw:[-31,-68],lk:[25,37],la:[40,61],rk:[-18,51],ra:[-37,69]},
  hammer:{s:[16,-34],h:[2,9],le:[-10,-21],lw:[-31,-3],re:[48,-45],rw:[73,-7],lk:[-7,44],la:[-18,68],rk:[29,38],ra:[47,61]},
  hang:{s:[30,-12],h:[21,31],le:[6,11],lw:[-9,25],re:[60,-31],rw:[81,-7],lk:[10,57],la:[-2,73],rk:[37,56],ra:[43,77]},
  block:{s:[9,-31],h:[-2,13],le:[-25,-34],lw:[-32,-57],re:[36,-61],rw:[60,-78],lk:[-20,40],la:[-32,65],rk:[17,42],ra:[34,65]},
  swipe:{s:[19,16],h:[0,45],le:[-9,20],lw:[-30,8],re:[44,30],rw:[72,37],lk:[-22,67],la:[-40,88],rk:[32,64],ra:[50,87]},
  recover:{s:[-5,3],h:[-10,43],le:[-21,20],lw:[1,28],re:[18,14],rw:[2,25],lk:[-27,60],la:[-43,88],rk:[15,64],ra:[34,86]},
  contact:{s:[-9,3],h:[0,44],le:[-34,-4],lw:[-51,-20],re:[19,-3],rw:[38,-25],lk:[-20,66],la:[-33,88],rk:[23,67],ra:[35,88]},
};
const sequences={
  shot:[[0,'crouch'],[.22,'set'],[.43,'release'],[.73,'follow'],[1,'ready']],
  freeThrow:[[0,'ready'],[.24,'set'],[.43,'release'],[.74,'follow'],[1,'ready']],
  layup:[[0,'run'],[.3,'set'],[.5,'release'],[.73,'follow'],[1,'ready']],
  dunk:[[0,'run'],[.25,'crouch'],[.48,'windup'],[.68,'hammer'],[.78,'hang'],[1,'ready']],
  rebound:[[0,'crouch'],[.28,'set'],[.53,'reach'],[.7,'clutch'],[1,'ready']],
  block:[[0,'crouch'],[.25,'set'],[.57,'block'],[.76,'contact'],[1,'ready']],
  steal:[[0,'ready'],[.24,'crouch'],[.52,'swipe'],[.74,'recover'],[1,'run']],
  foul:[[0,'ready'],[.4,'contact'],[.7,'contact'],[1,'ready']],
  turnover:[[0,'ready'],[.45,'contact'],[1,'ready']],
};
function interpolatePose(kind,t) {
  const seq=sequences[kind]??sequences.shot;
  let index=seq.findIndex(([time])=>time>=t);if(index<=0) return poses[seq[0][1]];
  const [a,pa]=seq[index-1], [b,pb]=seq[index];const f=clamp((t-a)/(b-a));
  return Object.fromEntries(Object.keys(poses.ready).map(key=>[key,mix(poses[pa][key],poses[pb][key],f)]));
}
function actor(parent,opacity=1) {
  const g=svgNode('g',{'class':'silhouette-body',opacity});parent.append(g);
  const legs=svgNode('path',{'stroke-width':13});const torso=svgNode('path');
  const arms=svgNode('path',{'stroke-width':9});const head=svgNode('circle',{r:11});
  const shoes=svgNode('path',{'stroke-width':8});
  g.append(legs,torso,arms,head,shoes);
  return {g,legs,torso,arms,head,shoes};
}
function drawActor(a,p,x=104,y=84,scale=1) {
  const {s,h,le,lw,re,rw,lk,la,rk,ra}=p;
  a.g.setAttribute('transform',`translate(${x} ${y}) scale(${scale})`);
  a.head.setAttribute('cx',s[0]+1);a.head.setAttribute('cy',s[1]-20);
  a.torso.setAttribute('d',`M${s[0]-12},${s[1]-3} Q${s[0]},${s[1]-9} ${s[0]+12},${s[1]-3} L${h[0]+13},${h[1]+7} L${h[0]-13},${h[1]+7} Z`);
  a.arms.setAttribute('d',`M${s} L${le} L${lw} M${s} L${re} L${rw}`);
  a.legs.setAttribute('d',`M${h[0]-7},${h[1]} L${lk} L${la} M${h[0]+7},${h[1]} L${rk} L${ra}`);
  a.shoes.setAttribute('d',`M${la} l12,2 M${ra} l12,2`);
}
export class ActionSilhouette {
  constructor(root) {
    this.root=root;
    this.svg=svgNode('svg',{viewBox:'0 0 240 200','aria-hidden':'true'});
    this.svg.innerHTML='<ellipse class="motion-floor" cx="119" cy="177" rx="71" ry="8"/><g class="motion-hoop"><path d="M226 26V170 M210 27V70"/><path d="M186 72H217 M189 73L196 90H210L216 73"/></g>';
    this.secondary=actor(this.svg,.32);this.primary=actor(this.svg);
    this.ball=svgNode('circle',{r:8,'class':'silhouette-ball'});this.svg.append(this.ball);
    this.caption=document.createElement('span');this.caption.className='motion-caption';
    root.append(this.svg,this.caption);
  }
  set(kind,label,direction) {
    this.kind=kind;this.caption.textContent=label;
    this.root.hidden=!sequences[kind];
    this.root.style.left=direction===0?'35%':'65%';
    this.svg.querySelector('.motion-hoop').style.opacity=['shot','freeThrow','layup','dunk','block'].includes(kind)?'1':'0';
    this.secondary.g.style.display=['block','steal','foul'].includes(kind)?'':'none';
  }
  draw(t) {
    if(this.root.hidden) return;
    const p=interpolatePose(this.kind,t);
    const travel=this.kind==='dunk' ? 38*clamp(t/.68) : this.kind==='steal' ? -14*clamp((t-.55)/.45) : 0;
    drawActor(this.primary,p,91+travel,84);
    if(['block','steal','foul'].includes(this.kind)) drawActor(this.secondary,interpolatePose(this.kind==='block'?'shot':'turnover',t),159,90,.84);
    let b=[91+travel+p.rw[0],84+p.rw[1]-7];
    if(['shot','freeThrow','layup'].includes(this.kind)&&t>.4) {
      const f=clamp((t-.4)/.33);b=[120+85*f,9-34*Math.sin(f*Math.PI)+62*f];
    } else if(this.kind==='rebound') {
      const f=clamp(t/.53);b=t<.53?[102,7+f*1]:[91+(p.lw[0]+p.rw[0])/2,84+(p.lw[1]+p.rw[1])/2-5];
    } else if(this.kind==='steal') b=t<.52?[164,125]:[91+travel+(p.lw[0]+p.rw[0])/2,84+(p.lw[1]+p.rw[1])/2];
    else if(this.kind==='block') b=t<.57?[165,12+55*(1-clamp(t/.57))]:[165-70*clamp((t-.57)/.43),12+130*clamp((t-.57)/.43)];
    this.ball.style.display=['foul','turnover'].includes(this.kind)?'none':'';
    this.ball.setAttribute('cx',b[0]);this.ball.setAttribute('cy',Math.max(8,b[1]));
  }
}

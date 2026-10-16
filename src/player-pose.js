import { clamp, mix } from './motion-model.js';
const poses = {
  ready: {s:[0,0],h:[0,43],le:[-18,20],lw:[-4,26],re:[19,18],rw:[28,10],lk:[-14,66],la:[-22,88],rk:[15,66],ra:[25,88]},
  crouch:{s:[7,12],h:[0,47],le:[-12,31],lw:[17,27],re:[23,30],rw:[29,20],lk:[-19,68],la:[-30,88],rk:[23,68],ra:[32,88]},
  set:{s:[0,-9],h:[-1,36],le:[-12,-12],lw:[12,-27],re:[23,-10],rw:[19,-32],lk:[-11,60],la:[-16,88],rk:[11,60],ra:[15,88]},
  release:{s:[0,-20],h:[-2,26],le:[-9,-45],lw:[16,-65],re:[21,-47],rw:[29,-70],lk:[-8,56],la:[-13,80],rk:[9,55],ra:[19,79]},
  follow:{s:[0,-10],h:[-2,34],le:[-10,-28],lw:[13,-42],re:[24,-36],rw:[39,-51],lk:[-12,61],la:[-18,88],rk:[11,62],ra:[19,88]},
  reach:{s:[0,-24],h:[-2,20],le:[-25,-50],lw:[-9,-45],re:[26,-31],rw:[15,-45],lk:[-19,46],la:[-31,65],rk:[23,42],ra:[35,63]},
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
export function interpolatePose(kind,t) {
  const seq=sequences[kind]??sequences.shot;
  let index=seq.findIndex(([time])=>time>=t);if(index<=0) return poses[seq[0][1]];
  const [a,pa]=seq[index-1], [b,pb]=seq[index];const f=clamp((t-a)/(b-a));
  return Object.fromEntries(Object.keys(poses.ready).map(key=>[key,mix(poses[pa][key],poses[pb][key],f)]));
}


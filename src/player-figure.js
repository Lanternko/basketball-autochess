import { interpolatePose } from './player-pose.js';
const path=(el,d)=>el.setAttribute('d',d);
export function playerFigure(number) {
  return `<svg class="player-figure" viewBox="-65 -100 150 200" aria-hidden="true"><g class="player-body"><path class="limb legs"/><path class="jersey"/><path class="shorts"/><path class="limb arms"/><circle class="head" r="17"/><path class="hair"/><path class="shoes"/><text class="jersey-number" text-anchor="middle">${number}</text></g></svg>`;
}
export function drawPlayer(token,kind,t,{moving=false,defending=false,phase=0,direction=1,jump=0}={}) {
  const p=structuredClone(interpolatePose(kind,t));
  if(kind==='idle'||kind==='handle'||kind==='pass') {
    Object.assign(p,structuredClone(interpolatePose('steal',0)));
    if(moving) {
      const stride=Math.sin(phase)*18;
      p.la=[-13+stride,88-Math.max(0,stride)*.3];p.ra=[14-stride,88-Math.max(0,-stride)*.3];
      p.lk=[-12+stride*.6,65];p.rk=[14-stride*.6,65];
      p.lw=[-22-stride,22];p.rw=[22+stride,15];
    } else if(defending) {
      p.le=[-27,8];p.lw=[-45,4];p.re=[28,8];p.rw=[45,4];
      p.la=[-25,88];p.ra=[26,88];
    } else if(kind==='handle') {p.re=[24,23];p.rw=[33,30+Math.abs(Math.sin(phase))*20];}
  }
  const {s,h,le,lw,re,rw,lk,la,rk,ra}=p;
  const figure=token.querySelector('.player-figure');
  figure.style.transform=`translateY(${-jump}px) scaleX(${direction})`;
  path(token.querySelector('.legs'),`M${h[0]-7},${h[1]} L${lk} L${la} M${h[0]+7},${h[1]} L${rk} L${ra}`);
  path(token.querySelector('.jersey'),`M${s[0]-14},${s[1]-3} Q${s[0]},${s[1]+6} ${s[0]+14},${s[1]-3} L${h[0]+15},${h[1]} L${h[0]-15},${h[1]}Z`);
  path(token.querySelector('.shorts'),`M${h[0]-15},${h[1]-7}H${h[0]+15}L${h[0]+18},${h[1]+16}H${h[0]+2}L${h[0]},${h[1]+6}L${h[0]-3},${h[1]+16}H${h[0]-18}Z`);
  path(token.querySelector('.arms'),`M${s[0]-13},${s[1]} L${le} L${lw} M${s[0]+13},${s[1]} L${re} L${rw}`);
  token.querySelector('.head').setAttribute('cx',s[0]);token.querySelector('.head').setAttribute('cy',s[1]-23);
  path(token.querySelector('.hair'),`M${s[0]-16},${s[1]-26}Q${s[0]-16},${s[1]-44} ${s[0]+6},${s[1]-39}Q${s[0]+18},${s[1]-37} ${s[0]+16},${s[1]-23}L${s[0]+10},${s[1]-31}L${s[0]-14},${s[1]-30}Z`);
  path(token.querySelector('.shoes'),`M${la}l13,2 M${ra}l13,2`);
  const number=token.querySelector('.jersey-number');number.setAttribute('x',s[0]);number.setAttribute('y',s[1]+27);
  number.setAttribute('transform',direction<0?`translate(${2*s[0]} 0) scale(-1 1)`:'');
}

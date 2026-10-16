import * as M from './probability_model.js';
import * as C from './constants.js';
import {defenseProbabilities} from './defense_probability.js';
export const logistic=x=>1/(1+Math.exp(-x));
export const logit=p=>Math.log(Math.max(1e-7,Math.min(1-1e-7,p))/(1-Math.max(1e-7,Math.min(1-1e-7,p))));
export const shifted=(p,e)=>logistic(logit(p)+e);
export const effect=(lineup,name,opt)=>lineup.reduce((s,p)=>s+(opt.defenseSignals?.values[p.playerId]?.[name]??0),0)/5-(opt.defenseSignals?.centers[name]??0);
export function fourthProbability(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){
  const p=defenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts);
  if(!(opt.neutralContests||opt.rimSignal||opt.zoneSignal))return p;
  const neutral=defenseProbabilities(handler,ctx,{...defender,onBall:70},70,oreb,dreb,70,opts);
  const old={...p.make};
  if(opt.neutralContests){p.make.long=neutral.make.long;p.make.mid=neutral.make.mid;}
  if(opt.rimSignal)p.make.short=shifted(neutral.make.short,effect(lineup,'shortFG',opt));
  const zones=['long','mid','short'];
  // Remove the old defense accessibility when its zone signal is replaced.
  if(opt.zoneSignal)p.zone={...neutral.zone};
  const weights=zones.map(z=>{
    const initial=opt.zoneSignal?neutral.make[z]:old[z];
    const evAdjusted=p.zone[z]*Math.exp((z==='long'?3:2)*(p.make[z]-initial)/C.EV_TEMP);
    return opt.zoneSignal?shifted(evAdjusted/(1+evAdjusted-p.zone[z]),effect(lineup,({long:'threeShare',mid:'midShare',short:'shortShare'})[z],opt)):evAdjusted;
  });
  const total=weights.reduce((a,b)=>a+b,0);zones.forEach((z,i)=>p.zone[z]=weights[i]/total);
  const shot=Math.max(0,1-p.pTovTouch-p.pFoul);
  p.ev=shot*zones.reduce((s,z)=>s+p.zone[z]*p.make[z]*(z==='long'?3:2),0)+p.pFoul*C.FT_ATTEMPTS*p.ftPct;
  return p;
}
const kernels=new WeakMap();
export function continuousDuration(cdf,limit,rng){
  let cells=kernels.get(cdf);
  if(!cells){cells=[];for(const t of cdf){if(cells.at(-1)?.t===t)cells.at(-1).n++;else cells.push({t,n:1});}let n=0;for(const c of cells){c.lo=Math.max(.1,c.t-.5);c.hi=c.t+.5;c.cum=n+=c.n;}kernels.set(cdf,cells);}
  let l=0,h=cells.length;while(l<h){const m=(l+h)>>1;if(cells[m].hi<=limit)l=m+1;else h=m;}
  const full=l,base=full?cells[full-1].cum:0;let mass=base;const partial=[];
  for(let i=full;i<cells.length&&cells[i].lo<limit;i++){const c=cells[i],w=c.n*(Math.min(limit,c.hi)-c.lo)/(c.hi-c.lo);mass+=w;partial.push({c,w});}
  if(mass<=0)return Math.max(.01,limit);
  let u=rng()*mass,c;
  if(u<base){l=0;h=full;while(l<h){const m=(l+h)>>1;if(cells[m].cum<=u)l=m+1;else h=m;}c=cells[l];}
  else{u-=base;for(const p of partial){c=p.c;if(u<p.w)break;u-=p.w;}}
  return c.lo+rng()*(Math.min(c.hi,limit)-c.lo);
}
export function starterTarget(period,clock,lead,curve){
  const remaining=(4-Math.min(period,4))*720+clock;
  const time=curve.remainingEdges.findIndex(x=>remaining>=x),bucket=curve.absoluteLeadEdges.findIndex(x=>Math.abs(lead)<=x);
  return curve.cells[time+':'+bucket]?.share??curve.overallStarterShare;
}

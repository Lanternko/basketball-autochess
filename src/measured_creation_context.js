import * as M from './probability_model.js';
import * as C from './constants.js';
const clamp=(x,lo,hi)=>Math.max(lo,Math.min(hi,x));
const rating=(x,pool)=>{
 const pct=100*(pool.filter(v=>v<x).length+.5*pool.filter(v=>v===x).length)/pool.length;
 return clamp(pct<50?40+(pct-1)*30/49:70+(pct-50)*29/49,40,99);
};
export function contextReference(players){
 const byId={};
 for(const p of players){const r=byId[p.playerId]??{minutes:0,threeMakes:0,threeAttempts:0,attempts:0};for(const[k,v]of [['minutes','MIN'],['threeMakes','FG3M'],['threeAttempts','FG3A'],['attempts','FGA']])r[k]+=p.observed[v];r.self=p.shotCreationMeasurement.selfMakesPerMinute;r.creation=p.opportunityMeasurement.selfOpportunityRate+p.opportunityMeasurement.passOpportunityRate;byId[p.playerId]=r;}
 const rows=Object.values(byId),prior=rows.reduce((s,r)=>s+r.threeMakes,0)/rows.reduce((s,r)=>s+r.minutes,0);
 for(const r of rows)r.spacing=r.attempts>=100&&r.threeAttempts===0?0:(r.threeMakes+60*prior)/(r.minutes+60);
 const pool=rows.filter(r=>r.minutes>=500);if(pool.length<5)throw Error('Insufficient observed context reference');
 return {byId,priorMinutes:60,minimumReferenceMinutes:500,priorThreeMakesPerMinute:prior,pools:Object.fromEntries(['spacing','self','creation'].map(k=>[k,pool.map(r=>r[k])]))};
}
export function attachCreationContext(players,reference){
 for(const p of players){
  const source=reference.byId[p.playerId]??{
   spacing:p.offenseMeasurement.attempts/p.offenseMeasurement.minutes*p.shotProfile.threeRate*M.interpolate(p.long,C.CURVE_3PT),
   self:p.shotCreationMeasurement.selfMakesPerMinute,creation:p.opportunityMeasurement.selfOpportunityRate+p.opportunityMeasurement.passOpportunityRate};
  if(![source.spacing,source.self,source.creation].every(x=>Number.isFinite(x)&&x>=0))throw Error('Missing measured context production');
  p.creationContextMeasurement={spacing:rating(source.spacing,reference.pools.spacing),self:rating(source.self,reference.pools.self),creation:rating(source.creation,reference.pools.creation),
   sourceLong:p.long,sourceMid:p.mid,sourceDouble:M.doubleThreat(p),sourceCreation:M.selfCreation(p),rates:{spacing:source.spacing,self:source.self,creation:source.creation},
   definition:'Observed 3PM/min, fresh self-made FG/min, and self+pass creation opportunities/min. Production/role proxies, not measured off-ball movement, speed, handling ability or double-team tracking.'};
 }
 return players;
}
export function measuredShootingThreat(p){const m=p.creationContextMeasurement;return m?m.spacing+C.SPACING_W.long*(p.long-m.sourceLong)+C.SPACING_W.mid*(p.mid-m.sourceMid):M.shootingThreat(p);}
export function measuredScoringThreat(p){const m=p.creationContextMeasurement;return m?m.self+M.doubleThreat(p)-m.sourceDouble:M.doubleThreat(p);}
export function measuredCreation(p){const m=p.creationContextMeasurement;return m?m.creation+M.selfCreation(p)-m.sourceCreation:M.selfCreation(p);}
export function measuredContext(lineup,i){
 const old=M.teammateContext(lineup,i),others=lineup.filter((_,j)=>j!==i),peer=Math.max(...others.map(measuredScoringThreat));
 const rel=measuredScoringThreat(lineup[i])-(C.DOUBLE_PEER_MIX*peer+(1-C.DOUBLE_PEER_MIX)*C.ATTR_MIDPOINT),brk=(lineup[i].breakDbl??70)-70;
 const rate=C.DOUBLE_BASE*(1+Math.tanh(rel/C.DOUBLE_REL_SCALE)*C.DOUBLE_REL_SPAN)*(1-Math.tanh(brk/C.DOUBLE_BREAK_SCALE)*C.DOUBLE_BREAK_SPAN);
 return {...old,spacing:others.reduce((s,p)=>s+measuredShootingThreat(p),0)/others.length,
  gravity:Math.max(...others.map(p=>Math.max(measuredShootingThreat(p),measuredScoringThreat(p)))),dblPeer:peer,
  create:C.weightedTop(others.map(measuredCreation),C.COMPOSITE.ctxCreate),defensiveDoubleRate:clamp(rate,...C.DOUBLE_CLAMP)};
}

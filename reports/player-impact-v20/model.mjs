import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {defenseProbabilities as previousProbability} from '../../src/defense_probability.js';

export function contestDeltas(lineup){
 if(lineup.length!==5)throw Error('Need five defensive players');
 const result={long:0,short:0};
 for(const p of lineup){
  const m=p.defenseExposureMeasurement;
  if(!m)throw Error('Missing tracking contest exposure');
  for(const [z,k,curve]of [['long','onBall',C.CURVE_DEF_3PT],['short','help',C.CURVE_DEF_RIM]]){
   const rate=m[z].rate,den=m.leagueAttemptsPerTeamMinute[z];
   if(!Number.isFinite(rate)||rate<0||!Number.isFinite(den)||den<=0||!Number.isFinite(p[k]))throw Error('Invalid tracking contest units');
   result[z]+=rate*(M.interpolate(p[k],curve)-M.interpolate(70,curve))/den;
  }
 }
 // No midrange tracking was supplied. Retain the existing explicit midpoint
 // proxy, with its inputs now gated by their measured contest exposure.
 result.mid=(result.long+result.short)*.5*C.DEF_MID_SCALE;
 return result;
}

export function exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup){
 const delta=contestDeltas(lineup);
 const q=previousProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,phys,opts);
 const zones=[['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']];
 const make={...q.make},shot=Math.max(0,1-q.pTovTouch-q.pFoul);
 for(const[z,m,x]of zones){
  const limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)];
  make[z]=Math.max(limits[0],Math.min(limits[1],make[z]+delta[z]));
  q[m]=shot*q.zone[z]*make[z];q[x]=shot*q.zone[z]*(1-make[z]);
 }
 q.make=make;q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+q.pFoul*C.FT_ATTEMPTS*q.ftPct;
 return q;
}

export function exposureFourthProbability(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){
 if(opt.neutralContests||opt.rimSignal||opt.zoneSignal)throw Error('Exposure defense must not overlap legacy replacement signals');
 return exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup);
}

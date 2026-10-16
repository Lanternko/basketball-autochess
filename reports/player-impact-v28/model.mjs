// Preserve the existing source shrinkage instead of clipping its probability
// effect through the display-attribute inverse/forward round trip.
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {defenseProbabilities as baseProbability,pressureSignal} from '../../src/defense_probability.js';
import {measuredTerminalRisk} from '../player-impact-v21/model.mjs';

export function contestDeltas(lineup){
 if(lineup.length!==5)throw Error('Need five defensive players');
 const result={long:0,short:0};
 for(const p of lineup){
  const m=p.defenseExposureMeasurement;if(!m)throw Error('Missing contest exposure');
  for(const[z,k,curve]of [['long','onBall',C.CURVE_DEF_3PT],['short','help',C.CURVE_DEF_RIM]]){
   const source=m[z],den=m.leagueAttemptsPerTeamMinute[z];
   if(!Number.isFinite(source.rate)||source.rate<0||!Number.isFinite(den)||den<=0)throw Error('Invalid contest units');
   let difference=M.interpolate(p[k],curve)-M.interpolate(70,curve);
   // Only actual measured cards receive the probability residual. Synthetic
   // mean70 profiles keep their normalized curves; missing tracking is neutral.
   if(!source.sourceMissing&&source.attempts>0&&Number.isFinite(source.rawDifference)&&Number.isFinite(source.sourceAttribute)){
    const posterior=source.rawDifference*source.attempts/(source.attempts+200);
    difference+=posterior-M.interpolate(source.sourceAttribute,curve);
   }
   result[z]+=source.rate*difference/den;
  }
 }
 result.mid=(result.long+result.short)*.5*C.DEF_MID_SCALE;return result;
}

export function exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup){
 const delta=contestDeltas(lineup),q=baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,phys,opts);
 const make={...q.make},shot=Math.max(0,1-q.pTovTouch-q.pFoul);
 for(const[z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){
  const limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)];
  make[z]=Math.max(limits[0],Math.min(limits[1],make[z]+delta[z]));q[m]=shot*q.zone[z]*make[z];q[x]=shot*q.zone[z]*(1-make[z]);
 }
 q.make=make;q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+q.pFoul*C.FT_ATTEMPTS*q.ftPct;return q;
}

export function terminalDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){
 if(!opt.measuredTouchTurnovers||opt.liveSignal||opt.neutralContests||opt.rimSignal||opt.zoneSignal)throw Error('Measured defense overlap');
 const q=exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup),risk=measuredTerminalRisk(handler.terminalRiskMeasurement,pressureSignal(lineup,opt.stealPriorRate).relative);
 const conditionalFoul=q.pFoul/(1-q.pTovTouch);q.pTovTouch=q.TOV=risk.total;q.pFoul=q.FOUL=(1-risk.total)*conditionalFoul;q.measuredTouchLiveShare=risk.liveShare;
 const shot=1-q.pTovTouch-q.pFoul;
 for(const[z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){q[m]=shot*q.zone[z]*q.make[z];q[x]=shot*q.zone[z]*(1-q.make[z]);}
 q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+q.pFoul*C.FT_ATTEMPTS*q.ftPct;return q;
}

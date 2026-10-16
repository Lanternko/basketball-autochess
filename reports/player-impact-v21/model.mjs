import {exposureDefenseProbabilities} from '../player-impact-v20/model.mjs';
import {pressureSignal} from '../../src/defense_probability.js';
import * as C from '../../src/constants.js';

export function measuredTerminalRisk(measurement,relative){
 if(!measurement||!Number.isFinite(relative)||relative<.4||relative>1.8)throw Error('Missing measured terminal risk or invalid pressure');
 const dead=measurement.deadProbability,live=measurement.neutralLiveProbability*relative,total=dead+live;
 if(![dead,live,total].every(Number.isFinite)||dead<0||live<0||total>=.95)throw Error('Invalid measured terminal probabilities');
 return {dead,live,total,liveShare:total?live/total:0};
}
export function terminalDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){
 if(!opt.measuredTouchTurnovers||opt.liveSignal||opt.neutralContests||opt.rimSignal||opt.zoneSignal)throw Error('Measured terminal mode must not overlap legacy replacement signals');
 const q=exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup);
 const risk=measuredTerminalRisk(handler.terminalRiskMeasurement,pressureSignal(lineup,opt.stealPriorRate).relative);
 // Preserve the conditional foul branch and every shooting/zone/context input.
 // Runtime uses observedFoulInputs for classified shooting fouls, independently.
 const conditionalFoul=q.pFoul/(1-q.pTovTouch);
 q.pTovTouch=q.TOV=risk.total;q.pFoul=q.FOUL=(1-risk.total)*conditionalFoul;
 q.measuredTouchLiveShare=risk.liveShare;
 const shot=1-q.pTovTouch-q.pFoul;
 for(const[z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){
  q[m]=shot*q.zone[z]*q.make[z];q[x]=shot*q.zone[z]*(1-q.make[z]);
 }
 q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+q.pFoul*C.FT_ATTEMPTS*q.ftPct;
 return q;
}

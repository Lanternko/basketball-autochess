import * as M from './probability_model.js';
import * as C from './constants.js';

export const DEFENSE_COUNT_KEYS=['liveTov','deadTov','clockTov','touchTov','passSteals','touchSteals','mida','midm','rima','rimm','xfgm','x3m','regulationSeconds'];
const bounded=(n,lo,hi)=>Math.max(lo,Math.min(hi,n));
// NBA FG% is conditional on a recorded FGA. A missed shooting-foul attempt is
// excluded from FGA. Sampling that FG% before excluding foul misses inflates
// recorded accuracy: recorded = raw / (1 - foul * (1 - raw)).
export function attemptMakeProbability(recordedMake,foulProbability){
  if(!Number.isFinite(recordedMake)||recordedMake<0||recordedMake>1||!Number.isFinite(foulProbability)||foulProbability<0||foulProbability>=1)throw new Error('Invalid conditional shooting inputs');
  return recordedMake*(1-foulProbability)/(1-recordedMake*foulProbability);
}
export function stealRate(player,priorRate,priorMinutes=240){
  if(!Number.isFinite(priorRate)||priorRate<=0)throw new Error('Need a measured league steal/minute prior');
  const measurement=player.defenseMeasurement;
  if(!measurement)return priorRate;
  if(!Number.isFinite(measurement.minutes)||measurement.minutes<0||!Number.isFinite(measurement.steals)||measurement.steals<0)throw new Error('Invalid defensive measurement');
  return (measurement.steals+priorMinutes*priorRate)/(measurement.minutes+priorMinutes);
}
export function pressureSignal(defense,priorRate){
  const rates=defense.map(p=>stealRate(p,priorRate));
  const relative=bounded(rates.reduce((n,r)=>n+r,0)/(defense.length*priorRate),.4,1.8);
  return {relative,attribute:70+25*Math.log(relative),weights:rates};
}
export function defenseProbabilities(handler,ctx,defender,help,offReb,defReb,defPhys,opts){
  let p=M.possessionProbabilities(handler,ctx,defender,help,offReb,defReb,defPhys,opts);
  if(opts.contextLongScale!==undefined||opts.contextShortScale!==undefined){
    const base=M.possessionProbabilities(handler,ctx,defender,help,offReb,defReb,defPhys,{...opts,contextScale:0});
    const full=M.possessionProbabilities(handler,ctx,defender,help,offReb,defReb,defPhys,{...opts,contextScale:1});
    p={...base,make:{...base.make},zone:{...base.zone}};
    for(const [zone,scale] of [['long',opts.contextLongScale??opts.contextScale??1],['short',opts.contextShortScale??opts.contextScale??1]]){
      if(!Number.isFinite(scale)||scale<0||scale>1)throw new Error('Invalid zone context coefficient');
      p.make[zone]=base.make[zone]+scale*(full.make[zone]-base.make[zone]);
    }
    // NBA shot profiles have unconstrained measured zone priors. Preserve the
    // same accessibility factors and change only the EV term of zone weights.
    // For missing profiles keep the base bounded prior rather than undo caps.
    if(Number.isFinite(handler.shotProfile?.threeRate)){
      const zones=['long','mid','short'],weights=zones.map(z=>base.zone[z]*Math.exp((z==='long'?3:2)*(p.make[z]-base.make[z])/C.EV_TEMP));
      const total=weights.reduce((a,b)=>a+b,0);zones.forEach((z,i)=>{p.zone[z]=weights[i]/total;});
    }
    rebuildExpectedEvents(p,p.TOV,p.FOUL);
  }
  if(opts.turnoverMode!=='pressure')return p;
  // Decouple turnover pressure from the 3-point contest attribute. This corrects
  // the existing pressure multiplier, without adding another turnover branch.
  const newFactor=1+M.tanhEff(opts.pressureAttribute,45)*.35;
  const consistent=Number.isFinite(handler.shotProfile?.freeThrowsPerAttempt);
  const limits=C.CLAMP.tov;
  let hazard=M.interpolate(handler.tovSkill??70,C.CURVE_TOV)*newFactor*(opts.turnoverScale??1);
  if(consistent)hazard*=C.HANDLER_TOV_SCALE;
  hazard=bounded(hazard,...limits);
  p.pTovTouch=consistent?hazard:bounded(hazard*C.HANDLER_TOV_SCALE,...limits);
  const fta=handler.shotProfile?.freeThrowsPerAttempt;
  if(Number.isFinite(fta))p.pFoul=bounded((1-p.pTovTouch)*fta/(C.FT_ATTEMPTS+fta),...C.CLAMP.foul);
  rebuildExpectedEvents(p,p.pTovTouch,p.pFoul);
  return p;
}
function rebuildExpectedEvents(p,tov,foul){
  const shot=Math.max(0,1-tov-foul);
  p.TOV=tov;p.FOUL=foul;
  for(const [zone,made,miss] of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){
    p[made]=shot*p.zone[zone]*p.make[zone];p[miss]=shot*p.zone[zone]*(1-p.make[zone]);
  }
  p.ev=p.FG3M*3+(p.MIDM+p.RIMM)*2+p.FOUL*C.FT_ATTEMPTS*p.ftPct;
}
export function passPressureDefender(defender,lineup,priorRate){
  return {...defender,onBall:pressureSignal(lineup,priorRate).attribute};
}
export function touchStealProbability(defense,priorRate,baseShare){
  return bounded(baseShare*pressureSignal(defense,priorRate).relative,0,.95);
}
export function volumeWeights(lineup,kind='touch'){
  return lineup.map(p=>{
    const m=p.offenseMeasurement;
    if(!m||!Number.isFinite(m.minutes)||m.minutes<=0)throw new Error('Volume selection needs measured offense/minutes');
    const count=kind==='shot'?m.attempts:m.attempts+.44*m.freeThrows+m.turnovers;
    if(!Number.isFinite(count)||count<0)throw new Error('Invalid offensive volume');
    return Math.max(.005,count/m.minutes);
  });
}

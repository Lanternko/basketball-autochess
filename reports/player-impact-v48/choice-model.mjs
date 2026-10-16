import {terminalDefenseProbabilities as previousTerminal,exposureDefenseProbabilities} from '../player-impact-v47/model.mjs';
import {collapseZone} from '../player-impact-v45/model.mjs';
export {exposureDefenseProbabilities};
const logit=p=>Math.log(p/(1-p)),sigmoid=x=>1/(1+Math.exp(-x));
export function offensiveChoicePlan(p,handler,offense,putback){
 const m=handler.offensiveChoiceMeasurement;if(!m||putback)return p;
 if(!p.finePlan||offense?.length!==5||new Set(offense.map(p=>p.playerId)).size!==5||!offense.some(p=>p.playerId===handler.playerId)||offense.some(p=>!p.offensiveChoiceMeasurement))throw Error('Missing offensive choice five');
 const zone={...p.finePlan.zone},two=zone.ra+zone.paint+zone.mid,oldPaint=(zone.ra+zone.paint)/two,oldRa=zone.ra/(zone.ra+zone.paint),delta=k=>m.shooterDelta[k]+offense.filter(p=>p.playerId!==handler.playerId).reduce((s,p)=>s+p.offensiveChoiceMeasurement.teammateLogits[k],0),paint=sigmoid(logit(oldPaint)+delta('paintGivenTwo')),ra=sigmoid(logit(oldRa)+delta('raGivenPaint'));
 zone.ra=two*paint*ra;zone.paint=two*paint*(1-ra);zone.mid=two*(1-paint);
 return {...p,defensiveZone:collapseZone(zone),finePlan:{...p.finePlan,zone}};
}
export function terminalDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){return offensiveChoicePlan(previousTerminal(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt),handler,opts.offensiveLineup,opts.putback);}

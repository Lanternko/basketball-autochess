import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {spaceProbability as syntheticProbability} from '../player-impact-v7/model.mjs';
import {freshZoneProbability} from '../player-impact-v5/model.mjs';
import {opportunityPlan as terminalPlan} from '../player-impact-v6/model.mjs';
import {opportunityPlan as supplyPlan} from '../player-impact-v11/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
export function opportunityPlan(ls,p,pressure,policy){return policy==='threat-flow'?terminalPlan(ls,p,pressure):supplyPlan(ls,p,pressure,'supply-creation');}
export function centeredMake(p,player,policy){
 const m=player.shootingMeasurement,context=m.contexts?.[policy],eff=player._eff??1;if(!context||!Number.isFinite(eff)||eff<=0)throw Error('Missing frozen source context or stamina multiplier');
 const curves={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT};
 return Object.fromEntries(Object.keys(curves).map(z=>{
  if(![m.rates[z],m.sourceBase[z],context[z],player[z],p.make[z]].every(Number.isFinite))throw Error('Invalid centered shooting input');
  const fatigueCorrection=M.interpolate(player[z]/eff,curves[z])-M.interpolate(player[z],curves[z]);
  const value=p.make[z]+m.rates[z]-m.sourceBase[z]+fatigueCorrection-context[z],limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)];
  return[z,Math.max(limits[0],Math.min(limits[1],value))];
 }));
}
export function spaceProbability(p,player,putback,opt){
 if(!player.shootingMeasurement||putback)return syntheticProbability(p,player,putback,opt);
 return freshZoneProbability({...p,make:centeredMake(p,player,opt.creationPolicy)},player,false);
}

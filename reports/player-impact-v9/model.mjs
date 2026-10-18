import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {opportunityPlan as terminalPlan} from '../player-impact-v6/model.mjs';
import {opportunityPlan as elasticPlan} from '../player-impact-v8/model.mjs';
import {freshZoneProbability} from '../player-impact-v5/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
export function opportunityPlan(ls,p,pressure,policy){return policy==='roundtrip-flow'?terminalPlan(ls,p,pressure):elasticPlan(ls,p,pressure,'elastic-creation');}
const curves={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT};
export function roundTripMake(p,player){
 const m=player.shootingMeasurement;if(!m)return {...p.make}; // Mean70 synthetic profiles keep their actual attribute curves.
 const eff=player._eff??1;if(!Number.isFinite(eff)||eff<=0)throw Error('Invalid shooting stamina multiplier');
 return Object.fromEntries(Object.keys(curves).map(z=>{
  if(!Number.isFinite(m.rates[z])||!Number.isFinite(m.sourceBase[z]))throw Error('Invalid source shooting baseline');
  // Recorded season FG already averages real fatigue. Remove that duplicate
  // reduction, while retaining changes to the current player's shooting attrs.
  // The source baseline is frozen: replacing the current attr must still matter.
  const fatigueCorrection=M.interpolate(player[z]/eff,curves[z])-M.interpolate(player[z],curves[z]);
  const value=p.make[z]+m.rates[z]-m.sourceBase[z]+fatigueCorrection;
  return[z,Math.max(C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)][0],Math.min(C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)][1],value))];
 }));
}
export function spaceProbability(p,player,putback,opt){
 // Immediate putbacks are generated separately and have no fresh-shot baseline.
 const make=putback?{...p.make}:roundTripMake(p,player);
 make.long=Math.max(.05,Math.min(.62,make.long-(opt.spaceCenter??0)));
 const r=freshZoneProbability({...p,make},player,false),zone=putback?{long:0,mid:0,short:1}:r.zone,shot=Math.max(0,1-r.pTovTouch-r.pFoul);
 for(const[z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){r[m]=shot*zone[z]*r.make[z];r[x]=shot*zone[z]*(1-r.make[z]);}
 r.zone=zone;r.ev=r.FG3M*3+(r.MIDM+r.RIMM)*2+r.pFoul*2*r.ftPct;return r;
}

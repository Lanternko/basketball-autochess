import {interpolate} from '../../src/probability_model.js';
import {CURVE_FT,ATTR_MIDPOINT} from '../../src/constants.js';
const clamp=p=>Math.max(.30,Math.min(.98,p));
const logit=p=>Math.log(p/(1-p)),sigmoid=x=>1/(1+Math.exp(-x));
export function measuredFreeThrowPercentage(player){
 const legacy=clamp(interpolate(player.ft??ATTR_MIDPOINT,CURVE_FT)),m=player.freeThrowAccuracyMeasurement;
 if(!m)return legacy;
 if(![m.probability,m.sourceProbability].every(p=>Number.isFinite(p)&&p>0&&p<1))throw Error('Invalid measured FT reference');
 // Keep the observed probability separate from its lossy display attribute.
 // Attribute changes still affect ability through the original curve's logit delta.
 return clamp(sigmoid(logit(m.probability)+logit(legacy)-logit(m.sourceProbability)));
}
export function withMeasuredFreeThrow(p,player){
 const ftPct=measuredFreeThrowPercentage(player);
 return {...p,ftPct,ev:p.ev+(p.pFoul??p.FOUL??0)*2*(ftPct-p.ftPct)};
}

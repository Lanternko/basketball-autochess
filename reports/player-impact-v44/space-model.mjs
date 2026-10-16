import {spaceProbability as previousSpace} from '../player-impact-v42/space-model.mjs';
import {applyRecordedZone} from '../player-impact-v42/choice-model.mjs';
import * as C from '../../src/constants.js';
export const logit=p=>{if(!(p>0&&p<1))throw Error('Need interior make probability');return Math.log(p)-Math.log1p(-p);};
export const logistic=x=>x>=0?1/(1+Math.exp(-x)):Math.exp(x)/(1+Math.exp(x));
export function transferredMake(raw,player,policy){
 const m=player.sourceMakeTransfer,ctx=m?.contexts?.[policy];if(!ctx)throw Error('Missing source logit centering');
 return Object.fromEntries(['long','mid','short'].map(z=>{
  const eta=logit(raw.make[z])+m.shooterLogits[z]-ctx[z],limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)];
  if(!Number.isFinite(eta))throw Error('Invalid source make transfer');
  return [z,Math.max(limits[0],Math.min(limits[1],logistic(eta)))];
 }));
}
export function spaceProbability(p,player,putback,opt){
 const q=previousSpace(p,player,putback,opt);if(putback)return q;
 return applyRecordedZone({...q,make:transferredMake(p,player,opt.creationPolicy)},p.defensiveZone);
}

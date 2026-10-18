import {spaceProbability as previousSpace} from '../player-impact-v42/space-model.mjs';
import {applyRecordedZone} from '../player-impact-v42/choice-model.mjs';
import {fineZones,coarseOf,collapseZone} from './model.mjs';
import {logit,logistic} from '../player-impact-v44/space-model.mjs';
export function transferredFineMake(p,player,policy){
 const ctx=player.fineDefenseMeasurement?.contexts?.[policy];if(!ctx||!p.finePlan)throw Error('Missing fine source context/plan');
 return Object.fromEntries(fineZones.map(z=>{
  const coarse=coarseOf[z],eta=logit(p.make[coarse])+p.finePlan.makeEta[z]-ctx[z];
  if(!Number.isFinite(eta))throw Error('Invalid fine transfer');return [z,Math.max(1e-6,Math.min(1-1e-6,logistic(eta)))];
 }));
}
export function spaceProbability(p,player,putback,opt){
 const q=previousSpace(p,player,putback,opt);if(putback)return q;
 const zone=p.finePlan.zone,fineMake=transferredFineMake(p,player,opt.creationPolicy),coarseZone=collapseZone(zone),make={long:0,mid:0,short:0};
 for(const z of fineZones)make[coarseOf[z]]+=zone[z]*fineMake[z];for(const z of Object.keys(make))make[z]/=coarseZone[z];
 return applyRecordedZone({...q,make,finePlan:{zone,make:fineMake}},coarseZone);
}

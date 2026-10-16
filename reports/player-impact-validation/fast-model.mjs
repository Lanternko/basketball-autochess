import {observedFoulInputs as compute} from '../player-impact-v5/model.mjs';
export {opportunityPlan,balancedReceivers,contestHelp,freshZoneProbability} from '../player-impact-v6/model.mjs';
const memo=new WeakMap();
export function observedFoulInputs(p,player,opt,attemptMakeProbability){
 const r=player.shotProfile.freeThrowsPerAttempt,old=memo.get(p);
 if(old?.r===r&&old.rates===opt.foulRates)return old.value;
 const value=compute(p,player,opt,attemptMakeProbability);memo.set(p,{r,rates:opt.foulRates,value});return value;
}

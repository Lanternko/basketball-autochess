import {offensiveReboundProbability,DEFAULT_OREB_SHARE,opportunityReboundWeights} from '../../../src/rebound_block_model.js';
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const logit=p=>Math.log(p/(1-p));
export const sigmoid=x=>1/(1+Math.exp(-x));
const neutral=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70}));
export function reboundChance(offense,defense,{zone,shooterIndex,oldChance,options}){
 let p=oldChance;
 if(options.individualOrebCard){
  const share=clamp(offense.reduce((s,p)=>s+p.individualOreb.share,0),.01,.95);
  const defend=offensiveReboundProbability(neutral,defense,{zone,shooterIndex:-1});
  p=sigmoid(logit(share)+logit(defend)-logit(DEFAULT_OREB_SHARE));
 }
 return clamp(sigmoid(logit(p)+(options.leagueOrbLogit??0)),.05,.60);
}
// Recipient allocation deliberately unchanged: this batch tests acquisition only.
export function reboundWeights(lineup,settings){return opportunityReboundWeights(lineup,settings);}

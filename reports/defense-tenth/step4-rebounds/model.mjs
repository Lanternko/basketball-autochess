// New experimental module; frozen rebound/game/season modules are never written.
import {offensiveReboundProbability,DEFAULT_OREB_SHARE,opportunityReboundWeights} from '../../../src/rebound_block_model.js';
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const logit=p=>Math.log(p/(1-p));
export const sigmoid=x=>1/(1+Math.exp(-x));
const neutral=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70}));
export function reboundChance(offense,defense,{zone,shooterIndex,oldChance,options}){
  let p=oldChance;
  if(options.individualDrebCard){
    const share=clamp(defense.reduce((s,p)=>s+p.individualDreb.share,0),.05,.95);
    // Preserve the old offensive contest relative to a canonical neutral defense.
    const attack=offensiveReboundProbability(offense,neutral,{zone,shooterIndex});
    p=sigmoid(logit(attack)-logit(DEFAULT_OREB_SHARE)-logit(share));
  }
  return clamp(sigmoid(logit(p)+(options.leagueOrbLogit??0)),.05,.60);
}
export function reboundWeights(lineup,settings,options){
  if(!options.individualDrebCard||settings.side!=='defense')return opportunityReboundWeights(lineup,settings);
  const sum=lineup.reduce((s,p)=>s+p.individualDreb.share,0);
  return lineup.map(p=>.30/lineup.length+.70*p.individualDreb.share/sum);
}

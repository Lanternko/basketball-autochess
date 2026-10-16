import {opportunityReboundWeights} from '../../../src/rebound_block_model.js';
export {reboundChance,logit,sigmoid} from '../step4-rebounds-oreb/model.mjs';
export function reboundWeights(lineup,settings,options={}){
 if(!options.individualOrebAllocation||settings.side!=='offense'||settings.freeThrow)return opportunityReboundWeights(lineup,settings);
 const shares=lineup.map(p=>p.individualOreb?.share);
 if(shares.some(x=>!Number.isFinite(x)||x<0))throw Error('Invalid individual OREB share');
 const sum=shares.reduce((s,x)=>s+x,0);if(!(sum>0))throw Error('Zero OREB share sum');
 return shares.map(x=>x/sum);
}

import {read} from '../scripts/defense_io.js';
// Ability estimators are independent from the frozen engine preset.
export function abilityJob(cutoff,{rolePrior=false,offenseResidual=false,neutralContests=false}={}){
 if(![25,41,55].includes(cutoff))throw Error('Need verified chronological cutoff');
 const cardVersion=rolePrior&&offenseResidual?'role-offense':rolePrior?'role':offenseResidual?'offense':undefined;
 return {cutoff,...(cardVersion?{cardVersion}:{}),options:{neutralContests}};
}
export function selectedAbilityJob(cutoff){const s=read('reports/defense-sixth/selection.json');return abilityJob(cutoff,{rolePrior:s.cardVersion==='role-offense',offenseResidual:true,neutralContests:s.neutral});}

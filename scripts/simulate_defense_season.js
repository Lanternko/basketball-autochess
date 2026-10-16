import {runDefenseSeason} from '../src/defense_validation.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {loadDefenseInputs,saveDefenseSeason} from './defense_io.js';
const args=process.argv.slice(2);
if(args.length&&!(args.length===2&&args[0]==='--seed'))throw new Error('Usage: simulate_defense_season.js [--seed INTEGER]');
const seed=args.length?Number(args[1]):20261012;
if(!Number.isInteger(seed)||seed<0||seed>0xffffffff)throw new Error('Invalid seed');
const inputs=loadDefenseInputs();
const run=runDefenseSeason(inputs.league,inputs.exposure,{seed,options:{...NBA_DEFENSE_V1,stealPriorRate:inputs.priorRate},replay:true,
  onProgress:n=>console.log('NBA defense v1 '+n+'/1230')});
console.log(saveDefenseSeason(run,inputs));

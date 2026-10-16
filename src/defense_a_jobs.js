import {loadDefenseInputs} from '../scripts/defense_io.js';
import {runDefenseSeason} from './defense_validation.js';
import {NBA_DEFENSE_V1} from './defense_presets.js';
import {runDefenseSeason as runASeason} from './defense_a_season.js';
import {read} from '../scripts/defense_io.js';
import {varianceJob} from './defense_a_variance.js';
import {stageAPreset,A_PRESET_NAMES} from './defense_a_presets.js';
let inputs;
export function executeJob(job){
  inputs??=loadDefenseInputs();
  if(job.kind==='variance')return varianceJob(inputs,job);
  if(job.kind!=='season')throw new Error('Unknown job kind');
  if(!['legacy','v1',...A_PRESET_NAMES].includes(job.preset))throw new Error('Unknown preset');
  const options=job.preset==='legacy'?{stealPriorRate:inputs.priorRate}:job.preset==='v1'?{...NBA_DEFENSE_V1,stealPriorRate:inputs.priorRate}:
    {...stageAPreset(job.preset,{rates:read('reports/defense-a/rebound-audit.json').rates,
      clock:job.preset.endsWith('-clock')?read('reports/defense-a/clock-calibration.json').selected:null}),stealPriorRate:inputs.priorRate};
  Object.assign(options,job.options??{});
  const engine=job.preset.startsWith('a-')?runASeason:runDefenseSeason;
  const run=engine(inputs.league,inputs.exposure,{seed:job.seed,indices:job.indices??null,options});
  return {...run,preset:job.preset};
}

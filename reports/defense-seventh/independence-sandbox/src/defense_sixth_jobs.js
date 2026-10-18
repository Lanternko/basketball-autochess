import {read} from '../scripts/defense_io.js';
import {fifthInputs} from './defense_fifth_jobs.js';
import {runDefenseSeason} from './defense_sixth_season.js';
export function sixthInputs(job){
 const base=fifthInputs({cutoff:job.cutoff,options:job.options??{}});
 if(job.cardVersion){const card=read(`reports/defense-sixth/pre${job.cutoff}-${job.cardVersion}-league.json`);base.league=card;
  if(card.sixthSignals)base.options.defenseSignals=card.sixthSignals;
 }
 return base;
}
export function executeSixthJob(job){const {league,exposure,options}=sixthInputs(job);
 return {...runDefenseSeason(league,exposure,{seed:job.seed,options,post41:true,cutoff:job.cutoff,phase:job.phase??'post',audit:true,replay:true}),preset:job.label,cutoff:job.cutoff,phase:job.phase??'post'};
}

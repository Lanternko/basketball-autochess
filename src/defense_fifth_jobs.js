import {read} from '../scripts/defense_io.js';
import {clockInputs} from './defense_clock_jobs.js';
import {fourthOptions} from './defense_fourth_jobs.js';
import {runDefenseSeason} from './defense_fifth_season.js';
import {NBA_DEFENSE_V3,NBA_DEFENSE_V3_HOLDOUT} from './defense_fifth_presets.js';
export function fifthInputs(job){
 const k=job.cutoff??0,{inputs}=clockInputs();
 const league=k?(k===41?read('reports/defense-fourth/pre41-league.json'):read('reports/defense-fifth/pre'+k+'-league.json')):inputs.league;
 let options=fourthOptions({label:job.oldSignal?'v1':'fifth',options:job.oldSignal?{}:(k?NBA_DEFENSE_V3_HOLDOUT:NBA_DEFENSE_V3)});
 if(k){options.seasonMinuteTargets=true;options.stealPriorRate=league.priorRate;options.foulProfileMeans=k===41?read('reports/defense-fourth/foul-profile-means.json').pre41:read('reports/defense-fifth/pre'+k+'-foul-means.json')['pre'+k];}
 if(k&&k!==41&&!job.oldSignal){
  const m=read('reports/defense-fifth/model-pre'+k+'/engine-signals.json');const shifts=read('reports/defense-fourth/normalization-pre41.json').shifts;
  options.defenseSignals={centers:Object.fromEntries(Object.entries(m.centers).map(([key,c])=>[key,c+(shifts[key]??0)])),values:Object.fromEntries(m.players.map((p,i)=>[p,Object.fromEntries(Object.entries(m.effects).map(([key,v])=>[key,v[i]]))]))};
 }
 return {league,exposure:inputs.exposure,options:{...options,...job.options}};
}
export function executeFifthJob(job){const {league,exposure,options}=fifthInputs(job);return {...runDefenseSeason(league,exposure,{seed:job.seed,options,indices:job.indices??null,post41:!!job.cutoff,cutoff:job.cutoff??41,audit:job.audit!==false}),preset:job.label,cutoff:job.cutoff??0};}

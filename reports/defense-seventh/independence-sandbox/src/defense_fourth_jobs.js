import fs from 'node:fs';
import {clockInputs} from './defense_clock_jobs.js';
import {thirdOptions} from './defense_third_jobs.js';
import {read} from '../scripts/defense_io.js';
import {runDefenseSeason} from './defense_fourth_season.js';
let models={};
function signals(mode){
  if(!models[mode]){const m=read('reports/defense-fourth/model-'+mode+'/engine-signals.json');models[mode]={centers:m.centers,values:Object.fromEntries(m.players.map((p,i)=>[p,Object.fromEntries(Object.entries(m.effects).map(([k,v])=>[k,v[i]]))]))};}return models[mode];
}
export function fourthOptions(job){
  const old=job.label==='v1'||job.oldSignal;
  const calibration=fs.existsSync('reports/defense-fourth/v2-calibration.json')?read('reports/defense-fourth/v2-calibration.json').selected:{};
  const base=old?thirdOptions('v1'):thirdOptions('combined',{...read('reports/defense-third/calibration-grid.json').selected,relativeFouls:true,continuousTiming:true,...calibration});
  const means=read('reports/defense-fourth/foul-profile-means.json');
  return {...base,foulProfileMeans:means.full,defenseSignals:signals(job.post41?'pre41':'full'),rotationCurve:read('reports/defense-fourth/rotation-curve.json'),...job.options};
}
export function executeFourthJob(job){
  const {inputs}=clockInputs();
  const league=job.post41?read('reports/defense-fourth/pre41-league.json'):inputs.league;
  const options=fourthOptions(job);
  if(job.post41){options.stealPriorRate=league.priorRate;options.seasonMinuteTargets=true;options.foulProfileMeans=read('reports/defense-fourth/foul-profile-means.json').pre41;}
  return {...runDefenseSeason(league,inputs.exposure,{seed:job.seed,options,indices:job.indices??null,audit:job.audit!==false,post41:!!job.post41}),preset:job.label};
}

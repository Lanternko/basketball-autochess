import fs from 'node:fs';
import {clockInputs,clockOptions} from './defense_clock_jobs.js';
import {read} from '../scripts/defense_io.js';
import {runDefenseSeason,checkDefenseAccounting} from './defense_third_season.js';
import {simulateDefenseThirdGame} from './defense_third_game.js';
import {thirdLineup} from './defense_third_minutes.js';
import {normalizeSimGame} from './defense_pbp_analysis.js';
export function thirdOptions(preset,extra={}){
  const {inputs}=clockInputs();const foul=read('reports/defense-third/foul-audit.json');
  const calibration=fs.existsSync('reports/defense-third/calibration.json')?read('reports/defense-third/calibration.json').selected:{};
  const flags={v1:{},accounting:{reboundAccounting:true},independent:{reboundAccounting:true,independentClock:true},empirical:{reboundAccounting:true,independentClock:true,empiricalTiming:true},fouls:{reboundAccounting:true,independentClock:true,empiricalTiming:true,foulOutcomes:true},combined:{reboundAccounting:true,independentClock:true,empiricalTiming:true,foulOutcomes:true,turnoverCategories:true}}[preset];
  if(!flags)throw Error('Unknown third preset '+preset);
  const base=clockOptions(flags.empiricalTiming?'c-empirical':flags.independentClock?'c-independent':flags.reboundAccounting?'a-instrumented':'v1-instrumented');
  const turnover=read('reports/defense-b1/turnover-types.json').groups;
  const leagueFTR=inputs.league.teams.reduce((n,t)=>n+t.roster.reduce((s,p)=>s+p.observed.FTA,0),0)/inputs.league.teams.reduce((n,t)=>n+t.roster.reduce((s,p)=>s+p.observed.FGA,0),0);
  return {...base,...flags,foulRates:foul.counts,leagueFTR,foulScale:1,passTurnoverScale:1.65,touchTurnoverScale:1.25,touchLiveShare:flags.turnoverCategories?.4:base.touchLiveShare,
    deadCategoryWeights:[turnover.offensiveFoul.dead,turnover.otherViolation.dead,turnover.passing.dead,turnover.handling.dead,turnover.outOfBoundsUnclassified.dead],
    ...(flags.empiricalTiming?{pace:.836}:{}),...(preset==='combined'?calibration:{}),...extra};
}
export function executeThirdJob(job){
  const {inputs}=clockInputs(),options=thirdOptions(job.preset,job.options??{});
  if(job.kind!=='replay')return {...runDefenseSeason(inputs.league,inputs.exposure,{seed:job.seed,options,indices:job.indices??null}),preset:job.label??job.preset};
  const teams=new Map(inputs.league.teams.map(t=>[t.id,t])),boxes=new Map(inputs.exposure.games.map(g=>[g.id,g]));
  const file='reports/defense-third/'+(job.label??job.preset)+'-replay-seed'+job.seed+'.jsonl',fd=fs.openSync(file,'w'),totals={};
  try{for(const [index,fixture] of inputs.league.schedule.entries()){
    const box=boxes.get(fixture.id),pair=[fixture.homeId,fixture.awayId].map((id,i)=>thirdLineup(teams.get(id),fixture[i?'awayPlayerIds':'homePlayerIds'],box.teams.find(t=>t.teamId===id),options.seasonMinuteTargets));
    const game=simulateDefenseThirdGame(...pair,{...options,replay:true,seed:(job.seed+Math.imul(index+1,7919))>>>0});checkDefenseAccounting(game);
    fs.writeSync(fd,JSON.stringify(normalizeSimGame(game,fixture,pair))+'\n');
    for(const s of [game.statA,game.statB])for(const [k,v] of Object.entries(s))if(Number.isFinite(v))totals[k]=(totals[k]??0)+v;
  }}finally{fs.closeSync(fd);}return {preset:job.preset,seed:job.seed,file,totals};
}

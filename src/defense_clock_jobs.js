import fs from 'node:fs';
import {loadDefenseInputs,read} from '../scripts/defense_io.js';
import {NBA_DEFENSE_V1} from './defense_presets.js';
import {stageAPreset} from './defense_a_presets.js';
import {runDefenseSeason,checkDefenseAccounting} from './defense_clock_season.js';
import {simulateDefenseClockGame} from './defense_clock_game.js';
import {observedLineup} from './minute_budget.js';
import {normalizeSimGame,varianceAnalysis} from './defense_pbp_analysis.js';
let inputs=null,timing=null;
export function clockInputs(){
  if(!inputs)inputs=loadDefenseInputs();
  if(!timing){const raw=read('reports/defense-b1/empirical-timing.json');timing={...raw,states:Object.fromEntries(Object.entries(raw.states).map(([k,a])=>[k,a.filter(x=>x>=.1).sort((a,b)=>a-b)]))};}
  return {inputs,timing};
}
export function clockOptions(preset,extra={}){
  const {inputs,timing}=clockInputs();
  const base=preset==='v1-instrumented'?NBA_DEFENSE_V1:stageAPreset('a-accounting-clock',{rates:read('reports/defense-a/rebound-audit.json').rates,clock:read('reports/defense-a/clock-calibration.json').selected});
  const empirical=['c-empirical','c-time-only'].includes(preset),independent=['c-empirical','c-independent'].includes(preset);
  if(!['v1-instrumented','a-instrumented','c-empirical','c-independent','c-time-only'].includes(preset))throw Error('Unknown clock preset');
  return {...base,stealPriorRate:inputs.priorRate,empiricalTiming:empirical,independentClock:independent,...(empirical?{pace:1,timingCDF:timing.states}:{}),clockViolationProbability:timing.clockViolationPerEligiblePossession??timing.clockViolationPerPossession,...extra};
}
export function executeClockJob(job){
  const {inputs}=clockInputs(),options=clockOptions(job.preset,job.options??{});
  if(job.kind!=='replay')return {...runDefenseSeason(inputs.league,inputs.exposure,{seed:job.seed,options,indices:job.indices??null}),preset:job.preset};
  const teams=new Map(inputs.league.teams.map(t=>[t.id,t])),boxes=new Map(inputs.exposure.games.map(g=>[g.id,g]));
  const games=[],totals={};const file='reports/defense-b1/'+job.preset+'-replay-seed'+job.seed+'.jsonl',fd=fs.openSync(file,'w');
  try{for(const [index,fixture] of inputs.league.schedule.entries()){
    const box=boxes.get(fixture.id),pair=[fixture.homeId,fixture.awayId].map((id,i)=>observedLineup(teams.get(id),fixture[i?'awayPlayerIds':'homePlayerIds'],box.teams.find(t=>t.teamId===id)));
    const game=simulateDefenseClockGame(...pair,{...options,replay:true,seed:(job.seed+Math.imul(index+1,7919))>>>0});checkDefenseAccounting(game);
    const normal=normalizeSimGame(game,fixture,pair);fs.writeSync(fd,JSON.stringify(normal)+'\n');games.push(normal);
    for(const s of [game.statA,game.statB])for(const [k,v] of Object.entries(s))if(Number.isFinite(v))totals[k]=(totals[k]??0)+v;
  }}finally{fs.closeSync(fd);}
  return {preset:job.preset,seed:job.seed,file,totals,analysis:varianceAnalysis(games)};
}

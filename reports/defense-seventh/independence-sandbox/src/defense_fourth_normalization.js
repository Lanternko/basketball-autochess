import {read,table} from '../scripts/defense_io.js';
import {teamDefenseMetrics,realCountStats,globalDefenseMetrics,runDefenseSeason} from './defense_fourth_season.js';
import {clockInputs} from './defense_clock_jobs.js';
import {fourthOptions} from './defense_fourth_jobs.js';
export function signalOptions(mode,shifts){
  const m=read('reports/defense-fourth/model-'+mode+'/engine-signals.json');
  return {values:Object.fromEntries(m.players.map((p,i)=>[p,Object.fromEntries(Object.entries(m.effects).map(([k,v])=>[k,v[i]]))])),centers:Object.fromEntries(Object.entries(m.centers).map(([k,v])=>[k,v+(shifts[k]??0)]))};
}
export function normalizationTarget(mode){
  const model=read('reports/defense-fourth/model-pre41/engine-signals.json'),train=new Set(model.trainGames),rows=table('data/season-source/team-games.json').filter(r=>mode==='full'||train.has(r.GAME_ID));
  const all=Object.fromEntries(['pts','fgm','fga','fg3m','fg3a','fta','oreb','dreb','tov','stl','blk','pf'].map(k=>[k,rows.reduce((n,r)=>n+(r[k.toUpperCase()]??0),0)]));
  const metrics=mode==='full'?clockInputs().inputs.target:teamDefenseMetrics(all,all,rows.length);let shortA=0,shortM=0,clock=0,pbpGames=0;
  for(const s of read('data/defense-a-source/manifest.json').sources)if(mode==='full'||train.has(s.id)){pbpGames++;for(const e of read(s.file).data.game.actions){if(e.actionType==='turnover'&&e.subType==='shot clock')clock++;if(e.isFieldGoal===1&&e.actionType==='2pt'&&e.area!=='Mid-Range'){shortA++;shortM+=e.shotResult==='Made';}}}
  return {...metrics,shortFG:shortM/shortA,clockTurnovers:clock/(2*pbpGames),teamGames:rows.length,trainingGames:mode==='full'?1230:train.size};
}
export function executeNormalizationJob({mode,seed,options}){
  const {inputs}=clockInputs(),league=mode==='full'?inputs.league:read('reports/defense-fourth/pre41-league.json');
  const opts=fourthOptions({label:'normalization',post41:mode==='pre41',options});
  let indices=null;if(mode==='pre41'){const train=new Set(read('reports/defense-fourth/model-pre41/engine-signals.json').trainGames);indices=league.schedule.flatMap((g,i)=>train.has(g.id)?[i]:[]);opts.seasonMinuteTargets=true;opts.stealPriorRate=league.priorRate;opts.foulProfileMeans=read('reports/defense-fourth/foul-profile-means.json').pre41;}
  const run=runDefenseSeason(league,inputs.exposure,{seed,options:opts,indices,audit:false});
  return {seed,metrics:globalDefenseMetrics(run),counts:Object.fromEntries(Object.keys(run.teams[0].stats).map(k=>[k,run.teams.reduce((s,t)=>s+t.stats[k],0)])),matches:run.matches.length};
}

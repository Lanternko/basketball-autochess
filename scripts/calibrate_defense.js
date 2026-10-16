import fs from 'node:fs';
import {runDefenseSeason,globalDefenseMetrics,teamDefenseMetrics} from '../src/defense_validation.js';
import {loadDefenseInputs,hash,codeFiles,read} from './defense_io.js';
const inputs=loadDefenseInputs(),indices=inputs.league.schedule.map((_,i)=>i).filter(i=>i%10===0);
const counts={pts:0,fga:0,fgm:0,fg3a:0,fg3m:0,oreb:0,dreb:0,tov:0,fta:0,stl:0};
const fields={pts:'points',fga:'fieldGoalsAttempted',fgm:'fieldGoalsMade',fg3a:'threePointersAttempted',fg3m:'threePointersMade',
  oreb:'reboundsOffensive',dreb:'reboundsDefensive',tov:'turnovers',fta:'freeThrowsAttempted',stl:'steals'};
for(const i of indices){
  const id=inputs.league.schedule[i].id,doc=read('data/defense-source/boxes/'+id+'.json'),box=doc.data.boxScoreTraditional??doc.data.game;
  for(const team of [box.homeTeam,box.awayTeam])for(const p of team.players)for(const [k,field] of Object.entries(fields))counts[k]+=p.statistics[field];
}
const target=teamDefenseMetrics(counts,counts,indices.length*2),trials=[];
// Predeclared objective: global FG / 3P accuracy and the same box-possession
// proxy. Do not fit points, player plus-minus, team wins or team-specific terms.
for(const contextLongScale of [0,.25,.5])for(const contextShortScale of [.25,.5,.75,1]){
  const pace=1.15;
  const options={minuteMode:'heuristic',observedTargets:true,excludeZeroTargets:true,turnoverMode:'pressure',foulConditioning:true,
    shotSelection:'volume',stealPriorRate:inputs.priorRate,touchLiveShare:.5,contextLongScale,contextShortScale,pace};
  const run=runDefenseSeason(inputs.league,inputs.exposure,{seed:731013,indices,options});
  const global=globalDefenseMetrics(run),loss=(global.fg-target.fg)**2+((global.three-target.three)/1.2)**2+((global.possessionsProxy-target.possessionsProxy)/2)**2;
  trials.push({contextLongScale,contextShortScale,pace,global,loss});
  console.log(JSON.stringify({contextLongScale,contextShortScale,pace,FG:global.fg,three:global.three,poss:global.possessionsProxy,PPG:global.ppg,loss}));
}
const best=[...trials].sort((a,b)=>a.loss-b.loss)[0];
const report={schemaVersion:1,scope:'Exploratory same-season calibration under normal dead-ball rotations, within-game fatigue and six-foul disqualification. Not held-out prediction.',
  objective:'(FG%-target)^2 + ((3P%-target)/1.2)^2 + ((boxPoss/G-target)/2)^2; no point, win or player +/- target',
  seed:731013,sampleGames:indices.length,indices,target,selected:{contextLongScale:best.contextLongScale,contextShortScale:best.contextShortScale,pace:best.pace},trials,
  provenance:{code:Object.fromEntries([...codeFiles.filter(f=>f!=='src/defense_presets.js'),'scripts/calibrate_defense.js'].map(f=>[f,hash(f)])),
    sources:Object.fromEntries(['data/season-league.json','data/defense-source/game-exposure.json'].map(f=>[f,hash(f)]))}};
fs.writeFileSync(new URL('../reports/defense-calibration.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log('Selected '+JSON.stringify(report.selected));

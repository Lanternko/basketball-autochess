import fs from 'node:fs';
import crypto from 'node:crypto';
import {defensiveMeasurements,runDefenseSeason,globalDefenseMetrics,boxPossessions} from '../src/defense_validation.js';
const read=f=>JSON.parse(fs.readFileSync(new URL('../'+f,import.meta.url)));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+f,import.meta.url))).digest('hex');
const set=read('data/benchmark-source/base.json').data.resultSets[0],rows=set.rowSet.map(r=>Object.fromEntries(set.headers.map((k,i)=>[k,r[i]])));
const {league,priorRate}=defensiveMeasurements(read('data/season-league.json'),rows),exposure=read('data/defense-source/game-exposure.json');
const indices=league.schedule.map((_,i)=>i).filter(i=>i%10===0);
let possessions=0;
for(const i of indices){
  const fixture=league.schedule[i],doc=read('data/defense-source/boxes/'+fixture.id+'.json'),box=doc.data.boxScoreTraditional??doc.data.game;
  const stats=[box.homeTeam,box.awayTeam].map(t=>Object.fromEntries([['fga','fieldGoalsAttempted'],['oreb','reboundsOffensive'],['tov','turnovers'],['fta','freeThrowsAttempted']].map(([key,field])=>[key,t.players.reduce((n,p)=>n+p.statistics[field],0)])));
  possessions+=boxPossessions(stats[0])+boxPossessions(stats[1]);
}
const target=possessions/(indices.length*2),trials=[];
for(const pace of [1,1.05,1.1,1.15,1.2,1.25,1.3]){
  const run=runDefenseSeason(league,exposure,{seed:731013,indices,options:{minuteMode:'budget',foulOut:99,turnoverMode:'pressure',foulConditioning:true,
    shotSelection:'volume',stealPriorRate:priorRate,touchLiveShare:.5,pace}});
  const global=globalDefenseMetrics(run);trials.push({pace,global,absolutePossessionError:Math.abs(global.possessionsProxy-target)});
  console.log(JSON.stringify({pace,possessions:global.possessionsProxy,target,FG:global.fg,PPG:global.ppg,clockTOV:global.clockTurnovers}));
}
const selected=[...trials].sort((a,b)=>a.absolutePossessionError-b.absolutePossessionError)[0].pace;
const result={schemaVersion:1,scope:'Exploratory retrospective clock calibration. Select pace only by box-possession proxy, not points, wins or OKC. Full-season input abilities still prevent held-out prediction claims.',
  sampleGames:indices.length,indices,seed:731013,targetPossessionsProxy:target,selectedPace:selected,trials,
  provenance:{sourceHashes:Object.fromEntries(['data/season-league.json','data/defense-source/game-exposure.json'].map(f=>[f,hash(f)])),
    codeHashes:Object.fromEntries(['src/defense_game.js','src/defense_probability.js','src/defense_validation.js','src/minute_budget.js','scripts/calibrate_defense_pace.js'].map(f=>[f,hash(f)]))}};
fs.writeFileSync(new URL('../reports/defense-pace-calibration.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log('Selected pace '+selected);

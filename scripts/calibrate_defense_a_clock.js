import fs from 'node:fs';
import {runJobs} from '../src/defense_a_pool.js';
import {teamDefenseMetrics,globalDefenseMetrics} from '../src/defense_validation.js';
import {read,hash,table} from './defense_io.js';
const league=read('data/season-league.json'),indices=league.schedule.map((_,i)=>i).filter(i=>i%10===0);
const counts={pts:0,fga:0,fgm:0,fg3a:0,fg3m:0,oreb:0,dreb:0,tov:0,fta:0,stl:0};
// Use the same official team-game count definitions as the scoreboard, including
// total team turnovers. CDN traditional turnovers can omit team turnovers.
const sampleIds=new Set(indices.map(i=>league.schedule[i].id));
for(const team of table('data/season-source/team-games.json').filter(t=>sampleIds.has(t.GAME_ID)))
  for(const key of Object.keys(counts))counts[key]+=team[key.toUpperCase()];
const target=teamDefenseMetrics(counts,counts,2*indices.length);
const jobs=['a-accounting','a-rebounds'].flatMap(preset=>[1.10,1.12,1.14,1.16,1.18,1.20,1.22].map(pace=>({kind:'season',preset,seed:731019,indices,options:{pace}})));
const runs=await runJobs(jobs,{onProgress:(n,total)=>console.log('Clock '+n+'/'+total)});
const trials=runs.map((r,i)=>({preset:jobs[i].preset,pace:jobs[i].options.pace,global:globalDefenseMetrics(r)}));
const selected=Object.fromEntries(['a-accounting','a-rebounds'].map(preset=>[preset,trials.filter(t=>t.preset===preset).sort((a,b)=>
  Math.abs(a.global.possessionsProxy-target.possessionsProxy)-Math.abs(b.global.possessionsProxy-target.possessionsProxy))[0].pace]));
const result={scope:'A3 retrospective clock-only calibration, no team or win fit; final FG/3P/TOV gates evaluated on complete four seeds afterwards.',
  objective:'Minimize absolute pooled box-possession proxy error on 123 interleaved games; no FG%, wins, OKC or efficiency target in selection.',
  seed:731019,indices,target,trials,selected,provenance:{sources:Object.fromEntries(['data/season-league.json','data/season-source/team-games.json','reports/defense-a/rebound-audit.json'].map(f=>[f,hash(f)])),
    code:Object.fromEntries(['src/defense_a_game.js','src/defense_a_season.js','src/defense_a_jobs.js','scripts/calibrate_defense_a_clock.js'].map(f=>[f,hash(f)]))}};
fs.writeFileSync(new URL('../reports/defense-a/clock-calibration.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({selected,target,trials},null,2));

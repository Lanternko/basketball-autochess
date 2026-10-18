import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadInput} from '../player-impact-v6/input.mjs';
import {impactEngine as originalEngine} from '../player-impact-v6/engine.mjs';
import {impactEngine} from './engine.mjs';
const oldRun=await originalEngine('terminal-flow'),newRun=await impactEngine('terminal-flow');let games=0,clocks=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),indices=Array.from({length:60},(_,i)=>i*19),a=oldRun(b.league,b.exposure,{seed:20261012,options:b.options,indices}),c=newRun(b.league,b.exposure,{seed:20261012,options:b.options,indices});
 assert.deepEqual(a.matches,c.matches);games+=indices.length;
 for(let t=0;t<a.teams.length;t++){
  const old=a.teams[t],team=c.teams[t];assert.deepEqual(old.stats,team.stats);assert.deepEqual(old.opponent,team.opponent);assert.equal(old.wins,team.wins);
  for(let i=0;i<old.players.length;i++){
   const p=old.players[i].stats,q=team.players[i].stats;clocks+=p.clockTov;
   for(const key of Object.keys(p))assert.equal(q[key],key==='clockTov'?0:['tov','deadTov'].includes(key)?p[key]-p.clockTov:p[key],season+' '+key);
  }
 }
 console.log(season,'60 games exact parity outside individual team-only turnover credits');
}
const out={games,clockViolationsReclassified:clocks,scoreAndTeamStatsExactParity:true,otherPlayerStatsExactParity:true,definition:'Individual TOV + team clock TOV = team TOV; all cached 2025-26 shot-clock PBP events have personId0.'};
fs.writeFileSync('reports/player-impact-team-clock/verification.json',JSON.stringify(out,null,2));console.log(out);

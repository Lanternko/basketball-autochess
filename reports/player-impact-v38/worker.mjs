import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parentPort} from 'node:worker_threads';
import {controlledInput} from './input.mjs';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
import {impactEngine as oldEngine} from '../player-impact-v30/engine.mjs';
import {impactEngine as nextEngine} from '../player-impact-v37/engine.mjs';
const inputs={v30:await controlledInput('v30'),v37:await controlledInput('v37')},runs={v30:await oldEngine('rotation-space',{game:true}),v37:await nextEngine('rotation-space',{game:true})},src=source();
const statKeys=['pts','ast','tov','stl','blk','oreb','dreb','fga','fgm','fg3a','fg3m','fta','ftm'];
const score=(g,side)=>side?g.scoreB-g.scoreA:g.scoreA-g.scoreB;
const win=margin=>margin>0?1:margin<0?0:.5;
parentPort.on('message',job=>{try{
 const x=inputs[job.variant],run=runs[job.variant];if(!x||!run)throw Error('Unknown variant');
 const p=x.players.find(p=>p.playerId===job.id),slot=x.roleMap.get(p.playerId).slot,e=src.players[p.playerId],cap=src.capMinutes;
 const arms=[['fullCapCounterfactual',cap],['supportedHealthy',e.supportedMinutes]];
 const rows=[],cache=new Map();let simulatedGames=0;
 for(const[arm,minutes]of arms){
  const tick=Math.round(minutes*600);
  if(cache.has(tick)){rows.push({...structuredClone(cache.get(tick)),arm,reusedIdenticalSchedule:true});continue;}
  const games=[];
  for(let opponent=0;opponent<x.opponents.length;opponent++)for(let i=0;i<job.samples;i++){
   const phase=i%2,a=workloadTeam(x,p,slot,minutes,cap,phase),base=workloadTeam(x,x.profiles[slot],slot,minutes,cap,phase),b=opponentTeam(x,x.opponents[opponent],cap,phase);
   const seed=(job.seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
   const pair=[];
   for(const side of [0,1]){
    const teams=side?[b.team,a.team]:[a.team,b.team],baseline=side?[b.team,base.team]:[base.team,b.team],schedules=side?[b.schedule,a.schedule]:[a.schedule,b.schedule];
    const g=run(...teams,options(x,seed,schedules)),h=run(...baseline,options(x,seed,schedules));simulatedGames+=2;
    const tag=side?'B':'A';
    for(const game of [g,h]){
     assert.equal(game.gameSeconds,2880);assert.equal(game.complete,true);
     assert.ok(Math.abs(game['players'+tag][slot].seconds-tick/10)<.011);
     for(const seat of ['A','B']){
      assert.equal(game['stat'+seat].pts,2*game['stat'+seat].fgm+game['stat'+seat].fg3m+game['stat'+seat].ftm);
      assert.ok(Math.abs(game['players'+seat].reduce((s,p)=>s+p.seconds,0)-14400)<.011);
      for(const k of statKeys){const teamOnly=k==='tov'?game['stat'+seat].clockTov:0;assert.equal(game['players'+seat].reduce((s,p)=>s+p[k],0)+teamOnly,game['stat'+seat][k]);}
     }
     assert.equal(game.statA.stl,game.statB.liveTov);assert.equal(game.statB.stl,game.statA.liveTov);
    }
    pair.push({side,margin:score(g,side),baselineMargin:score(h,side),win:win(score(g,side)),baselineWin:win(score(h,side)),
     playerMinutes:g['players'+tag][slot].seconds/60,playerStats:Object.fromEntries(statKeys.map(k=>[k,g['players'+tag][slot][k]]))});
   }
   games.push({opponent,seed,i,phase,pair});
  }
  const result={arm,minutes:tick/600,games};cache.set(tick,result);rows.push(result);
 }
 parentPort.postMessage({job,result:{variant:job.variant,playerId:p.playerId,name:p.name,position:x.profiles[slot].pos,slot,arms:rows,simulatedGames}});
}catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

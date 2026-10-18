// Same paired v47 simulation as worker.mjs, but seed indices start at job.start so new
// draws continue the original sequence (original run used i = 0..3).
import {parentPort} from 'node:worker_threads';
import {ovrInput} from './input.mjs';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
import {impactEngine} from '../player-impact-v47/engine.mjs';
const x=await ovrInput(),run=await impactEngine('rotation-space',{game:true}),src=source();
const score=(g,side)=>side?g.scoreB-g.scoreA:g.scoreA-g.scoreB;
parentPort.on('message',job=>{try{
 const p=x.players.find(p=>p.playerId===job.id),slot=x.roleMap.get(p.playerId).slot,cap=src.capMinutes,minutes=src.players[p.playerId].supportedMinutes;
 const draws=[];
 for(let opponent=0;opponent<x.opponents.length;opponent++)for(let i=job.start;i<job.start+job.samples;i++){
  const phase=i%2,a=workloadTeam(x,p,slot,minutes,cap,phase),base=workloadTeam(x,x.profiles[slot],slot,minutes,cap,phase),b=opponentTeam(x,x.opponents[opponent],cap,phase);
  const seed=(job.seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
  let margin=0,baselineMargin=0;
  for(const side of [0,1]){
   const teams=side?[b.team,a.team]:[a.team,b.team],baseline=side?[b.team,base.team]:[base.team,b.team],schedules=side?[b.schedule,a.schedule]:[a.schedule,b.schedule];
   const g=run(...teams,options(x,seed,schedules)),h=run(...baseline,options(x,seed,schedules));
   if(g.gameSeconds!==2880||h.gameSeconds!==2880||!g.complete||!h.complete)throw Error('Incomplete game');
   margin+=score(g,side)/2;baselineMargin+=score(h,side)/2;
  }
  draws.push([opponent,i,margin,baselineMargin]);
 }
 parentPort.postMessage({job,result:{playerId:p.playerId,name:p.name,position:x.profiles[slot].pos,minutes:Math.round(minutes*600)/600,draws}});
}catch(e){parentPort.postMessage({job,error:e.stack});}});

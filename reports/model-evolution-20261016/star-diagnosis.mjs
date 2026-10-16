import fs from 'node:fs';
import assert from 'node:assert/strict';
import {ovrInput} from '../player-impact-v41/ovr-input.mjs';
import {impactEngine} from '../player-impact-v41/engine.mjs';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
const root='reports/model-evolution-20261016',x=await ovrInput(),run=await impactEngine('rotation-space',{game:true});
const protocol=JSON.parse(fs.readFileSync(root+'/latest-full-ovr/healthy-protocol.json'));
const ranks=JSON.parse(fs.readFileSync(root+'/latest-full-ovr/ranking.json')).players;
const src=source(),out=[];
for(const name of ['Stephen Curry','Cade Cunningham','Victor Wembanyama','Mitchell Robinson']){
 const p=x.players.find(p=>p.name===name),rank=ranks.find(r=>r.playerId===p.playerId),slot=x.roleMap.get(p.playerId).slot,minutes=src.players[p.playerId].supportedMinutes,cap=src.capMinutes;
 let own=0,opp=0,n=0;
 for(let opponent=0;opponent<x.opponents.length;opponent++)for(let i=0;i<protocol.samples;i++){
  const phase=i%2,a=workloadTeam(x,p,slot,minutes,cap,phase),base=workloadTeam(x,x.profiles[slot],slot,minutes,cap,phase),b=opponentTeam(x,x.opponents[opponent],cap,phase);
  const seed=(protocol.seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
  for(const side of [0,1]){
   const schedules=side?[b.schedule,a.schedule]:[a.schedule,b.schedule];
   const g=run(...(side?[b.team,a.team]:[a.team,b.team]),options(x,seed,schedules));
   const h=run(...(side?[b.team,base.team]:[base.team,b.team]),options(x,seed,schedules));
   own+=(side?g.scoreB:g.scoreA)-(side?h.scoreB:h.scoreA);
   opp+=(side?g.scoreA:g.scoreB)-(side?h.scoreA:h.scoreB);n++;
  }
 }
 assert.ok(Math.abs((own-opp)/n-rank.healthy.meanContribution)<1e-10);
 const row={name,rank:rank.rank,minutes,ownScoreDelta:own/n,opponentScoreDelta:opp/n,netContribution:(own-opp)/n,matchedFullRanking:true,
  attributes:Object.fromEntries(['long','mid','short','offBall','screen','handle','breakDbl','onBall','help','physique'].map(k=>[k,p[k]])),
  context:p.creationContextMeasurement,defense:p.freshDefenseMeasurement,opportunities:p.opportunityMeasurement,shooting:p.shootingMeasurement,role:x.roleMap.get(p.playerId)};
 out.push(row);console.log(JSON.stringify({name,ownScoreDelta:own/n,opponentScoreDelta:opp/n,netContribution:row.netContribution}));
 fs.writeFileSync(root+'/star-diagnosis.json',JSON.stringify({season:'2025-26',description:'Exact replay of ranking protocol; score deltas include possession changes, not per-possession offensive/defensive causal effects.',players:out},null,2));
}

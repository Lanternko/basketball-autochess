import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput as previousInput} from '../player-impact-v30/input.mjs';
import {loadInput} from './input.mjs';
import {ovrInput} from '../player-impact-v30/ovr-input.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
import {supplyFlow} from '../player-impact-v11/model.mjs';
import {sourceFlow} from './model.mjs';
const root='reports/player-impact-v37',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=[],inputs=[],transportSamples=[];let cards=0,teamCards=0,totalStates=0;
function evaluate(ps,sampleTag=null){
 const ls=elasticLineup(ps,'elastic-creation'),old=supplyFlow(ls),flow=sourceFlow(ls);
 for(let i=0;i<5;i++){
  const m=ls[i].opportunityMeasurement;
  assert.ok(flow.self[i]>0);
  if(flow.branch==='fixed-pass-rows')assert.ok(Math.abs(flow.rows[i]-old.rows[i])<1e-8);
  assert.ok(Math.abs(flow.self[i]+flow.incoming[i]-m.terminalOpportunityRate)<1e-8);
  assert.equal(flow.matrix[i][i],0);
 }
 assert.ok(Math.abs(flow.self.reduce((s,v)=>s+v,0)+flow.rows.reduce((s,v)=>s+v,0)-old.terminal.reduce((s,v)=>s+v,0))<1e-8);
 if(sampleTag||flow.branch==='relaxed-source-columns')transportSamples.push({tag:sampleTag,branch:flow.branch,oldRows:old.rows,ownPool:flow.ownPool,prior:flow.prior,playerIds:ls.map(p=>p.playerId),measurements:ls.map(p=>p.opportunityMeasurement),joint:flow.joint,terminal:flow.terminal});
 return ls.map((p,i)=>({playerId:p.playerId,sourceSelf:p.opportunityMeasurement.selfOpportunityRate,sourceReceive:p.opportunityMeasurement.receiveOpportunityRate,terminal:flow.terminal[i],incoming:flow.incoming[i],previousAssignedSelf:old.self[i],assignedSelf:flow.self[i],addedSelf:flow.self[i]-old.self[i],previousPass:old.rows[i],assignedPass:flow.rows[i],branch:flow.branch}));
}
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const before=structuredClone(previousInput(season)),current=loadInput(season),ctx=read(`${root}/${season}-contexts.json`),prior=read(`reports/player-impact-v30/${season}-contexts.json`);
 for(const k of ['states','stints','strictMinutes','contextReference'])assert.deepEqual(ctx[k],prior[k]);
 for(const k of ['options','exposure'])assert.deepEqual(current[k],before[k]);assert.deepEqual(current.league.schedule,before.league.schedule);
 totalStates+=ctx.states;cards+=Object.keys(ctx.cards).length;const teams=new Map();
 for(let i=0;i<before.league.teams.length;i++){
  const a=before.league.teams[i],b=current.league.teams[i];assert.equal(a.id,b.id);assert.equal(a.roster.length,b.roster.length);
  for(let j=0;j<a.roster.length;j++){
   const p=a.roster[j],q=b.roster[j],v=structuredClone(q);
   assert.deepEqual(q.shootingMeasurement,{...p.shootingMeasurement,...ctx.cards[p.playerId]});
   for(const k of ['strictSeconds','sourceZoneAttempts','meanSourceShootingMultiplier'])assert.deepEqual(ctx.cards[p.playerId][k],prior.cards[p.playerId][k]);
   v.shootingMeasurement=p.shootingMeasurement;assert.deepEqual(v,p);teamCards++;
  }
  teams.set(a.id,new Map(a.roster.map(p=>[p.playerId,p])));
 }
 const f=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,valid=new Set(read(`reports/player-impact-v1/${season}-on-court-truth.json`).gameIds);
 inputs.push(f,`${root}/${season}-contexts.json`,`reports/player-impact-v30/${season}-contexts.json`);
 const source=new Map(),cache=new Map();let states=0;const flowBranches={};
 for(const line of fs.readFileSync(f,'utf8').trim().split('\n')){
  const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<0)continue;
  for(const t of s.teams){
   const ids=[...t.players].sort((a,b)=>a-b),key=t.teamId+':'+ids.join(',');let rows=cache.get(key);
   if(!rows){rows=evaluate(ids.map(pid=>teams.get(t.teamId).get(pid)),cache.size%375===0?{season,teamId:t.teamId,key}:null);cache.set(key,rows);}
   flowBranches[rows[0].branch]=(flowBranches[rows[0].branch]??0)+1;
   for(const r of rows){
    const p=source.get(r.playerId)??{playerId:r.playerId,name:teams.get(t.teamId).get(r.playerId).name,seconds:0,totals:{}};p.seconds+=s.seconds;
    for(const[k,v]of Object.entries(r))if(k!=='playerId'&&typeof v==='number')p.totals[k]=(p.totals[k]??0)+v*s.seconds/60;
    source.set(r.playerId,p);
   }
   states++;
  }
 }
 assert.equal(states,ctx.states);
 seasons.push({season,states,flowBranches,uniqueTeamFives:cache.size,players:[...source.values()].map(p=>({...p,rates:Object.fromEntries(Object.entries(p.totals).map(([k,v])=>[k,v/(p.seconds/60)]))}))});
 console.log(JSON.stringify({season,states,uniqueTeamFives:cache.size}));
}
const x=await ovrInput(),mean70=x.players.map((p,index)=>({playerId:p.playerId,name:p.name,position:x.profiles[x.roleMap.get(p.playerId).slot].pos,rows:evaluate(x.profiles.map((q,i)=>i===x.roleMap.get(p.playerId).slot?p:q),index%29===0?{mean70Subject:p.playerId}:null)}));
assert.equal(cards,2262);assert.equal(totalStates,270090);assert.equal(mean70.length,582);
const files=[...inputs,root+'/model.mjs',root+'/input.mjs',root+'/audit-flow.mjs','test/own_pool_transport.js'];
const hashes=Object.fromEntries(files.map(f=>[f,hash(f)]));
fs.writeFileSync(root+'/flow-audit.json',JSON.stringify({design:'Fixed passer rows plus separate own pool where strictly feasible; explicit unfitted source-column projection otherwise; same frozen attributes, roles, exposures and energy.',seasons,mean70,hashes}));
fs.writeFileSync(root+'/transport-samples.json',JSON.stringify({scope:'Every375th distinct source team-five within each season and every29th natural-position mean70 subject; deterministic diagnostic sample only, no fitted choice.',samples:transportSamples,hashes}));
fs.writeFileSync(root+'/source-verification.json',JSON.stringify({passed:true,sourceRoleCards:cards,teamCards,sourceContextStates:totalStates,allRawAttributesAndOtherInputsUnchanged:true,sourceContextExposureExactlyRetained:true,terminalConserved:true,positiveSelfSupport:true,passerRowsConservedWhenStrictlyFeasible:true,nonStrictRowsExplicitlyRelaxed:true,noSelfAssist:true,mean70PlayerLineups:582,hashes},null,2));

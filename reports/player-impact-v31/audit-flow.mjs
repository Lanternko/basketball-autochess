import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput as previousInput} from '../player-impact-v30/input.mjs';
import {loadInput} from './input.mjs';
import {ovrInput} from '../player-impact-v30/ovr-input.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
import {supplyFlow} from '../player-impact-v11/model.mjs';
import {supportedFlow} from './model.mjs';
const root='reports/player-impact-v31',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=[];let cards=0,teamCards=0,totalStates=0;const inputFiles=[];
function evaluate(ps){
 const ls=elasticLineup(ps,'elastic-creation'),old=supplyFlow(ls),next=supportedFlow(ls);
 assert.deepEqual(old.matrix,next.matrix);assert.deepEqual(old.incoming,next.incoming);
 const rows=ls.map((p,i)=>{
  const m=p.opportunityMeasurement;assert.ok(next.self[i]<=m.selfOpportunityRate+1e-8);
  assert.ok(next.self[i]+next.incoming[i]<=m.terminalOpportunityRate+1e-8);
  return {playerId:p.playerId,sourceSelf:m.selfOpportunityRate,sourceReceive:m.receiveOpportunityRate,terminal:m.terminalOpportunityRate,incoming:old.incoming[i],previousAssignedSelf:old.self[i],supportedSelf:next.self[i],unfilledReceive:next.unusedTerminal[i]};
 });
 return rows;
}
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const before=structuredClone(previousInput(season)),current=loadInput(season),ctx=read(`${root}/${season}-contexts.json`),prior=read(`reports/player-impact-v30/${season}-contexts.json`);
 for(const k of ['states','stints','strictMinutes','contextReference'])assert.deepEqual(ctx[k],prior[k]);
 totalStates+=ctx.states;
 for(const k of ['options','exposure'])assert.deepEqual(current[k],before[k]);assert.deepEqual(current.league.schedule,before.league.schedule);
 const teams=new Map();
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
 const file=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,valid=new Set(read(`reports/player-impact-v1/${season}-on-court-truth.json`).gameIds);
 inputFiles.push(file,`${root}/${season}-contexts.json`,`reports/player-impact-v30/${season}-contexts.json`);
 const source=new Map(),cache=new Map();let states=0;
 for(const line of fs.readFileSync(file,'utf8').trim().split('\n')){
  const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<0)continue;
  for(const t of s.teams){
   const ids=[...t.players].sort((a,b)=>a-b),key=t.teamId+':'+ids.join(',');let rows=cache.get(key);
   if(!rows){rows=evaluate(ids.map(id=>teams.get(t.teamId).get(id)));cache.set(key,rows);}
   for(const row of rows){
    const r=source.get(row.playerId)??{playerId:row.playerId,name:teams.get(t.teamId).get(row.playerId).name,seconds:0,totals:{}};r.seconds+=s.seconds;
    for(const[k,v]of Object.entries(row))if(k!=='playerId')r.totals[k]=(r.totals[k]??0)+v*s.seconds/60;
    source.set(row.playerId,r);
   }
   states++;
  }
 }
 assert.equal(states,ctx.states);cards+=Object.keys(ctx.cards).length;
 const rows=[...source.values()].map(p=>({...p,rates:Object.fromEntries(Object.entries(p.totals).map(([k,v])=>[k,v/(p.seconds/60)]))}));
 seasons.push({season,states,uniqueTeamFives:cache.size,players:rows,contextChange:Object.fromEntries(['long','mid','short'].map(z=>{
  const v=Object.keys(ctx.cards).map(id=>ctx.cards[id].contexts['rotation-space'][z]-prior.cards[id].contexts['rotation-space'][z]);
  return [z,{minimum:Math.min(...v),maximum:Math.max(...v)}];
 }))});
 console.log(JSON.stringify({season,states,uniqueTeamFives:cache.size,sourcePlayers:rows.length}));
}
const x=await ovrInput(),mean70=x.players.map(p=>{
 const slot=x.roleMap.get(p.playerId).slot,rows=evaluate(x.profiles.map((q,i)=>i===slot?p:q));
 return {playerId:p.playerId,name:p.name,position:x.profiles[slot].pos,rows};
});
assert.equal(cards,2262);assert.equal(totalStates,270090);assert.equal(mean70.length,582);
const files=[...inputFiles,'src/source_self_opportunities.js',root+'/model.mjs',root+'/input.mjs',root+'/audit-flow.mjs'];
fs.writeFileSync(root+'/flow-audit.json',JSON.stringify({design:'Frozen source roles before and after restricting automatic self compensation. Opportunity rates and assignments are descriptive model quantities, not observed extra attempts or physiological capacities. No role/attribute edits. All passing transport marginals unchanged; total realized terminal demand can fall. Mean70 cases contain each subject only at natural position.',seasons,mean70,hashes:Object.fromEntries(files.map(f=>[f,hash(f)]))}));
fs.writeFileSync(root+'/source-verification.json',JSON.stringify({passed:true,sourceRoleCards:cards,teamCards,sourceContextStates:totalStates,allRawAttributesAndOtherInputsUnchanged:true,sourceContextExposureExactlyRetained:true,allPassTransportUnchanged:true,mean70PlayerLineups:582,hashes:Object.fromEntries(files.map(f=>[f,hash(f)])),scope:'Source role restriction and contexts only; source rates are not validated maximum capacities.'},null,2));

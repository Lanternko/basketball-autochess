import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
import {sourceFreshDefense} from '../../src/source_fresh_defense.js';
import {ovrInput as previousInput} from '../player-impact-v39/ovr-input.mjs';
import {ovrInput} from './ovr-input.mjs';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
import {impactEngine} from './engine.mjs';
const root='reports/player-impact-v41',sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),read=p=>JSON.parse(fs.readFileSync(p)),close=(a,b)=>assert.ok(Math.abs(a-b)<1e-11,[a,b]);
const a=await previousInput(),x=await ovrInput(),clean=structuredClone(x),ctx=read(root+'/2025-26-contexts.json'),fit=read(root+'/fit.json').seasons.find(s=>s.season==='2025-26'),indices=new Map(fit.playerIds.map((p,i)=>[p,i]));
const actual=[...x.players,...x.opponents.flatMap(t=>t.roster)],old=[...a.players,...a.opponents.flatMap(t=>t.roster)],cleanActual=[...clean.players,...clean.opponents.flatMap(t=>t.roster)];
assert.equal(x.players.length,582);assert.equal(actual.length,732);assert.equal(x.profiles.length,5);assert.equal(new Set(x.profiles.map(p=>p.pos)).size,5);
for(let i=0;i<actual.length;i++){
 const p=actual[i],q=old[i];assert.equal(p.playerId,q.playerId);
 for(const k of ATTRIBUTES)assert.equal(p[k],q[k]);
 assert.deepEqual(p.shootingMeasurement,{...q.shootingMeasurement,...ctx.cards[p.playerId]});
 for(const z of fit.zones)assert.equal(p.freshDefenseMeasurement.logits[z.zone],z.defenderLogits[indices.get(p.playerId)]);
 delete cleanActual[i].freshDefenseMeasurement;cleanActual[i].shootingMeasurement=structuredClone(q.shootingMeasurement);
}
for(let slot=0;slot<5;slot++){
 const p=x.profiles[slot],pool=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),minutes=pool.reduce((s,q)=>s+q.observed.MIN,0);
 for(const z of ['long','mid','short'])close(p.freshDefenseMeasurement.logits[z],pool.reduce((s,q)=>s+q.observed.MIN*q.freshDefenseMeasurement.logits[z],0)/minutes);
 close(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/ATTRIBUTES.length,70);assert.equal(p.shootingMeasurement,undefined);delete clean.profiles[slot].freshDefenseMeasurement;
}
assert.deepEqual(clean,a);sourceFreshDefense(x.profiles);
const src=source();let teammateChecks=0;
for(const p of x.players){const slot=x.roleMap.get(p.playerId).slot,team=workloadTeam(x,p,slot,src.players[p.playerId].supportedMinutes,src.capMinutes,0).team;
 for(let i=0;i<5;i++)if(i!==slot){const q=team.roster[i];assert.equal(q.pos,x.profiles[i].pos);close(ATTRIBUTES.reduce((s,k)=>s+q[k],0)/ATTRIBUTES.length,70);teammateChecks++;}
}
const run=await impactEngine('rotation-space',{game:true}),games=[];
for(const name of ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Victor Wembanyama','Mitchell Robinson']){
 const p=x.players.find(p=>p.name===name);assert.ok(p,name);const slot=x.roleMap.get(p.playerId).slot;
 for(const minutes of [src.players[p.playerId].supportedMinutes,src.capMinutes])for(const side of [0,1]){
  const teams=[workloadTeam(x,p,slot,minutes,src.capMinutes,0),opponentTeam(x,x.opponents[0],src.capMinutes,0)];if(side)teams.reverse();
  const opt=options(x,20261012,teams.map(t=>t.schedule)),g=run(...teams.map(t=>t.team),opt),tag=side?'B':'A';assert.ok(g.complete);assert.equal(g.gameSeconds,2880);close(g['players'+tag][slot].seconds/60,Math.round(minutes*600)/600);
  for(const seat of ['A','B']){const t=g['stat'+seat];assert.equal(t.pts,2*t.fgm+t.fg3m+t.ftm);for(const k of ['pts','ast','tov','stl','blk','oreb','dreb','fga','fgm','fg3a','fg3m','fta','ftm'])assert.equal(g['players'+seat].reduce((s,q)=>s+q[k],0)+(k==='tov'?t.clockTov:0),t[k]);}
  games.push({name,playerId:p.playerId,slot,minutes,side,scoreA:g.scoreA,scoreB:g.scoreB});
 }
}
const files=['ovr-input.mjs','verify-input.mjs','input.mjs','fit.json','2025-26-contexts.json','engine.mjs','model.mjs'].map(p=>root+'/'+p).concat(['reports/player-impact-v39/ovr-input.mjs','src/source_fresh_defense.js']);
fs.writeFileSync(root+'/input-verification.json',JSON.stringify({passed:true,actualPlayers:582,opponentCards:150,profiles:5,attributeArithmeticMean:70,actualRawAttributesAndCanonicalRolesUnchanged:true,independentPositionLogitPools:true,teammateChecks,smokeGames:games.length,games,scope:'Input and arithmetic conservation smoke checks, not a full ranking, exposure uncertainty estimate or adoption test.',hashes:Object.fromEntries(files.map(p=>[p,sha(p)]))},null,2));console.log({passed:true,teammateChecks,smokeGames:games.length});

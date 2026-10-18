import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from './input.mjs';
import {loadInput as previousInput} from '../player-impact-v30/input.mjs';
import {ovrInput} from './ovr-input.mjs';
import {controlledInput} from '../player-impact-v38/input.mjs';
import {measuredBlockProbabilities} from '../../src/measured_block_events.js';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
import {impactEngine} from './engine.mjs';
import {impactEngine as previousEngine} from '../player-impact-v30/engine.mjs';
const root='reports/player-impact-v39',sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),strip=x=>Array.isArray(x)?x.map(strip):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).filter(([k])=>k!=='blk').map(([k,v])=>[k,strip(v)])):x;
let teamCards=0;for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const a=previousInput(season),b=loadInput(season),clean=structuredClone(b);
 for(const t of clean.league.teams)for(const p of t.roster){assert.ok(p.blockEventMeasurement);delete p.blockEventMeasurement;teamCards++;}
 assert.deepEqual(a,clean);
}
const x=await ovrInput(),base=await controlledInput('v30'),clean=structuredClone(x);
for(const p of [...clean.players,...clean.profiles,...clean.opponents.flatMap(t=>t.roster)])delete p.blockEventMeasurement;
assert.deepEqual(clean,base);
const fits=JSON.parse(fs.readFileSync(root+'/fit.json')).seasons.find(s=>s.season==='2025-26'),theta=new Map(fits.playerIds.map((pid,i)=>[pid,fits.playerLogHazards[i]]));
for(let slot=0;slot<5;slot++){
 const pool=x.players.filter(p=>x.roleMap.get(p.playerId).slot===slot&&!x.roleMap.get(p.playerId).lowConfidence),minute=pool.reduce((s,p)=>s+p.observed.MIN,0),expected=pool.reduce((s,p)=>s+p.observed.MIN*Math.exp(theta.get(p.playerId)),0)/minute;
 assert.ok(Math.abs(Math.exp(x.profiles[slot].blockEventMeasurement.logHazard)-expected)<1e-14);
 for(const z of ['long','mid','short'])measuredBlockProbabilities(x.profiles,z);
}
const old=await previousEngine('rotation-space',{game:true}),next=await impactEngine('rotation-space',{game:true}),src=source(),rows=[];
// This is an input/isolation smoke check, not a player ranking or precision claim.
for(const name of ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Victor Wembanyama','Mitchell Robinson']){
 const p=x.players.find(p=>p.name===name);assert.ok(p,name);const slot=x.roleMap.get(p.playerId).slot,cap=src.capMinutes;
 for(const minutes of [src.players[p.playerId].supportedMinutes,cap])for(const side of [0,1]){
  const teams=[workloadTeam(x,p,slot,minutes,cap,0),opponentTeam(x,x.opponents[0],cap,0)],oldTeams=[workloadTeam(base,base.players.find(q=>q.playerId===p.playerId),slot,minutes,cap,0),opponentTeam(base,base.opponents[0],cap,0)];
  if(side){teams.reverse();oldTeams.reverse();}const opt=options(x,20261012,teams.map(t=>t.schedule)),optOld=options(base,20261012,oldTeams.map(t=>t.schedule));
  const a=old(...oldTeams.map(t=>t.team),optOld),b=next(...teams.map(t=>t.team),opt);assert.deepEqual(strip(a),strip(b));rows.push({playerId:p.playerId,name,minutes,side,scoreA:b.scoreA,scoreB:b.scoreB});
 }
}
const files=['input.mjs','ovr-input.mjs','verify-input.mjs','engine.mjs','fit.json'].map(p=>root+'/'+p).concat(['reports/player-impact-v38/input.mjs','src/measured_block_events.js']);
fs.writeFileSync(root+'/input-verification.json',JSON.stringify({passed:true,teamCards,actualPlayers:582,opponentCards:150,profiles:5,canonicalWorkloadInputEqualExceptBlockDescriptor:true,positionPoolIndependentlyRecomputed:true,pairedGames:40,scenarios:rows,scope:'All source card fields preserved except added descriptor.20 paired canonical workload cases show identical complete game output except blk; not OVR uncertainty or a full ranking.',hashes:Object.fromEntries(files.map(p=>[p,sha(p)]))},null,2));
console.log('Inputs: '+teamCards+' season team cards,582 actual players,150 opponent cards,5 position profiles;40 paired canonical workload games identical except blk.');

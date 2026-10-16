import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import * as M from '../../src/probability_model.js';
import {loadInput as oldInput} from '../player-impact-v28/input.mjs';
import {loadInput} from './input.mjs';
const root='reports/player-impact-v30',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const protocol=read(root+'/validation-protocol.json'),audit=read(root+'/dependence-audit.json'),seen=new Set();let teamCards=0,states=0;
for(const[f,h]of Object.entries({...protocol.hashes,...audit.hashes}))assert.equal(hash(f),h,f);
for(const season of protocol.seasons){
 const old=structuredClone(oldInput(season)),current=loadInput(season),ctx=read(`${root}/${season}-contexts.json`),previousCtx=read(`reports/player-impact-v28/${season}-contexts.json`);
 assert.equal(ctx.states,previousCtx.states);assert.equal(ctx.stints,previousCtx.stints);assert.deepEqual(ctx.contextReference,previousCtx.contextReference);states+=ctx.states;
 assert.deepEqual(current.options,old.options);assert.deepEqual(current.exposure,old.exposure);assert.deepEqual(current.league.schedule,old.league.schedule);
 for(let t=0;t<old.league.teams.length;t++){
  const a=old.league.teams[t],b=current.league.teams[t];assert.equal(a.id,b.id);assert.equal(a.roster.length,b.roster.length);
  for(let i=0;i<a.roster.length;i++){
   const p=a.roster[i],q=b.roster[i],v=structuredClone(q);assert.equal(q.playerId,p.playerId);
   const dep=q.creationDependenceMeasurement;
   assert.equal(dep.receivedShare,p.opportunityMeasurement.receiveOpportunityRate/p.opportunityMeasurement.terminalOpportunityRate);
   assert.equal(dep.sourceSelfCreation,M.selfCreation(p));
   assert.deepEqual(q.shootingMeasurement,{...p.shootingMeasurement,...ctx.cards[p.playerId]});
   for(const f of ['strictSeconds','sourceZoneAttempts','meanSourceShootingMultiplier'])assert.deepEqual(ctx.cards[p.playerId][f],previousCtx.cards[p.playerId][f]);
   delete v.creationDependenceMeasurement;v.shootingMeasurement=structuredClone(p.shootingMeasurement);assert.deepEqual(v,p);
   seen.add(season+'/'+p.playerId);teamCards++;
  }
 }
}
assert.equal(seen.size,2262);assert.equal(states,270090);
const fallback=read(root+'/fallback-parity.json');assert.equal(fallback.games,96);assert.equal(fallback.passed,true);assert.equal(fallback.allGameAndPersonalCountersExactlyV28,true);
const files=[root+'/verify-source.mjs','src/source_creation_dependence.js',root+'/model.mjs',root+'/input.mjs',root+'/dependence-audit.json'];
fs.writeFileSync(root+'/source-verification.json',JSON.stringify({passed:true,sourceRoleCards:seen.size,teamCards,sourceContextStates:states,
 allRawAttributesAndOtherInputsUnchanged:true,sourceContextExposureExactlyRetained:true,fallbackExactGames:96,
 hashes:Object.fromEntries(files.map(f=>[f,hash(f)])),scope:'Source-role dependence and source calibration accounting. No causal skill or ranking accuracy claim.'},null,2));
console.log(JSON.stringify({passed:true,sourceRoleCards:seen.size,teamCards,sourceContextStates:states}));

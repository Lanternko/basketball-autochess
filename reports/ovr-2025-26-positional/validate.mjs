import fs from 'node:fs';
import assert from 'node:assert/strict';
import {ROOT,positionalInputs,lineup,centered,unknown} from './protocol.mjs';
import {gameEngine} from '../ovr-2025-26-latest/runtime.mjs';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
const x=positionalInputs();
for(const p of x.profiles){
  assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/16-70)<1e-10);
  for(const k of unknown)assert.equal(p[k],70);
  for(const level of [40,70,99]){
    const a=centered(p,level);
    assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+a[k],0)/16-level)<1e-10);
    assert.ok(ATTRIBUTES.every(k=>Number.isFinite(a[k])&&a[k]>=0&&a[k]<=120));
  }
}
for(const [id,pos]of [[1629674,'C'],[201939,'PG'],[1629029,'PG'],[1630162,'SG'],[203507,'PF']])assert.equal(x.roleMap.get(id).position,pos);
assert.ok(x.profiles[0].pass>x.profiles[4].pass&&x.profiles[0].long>x.profiles[4].long);
assert.ok(x.profiles[0].physique<x.profiles[4].physique&&x.profiles[0].rebound<x.profiles[4].rebound);
const native=await gameEngine(),cached=await gameEngine({memoized:true});let games=0;
for(const id of [1629674,201939,203999,1628983])for(const oi of [0,13,29]){
  const p=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,team=lineup(x,p,slot),op=x.opponents[oi];
  for(const [a,b]of [[team,op],[op,team]]){
    const cache=new Map();
    for(const seed of [20261015,20268934]){
      const actual=cached(a,b,{...x.options,seed,ovrCache:cache}),expected=native(a,b,{...x.options,seed});
      assert.deepEqual(actual,expected);assert.equal(actual.gameSeconds,864);
      assert.equal(actual.scoreA,actual.statA.pts);assert.equal(actual.scoreB,actual.statB.pts);games++;
    }
  }
}
const result={passed:true,profileMean70:true,anchorsExactMean:true,knownPlayerRoles:true,profilesHaveDistinctRoles:true,
  cacheNativeFullOutputParityGames:games,roleAudit:x.roleAudit,
  notValidated:['Individual ability truth','Counterfactual transfer','Four unmeasured attributes','Whole-league player ranking']};
fs.writeFileSync(ROOT+'/validation.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));

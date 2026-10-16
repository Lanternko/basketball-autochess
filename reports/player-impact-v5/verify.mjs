import assert from 'node:assert/strict';
import {ovrInput} from './ovr-input.mjs';
import {impactEngine} from './engine.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
const x=ovrInput();let games=0;
for(const version of ['profile-flow','profile-contests']){
 const regular=await impactEngine(version,{game:true}),cached=await impactEngine(version,{game:true,memoized:true});
 for(const id of [1628983,203999,1629674]){
  const p=x.players.find(p=>p.playerId===id),team=lineup(x,p,x.roleMap.get(id).slot),cache=new Map();
  for(let i=0;i<10;i++){
   const options={...x.options,seed:20261015+i};
   assert.deepEqual(regular(team,x.opponents[i%3],options),cached(team,x.opponents[i%3],{...options,ovrCache:new Map()}));
   // Cross-game reuse is safe only for this same fixed pair and seat order.
   const op=x.opponents[0];assert.deepEqual(regular(team,op,options),cached(team,op,{...options,ovrCache:cache}));games+=4;
  }
 }
}
console.log(JSON.stringify({games,exactMemoizationParity:true}));

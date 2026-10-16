import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {impactEngine} from '../player-impact-v6/engine.mjs';
import {impactEngine as accelerated} from './fast-engine.mjs';
import {ovrInput} from '../player-impact-v6/ovr-input.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
const x=ovrInput();let games=0;
for(const version of ['terminal-flow','terminal-contests']){
 const a=await impactEngine(version,{game:true,memoized:true}),b=await accelerated(version,{game:true,memoized:true});
 for(const id of [1628983,203999,1629674]){
  const p=x.players.find(p=>p.playerId===id),team=lineup(x,p,x.roleMap.get(id).slot),ca=new Map(),cb=new Map();
  for(let i=0;i<20;i++){
   const opts={...x.options,seed:20261015+i};
   assert.deepEqual(a(team,x.opponents[0],{...opts,ovrCache:ca}),b(team,x.opponents[0],{...opts,ovrCache:cb}));games+=2;
  }
 }
}
const files=['fast-model.mjs','fast-engine.mjs','verify-fast.mjs'];
fs.writeFileSync('reports/player-impact-validation/acceleration-verification.json',JSON.stringify({games,exactFullResultParity:true,rngCaching:false,cache:'Deterministic foul inputs only; key includes exact probability object, FT/FGA and foul rate object. No rounding or quantization.',hashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync('reports/player-impact-validation/'+f)).digest('hex')]))},null,2));
console.log(JSON.stringify({games,exactFullResultParity:true}));

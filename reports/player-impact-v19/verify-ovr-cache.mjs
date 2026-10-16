import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {ovrInput} from './ovr-input.mjs';
import {impactEngine} from '../player-impact-v14/engine.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';

const x=await ovrInput('2025-26'),normal=await impactEngine('rotation-space',{game:true}),cached=await impactEngine('rotation-space',{game:true,memoized:true});
const center=JSON.parse(fs.readFileSync('reports/player-impact-v19/2025-26-synthetic-center.json')).fullCenter;
const options={...x.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};
let games=0;
for(const id of [201939,1628983,1629029,203999,1629674,1630162]){
 const p=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,own=lineup(x,p,slot);
 for(const opponent of [0,9,19,29])for(const reversed of [false,true])for(const seed of [20261015,20261016]){
  const [a,b]=reversed?[x.opponents[opponent],own]:[own,x.opponents[opponent]];
  const q=normal(a,b,{...options,seed}),r=cached(a,b,{...options,seed,ovrCache:new Map()});
  assert.deepEqual(r,q,'Caching must preserve every game result and player counter');games++;
 }
}
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const result={games,exactGameAndIndividualCounterParity:true,scope:'Fixed-lineup, no-fatigue OVR only; not a season approximation',hashes:Object.fromEntries(['reports/player-impact-v19/ovr-input.mjs','reports/player-impact-v19/role-input.mjs','reports/player-impact-v19/ftr-prior.json','reports/player-impact-v14/engine.mjs','reports/player-impact-v14/model.mjs','src/measured_creation_context.js'].map(f=>[f,hash(f)]))};
fs.writeFileSync('reports/player-impact-v19/ovr-cache-verification.json',JSON.stringify(result,null,2));console.log(result);

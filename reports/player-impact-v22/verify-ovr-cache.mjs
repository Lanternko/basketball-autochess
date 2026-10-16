import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {ovrInput} from './ovr-input.mjs';
import {impactEngine} from './engine.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';

const x=await ovrInput('2025-26'),normal=await impactEngine('rotation-space',{game:true}),cached=await impactEngine('rotation-space',{game:true,memoized:true});
const center=JSON.parse(fs.readFileSync('reports/player-impact-v20/2025-26-synthetic-center.json')).fullCenter;
const options={...x.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};
let games=0;
for(const id of [201939,1628983,1629029,203999,1629674,1630162]){
 const p=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,own=lineup(x,p,slot);
 for(const opponent of [0,9,19,29])for(const reversed of [false,true])for(const seed of [20261015,20261016]){
  const [a,b]=reversed?[x.opponents[opponent],own]:[own,x.opponents[opponent]];
  const q=normal(a,b,{...options,seed}),r=cached(a,b,{...options,seed,ovrCache:new Map()});
  assert.deepEqual(r,q,'Caching must preserve every game result and player counter');const altered=cached(a,b,{...options,seed,touchLiveShare:seed%2,touchTurnoverScale:seed%2?0:100,ovrCache:new Map()});assert.deepEqual(altered,q,'Legacy touch multiplier/live split must have no effect in measured mode');games++;
 }
}
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const result={games,exactGameAndIndividualCounterParity:true,scope:'Fixed-lineup, no-fatigue OVR only; not a season approximation',hashes:Object.fromEntries(['reports/player-impact-v22/ovr-input.mjs','reports/player-impact-v22/input.mjs','reports/player-impact-v19/ftr-prior.json','reports/player-impact-v22/engine.mjs','reports/player-impact-v14/model.mjs','src/measured_creation_context.js'].map(f=>[f,hash(f)]))};
fs.writeFileSync('reports/player-impact-v22/ovr-cache-verification.json',JSON.stringify(result,null,2));console.log(result);

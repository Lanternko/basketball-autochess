import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {ovrInput as previousInput} from '../player-impact-v23/ovr-input.mjs';
import {ovrInput} from './ovr-input.mjs';
import {impactEngine as previousEngine} from '../player-impact-v23/engine.mjs';
import {impactEngine} from './engine.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
const before=await previousInput('2025-26'),snapshot=structuredClone(before),x=await ovrInput('2025-26');assert.deepEqual(before,snapshot);
for(let i=0;i<5;i++)for(const k of ATTRIBUTES)assert.equal(x.profiles[i][k],before.profiles[i][k]);
const old=await previousEngine('rotation-space',{game:true,memoized:true}),normal=await impactEngine('rotation-space',{game:true}),cached=await impactEngine('rotation-space',{game:true,memoized:true});
const center=JSON.parse(fs.readFileSync('reports/player-impact-v20/2025-26-synthetic-center.json')).fullCenter,options={...x.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};
function exceptDreb(value){const copy=structuredClone(value);for(const side of ['playersA','playersB'])for(const p of copy[side]){delete p.dreb;delete p.reb;}return copy;}
let games=0,changedRecipientGames=0;
for(const id of [201939,1628983,1629029,203999,1629674,1630162]){
 const p=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,own=lineup(x,p,slot);
 for(const opponent of [0,9,19,29])for(const reversed of [false,true])for(const seed of [20261015,20261016]){
  const [a,b]=reversed?[x.opponents[opponent],own]:[own,x.opponents[opponent]],opt={...options,seed};
  const q=old(a,b,{...opt,ovrCache:new Map()}),r=normal(a,b,opt),s=cached(a,b,{...opt,ovrCache:new Map()});
  assert.deepEqual(r,s,'Cache exact parity');assert.deepEqual(exceptDreb(r),exceptDreb(q),'Only individual DREB and REB counters may differ');
  if(JSON.stringify(r.playersA)!==JSON.stringify(q.playersA)||JSON.stringify(r.playersB)!==JSON.stringify(q.playersB))changedRecipientGames++;games++;
 }
}
assert.ok(changedRecipientGames>0);
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),root='reports/player-impact-v24';
const out={games,changedRecipientGames,allNonDrebCountersExact:true,cacheExactParity:true,previousInputUnchanged:true,syntheticAttributesUnchanged:true,scope:'Fixed-lineup counterfactual probes only; no new all-player OVR ranking. Full-season parity separately required.',hashes:Object.fromEntries(['engine.mjs','input.mjs','model.mjs','ovr-input.mjs','verify-counterfactual-parity.mjs'].map(f=>[root+'/'+f,hash(root+'/'+f)]))};
fs.writeFileSync(root+'/counterfactual-parity.json',JSON.stringify(out,null,2));console.log(out);

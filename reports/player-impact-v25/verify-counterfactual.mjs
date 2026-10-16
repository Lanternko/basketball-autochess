import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {ovrInput as previousInput} from '../player-impact-v24/ovr-input.mjs';
import {ovrInput} from './ovr-input.mjs';
import {impactEngine as previousEngine} from '../player-impact-v24/engine.mjs';
import {impactEngine} from './engine.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
const before=await previousInput('2025-26'),snapshot=structuredClone(before),x=await ovrInput('2025-26');assert.deepEqual(before,snapshot);
for(let i=0;i<5;i++)for(const k of ATTRIBUTES)assert.equal(x.profiles[i][k],before.profiles[i][k]);
const old=await previousEngine('rotation-space',{game:true}),normal=await impactEngine('rotation-space',{game:true}),cached=await impactEngine('rotation-space',{game:true,memoized:true});
const center=JSON.parse(fs.readFileSync('reports/player-impact-v20/2025-26-synthetic-center.json')).fullCenter,options={...x.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};
let games=0;
for(const id of [201939,1628983,1629029,203999,1629674,1630162]){
 const p=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,own=lineup(x,p,slot);
 for(const opponent of [0,9,19,29])for(const reversed of [false,true])for(const seed of [20261015,20261016]){
  const [a,b]=reversed?[x.opponents[opponent],own]:[own,x.opponents[opponent]],opt={...options,seed};
  assert.deepEqual(normal(a,b,opt),cached(a,b,{...opt,ovrCache:new Map()}),'Every game and personal counter cache parity');
  const noContact={...opt,nonShootingFoulRate:0,endgameStrategies:false};assert.deepEqual(normal(a,b,noContact),old(a,b,noContact),'Without ordinary/forced contacts every mechanism must exactly match v24');games++;
 }
}
const root='reports/player-impact-v25',hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const out={games,cacheExactParity:true,zeroContactExactPreviousParity:true,previousInputUnchanged:true,syntheticAttributesUnchanged:true,scope:'Fixed-lineup OVR diagnostic probes only. Contact victim and ordinary rate changed; every mechanism matches v24 when ordinary/forced nonshooting contacts disabled. No new all-player ranking.',hashes:Object.fromEntries(['input.mjs','model.mjs','engine.mjs','ovr-input.mjs','verify-counterfactual.mjs'].map(f=>[root+'/'+f,hash(root+'/'+f)]))};
fs.writeFileSync(root+'/counterfactual-verification.json',JSON.stringify(out,null,2));console.log(out);

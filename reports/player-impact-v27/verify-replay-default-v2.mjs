import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {impactEngine as oldEngine} from '../player-impact-v26/engine.mjs';
import {impactEngine} from './replay-engine-v2.mjs';
import {ovrInput} from '../player-impact-v26/ovr-input.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
const x=await ovrInput('2025-26'),a=await oldEngine('rotation-space',{game:true}),b=await impactEngine('rotation-space',{game:true}),center=JSON.parse(fs.readFileSync('reports/player-impact-v20/2025-26-synthetic-center.json')).fullCenter;
let games=0;
for(const id of [201939,1628983,1629029,203999,1629674,1630162]){
 const p=x.players.find(p=>p.playerId===id),own=lineup(x,p,x.roleMap.get(id).slot);
 for(const j of [0,9,19,29])for(const reverse of [false,true])for(const seed of [20261015,20261016]){
  const pair=reverse?[x.opponents[j],own]:[own,x.opponents[j]],opt={...x.options,seed,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};assert.deepEqual(b(...pair,opt),a(...pair,opt));games++;
 }
}
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),out={games,defaultV26ExactParity:true,scope:'No source rotation/fixed-horizon options: all default game and personal counters exactly match v26.',hashes:Object.fromEntries(['reports/player-impact-v27/replay-engine-v2.mjs','reports/player-impact-v27/verify-replay-default-v2.mjs'].map(f=>[f,hash(f)]))};
fs.writeFileSync('reports/player-impact-v27/default-parity-v2.json',JSON.stringify(out,null,2));console.log(out);

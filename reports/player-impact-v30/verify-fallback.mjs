import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {impactEngine as previousEngine} from '../player-impact-v28/engine.mjs';
import {impactEngine} from './engine.mjs';
import {ovrInput} from '../player-impact-v29/ovr-input.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
const x=await ovrInput('2025-26'),old=await previousEngine('rotation-space',{game:true}),run=await impactEngine('rotation-space',{game:true});
const center=JSON.parse(fs.readFileSync('reports/player-impact-v20/2025-26-synthetic-center.json')).fullCenter;let games=0;
for(const id of [1629011,1641705,1630595,1628983,1629029,203999]){
 const p=x.players.find(p=>p.playerId===id),team=lineup(x,p,x.roleMap.get(id).slot);
 for(const j of [0,9,19,29])for(const reverse of [false,true])for(const seed of [20261015,20261016]){
  const pair=reverse?[x.opponents[j],team]:[team,x.opponents[j]],options={...x.options,seed,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};
  assert.deepEqual(run(...pair,options),old(...pair,options));games++;
 }
}
const files=['engine.mjs','model.mjs','verify-fallback.mjs'].map(p=>'reports/player-impact-v30/'+p),hashes=Object.fromEntries(files.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]));
fs.writeFileSync('reports/player-impact-v30/fallback-parity.json',JSON.stringify({passed:true,games,allGameAndPersonalCountersExactlyV28:true,scope:'v28 inputs with source defense anchors and v28 shooting contexts, without new creation-dependence anchors. No role override; every counter must exactly match v28.',hashes},null,2));console.log({games,exactV28:true});

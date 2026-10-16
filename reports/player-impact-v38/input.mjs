// Controlled OVR input: reconstruct once from immutable source role cards.
// Baseline and candidate differ only in the intended shooting context centering.
import fs from 'node:fs';
import {ovrInput as previousInput} from '../player-impact-v30/ovr-input.mjs';
import {attachCanonicalCreationRoles} from '../../src/source_creation_roles.js';
const read=f=>JSON.parse(fs.readFileSync(f));
export async function controlledInput(variant,season='2025-26'){
 if(!['v30','v37'].includes(variant))throw Error('Unknown controlled transport');
 const x=structuredClone(await previousInput(season)),cards=read(`reports/player-impact-v6/${season}-cards.json`).cards,audit=read(`reports/player-impact-v17/${season}-creation-audit.json`);
 const actual=[...x.players,...x.opponents.flatMap(t=>t.roster)];attachCanonicalCreationRoles(actual,cards,audit);
 if(variant==='v37'){
  const contexts=read(`reports/player-impact-v37/${season}-contexts.json`);
  for(const p of actual){const m=contexts.cards[p.playerId];if(!m)throw Error('Missing candidate centering');p.shootingMeasurement={...p.shootingMeasurement,...m};}
 }
 return x;
}

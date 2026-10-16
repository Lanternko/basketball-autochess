import fs from 'node:fs';
import {ovrInput as previousInput} from '../player-impact-v39/ovr-input.mjs';
import {attachFreshDefense} from './input.mjs';
export async function ovrInput(season='2025-26'){
 const x=structuredClone(await previousInput(season)),actual=[...x.players,...x.opponents.flatMap(t=>t.roster)],ctx=JSON.parse(fs.readFileSync(`reports/player-impact-v41/${season}-contexts.json`));
 attachFreshDefense(actual,season);
 for(const p of actual){const c=ctx.cards[p.playerId];if(!c)throw Error('Missing fresh defense shooting centering');p.shootingMeasurement={...p.shootingMeasurement,...c};}
 for(let slot=0;slot<x.profiles.length;slot++){
  const p=x.profiles[slot],pool=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),minutes=pool.reduce((s,q)=>s+q.observed.MIN,0);
  if(!(minutes>0))throw Error('Missing natural-position fresh defense pool');
  p.freshDefenseMeasurement={logits:Object.fromEntries(['long','mid','short'].map(z=>[z,pool.reduce((s,q)=>s+q.observed.MIN*q.freshDefenseMeasurement.logits[z],0)/minutes])),sourceOnBall:p.onBall,sourceHelp:p.help,sourcePhysique:p.physique,source:'Confident natural-position source-minute weighted arithmetic defender logit. Additive logit feature pool, not a re-estimate of unknown attributes. All synthetic attributes retain arithmetic mean70.'};
 }
 return x;
}

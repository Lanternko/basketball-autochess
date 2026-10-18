import assert from 'node:assert/strict';
import { offensiveReboundProbability as p } from '../src/rebound_block_model.js';
const base=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70}));
for(const zone of ['long','mid','short']) for(let shooterIndex=0;shooterIndex<5;shooterIndex++) {
 const opts={zone,shooterIndex,leagueShare:.24};
 assert.ok(Math.abs(p(base,base,opts)-.24)<1e-12);
 const strong=base.map(x=>({...x,rebound:95}));
 assert.ok(p(strong,base,opts)>.24);
 assert.ok(p(base,strong,opts)<.24);
}
for(const leagueShare of [NaN,0,1,-1]) assert.throws(()=>p(base,base,{leagueShare}));
const ordered=base.map((p,i)=>({...p,rebound:55+i*10}));
assert.ok(Math.abs(p(ordered,base,{shooterIndex:4})-p([...ordered].reverse(),base,{shooterIndex:0}))<1e-12);
console.log('PASS league anchor, defensive advantage, skill direction, invalid input');

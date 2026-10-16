import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadInput} from '../reports/player-impact-v24/input.mjs';
import {recipientWeights} from '../reports/player-impact-v24/model.mjs';
import {measuredRecipientWeights} from '../src/individual_box_allocation.js';
let lineups=0,cards=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),source=JSON.parse(fs.readFileSync(`reports/player-impact-v24/${season}-dreb-rates.json`));
 for(const t of b.league.teams){
  const ls=t.roster.slice(0,5),w=recipientWeights(ls,'dreb');assert.ok(Math.abs(w.reduce((s,x)=>s+x,0)-1)<1e-12);assert.ok(w.every(x=>x>0));
  assert.deepEqual(recipientWeights(ls,'blk'),measuredRecipientWeights(ls,'blk'));
  const reverse=recipientWeights([...ls].reverse(),'dreb').reverse();reverse.forEach((v,i)=>assert.ok(Math.abs(v-w[i])<1e-12));
  assert.deepEqual(recipientWeights(ls.map(p=>({...p,rebound:0,physique:150})),'dreb'),w,'Allocation propensity must not double-count physique or measured rebound skill');
  for(const p of t.roster){assert.deepEqual(p.drebRecipientMeasurement.strength,source.cards[p.playerId].strength);cards++;}lineups++;
 }
 for(const c of Object.values(source.cards))assert.ok(Math.abs(c.sourceExpectedDreb-c.sourceDreb+source.l2Precision*c.logStrength)<.005,'Source conditional likelihood gradient must converge');
}
assert.throws(()=>recipientWeights([{}],'dreb'),/Missing/);
console.log(JSON.stringify({lineups,cards,normalized:true,blockAllocationUnchanged:true,likelihoodConverged:true}));

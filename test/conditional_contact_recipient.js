import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadInput,ordinaryContactReference} from '../reports/player-impact-v25/input.mjs';
import {contactRecipientWeights} from '../reports/player-impact-v25/model.mjs';
let cards=0,lineups=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),source=JSON.parse(fs.readFileSync(`reports/player-impact-v25/${season}-contact-recipient.json`)),audit=JSON.parse(fs.readFileSync(`reports/player-impact-v25/${season}-contact-policy.json`)),old=JSON.parse(fs.readFileSync(`reports/player-impact-v19/${season}-ft-kinds.json`));
 for(const kind of ['shooting','nonshooting','technical','unresolved'])assert.equal(Object.values(audit.ftGroups).reduce((s,c)=>s+(c[kind]??0),0),old.totals[kind]);
 const rate=ordinaryContactReference(season);assert.ok(rate.rate>0&&rate.rate<=rate.upper);assert.equal(b.options.nonShootingFoulRate,rate.rate);
 for(const t of b.league.teams){
  const ls=t.roster.slice(0,5),w=contactRecipientWeights(ls);assert.ok(Math.abs(w.reduce((s,x)=>s+x,0)-1)<1e-12);assert.ok(w.every(x=>x>0));
  assert.deepEqual(contactRecipientWeights(ls.map(p=>({...p,physique:0,handle:150,drive:150}))),w,'No extra attribute boost on measured contact-victim style');
  const reverse=contactRecipientWeights([...ls].reverse()).reverse();reverse.forEach((v,i)=>assert.ok(Math.abs(v-w[i])<1e-12));
  for(const p of t.roster){assert.equal(p.contactRecipientMeasurement.strength,source.cards[p.playerId].strength);cards++;}lineups++;
 }
 for(const c of Object.values(source.cards))assert.ok(Math.abs(c.sourceExpectedContacts-c.sourceDrawnContacts+source.l2Precision*c.logStrength)<.005);
}
assert.throws(()=>contactRecipientWeights([{}, {}, {}, {}, {}]),/Missing/);
console.log(JSON.stringify({cards,lineups,normalized:true,sourceFtCategoriesReconciled:true,sourceLikelihoodConverged:true}));

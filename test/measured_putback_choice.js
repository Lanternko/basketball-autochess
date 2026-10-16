import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadInput} from '../reports/player-impact-v23/input.mjs';
import {measuredPutbackChoice} from '../reports/player-impact-v23/model.mjs';
let players=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),src=JSON.parse(fs.readFileSync(`reports/player-impact-v23/${season}-choice-survival.json`));
 assert.equal(src.games.reduce((s,g)=>s+g.rows.length,0),src.count);
 for(const t of b.league.teams)for(const p of t.roster){
  const q=measuredPutbackChoice(p);assert.ok(q>0&&q<1);assert.equal(measuredPutbackChoice({...p,physique:0}),q);assert.equal(measuredPutbackChoice({...p,physique:150}),q);players++;
 }
}
assert.throws(()=>measuredPutbackChoice({}),/Missing/);
assert.throws(()=>measuredPutbackChoice({putbackChoiceMeasurement:{selectionProbabilityMAP:1}}),/Missing/);
console.log(JSON.stringify({players,sourceOpportunityCoverage:true,styleTendencyIndependentOfExtraPhysiqueMultiplier:true}));

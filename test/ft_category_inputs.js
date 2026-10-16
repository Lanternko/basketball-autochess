import assert from 'node:assert/strict';
import fs from 'node:fs';
import {ATTRIBUTES} from '../src/strength_benchmark.js';
import {ovrInput} from '../reports/player-impact-v19/ovr-input.mjs';
import {loadInput} from '../reports/player-impact-v19/input.mjs';

for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const source=JSON.parse(fs.readFileSync(`reports/player-impact-v19/${season}-ft-kinds.json`));
 const sum={};
 for(const row of Object.values(source.players)){
  assert.equal(row.fta??0,['shooting','nonshooting','technical','unresolved'].reduce((s,k)=>s+(row[k]??0),0));
  for(const[k,n]of Object.entries(row))sum[k]=(sum[k]??0)+n;
 }
 assert.deepEqual(sum,source.totals);
 const b=loadInput(season),contact=JSON.parse(fs.readFileSync(`reports/player-impact-v19/${season}-foul-contact-audit.json`));
 assert.equal(b.options.nonShootingFoulRate,contact.nonshootingContactRateBounds.lower);
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  assert.equal(p.freeThrowProfileMeasurement.freeThrowScope,'shooting-only');
  assert.ok(Number.isFinite(p.shotProfile.freeThrowsPerAttempt));
  assert.equal(p.freeThrowProfileMeasurement.driveAttributeChanged,false);
 }
}
const x=await ovrInput('2025-26');
for(const p of x.profiles){
 assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/ATTRIBUTES.length-70)<1e-10);
 for(const k of ['offBall','screen','handle','breakDbl'])assert.equal(p[k],70);
 assert.ok(p.shotProfile.source.includes('shooting-only'));
 assert.ok(p.profileMetadata.creationPolicy.includes('corrected'));
}
assert.ok(x.profiles[0].heightInches<x.profiles[4].heightInches);
for(const p of [...x.players,...x.opponents.flatMap(t=>t.roster)])assert.equal(p.freeThrowProfileMeasurement.freeThrowScope,'shooting-only');
console.log('Four-season FT category conservation, bounded source contacts, consistent candidate/opponent/mean70 shooting scope and positional profiles passed');

import assert from 'node:assert/strict';
import fs from 'node:fs';
import {workloadEvidence,recurrentAbsence,workloadRotation} from '../src/player_workload.js';
const cap=34.983004987224845;
const s=n=>workloadEvidence(Array(10).fill(n),cap).supportedMinutes;
assert.equal(s(36),s(42));assert.ok(s(36)>s(24)&&s(24)>s(12));
assert.equal(workloadEvidence([12,42],cap).supportedMinutes,(12+cap)/2);
assert.notEqual(workloadEvidence([12,42],cap).supportedMinutes,Math.min(27,cap));
const h=(injury,listed=82,coverage=true)=>({documentedInjuryIllnessGames:injury,listedGames:listed,historyCoverageAdequate:coverage});
assert.equal(recurrentAbsence([h(70),h(0),h(0)]).reliabilityScale,1);
assert.equal(recurrentAbsence([h(70)]).reliabilityScale,1);
assert.equal(recurrentAbsence([h(70),h(41)]).persistentRate,.5);
assert.equal(recurrentAbsence([h(70),h(41)],0).reliabilityScale,1);
assert.equal(recurrentAbsence([h(70),h(41)],.10).reliabilityScale,.95);
assert.equal(recurrentAbsence([h(70),h(20,20,false)]).reliabilityScale,1);
for(const coef of [0,.05,.1])assert.ok(recurrentAbsence([h(82),h(82)],coef).reliabilityScale>=.9);
let scheduleChecks=0;
for(const phase of [0,1,-1])for(const minutes of [[0,12,24,36,48],[cap,19.575,28.7659,32.179,33.4366],[.001,.05,47.999,0,48]]){
 const rows=workloadRotation(minutes,phase),totals=Array(10).fill(0);assert.equal(rows[0].start,0);assert.equal(rows.at(-1).end,2880);
 for(let i=0;i<rows.length;i++){
  const r=rows[i];if(i)assert.equal(r.start,rows[i-1].end);
  assert.equal(r.lineup.length,5);assert.equal(new Set(r.lineup.map(i=>i%5)).size,5);
  for(const player of r.lineup)totals[player]+=r.end-r.start;
 }
 for(let slot=0;slot<5;slot++){
  assert.ok(Math.abs(totals[slot]-Math.round(minutes[slot]*600)/10)<1e-7);
  assert.ok(Math.abs(totals[slot]+totals[slot+5]-2880)<1e-7);
 }scheduleChecks++;
}
const src=JSON.parse(fs.readFileSync('reports/player-impact-v29/workload-source.json'));
let sourceChecks=0;
for(const p of Object.values(src.players)){
 const actual=workloadEvidence(p.history['2025-26'].playedMinutes,src.capMinutes);
 const absence=recurrentAbsence(Object.values(p.history));
 assert.ok(Math.abs(actual.supportedMinutes-p.supportedMinutes)<1e-10);
 assert.ok(Math.abs(absence.persistentRate-p.persistentDocumentedInjuryIllnessRate)<1e-12);
 assert.ok(Math.abs(absence.reliabilityScale*p.supportedMinutes-p.primaryBenchmarkMinutes)<1e-10);sourceChecks++;
}
assert.equal(sourceChecks,582);
console.log(JSON.stringify({passed:true,scheduleChecks,allSourcePlayers:sourceChecks,capMinutes:src.capMinutes}));

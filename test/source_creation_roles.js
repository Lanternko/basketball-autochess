import fs from 'node:fs';
import assert from 'node:assert/strict';
import {attachCanonicalCreationRoles} from '../src/source_creation_roles.js';
import {loadInput} from '../reports/player-impact-v30/input.mjs';
const read=f=>JSON.parse(fs.readFileSync(f));let cards=0,teamCards=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const source=read(`reports/player-impact-v6/${season}-cards.json`).cards,audit=read(`reports/player-impact-v17/${season}-creation-audit.json`),bytes=JSON.stringify([source,audit]);
 const expected=structuredClone(loadInput(season).league.teams.flatMap(t=>t.roster)),players=structuredClone(expected);
 for(const p of players){p.opportunityMeasurement.passOpportunityRate*=.1;p.creationSuccessMeasurement.rawPassRate*=.2;}
 attachCanonicalCreationRoles(players,source,audit);assert.deepEqual(players,expected);
 for(let i=0;i<5;i++)attachCanonicalCreationRoles(players,source,audit);
 assert.deepEqual(players,expected);assert.equal(JSON.stringify([source,audit]),bytes);
 const a=players[0],b=players.find(p=>p!==a&&p.playerId===a.playerId);
 if(b){a.opportunityMeasurement.freshZone.long+=1;assert.notEqual(a.opportunityMeasurement.freshZone.long,b.opportunityMeasurement.freshZone.long);}
 const invalid=structuredClone(expected.slice(0,2));invalid[1].playerId=-987654;const before=JSON.stringify(invalid);
 assert.throws(()=>attachCanonicalCreationRoles(invalid,source,audit));assert.equal(JSON.stringify(invalid),before);
 cards+=new Set(expected.map(p=>p.playerId)).size;teamCards+=expected.length;
}
console.log(JSON.stringify({passed:true,sourcePlayerSeasons:cards,teamCards,idempotent:true,exactlyMatchesOnceCorrectedSeasonInput:true,noSourceMutation:true,independentCopies:true,batchFailureAtomic:true}));

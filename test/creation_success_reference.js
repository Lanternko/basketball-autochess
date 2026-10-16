import assert from 'node:assert/strict';
import {conditionalCreationReference,attachCreationReference} from '../reports/player-impact-v18/creation-reference.mjs';
import {supplyFlow} from '../reports/player-impact-v11/model.mjs';

assert.equal(conditionalCreationReference({minutes:0,conditionalSuccess:null},.4),.4);
assert.ok(Math.abs(conditionalCreationReference({minutes:60,conditionalSuccess:.6},.4)-.5)<1e-12);
assert.throws(()=>conditionalCreationReference({minutes:2,conditionalSuccess:0},.4));
assert.throws(()=>conditionalCreationReference({minutes:0},0));

// Two creators produce the same observed assists. Better receiver success
// requires fewer delivered opportunities, while preserving observed assists.
const players=[.3,.6].map((probability,i)=>({playerId:i,opportunityMeasurement:{
 terminalOpportunityRate:.5,receiveOpportunityRate:.2,passOpportunityRate:.12/.4,passStolenPerMinute:.01
},probability}));
const original=players.map(p=>p.opportunityMeasurement);
attachCreationReference(players,{conditionalSuccess:.4,rows:players.map(p=>({
 playerId:p.playerId,minutes:1e12,conditionalSuccess:p.probability,oldGlobalSuccess:.4
}))});
for(const p of players)assert.ok(Math.abs(p.opportunityMeasurement.passOpportunityRate*p.probability-.12)<1e-10);
assert.ok(players[0].opportunityMeasurement.passOpportunityRate>players[1].opportunityMeasurement.passOpportunityRate);
assert.equal(original[0].passOpportunityRate,.3);
assert.equal(original[1].passOpportunityRate,.3);

// Corrected creation remains subject to each receiver's terminal capacity.
const lineup=[...players,...[2,3,4].map(playerId=>({playerId,opportunityMeasurement:{
 terminalOpportunityRate:.4,receiveOpportunityRate:.2,passOpportunityRate:.15,passStolenPerMinute:.01
}}))];
const flow=supplyFlow(lineup);
for(let i=0;i<5;i++){
 assert.equal(flow.matrix[i][i],0);
 assert.ok(flow.incoming[i]<=flow.terminal[i]+1e-9);
 assert.ok(Math.abs(flow.matrix[i].reduce((s,x)=>s+x,0)-flow.rows[i])<1e-9);
}
console.log('Conditional-success reconstruction, missing-exposure prior, immutable source rates and creation conservation passed');

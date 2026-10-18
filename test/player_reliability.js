import assert from 'node:assert/strict';
import {reliabilityAdjustedContribution as rate} from '../src/player_reliability.js';
const h=n=>({listedGames:82,documentedInjuryIllnessGames:n,historyCoverageAdequate:true});
for(const value of [-20,-1,0,.01,1,20]){
 for(const history of [[],[h(82)],[h(82),h(82)],[h(40),h(10),h(0)]]){
  const r=rate(value,history);
  assert.ok(r.adjustedContribution<=value);
  assert.ok(r.deduction>=0);
  if(value<=0)assert.equal(r.adjustedContribution,value);
  else assert.ok(r.adjustedContribution>=.9*value-1e-10);
 }
 assert.equal(rate(value,[h(82),h(0)]).adjustedContribution,value);
}
const healthy=rate(5,[h(82),h(41)],0),low=rate(5,[h(82),h(41)],.05),high=rate(5,[h(82),h(41)],.10);
assert.equal(healthy.adjustedContribution,5);assert.equal(low.adjustedContribution,4.875);assert.equal(high.adjustedContribution,4.75);
console.log(JSON.stringify({passed:true,absenceNeverAwardsPoints:true,singleSeasonHasNoDeduction:true,maximumPositiveContributionDiscount:.10}));

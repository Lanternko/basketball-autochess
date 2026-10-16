import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as M from '../src/probability_model.js';
import * as C from '../src/constants.js';
import {attachCreationDependence,creationDependence} from '../src/source_creation_dependence.js';
import {loadInput} from '../reports/player-impact-v28/input.mjs';
import {exposureDefenseProbabilities as oldProbability} from '../reports/player-impact-v28/model.mjs';
import {exposureDefenseProbabilities as newProbability} from '../reports/player-impact-v30/model.mjs';
const clamp=x=>Math.max(0,Math.min(1,x));
let cards=0,probabilityChecks=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),all=[...new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])).values()];
 for(const p of all){
  const old=clamp(C.CREATE_DEP_BASE+(70-M.selfCreation(p))/C.CREATE_DEP_SCALE);
  assert.equal(creationDependence(p),old);
  const q=structuredClone(p);attachCreationDependence([q]);
  assert.equal(creationDependence(q),p.opportunityMeasurement.receiveOpportunityRate/p.opportunityMeasurement.terminalOpportunityRate);
  const changed={...q,drive:q.drive+1};
  const expected=clamp(creationDependence(q)-(M.selfCreation(changed)-M.selfCreation(q))/C.CREATE_DEP_SCALE);
  assert.equal(creationDependence(changed),expected);cards++;
 }
 for(const team of b.league.teams){
  const os=team.roster.slice(0,5),ds=b.league.teams.find(t=>t.id!==team.id).roster.slice(0,5);
  for(let i=0;i<5;i++)for(const assist of [null,70,99]){
   const args=[os[i],M.teammateContext(os,i),ds[i],M.helpDefense(ds),70,70,M.teamPhysique(ds),{assist,contextScale:1,contextLongScale:1,contextShortScale:1,turnoverScale:1},ds];
   assert.deepEqual(newProbability(...args),oldProbability(...args),'No source anchor changed existing probabilities');
   const p=structuredClone(os[i]);attachCreationDependence([p]);p.creationDependenceMeasurement.receivedShare=creationDependence(os[i]);
   assert.deepEqual(newProbability(p,...args.slice(1)),oldProbability(...args),'Source anchor set to old dependence must exactly restore old probabilities');
   probabilityChecks+=2;
  }
 }
}
assert.equal(cards,2262);
console.log(JSON.stringify({passed:true,cards,probabilityChecks,sourceRoleCountsOnly:true,currentAttributeSlopePreserved:true}));

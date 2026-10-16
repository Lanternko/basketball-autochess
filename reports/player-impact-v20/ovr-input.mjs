import fs from 'node:fs';
import {positionalOvrInput} from '../player-impact-validation/positional-input.mjs';
import {attachMeasurements,loadInput} from './input.mjs';
import {attachCreationContext} from '../../src/measured_creation_context.js';
import {posteriorFreeThrowRatio} from '../../src/free_throw_profile_prior.js';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=await positionalOvrInput(season),b=loadInput(season),fit=JSON.parse(fs.readFileSync('reports/player-impact-v19/ftr-prior.json')),ref=fit.references[season];
 attachMeasurements(x.players,season);for(const t of x.opponents)attachMeasurements(t.roster,season);
 x.options.nonShootingFoulRate=b.options.nonShootingFoulRate;
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),minutes=ps.reduce((s,q)=>s+q.observed.MIN,0);
  const counts=ps.reduce((s,q)=>({FGA:s.FGA+ref.counts[q.playerId].FGA,FTA:s.FTA+ref.counts[q.playerId].FTA}),{FGA:0,FTA:0});
  return {...p,defenseExposureMeasurement:{leagueAttemptsPerTeamMinute:ps[0].defenseExposureMeasurement.leagueAttemptsPerTeamMinute,...Object.fromEntries(['long','short'].map(z=>[z,{rate:ps.reduce((s,q)=>s+q.observed.MIN*q.defenseExposureMeasurement[z].rate,0)/minutes,source:'Minute-weighted confident natural-position contest activity pool; ability remains normalized synthetic attributes.'}]))},opportunityMeasurement:{...p.opportunityMeasurement,passOpportunityRate:ps.reduce((s,q)=>s+q.observed.MIN*q.opportunityMeasurement.passOpportunityRate,0)/minutes},
   shotProfile:{...p.shotProfile,freeThrowsPerAttempt:posteriorFreeThrowRatio(counts.FGA,counts.FTA,ref.leagueFtr,fit.kappaFga),source:'Position-pooled strict shooting-only FT counts, common count prior; same shooting scope as actual candidates/opponents.'},
   profileMetadata:{...p.profileMetadata,creationPolicy:'Minute-weighted source-reference corrected pass rate, same confident natural-position pool.',freeThrowPolicy:'Position-pooled shooting-only source FT/FGA, same fitted prior as actual cards.'}};
 });
 attachCreationContext(x.profiles,JSON.parse(fs.readFileSync(`reports/player-impact-v20/${season}-contexts.json`)).contextReference);
 cache.set(season,x);return x;
}

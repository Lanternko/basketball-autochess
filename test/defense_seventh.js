import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash} from '../scripts/defense_io.js';
import {executeSeventhJob,seventhInputs} from '../src/defense_seventh_jobs.js';
import {runDefenseSeason} from '../src/defense_sixth_season.js';
const frozen=read('reports/defense-seventh/v4-freeze.json');assert.equal(frozen.blindSeasonDataPresent,false);
const corrections=read('reports/defense-seventh/v4-execution-fixes.json').fixes;
for(const[file,value]of Object.entries(frozen.sources)){const fix=corrections.find(f=>f.file===file);if(fix){assert.equal(fix.frozenHash,value);assert.equal(hash(file),fix.executionHash);}else assert.equal(hash(file),value,'Frozen source changed: '+file);}
for(const k of [25,41,55]){
 const d=read(`reports/defense-seventh/model-pre${k}-forward.json`);for(const model of Object.values(d.models))for(const fold of model.CV.folds){assert(fold.lastTrainingDate<fold.firstValidationDate);assert(!fold.training.some(g=>fold.validation.includes(g)));}
 assert.equal(d.models.role.CV.selected,300);
}
// Unchanged engine, same inputs: legacy branch must retain exact game scores.
const job={cutoff:41,seed:20261012,label:'parity',indices:[1000,1001]},a=executeSeventhJob(job),b=seventhInputs(job),old=runDefenseSeason(b.league,b.exposure,{seed:job.seed,options:b.options,post41:true,cutoff:41,indices:job.indices});
assert.equal(a.matches.length,2);
assert.deepEqual(a.matches.map(g=>[g.id,g.scoreA,g.scoreB]),old.matches.map(g=>[g.id,g.scoreA,g.scoreB]));
// No future observed minutes even affect bench priority in calendar bundle mode.
const config=read('reports/defense-seventh/2025-26/calendar-41/config.json'),bundle=seventhInputs({cutoff:41,bundle:config.root+'/bundle.json'}),players=new Map(bundle.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
for(const g of bundle.exposure.games)for(const t of g.teams)for(const p of t.players)assert.equal(p.seconds,60*(players.get(t.teamId).get(p.playerId)?.seasonMinutesPerGame??20));
assert(a.analysis.marginResidualSD>=0);
console.log('seventh frozen hashes, forward dates, parity, past-only minute inputs: passed');

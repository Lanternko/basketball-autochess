import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash,table} from '../scripts/defense_io.js';
const root='reports/defense-seventh',expected=Array.from({length:20},(_,i)=>20261012+i);
for(const season of ['2024-25','2025-26'])for(const k of [25,41,55]){
 const c=read(`${root}/${season}/calendar-${k}/config.json`),league=read(c.leagueFile),dates=new Map(league.schedule.map(g=>[g.id,g.date])),model=read(c.root+'/ability-model-forward.json');assert(model.trainGames.every(g=>dates.get(g)<=c.date));
 for(const m of Object.values(model.models))for(const f of m.CV.folds){assert(f.lastTrainingDate<f.firstValidationDate);assert(f.validation.every(g=>dates.get(g)<=c.date));}
 for(const v of ['v3','v4']){const d=read(`${root}/${season}-calendar-${k}-${v}-seeds.json`);assert.deepEqual(d.files.map(f=>f.seed),expected);for(const f of d.files){assert.equal(hash(f.file),f.sha256);const r=read(f.file);assert(r.matches.every(g=>dates.get(g.id)>c.date));assert.equal(r.matches.length,league.schedule.filter(g=>g.date>c.date).length);assert(Number.isFinite(r.analysis.marginResidualSD));}}
 const bundle=read(c.root+'/bundle.json');for(const v of ['v3','v4']){const cal=read(c.root+'/calibration-'+v+'.json');assert(cal.trainGames.every(g=>dates.get(g)<=c.date));assert(cal.history.length<=5);assert.deepEqual(cal.seeds,[20260101,20260102,20260103]);}
}
for(const k of [25,41,55]){
 const c=read(`${root}/prior/calendar-${k}/config.json`),m=read(c.root+'/ability-model-forward.json'),dates=new Map(read(c.leagueFile).schedule.map(g=>[g.id,g.date]));assert(m.previousSeasonPrior);assert(m.trainGames.every(g=>dates.get(g)<=c.date));for(const x of Object.values(m.models))for(const f of x.CV.folds)assert(f.lastTrainingDate<f.firstValidationDate);
 const manifest=read(`${root}/2025-26-calendar-${k}-prior-seeds.json`);assert.deepEqual(manifest.files.map(f=>f.seed),expected);for(const f of manifest.files)assert.equal(hash(f.file),f.sha256);
}
const opening=read('data/defense-seventh/preseason-2025-26/opening-rosters.json');assert.equal(opening.teams.length,30);assert.equal(opening.unmatched.length,0);assert.equal(opening.teams.flatMap(t=>t.roster).length,522);assert.equal(new Set(opening.teams.flatMap(t=>t.roster.map(p=>p.playerId))).size,522);
const schedule=read('data/defense-seventh/preseason-2025-26/opening-schedule.json');assert.equal(schedule.fixedGames,1200);assert.equal(schedule.assumedTBDGames,30);
for(const seed of expected){const b=read(`${root}/prior/preseason-0/bundle-seed${seed}.json`),rosters=new Map(opening.teams.map(t=>[t.id,new Set(t.roster.map(p=>p.playerId))])),players=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),count={};assert.equal(b.league.schedule.length,1230);
 for(const g of b.exposure.games)for(const t of g.teams){count[t.teamId]=(count[t.teamId]??0)+1;assert.equal(t.players.filter(p=>p.starter).length,5);assert(t.players.length>=8&&t.players.length<=12);for(const p of t.players){assert(rosters.get(t.teamId).has(p.playerId));const card=players.get(t.teamId).get(p.playerId);assert(count[t.teamId]>card.preseasonAvailableAfter);assert.equal(p.seconds,60*card.seasonMinutesPerGame);assert(card.offenseMeasurement.minutes>0);}}
 assert(Object.values(count).every(n=>n===82));
}
const freeze=read(root+'/v4-freeze.json'),fixes=read(root+'/v4-execution-fixes.json').fixes;for(const[f,v]of Object.entries(freeze.sources))assert.equal(hash(f),fixes.find(x=>x.file===f)?.executionHash??v);assert.equal(freeze.switches.previousSeasonPrior,false);
console.log('Calendar/prior dates, 20 seeds, source hashes, genuine preseason roster/availability/schedule and unchanged freeze: passed');

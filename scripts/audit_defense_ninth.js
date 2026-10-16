import fs from 'node:fs';
import assert from 'node:assert/strict';
import {read,hash,table} from './defense_io.js';
import {inputN,pairN,seasonsN,cutoffsN,configN} from '../src/defense_ninth_rosters.js';
const root='reports/defense-ninth/development',spec=read(root+'/prereg.json'),rows=[];
assert.equal(hash(root+'/prereg.json'),fs.readFileSync(root+'/prereg.sha256','utf8').trim());
assert.equal(hash(root+'/prereg-supplement.json'),fs.readFileSync(root+'/prereg-supplement.sha256','utf8').trim());
for(const [p,h]of Object.entries(spec.sourceHashes))assert.equal(hash(p),h,p);
for(const season of seasonsN)for(const k of cutoffsN){
 const c=read(configN(season,k)),base=inputN(c,'v3'),trainRows=table(c.paths['data/season-source/player-games.json']).filter(r=>r.GAME_DATE.slice(0,10)<=c.date),dates=trainRows.map(r=>r.GAME_DATE.slice(0,10)),sourceDates=[...base.pools.values()].flat().map(t=>t.date);
 assert(dates.every(d=>d<=c.date)&&sourceDates.every(d=>d<=c.date));
 let draws=0,targets=0,sourceCards=0;
 for(const [index,g]of base.league.schedule.entries())if(g.date>c.date){for(const seed of [20261012,20261031])for(const team of pairN(base,g,index,seed,true)){assert(Math.abs(team.roster.reduce((n,p)=>n+p.targetMinutes,0)-240)<1e-8);assert(team.roster.every(p=>p.targetMinutes<=48+1e-8));draws++;targets+=team.roster.length;}}
 for(const v of ['v3','v4']){
  const manifest=read(`${root}/${season}-K${k}-${v}.json`);assert.equal(manifest.files.length,20);assert.equal(manifest.preregHash,hash(root+'/prereg.json'));
  for(const [p,h]of Object.entries(manifest.sources))assert.equal(hash(p),h,'Ninth execution code changed');
  for(const [i,f]of manifest.files.entries()){assert.equal(f.seed,20261012+i);assert.equal(hash(f.file),f.sha256);const r=read(f.file);assert.equal(r.seed,f.seed);assert(r.teams.every(t=>Number.isFinite(t.net)));sourceCards++;}
 }
 rows.push({season,k,cutoff:c.date,lastNaiveTrainingDate:dates.sort().at(-1),lastTemplateDate:sourceDates.sort().at(-1),trainingPlayerRows:trainRows.length,poolSizes:Object.fromEntries([...base.pools].map(([id,p])=>[id,p.length])),checkedRosterDraws:draws,checkedPlayerTargets:targets,checkedSeedFiles:sourceCards});
}
const newSeasonPaths=['2021-22','2018-19','2017-18'].map(s=>'data/defense-seventh/'+s),newSeasonDirectories=newSeasonPaths.filter(p=>fs.existsSync(p));assert.equal(newSeasonDirectories.length,0,'No blind season dataset may be created');
const supplement=read(root+'/prereg-supplement.json');assert(supplement.beforeDatasetOrAssessment);assert(Date.parse(spec.registeredAt)<fs.statSync(`${root}/2024-25-K25-v3.json`).mtimeMs);
fs.writeFileSync(root+'/execution-audit.json',JSON.stringify({checkedAt:new Date().toISOString(),preregHash:hash(root+'/prereg.json'),sourceHashesUnchanged:true,all20SeedsPaired:true,newGamePayloadsDownloaded:false,newSeasonDirectories,rows,newCodeHashes:Object.fromEntries(['src/defense_ninth_rosters.js','src/defense_ninth_statistics.js','scripts/register_defense_ninth.js','scripts/run_defense_ninth.js','scripts/defense_ninth_worker.js','scripts/prepare_defense_ninth.js','scripts/assess_defense_ninth.js','scripts/report_defense_ninth.js'].map(p=>[p,hash(p)]))},null,2)+'\n');console.log('AUDIT PASS frozen sources,date boundaries,480 seed files,240/48 targets,no blind data');

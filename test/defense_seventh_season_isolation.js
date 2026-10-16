// Prove blind simulation does not use fitted2025-26 numbers, including lazy
// legacy import dependencies. Empty legacy presets in an isolated checkout.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {read,hash} from '../scripts/defense_io.js';
import {executeSeventhJob} from '../src/defense_seventh_jobs.js';
const target=path.resolve('reports/defense-seventh/independence-sandbox');assert(target.startsWith(path.resolve('reports/defense-seventh')+path.sep));
for(const dir of ['src','scripts','reports/defense-fifth','reports/defense-fourth','input'])fs.mkdirSync(path.join(target,dir),{recursive:true});
for(const dir of ['src','scripts'])for(const file of fs.readdirSync(dir).filter(f=>f.endsWith('.js')))fs.copyFileSync(path.join(dir,file),path.join(target,dir,file));
fs.writeFileSync(path.join(target,'package.json'),' {"type":"module"}\n');fs.writeFileSync(path.join(target,'reports/defense-fifth/v3-frozen.json'),'{"options":{}}\n');fs.writeFileSync(path.join(target,'reports/defense-fourth/normalization-pre41.json'),'{"selected":{}}\n');
const c=read('reports/defense-seventh/2024-25/calendar-25/config.json'),bundle=read(c.root+'/bundle.json'),card=read(c.root+'/pre25-v4-league.json'),calibration=read(c.root+'/calibration-v4.json').selected;
fs.writeFileSync(path.join(target,'input/bundle.json'),JSON.stringify(bundle));fs.writeFileSync(path.join(target,'input/card.json'),JSON.stringify(card));
const original=executeSeventhJob({label:'isolation',bundle:c.root+'/bundle.json',cardFile:c.root+'/pre25-v4-league.json',calibration,cutoff:25,calendarDate:c.date,indices:[1000,1001],seed:20261012});
const job={label:'isolation',bundle:'input/bundle.json',cardFile:'input/card.json',calibration,cutoff:25,calendarDate:c.date,indices:[1000,1001],seed:20261012};
fs.writeFileSync(path.join(target,'input/job.json'),JSON.stringify(job));fs.writeFileSync(path.join(target,'runner.js'),"import fs from 'node:fs';import {executeSeventhJob}from './src/defense_seventh_jobs.js';const r=executeSeventhJob(JSON.parse(fs.readFileSync('input/job.json')));fs.writeFileSync('input/result.json',JSON.stringify(r));\n");
execFileSync(process.execPath,['runner.js'],{cwd:target,stdio:'inherit'});const isolated=JSON.parse(fs.readFileSync(path.join(target,'input/result.json')));
assert.deepEqual(original.matches,isolated.matches);assert.deepEqual(original.teams,isolated.teams);
fs.writeFileSync('reports/defense-seventh/season-isolation-test.json',JSON.stringify({passed:true,games:original.matches.map(g=>g.id),definition:'Identical complete scores/player/team stats after removing all2025-26 data and replacing fitted legacy presets with empty stubs. Only2024-25 cutoff inputs and frozen structural source files supplied.',blindBundleHash:hash(c.root+'/bundle.json')},null,2)+'\n');console.log('2024-25 season-isolation exact score/stat parity passed');

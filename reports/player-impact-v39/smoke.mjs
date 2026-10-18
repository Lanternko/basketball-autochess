import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadInput} from './input.mjs';
import {loadInput as baselineInput} from '../player-impact-v30/input.mjs';
import {impactEngine} from './engine.mjs';
import {impactEngine as baselineEngine} from '../player-impact-v30/engine.mjs';
const strip=x=>Array.isArray(x)?x.map(strip):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).filter(([k])=>k!=='blk').map(([k,v])=>[k,strip(v)])):x;
const x=loadInput('2025-26'),base=baselineInput('2025-26'),clean=structuredClone(x);for(const t of clean.league.teams)for(const p of t.roster)delete p.blockEventMeasurement;assert.deepEqual(clean,base);
for(const b of [x,base]){b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=JSON.parse(fs.readFileSync('reports/player-impact-v7/2025-26-center.json')).fullCenter;}
const a=await baselineEngine('rotation-space'),b=await impactEngine('rotation-space');
const r1=a(base.league,base.exposure,{seed:20261012,options:base.options,audit:false,replay:false,indices:[0,1,2,3]}),r2=b(x.league,x.exposure,{seed:20261012,options:x.options,audit:false,replay:false,indices:[0,1,2,3]});
assert.deepEqual(strip(r1),strip(r2));console.log('Four-game smoke: every non-blk field and score identical; source input differs only by block event descriptor.');

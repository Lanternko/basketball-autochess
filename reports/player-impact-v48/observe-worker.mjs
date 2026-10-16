import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parentPort} from 'node:worker_threads';
import {loadInput} from '../player-impact-v47/input.mjs';
import {impactEngine} from '../player-impact-v47/engine.mjs';
import {fineCollector} from '../player-impact-v45/fine-collector.mjs';
import {onCourtCollector} from '../player-impact-v1/on-court.mjs';
import {defenseCollector} from '../player-impact-v42/defense-collector.mjs';
import {offenseCollector} from './offense-collector.mjs';
parentPort.on('message',async job=>{try{
 const b=loadInput(job.season),run=await impactEngine('rotation-space'),on=onCourtCollector(),defense=defenseCollector(),fine=fineCollector(job.seed^0x45F1A),offense=offenseCollector(job.seed^0x45F1A);
 b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=JSON.parse(fs.readFileSync(`reports/player-impact-v7/${job.season}-center.json`)).fullCenter;b.options.onCourtObserver=e=>{on.event(e);defense.event(e);fine.event(e);offense.event(e);};
 const valid=new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${job.season}-on-court-truth.json`)).gameIds),indices=b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[]);
 const r=run(b.league,b.exposure,{seed:job.seed,options:b.options,audit:false,replay:false,indices});r.onCourt=on.finish();r.defense=defense.finish(r.teams);r.fineDefense=fine.finish(r.teams);r.fineOffense=offense.finish(r.teams);delete r.options.onCourtObserver;
 const old=JSON.parse(fs.readFileSync(`reports/player-impact-v47/runs/${job.season}-v47-strict-${job.seed}.json`));for(const k of ['matches','teams','onCourt','defense','fineDefense'])assert.deepEqual(r[k],old[k],k);
 assert.deepEqual(r.fineOffense.total,r.fineDefense.total);r.observerOnlyBaselineParityPassed=true;
 fs.writeFileSync(job.file+'.tmp',JSON.stringify(r));fs.renameSync(job.file+'.tmp',job.file);parentPort.postMessage({job,games:r.matches.length});
 }catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

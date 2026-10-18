import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parentPort} from 'node:worker_threads';
import {loadInput} from './input.mjs';
import {impactEngine} from './engine.mjs';
import {fineCollector} from '../player-impact-v45/fine-collector.mjs';
import {onCourtCollector} from '../player-impact-v1/on-court.mjs';
import {defenseCollector} from '../player-impact-v42/defense-collector.mjs';
import {offenseCollector} from '../player-impact-v48/offense-collector.mjs';
import {rotationCollector} from './rotation-collector.mjs';
parentPort.on('message',async job=>{try{
 const b=loadInput(job.season),run=await impactEngine('rotation-space'),on=onCourtCollector(),defense=defenseCollector(),fine=fineCollector(job.seed^0x45F1A),offense=offenseCollector(job.seed^0x45F1A),rotation=rotationCollector();
 Object.assign(b.options,{creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:JSON.parse(fs.readFileSync(`reports/player-impact-v7/${job.season}-center.json`)).fullCenter,rotationIntervalObserver:e=>rotation.interval(e)});
 if(job.variant==='v47')b.options.rotationPolicy='legacy';
 const exceptions=new Map();b.options.rotationExceptionObserver=e=>exceptions.set(e.gameId,e);
 if(job.strict&&job.variant==='v49')b.options.onCourtObserver=e=>{on.event(e);defense.event(e);fine.event(e);offense.event(e);};
 const valid=job.strict?new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${job.season}-on-court-truth.json`)).gameIds):null,indices=valid?b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[]):null;
 const r=run(b.league,b.exposure,{seed:job.seed,options:b.options,audit:false,replay:false,indices});r.rotation=rotation.finish(r.teams);
 if(job.variant==='v47'){
  const original=JSON.parse(fs.readFileSync(`reports/player-impact-v47/runs/${job.season}-v47-strict-${job.seed}.json`));for(const k of ['matches','teams'])assert.deepEqual(r[k],original[k]);r.observerOnlyBaselineParityPassed=true;
 }else if(job.strict){r.onCourt=on.finish();r.defense=defense.finish(r.teams);r.fineDefense=fine.finish(r.teams);r.fineOffense=offense.finish(r.teams);assert.deepEqual(r.fineOffense.total,r.fineDefense.total);}
 r.rotationExceptions=[...exceptions.values()];delete r.options.rotationExceptionObserver;delete r.options.onCourtObserver;delete r.options.rotationIntervalObserver;delete r.options.measuredRotationProfiles;
 fs.writeFileSync(job.file+'.tmp',JSON.stringify(r));fs.renameSync(job.file+'.tmp',job.file);parentPort.postMessage({job,games:r.matches.length});
 }catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

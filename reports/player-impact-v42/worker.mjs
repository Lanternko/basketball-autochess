import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parentPort} from 'node:worker_threads';
import {loadInput as candidateInput} from './input.mjs';
import {loadInput as baselineInput} from '../player-impact-v41/input.mjs';
import {impactEngine as candidateEngine} from './engine.mjs';
import {impactEngine as baselineEngine} from './baseline-engine.mjs';
import {onCourtCollector} from '../player-impact-v1/on-court.mjs';
import {defenseCollector} from './defense-collector.mjs';
parentPort.on('message',async job=>{try{
 const b=(job.variant==='v42'?candidateInput:baselineInput)(job.season),run=await(job.variant==='v42'?candidateEngine:baselineEngine)('rotation-space'),on=onCourtCollector(),defense=defenseCollector();
 b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=JSON.parse(fs.readFileSync(`reports/player-impact-v7/${job.season}-center.json`)).fullCenter;
 if(job.strict)b.options.onCourtObserver=e=>{on.event(e);defense.event(e);};
 const valid=job.strict?new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${job.season}-on-court-truth.json`)).gameIds):null;
 const indices=job.indices??(valid?b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[]):null);
 const r=run(b.league,b.exposure,{seed:job.seed,options:b.options,audit:false,replay:false,indices});
 if(job.strict){r.onCourt=on.finish();r.defense=defense.finish(r.teams);assert.equal(r.defense.games,r.matches.length);}
 delete r.options.onCourtObserver;
 if(job.variant==='v41'){
  const archived=JSON.parse(fs.readFileSync(`reports/player-impact-v41/runs/${job.season}-rotation-space-strict-${job.seed}.json`));
  assert.deepEqual(r.matches,archived.matches);assert.deepEqual(r.teams,archived.teams);assert.deepEqual(r.onCourt,archived.onCourt);r.baselineParityPassed=true;
 }
 fs.writeFileSync(job.file,JSON.stringify(r));parentPort.postMessage({job,games:r.matches.length});
}catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

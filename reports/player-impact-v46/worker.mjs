import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parentPort} from 'node:worker_threads';
import {loadInput} from './input.mjs';
import {impactEngine} from '../player-impact-v45/engine.mjs';
import {fineCollector} from '../player-impact-v45/fine-collector.mjs';
import {onCourtCollector} from '../player-impact-v1/on-court.mjs';
import {defenseCollector} from '../player-impact-v42/defense-collector.mjs';
parentPort.on('message',async job=>{try{
 const b=loadInput(job.season),run=await impactEngine('rotation-space'),on=onCourtCollector(),defense=defenseCollector(),fine=fineCollector(job.seed^0x45F1A);
 b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=JSON.parse(fs.readFileSync(`reports/player-impact-v7/${job.season}-center.json`)).fullCenter;
 if(job.strict)b.options.onCourtObserver=e=>{on.event(e);defense.event(e);fine.event(e);};
 const valid=job.strict?new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${job.season}-on-court-truth.json`)).gameIds):null;
 const indices=valid?b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[]):null;
 const r=run(b.league,b.exposure,{seed:job.seed,options:b.options,audit:false,replay:false,indices});
 if(job.strict){r.onCourt=on.finish();r.defense=defense.finish(r.teams);r.fineDefense=fine.finish(r.teams);assert.equal(r.defense.games,r.matches.length);}
 delete r.options.onCourtObserver;
 fs.writeFileSync(job.file,JSON.stringify(r));parentPort.postMessage({job,games:r.matches.length});
}catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

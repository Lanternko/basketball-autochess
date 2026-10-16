import fs from 'node:fs';
import {parentPort} from 'node:worker_threads';
import {loadInput} from './input.mjs';
import {impactEngine} from './engine.mjs';
import {onCourtCollector} from '../player-impact-v1/on-court.mjs';
parentPort.on('message',async job=>{try{
 const b=loadInput(job.season),run=await impactEngine(job.version),collector=onCourtCollector();
 if(job.onCourt)b.options.onCourtObserver=e=>collector.event(e);
 const strict=job.strict?new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${job.season}-on-court-truth.json`)).gameIds):null;
 const indices=job.indices??(strict?b.league.schedule.flatMap((g,i)=>strict.has(g.id)?[i]:[]):null);
 const r=run(b.league,b.exposure,{seed:job.seed,options:b.options,audit:false,replay:false,indices});
 if(job.onCourt){r.onCourt=collector.finish();if(r.onCourt.games!==r.matches.length)throw Error('On-court game coverage mismatch');}
 delete r.options.onCourtObserver;fs.writeFileSync(job.file,JSON.stringify(r)+'\n');
 parentPort.postMessage({job,result:{games:r.matches.length}});
}catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(s=>!s.includes('data:text/javascript;base64')).join('\n')});}});

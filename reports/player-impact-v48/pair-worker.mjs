import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parentPort} from 'node:worker_threads';
import {loadInput} from '../player-impact-v47/input.mjs';
import {impactEngine} from './pair-engine.mjs';
parentPort.on('message',async job=>{try{
 const b=loadInput('2025-26'),run=await impactEngine('rotation-space'),pairs={};
 Object.assign(b.options,{creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:JSON.parse(fs.readFileSync('reports/player-impact-v7/2025-26-center.json')).fullCenter});
 b.options.pairMinuteObserver=e=>{for(const t of e.teams){if(!t.active.includes(201939))continue;const arm=t.lineup.includes(201939)?'on':'off';for(const pid of t.lineup){const x=pairs[pid]??={on:0,off:0};x[arm]+=e.seconds;}}};
 const valid=new Set(JSON.parse(fs.readFileSync('reports/player-impact-v1/2025-26-on-court-truth.json')).gameIds),indices=b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[]);
 const r=run(b.league,b.exposure,{seed:job.seed,options:b.options,audit:false,replay:false,indices});
 const old=JSON.parse(fs.readFileSync(`reports/player-impact-v47/runs/2025-26-v47-strict-${job.seed}.json`));for(const k of ['matches','teams'])assert.deepEqual(r[k],old[k],k);
 assert(Math.abs(pairs[201939].on-old.teams.flatMap(t=>t.players).filter(p=>p.playerId===201939).reduce((s,p)=>s+p.stats.seconds,0))<1e-6);
 fs.writeFileSync(job.file,JSON.stringify({seed:job.seed,pairs,baselineParityPassed:true}));parentPort.postMessage({passed:true,seed:job.seed});
 }catch(e){parentPort.postMessage({error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

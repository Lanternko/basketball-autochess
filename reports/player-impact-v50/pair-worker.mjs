import fs from 'node:fs';
import {parentPort} from 'node:worker_threads';
import {loadInput} from '../player-impact-v49/input.mjs';
import {impactEngine} from './pair-engine.mjs';
import {rotationCollector} from '../player-impact-v49/rotation-collector.mjs';
parentPort.on('message',async job=>{try{
 const b=loadInput(job.season),run=await impactEngine('rotation-space'),c=rotationCollector(),valid=new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${job.season}-on-court-truth.json`)).gameIds),all=b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[]),indices=Array.from({length:60},(_,i)=>all[Math.floor(i*(all.length-1)/59)]);
 Object.assign(b.options,{creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:JSON.parse(fs.readFileSync(`reports/player-impact-v7/${job.season}-center.json`)).fullCenter,rotationController:job.variant,measuredPairPhases:JSON.parse(fs.readFileSync(`reports/player-impact-v50/${job.season}-pair-phase.json`)),rotationIntervalObserver:e=>c.interval(e)});
 const r=run(b.league,b.exposure,{seed:20261012,options:b.options,indices,audit:false,replay:false});fs.writeFileSync(job.file,JSON.stringify({season:job.season,variant:job.variant,rotation:c.finish(r.teams),matches:r.matches}));parentPort.postMessage({passed:true,season:job.season,variant:job.variant});
 }catch(e){parentPort.postMessage({error:e.stack.split('\n').filter(l=>!l.includes('data:text/javascript;base64')).join('\n')});}});

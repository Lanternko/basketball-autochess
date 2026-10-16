import {attachCreationContext} from '../../src/measured_creation_context.js';
import fs from 'node:fs';
import {parentPort} from 'node:worker_threads';
import {positionalOvrInput} from './positional-input.mjs';
import {attachMeasurements} from '../player-impact-v13/input.mjs';
import {impactEngine} from '../player-impact-v13/engine.mjs';
import {lineup} from '../ovr-2025-26-positional/protocol.mjs';
import {summarizeStrata} from '../../src/strength_benchmark.js';
const inputs=new Map();
parentPort.on('message',async job=>{try{
 let x=inputs.get(job.season);if(!x){x=await positionalOvrInput(job.season);attachMeasurements(x.players,job.season);for(const t of x.opponents)attachMeasurements(t.roster,job.season);attachCreationContext(x.profiles,JSON.parse(fs.readFileSync(`reports/player-impact-v13/${job.season}-contexts.json`)).contextReference);inputs.set(job.season,x);}
 const center=JSON.parse(fs.readFileSync(`reports/player-impact-v13/${job.season}-synthetic-center.json`)).fullCenter;const settings=v=>{const scale=v==='threat-space'?1:0;return {...x.options,creationPolicy:v,contextLongScale:scale,spaceCenter:scale*center};};
 const run=await impactEngine(job.version,{game:true,memoized:true}),original=job.kind==='baseline'?x.profiles[job.slot]:x.players.find(p=>p.playerId===job.id),p=structuredClone(original),slot=job.slot??x.roleMap.get(p.playerId).slot;
 const team=lineup(x,p,slot),strata=[],margins=[],stats={pts:0,allowed:0,ast:0,oreb:0,tov:0,fgm:0,fga:0,fg3m:0,fg3a:0};
 for(let opponent=0;opponent<x.opponents.length;opponent++){
  const values=[],cacheA=new Map(),cacheB=new Map();let margin=0;
  for(let i=0;i<job.samples;i++){
   const seed=(job.seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
   const a=run(team,x.opponents[opponent],{...settings(job.version),seed,ovrCache:cacheA}),b=run(x.opponents[opponent],team,{...settings(job.version),seed,ovrCache:cacheB});
   if(a.gameSeconds!==864||b.gameSeconds!==864)throw Error('Probe exposure drift');
   values.push(((a.scoreA>a.scoreB?1:a.tie?.5:0)+(b.scoreB>b.scoreA?1:b.tie?.5:0))/2);margin+=(a.scoreA-a.scoreB+b.scoreB-b.scoreA)/2;
   for(const [own,op]of [[a.statA,a.statB],[b.statB,b.statA]]){for(const k of Object.keys(stats).filter(k=>k!=='allowed'))stats[k]+=own[k];stats.allowed+=op.pts;}
  }
  strata.push(values);margins.push(margin/job.samples);
 }
 parentPort.postMessage({job,result:{playerId:p.playerId,name:p.name,position:x.profiles[slot].pos,...summarizeStrata(strata),meanMargin:margins.reduce((s,v)=>s+v,0)/margins.length,statsPerGame:Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,v/(60*job.samples)]))}});
}catch(e){parentPort.postMessage({job,error:e.stack.split('\n').filter(x=>!x.includes('data:text/javascript;base64')).join('\n')});}});

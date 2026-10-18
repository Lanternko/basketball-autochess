import {parentPort} from 'node:worker_threads';
import {positionalInputs,lineup,centered} from './protocol.mjs';
import {gameEngine} from '../ovr-2025-26-latest/runtime.mjs';
import {summarizeStrata} from '../../src/strength_benchmark.js';
const x=positionalInputs(),run=await gameEngine({memoized:true});
parentPort.on('message',job=>{try{
  const original=job.kind==='anchor'?centered(x.profiles[job.slot],job.level):x.players.find(p=>p.playerId===job.id);
  if(!original)throw Error('Missing player '+job.id);
  const p=structuredClone(original),slot=job.slot??x.roleMap.get(p.playerId).slot;
  if(job.intervention==='physique70')p.physique=70;
  if(job.intervention==='rebound-neutral'){p.rebound=70;p.individualOreb=structuredClone(x.profiles[slot].individualOreb);}
  if(job.intervention==='help70')p.help=70;
  if(job.intervention==='short70')p.short=70;
  const team=lineup(x,p,slot,job.baseline),strata=[],outcomes=[],margins=[],stats={pts:0,allowed:0,oreb:0,dreb:0,tov:0,fga:0,fta:0};
  for(let opponent=0;opponent<x.opponents.length;opponent++){
    const values=[],cacheA=new Map(),cacheB=new Map();let margin=0;
    for(let i=0;i<job.samples;i++){
      const seed=(job.seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
      const a=run(team,x.opponents[opponent],{...x.options,seed,ovrCache:cacheA});
      const b=run(x.opponents[opponent],team,{...x.options,seed,ovrCache:cacheB});
      if(a.gameSeconds!==864||b.gameSeconds!==864)throw Error('Exposure drift');
      const credit=((a.scoreA>a.scoreB?1:a.tie?.5:0)+(b.scoreB>b.scoreA?1:b.tie?.5:0))/2;
      values.push(credit);outcomes.push(credit);margin+=(a.scoreA-a.scoreB+b.scoreB-b.scoreA)/2;
      for(const [own,op]of [[a.statA,a.statB],[b.statB,b.statA]]){
        for(const k of ['pts','oreb','dreb','tov','fga','fta'])stats[k]+=own[k];stats.allowed+=op.pts;
      }
    }
    strata.push(values);margins.push(margin/job.samples);
  }
  const result={playerId:p.playerId,name:original.name,position:x.profiles[slot].pos,...summarizeStrata(strata),
    meanMargin:margins.reduce((s,v)=>s+v,0)/margins.length,statsPerGame:Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,v/(60*job.samples)])),outcomes};
  parentPort.postMessage({job,result});
}catch(e){parentPort.postMessage({job,error:e.stack});}});

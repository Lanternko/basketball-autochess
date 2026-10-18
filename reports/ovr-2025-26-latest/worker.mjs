import {parentPort} from 'node:worker_threads';
import {inputs,gameEngine,probe} from './runtime.mjs';
import {summarizeStrata} from '../../src/strength_benchmark.js';
const x=inputs(),run=await gameEngine({memoized:true});
parentPort.on('message',job=>{try{
  const p=job.kind==='anchor'?x.anchors.find(p=>p.playerId===job.id):x.players.find(p=>p.playerId===job.id);
  if(!p)throw Error('Unknown player '+job.id);
  const lineups=Array.from({length:5},(_,i)=>probe(x.base,p,i));
  const strata=[],margins=[];
  let tied=0;
  for(let opponent=0;opponent<x.opponents.length;opponent++)for(let slot=0;slot<5;slot++){
    const values=[],cacheA=new Map(),cacheB=new Map();let margin=0;
    for(let i=0;i<job.samples;i++){
      const seed=(job.seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
      const a=run(lineups[slot],x.opponents[opponent],{...x.options,seed,ovrCache:cacheA});
      const b=run(x.opponents[opponent],lineups[slot],{...x.options,seed,ovrCache:cacheB});
      for(const g of [a,b])if(g.gameSeconds!==864||g.statA.pts!==g.scoreA||g.statB.pts!==g.scoreB)throw Error('Exposure/accounting failed');
      tied+=Number(a.tie)+Number(b.tie);
      values.push(((a.scoreA>a.scoreB?1:a.tie?.5:0)+(b.scoreB>b.scoreA?1:b.tie?.5:0))/2);
      margin+=(a.scoreA-a.scoreB+b.scoreB-b.scoreA)/2;
    }
    strata.push(values);margins.push(margin/job.samples);
  }
  parentPort.postMessage({job,result:{playerId:p.playerId,name:p.name,...summarizeStrata(strata),
    meanMargin:margins.reduce((a,b)=>a+b,0)/margins.length,tiedGames:tied,
    stratumWinRates:strata.map(s=>s.reduce((a,b)=>a+b,0)/s.length),
    stratumSumSquares:strata.map(s=>s.reduce((a,b)=>a+b*b,0))}});
}catch(e){parentPort.postMessage({job,error:e.stack});}});

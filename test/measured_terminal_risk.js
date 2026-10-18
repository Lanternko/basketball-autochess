import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadInput} from '../reports/player-impact-v21/input.mjs';
import {measuredTerminalRisk,terminalDefenseProbabilities} from '../reports/player-impact-v21/model.mjs';
import {exposureDefenseProbabilities} from '../reports/player-impact-v20/model.mjs';
import {observedFoulInputs} from '../reports/player-impact-v5/model.mjs';
import {attemptMakeProbability,pressureSignal} from '../src/defense_probability.js';
import {measuredContext} from '../src/measured_creation_context.js';
import {ovrInput} from '../reports/player-impact-v21/ovr-input.mjs';
const r={deadProbability:.05,neutralLiveProbability:.03};
assert.deepEqual(measuredTerminalRisk(r,1),{dead:.05,live:.03,total:.08,liveShare:.375});
assert.equal(measuredTerminalRisk(r,1.8).dead,.05);
assert.ok(measuredTerminalRisk(r,1.8).live>measuredTerminalRisk(r,.4).live);
assert.throws(()=>measuredTerminalRisk(null,1),/Missing/);
assert.throws(()=>measuredTerminalRisk(r,2),/invalid pressure/);
assert.throws(()=>measuredTerminalRisk({deadProbability:.9,neutralLiveProbability:.1},1.8),/Invalid/);
let checked=0,maxCenterDifference=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),src=JSON.parse(fs.readFileSync(`reports/player-impact-v21/${season}-terminal-events.json`));
 const totals=src.games.flatMap(g=>g.rows).reduce((s,r)=>s+r[1],0);
 assert.equal(totals,src.totals.fga+src.totals.unrecordedShootingFouls+src.totals.nonpassLive+src.totals.nonpassDead);
 assert.equal(src.totals.unmappedEvents,0);assert.equal(src.totals.actorOutsideLineup,0);
 for(let t=0;t<b.league.teams.length;t++){
  const os=b.league.teams[t].roster.slice(0,5),ds=b.league.teams[(t+1)%b.league.teams.length].roster.slice(0,5);
  for(let i=0;i<5;i++){
   const p=os[i],ctx=measuredContext(os,i),base={turnoverMode:'pressure',pressureAttribute:pressureSignal(ds,b.options.stealPriorRate).attribute,contextLongScale:1,contextShortScale:b.options.contextShortScale};
   const a=[],c=[];
   for(let j=0;j<5;j++){
    const opts={...base,assist:j===i?null:os[j].pass};
    const q=exposureDefenseProbabilities(p,ctx,ds[i],70,70,70,70,opts,ds),n=terminalDefenseProbabilities(p,ctx,ds[i],70,70,70,70,opts,ds,b.options);
    assert.deepEqual(n.make,q.make);assert.deepEqual(n.zone,q.zone);
    assert.ok(Math.abs(n.pFoul/(1-n.pTovTouch)-q.pFoul/(1-q.pTovTouch))<1e-14);
    assert.ok(Math.abs(['TOV','FOUL','FG3M','FG3X','MIDM','MIDX','RIMM','RIMX'].reduce((s,k)=>s+n[k],0)-1)<1e-12);
    const foul=observedFoulInputs(q,p,b.options,attemptMakeProbability),den=['long','mid','short'].reduce((s,z)=>s+q.zone[z]/foul[z].recorded,0);
    a.push({w:(j+1)*(1-q.pTovTouch*b.options.touchTurnoverScale)/den,make:q.make});
    c.push({w:(j+1)*(1-n.pTovTouch)/den,make:n.make});
    checked++;
   }
   for(const z of ['long','mid','short']){
    const avg=xs=>xs.reduce((s,x)=>s+x.w*x.make[z],0)/xs.reduce((s,x)=>s+x.w,0);
    maxCenterDifference=Math.max(maxCenterDifference,Math.abs(avg(a)-avg(c)));
   }
  }
 }
}
assert.ok(maxCenterDifference<1e-12,'Handler-only survival cancels inside the conditioned self/received source mixture; retain frozen v20 centers.');
const x=await ovrInput('2025-26');for(const p of [...x.players,...x.profiles,...x.opponents.flatMap(t=>t.roster)])for(const pressure of [.4,1,1.8])measuredTerminalRisk(p.terminalRiskMeasurement,pressure);
console.log(JSON.stringify({checked,maxCenterDifference,sourceScope:'All four strict seasons, source totals conserved; measured dead/live split and pooled synthetic cards valid.'}));

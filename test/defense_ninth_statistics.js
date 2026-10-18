import assert from 'node:assert/strict';
import {fitN,aggregateN,evaluateN,logisticSlopeN,sigmoidN} from '../src/defense_ninth_statistics.js';
const data=Array.from({length:4},(_,s)=>Array.from({length:3},(_,k)=>{const x=Array.from({length:30},(_,i)=>i-14.5),d=x.map((_,i)=>(i%4)-1.5),dm=d.reduce((a,b)=>a+b,0)/30,y=x.map((v,i)=>.8*v+2*(d[i]-dm));return {season:'s'+s,k:[25,41,55][k],x,y,games:x.map(()=>40),wins:y.map(v=>40*sigmoidN(.2*v)),simpleWins:x.map(()=>20),ms:1,deltas:Object.fromEntries(['sim-v3','sim-v4','seg','naive'].map(v=>[v,Array.from({length:20},()=>d)])),refSD:Array(20).fill(17)};}));
const blocks=aggregateN(data,Array(20).fill(1),Array(30).fill(1)),f=fitN(blocks,[0,1,2],'seg',Array(30).fill(1));assert(Math.abs(f.b-2)<1e-10);assert(f.a.every(x=>Math.abs(x-.8)<1e-10));
const e=evaluateN(data);assert(e.pooled.every(c=>c.versions['seg-fit'].netRMSE<1e-10));assert(e.pooled.every(c=>c.versions['seg-b1'].netRMSE>.5));
const slope=logisticSlopeN([{p:blocks[0][0].y,c:blocks[0][0]}],Array(30).fill(1));assert(Math.abs(slope-.2)<1e-6);
const changed=structuredClone(data);changed[3].forEach(c=>c.y=c.y.map(v=>v*10));const fit=fitN(aggregateN(changed,Array(20).fill(1),Array(30).fill(1)),[0,1,2],'seg',Array(30).fill(1));assert.deepEqual(fit,f,'Held-out targets never enter own coefficient fit');
changed[3].forEach(c=>c.wins=c.wins.map(v=>40-v));const changedEval=evaluateN(changed);for(let k=0;k<3;k++)for(const v of ['seg-fit','sim-v3-fit','naive-b1','simple'])assert.equal(changedEval.cells[3][k].versions[v].linkBeta,e.cells[3][k].versions[v].linkBeta,'Heldout wins/net do not enter nested link calibration');
console.log('PASS identifiable coefficients,exact holdout prediction,b1 control,logistic recovery,heldout-target exclusion');

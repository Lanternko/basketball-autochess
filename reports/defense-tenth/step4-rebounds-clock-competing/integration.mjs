import {Worker} from 'node:worker_threads';
import assert from 'node:assert/strict';import fs from 'node:fs';
import {read} from '../../../scripts/defense_io.js';
import {job} from '../step4-rebounds-turnover-time/run.mjs';
const root='reports/defense-tenth/step4-rebounds-clock-competing',s='2025-26';
const j={...job(s,'split',20261012,read(`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`).selected),clockCalibration:read(`reports/defense-tenth/step4-rebounds-turnover-time/${s}/calibration.json`).selected,mode:'combined',indices:[0],pEffective:0,freshClockProbability:0,postOrebClockProbability:1};
const w=new Worker(new URL('./worker.mjs',import.meta.url));
try{const m=await new Promise((resolve,reject)=>{w.on('message',resolve);w.on('error',reject);w.postMessage(j);});if(m.error)throw Error(m.error);const r=m.result;
assert.ok(r.clockTrials[0].postOreb>0);assert.equal(r.eventCounts[0].postOrebClock,r.clockTrials[0].postOreb);assert.equal(r.eventCounts[0].clock,r.eventCounts[0].postOrebClock);assert.equal(r.eventCounts[0].natural,0);
fs.writeFileSync(root+'/integration.json',JSON.stringify({passed:true,forcedProbability:1,trials:r.clockTrials,events:r.eventCounts,matches:r.matches,accounting:'runDefenseSeason checks passed'},null,2)+'\n');console.log('Forced deadline integration passed');
}finally{await w.terminate();}

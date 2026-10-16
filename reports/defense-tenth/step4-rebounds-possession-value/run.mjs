import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import assert from 'node:assert/strict';
import {read,hash} from '../../../scripts/defense_io.js';
import {normalizeRealGame,realFactorEvent} from '../../../src/defense_pbp_analysis.js';
const root='reports/defense-tenth/step4-rebounds-possession-value',old='reports/defense-tenth/step4-rebounds-turnover-time';
const p=read(root+'/protocol.json');assert.equal(hash(root+'/protocol.json'),fs.readFileSync(root+'/protocol.sha256','utf8').trim());
const special=e=>/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test((e.qualifiers??[]).join(' '));
const real={};
for(const season of p.seasons){
 const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),folder=season==='2025-26'?'data/defense-a-source/pbp':`data/defense-seventh/${season}/pbp`,games=[],failures=[];
 for(const f of b.league.schedule){const id=f.id??f.gameId;try{
  const actions=read(`${folder}/${id}.json`).data.game.actions,refs=new Map(actions.map(e=>[e.actionNumber,e])),n=normalizeRealGame(actions,f,null);
  if(!n.pointsValid){failures.push({id,reason:'score-accounting',anomalies:n.anomalies});continue;}
  const rows=[];for(const pos of n.possessions){const es=actions.slice(pos.startIndex,pos.endIndex+1);if(es.some(e=>e.actionType==='freethrow'&&special(e)))continue;
   const anchors=es.flatMap((e,i)=>{const s=refs.get(e.shotActionNumber);return e.actionType==='rebound'&&e.subType==='offensive'&&e.personId>0&&!(e.qualifiers??[]).includes('team')&&s?.teamId===e.teamId&&s?.period===e.period&&['2pt','3pt'].includes(s?.actionType)&&s.shotResult==='Missed'?[i]:[];});
   for(let k=0;k<anchors.length;k++){let fg=0,ft=0;for(const e of es.slice(anchors[k]+1))if(e.teamId===n.ids[pos.side]){const c=realFactorEvent(e);if(e.actionType==='freethrow')ft+=c.points;else fg+=c.points;}rows.push({off:pos.side,first:k===0,points:fg+ft,fgPoints:fg,ftPoints:ft,additionalOreb:anchors.length-k-1});}
  }games.push({id,ids:n.ids,rows});
 }catch(e){failures.push({id,reason:e.message});}}
 real[season]={games,failures};console.log('REAL',season,games.length,'failed',failures.length);
}
fs.writeFileSync(root+'/real.json',JSON.stringify(real));
const jobs=p.seasons.flatMap(season=>p.seeds.map(seed=>({season,seed,version:'split',bundle:`reports/defense-tenth/step4-t0/${season}/bundle.json`,baseCalibration:season==='2025-26'?null:read(`reports/defense-tenth/step4-t0/${season}/calibration-v3.json`).selected,calibration:read(`reports/defense-tenth/step4-rebounds-oreb/${season}/calibration-oreb.json`).selected,clockCalibration:read(`${old}/${season}/calibration.json`).selected,diagnostic:true,file:`${root}/runs/${season}-${seed}.json`})));
fs.mkdirSync(root+'/runs',{recursive:true});let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{for(let i=0;i<Math.min(8,jobs.length);i++){const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log('SIM',++done,jobs.length,m.job.season,m.job.seed);if(done===jobs.length)resolve();else if(next<jobs.length)w.postMessage(jobs[next++]);});w.postMessage(jobs[next++]);}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
const parity=[];for(const j of jobs){const x=read(j.file),y=read(`${old}/runs/${j.season}-split-${j.seed}.json`);assert.deepEqual(x.matches,y.matches);assert.deepEqual(x.teams,y.teams);parity.push({season:j.season,seed:j.seed,games:x.matches.length,exactScoresAndStats:true});}
fs.writeFileSync(root+'/parity.json',JSON.stringify(parity,null,2));

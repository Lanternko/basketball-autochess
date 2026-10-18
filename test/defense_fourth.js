import assert from 'node:assert/strict';
import {executeFourthJob,fourthOptions} from '../src/defense_fourth_jobs.js';
import {executeThirdJob} from '../src/defense_third_jobs.js';
import {runFourthJobs} from '../src/defense_fourth_pool.js';
import {continuousDuration,effect,fourthProbability} from '../src/defense_fourth_effects.js';
import * as M from '../src/probability_model.js';
import {makeRng} from '../src/rng.js';
import {read,hash} from '../scripts/defense_io.js';
import {summarize,comparison} from '../src/defense_fourth_scoreboard.js';
const job={label:'v1',seed:20261012,indices:Array.from({length:12},(_,i)=>i),audit:false};
assert.deepEqual(executeFourthJob(job).matches,executeThirdJob({...job,preset:'v1'}).matches);
const jobs=[{label:'v2',seed:20261012,indices:[0,1],audit:false},{label:'v2',seed:20261013,indices:[0,1],audit:false}];
const parallel=await runFourthJobs(jobs,{workers:2});for(let i=0;i<2;i++)assert.deepEqual(parallel[i],executeFourthJob(jobs[i]));
const rng=makeRng(8),a=Array(100).fill(21),values=Array.from({length:10000},()=>continuousDuration(a,21,rng));assert.ok(values.every(v=>v>=20.5&&v<=21));assert.ok(Math.abs(values.reduce((a,b)=>a+b,0)/values.length-20.75)<.01);
const fake=Array.from({length:5},(_,i)=>({playerId:i,long:70,mid:70,short:70,drive:70,ft:70,pass:70,rebound:70,onBall:70,help:70,physique:70,offBall:70,screen:70,handle:70,breakDbl:70,tovSkill:70}));
for(let i=0;i<5;i++){
  const opt={rimSignal:true,defenseSignals:{values:{[i]:{shortFG:.5}},centers:{shortFG:0}}};assert.equal(effect(fake,'shortFG',opt),.1);
  const args=[fake[0],M.teammateContext(fake,0),fake[0],70,70,70,70,{turnoverMode:'legacy'},fake];
  const base=fourthProbability(...args,{rimSignal:true,defenseSignals:{values:{},centers:{shortFG:0}}}),shift=fourthProbability(...args,opt);
  assert.ok(shift.make.short>base.make.short);assert.ok(Math.abs(Object.values(shift.zone).reduce((a,b)=>a+b,0)-1)<1e-12);
}
for(const flag of ['relativeFouls','continuousTiming','neutralContests','reboundSignal','rimSignal','liveSignal','zoneSignal','foulSignal','scoreRotation'])assert.equal(fourthOptions({label:'v2',options:{[flag]:false}})[flag],false);
const pre=read('reports/defense-fourth/pre41-league.json'),model=read('reports/defense-fourth/model-pre41/engine-signals.json');assert.equal(model.trainGames.length,574);assert.deepEqual(new Set(pre.fourthProvenance.trainingGames),new Set(model.trainGames));
if(process.argv.includes('--artifacts')){
  const selected=read('reports/defense-fourth/final-selection.json');
  const labels=[...new Set(['v1','v2',...read('reports/defense-fourth/signal-sequence.json').results.map(r=>r.label),'rotation-only','rotation-signals','holdout-v1','holdout-v2','holdout-final',selected.finalLabel,selected.holdoutFinalLabel])];
  for(const label of labels){const m=read('reports/defense-fourth/'+label+'-seeds.json');assert.equal(m.files.length,20);for(const [file,h] of Object.entries(m.code))assert.equal(hash(file),h);for(const f of m.files){assert.equal(hash(f.file),f.sha256);const r=read(f.file);assert.ok(r.teams.every(t=>t.games===(label.startsWith('holdout')?41:82)));assert.ok(r.analysis.games>600);}}
  const old=read('reports/defense-a/v1-seeds.json'),now=read('reports/defense-fourth/v1-seeds.json');for(let i=0;i<20;i++)assert.deepEqual(read(now.files[i].file).matches,read(old.files[i].file).matches);
  const original=now.files.map(f=>read(f.file)),shuffled=original.map(r=>({...r,teams:r.teams.slice().reverse()}));
  assert.deepEqual(summarize(original).metrics,summarize(shuffled).metrics);
  for(const d of Object.values(comparison(original,shuffled,false,100)))assert.equal(d.estimate,0);
  for(const mode of ['full','pre41']){
    const m=read('reports/defense-fourth/model-'+mode+'/engine-signals.json'),n=read('reports/defense-fourth/normalization-'+mode+'.json');
    for(let i=0;i<m.players.length;i++)for(const [k,v] of Object.entries(m.effects))assert.equal(n.selected.defenseSignals.values[m.players[i]][k],v[i]);
    for(const [k,c] of Object.entries(m.centers))assert.equal(n.selected.defenseSignals.centers[k],c+(n.shifts[k]??0));
  }
  const report=read('reports/defense-fourth/closeout.json');assert.ok(Math.abs(report.errorDecomposition.offenseShare+report.errorDecomposition.defenseShare-1)<1e-9);
  for(const [file,h] of Object.entries(report.sources))assert.equal(hash(file),h,'closeout provenance: '+file);
  assert.ok(Math.abs(report.heldout.errorDecomposition.totalMSE-report.heldout.final.netRMSE**2)<1e-8);
  assert.equal(report.verdict,'部分成功');assert.equal(report.heldoutVerdict,'部分成功');assert.equal(selected.rotationAccepted,false);
  assert.equal(report.fullSeasonVerdict,report.paired.finalVsV1.netRMSE.ci95[1]<0&&report.paired.finalVsV1.winMAE.ci95[1]<0&&report.paired.finalVsV1.netSDRatio.ci95[1]>=0?'成功':report.fullSeasonVerdict);
}
console.log('Defense fourth: frozen parity, worker identity, continuous conditional timing, switches and cutoff provenance PASS');

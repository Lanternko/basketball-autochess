import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {pressureSignal} from '../../src/defense_probability.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import {loadSourceInput} from './input.mjs';
import {exposureDefenseProbabilities,terminalDefenseProbabilities} from './model.mjs';
import {exposureDefenseProbabilities as oldProbability,terminalDefenseProbabilities as oldTerminal} from '../player-impact-v30/model.mjs';
import {sourceFreshDefense,shiftMakeLogit} from '../../src/source_fresh_defense.js';
const root='reports/player-impact-v41',sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),close=(a,b)=>assert.ok(Math.abs(a-b)<1e-12,[a,b]);
let sourceRows=0,counterfactuals=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadSourceInput(season);
 for(let team=0;team<30;team+=3){
  const os=b.league.teams[team].roster.slice(0,5),ds=b.league.teams[(team+1)%30].roster.slice(0,5),ctx=measuredContext(os,0),neutral=ds.map(p=>{const q=structuredClone(p);delete q.freshDefenseMeasurement;return q;}),phys=M.teamPhysique(ds),pressure=pressureSignal(ds,b.options.stealPriorRate).attribute,opt={...b.options,pressureAttribute:pressure,assist:null,contextLongScale:1},args=def=>[os[0],ctx,def[0],M.helpDefense(def),70,70,M.teamPhysique(def),opt,def];
  assert.deepEqual(exposureDefenseProbabilities(...args(neutral)),oldProbability(...args(neutral)));
  assert.deepEqual(terminalDefenseProbabilities(...args(neutral),b.options),oldTerminal(...args(neutral),b.options));
  for(const def of [ds,neutral]){const a=args(def);a[7]={...opt,putback:true};assert.deepEqual(exposureDefenseProbabilities(...a),oldProbability(...a));}
  const actual=exposureDefenseProbabilities(...args(ds));
  // Use the frozen v30 base with zero tracking delta and neutral defensive
  // physique, isolating only the current raw offensive context and defense70.
  const zeroTracking=neutral.map(p=>({...p,physique:70,defenseExposureMeasurement:{...p.defenseExposureMeasurement,long:{...p.defenseExposureMeasurement.long,rate:0},short:{...p.defenseExposureMeasurement.short,rate:0}}}));
  const reference=oldProbability(os[0],ctx,{onBall:70},70,70,70,70,opt,zeroTracking),delta=sourceFreshDefense(ds);
  for(const z of ['long','mid','short']){
   const limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)];close(actual.make[z],Math.max(limits[0],Math.min(limits[1],shiftMakeLogit(reference.make[z],delta.logits[z]))));
  }
  close(actual.TOV+actual.FOUL+actual.FG3M+actual.FG3X+actual.MIDM+actual.MIDX+actual.RIMM+actual.RIMX,1);sourceRows++;
  for(const key of ['onBall','help','physique']){
   const stronger=structuredClone(ds);stronger[0][key]+=10;const q=exposureDefenseProbabilities(...args(stronger));
   if(key==='onBall')assert.ok(q.make.long<=actual.make.long+1e-12);
   else assert.ok(q.make.short<=actual.make.short+1e-12);
   counterfactuals++;
  }
 }
}
const files=['model.mjs','input.mjs','engine.mjs','verify-model.mjs','fit.json'].map(p=>root+'/'+p).concat(['src/source_fresh_defense.js','test/source_fresh_defense.js']);fs.writeFileSync(root+'/model-verification.json',JSON.stringify({passed:true,sourceRows,counterfactuals,unmeasuredFallbackExact:true,putbackDefenseExact:true,sourceFreshLogitFormulaExact:true,scope:'Raw probability and source-relative attribute slopes; no full-season or ranking claim.',hashes:Object.fromEntries(files.map(p=>[p,sha(p)]))},null,2));console.log({passed:true,sourceRows,counterfactuals});

import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import {defenseProbabilities,pressureSignal} from '../../src/defense_probability.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import {measuredRecipientWeights} from '../../src/individual_box_allocation.js';
import {loadInput as oldInput} from '../player-impact-v14/input.mjs';
import {loadInput} from './input.mjs';
let checks=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const a=oldInput(season),b=loadInput(season);
 for(let ti=0;ti<30;ti++)for(const fatigue of [0,.35,.8]){
  const os=a.league.teams[ti].roster.slice(0,5).map(p=>M.applyStamina(p,fatigue));
  const ns=b.league.teams[ti].roster.slice(0,5).map(p=>M.applyStamina(p,fatigue));
  const ds=a.league.teams[(ti+7)%30].roster.slice(0,5);
  assert.deepEqual(measuredRecipientWeights(ns,'dreb'),measuredRecipientWeights(os,'dreb'));
  assert.deepEqual(measuredRecipientWeights(ns,'blk'),measuredRecipientWeights(os,'blk'));
  for(let i=0;i<5;i++)for(const assisted of [false,true]){
   const opts={assist:assisted?os[(i+1)%5].pass:null,contextScale:a.options.contextScale,contextLongScale:1,contextShortScale:a.options.contextShortScale,turnoverMode:a.options.turnoverMode,turnoverScale:a.options.turnoverScale,pressureAttribute:pressureSignal(ds,a.options.stealPriorRate).attribute};
   const q=(ls)=>defenseProbabilities(ls[i],measuredContext(ls,i),ds[i],M.helpDefense(ds),70,70,M.teamPhysique(ds),opts);
   const x=q(os),y=q(ns);assert.deepEqual(y.make,x.make);assert.deepEqual(y.zone,x.zone);assert.equal(y.pTovTouch,x.pTovTouch);checks++;
  }
 }
}
const files=['src/free_throw_profile_prior.js','reports/player-impact-v16/input.mjs','reports/player-impact-v16/ftr-prior.json'];
const out={checks,sourceMakeZoneTurnoverAndConditionalReboundBlockWeightsUnchanged:true,sourceContextReuse:'v14 make-context centers remain applicable: FTR changes foul-event conditioning, not the source make/context/role predictors. Keeping original drive is deliberate isolation; its raw-proxy reliability remains unresolved.',hashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')]))};
fs.writeFileSync('reports/player-impact-v16/isolation-verification.json',JSON.stringify(out,null,2));console.log(out);

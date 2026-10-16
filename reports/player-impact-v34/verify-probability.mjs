// Compare standalone source reconstruction against the actual v34 game closure.
// The observer changes no return value or random draw and the original engine
// source is only read. A missing pressure covariate must fail finite checks.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import {terminalDefenseProbabilities} from '../player-impact-v30/model.mjs';
import {spaceProbability} from '../player-impact-v22/model.mjs';
import {pressureSignal} from '../../src/defense_probability.js';
import {ovrInput} from './ovr-input.mjs';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
let code=fs.readFileSync('reports/player-impact-v34/engine.mjs','utf8');
const anchor='return spaceProbability(originalProbability,os[i],putback!==null,opt);';
assert.ok(code.includes(anchor));
code=code.replaceAll(anchor,'const checkedProbability=spaceProbability(originalProbability,os[i],putback!==null,opt); opt.probabilityAudit?.({os,ds,i,a,forced,putback:putback!==null,actual:checkedProbability}); return checkedProbability;');
const {impactEngine}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const run=await impactEngine('rotation-space',{game:true}),x=await ovrInput(),cap=source().capMinutes;
let checks=0,received=0,self=0,rejectedMissingPressure=false;
for(const pid of [1628983,201939,1629011,1641705]){
 const p=x.players.find(p=>p.playerId===pid),slot=x.roleMap.get(pid).slot,a=workloadTeam(x,p,slot,cap,cap,0),b=opponentTeam(x,x.opponents[0],cap,0);
 const opt=options(x,20261021+slot,[a.schedule,b.schedule]);
 opt.probabilityAudit=({os,ds,i,a,forced,putback,actual})=>{
  const tr=lineup=>C.weightedTop(lineup.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound);
  const opts={assist:a,forced,putback,contextScale:opt.contextScale,turnoverScale:opt.turnoverScale,turnoverMode:opt.turnoverMode,pressureAttribute:pressureSignal(ds,opt.stealPriorRate).attribute,contextLongScale:opt.contextLongScale,contextShortScale:opt.contextShortScale};
  const args=[os[i],measuredContext(os,i),ds[i],M.helpDefense(ds),tr(os),tr(ds),M.teamPhysique(ds)];
  const q=terminalDefenseProbabilities(...args,opts,ds,opt),standalone=spaceProbability(q,os[i],putback,opt);
  assert.deepEqual(standalone,actual);
  for(const v of [standalone.ev,standalone.pFoul,standalone.pTovTouch,...Object.values(standalone.make)])assert.ok(Number.isFinite(v));
  if(!rejectedMissingPressure){
   const broken={...opts};delete broken.pressureAttribute;
   const bad=terminalDefenseProbabilities(...args,broken,ds,opt);
   assert.throws(()=>{for(const v of [bad.ev,bad.pFoul,bad.pTovTouch])assert.ok(Number.isFinite(v));});
   rejectedMissingPressure=true;
  }
  checks++;if(a===null)self++;else received++;
 };
 run(a.team,b.team,opt);
}
assert.ok(checks>100&&received>0&&self>0&&rejectedMissingPressure);
const root='reports/player-impact-v34',files=[root+'/verify-probability.mjs','reports/player-impact-v34/engine.mjs','reports/player-impact-v30/model.mjs',root+'/prepare-data.mjs'];
fs.writeFileSync(root+'/probability-verification.json',JSON.stringify({passed:true,games:4,probabilityComparisons:checks,selfComparisons:self,receivedComparisons:received,allProbabilitiesExactlyGameClosure:true,missingPressureRejected:true,
 scope:'Diagnostic reconstruction against actual game closure, including forced/putback/fatigue states. Does not validate source mean-energy or role adaptations as physiology.',
 hashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')]))},null,2));
console.log(JSON.stringify({passed:true,checks,self,received,missingPressureRejected:true}));

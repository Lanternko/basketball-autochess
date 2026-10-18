import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {loadInput,loadSourceInput} from './input.mjs';
import {loadInput as previousInput} from '../player-impact-v39/input.mjs';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import {measuredContext,contextReference,attachCreationContext} from '../../src/measured_creation_context.js';
import {pressureSignal,attemptMakeProbability} from '../../src/defense_probability.js';
import {observedFoulInputs} from '../player-impact-v5/model.mjs';
import {opportunityPlan} from '../player-impact-v11/model.mjs';
import {exposureDefenseProbabilities as probability} from './model.mjs';
import {exposureDefenseProbabilities as oldProbability} from '../player-impact-v30/model.mjs';
const root='reports/player-impact-v41',read=p=>JSON.parse(fs.readFileSync(p)),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const zones=['long','mid','short'],structureOnly=process.argv.includes('--structure-only');
const close=(a,b,tolerance=2e-11)=>assert.ok(Math.abs(a-b)<=tolerance*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
const protocol=read(root+'/context-protocol.json');for(const[p,h]of Object.entries(protocol.hashes))assert.equal(sha(p),h,p);
let teamCards=0,uniqueCards=0,totalStates=0,probabilityChecks=0;const results=[];
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const previous=previousInput(season),current=loadInput(season),source=loadSourceInput(season),ctx=read(`${root}/${season}-contexts.json`),oldctx=read(`reports/player-impact-v30/${season}-contexts.json`);
 const cleaned=structuredClone(current),unique=new Set();
 for(let t=0;t<current.league.teams.length;t++)for(let i=0;i<current.league.teams[t].roster.length;i++){
  const p=current.league.teams[t].roster[i],q=previous.league.teams[t].roster[i],c=cleaned.league.teams[t].roster[i];
  assert.ok(p.freshDefenseMeasurement);assert.deepEqual(p.shootingMeasurement,{...q.shootingMeasurement,...ctx.cards[p.playerId]});
  delete c.freshDefenseMeasurement;c.shootingMeasurement=structuredClone(q.shootingMeasurement);unique.add(p.playerId);teamCards++;
  for(const k of ['strictSeconds','sourceZoneAttempts','meanSourceShootingMultiplier'])assert.deepEqual(ctx.cards[p.playerId][k],oldctx.cards[p.playerId][k]);
 }
 assert.deepEqual(cleaned,previous);assert.deepEqual(ctx.contextReference,oldctx.contextReference);assert.equal(ctx.states,oldctx.states);assert.equal(ctx.stints,oldctx.stints);assert.equal(ctx.strictMinutes,oldctx.strictMinutes);assert.deepEqual(ctx.priorAttempts,oldctx.priorAttempts);
 uniqueCards+=unique.size;totalStates+=ctx.states;
 if(structureOnly)continue;
 attachCreationContext(source.league.teams.flatMap(t=>t.roster),contextReference(source.league.teams.flatMap(t=>t.roster)));
 const teams=new Map(source.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),gameIds=new Set(read(`reports/player-impact-v1/${season}-on-court-truth.json`).gameIds),shot=read(`reports/player-impact-v17/${season}-shot-exposures.json`),games=new Map();
 for(const line of fs.readFileSync(ctx.sources.stints,'utf8').trim().split('\n')){const s=JSON.parse(line);if(gameIds.has(s.id)&&s.seconds>=0){if(!games.has(s.id))games.set(s.id,[]);games.get(s.id).push(s);}}
 const sums=new Map();let states=0,stints=0;
 for(const[gameId,rows]of games){
  rows.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);const energy=new Map();let period=1;
  for(const s of rows){
   if(s.period>period){for(const[id,value]of energy)energy.set(id,periodEnergyRecovery(value,s.period-period));period=s.period;}
   const lineups=s.teams.map(t=>{
    const active=new Set(t.players),players=[];
    for(const[id,p]of teams.get(t.teamId)){
     const key=`${t.teamId}:${id}`,step=rotationEnergyStep(energy.get(key)??1,s.seconds,active.has(id),p.stamina);energy.set(key,step.end);
     if(active.has(id))players.push(M.applyStamina(p,1-step.mean));
    }
    return players.sort((a,b)=>a.playerId-b.playerId);
   });
   const attempts=shot.games[gameId][s.startIndex+':'+s.endIndex];assert.ok(attempts);stints++;
   for(let side=0;side<2;side++){
    const own=lineups[side],def=lineups[1-side],plan=opportunityPlan(own,undefined,1,'supply-creation');
    const reb=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound);
    const oreb=reb(own),dreb=reb(def),help=M.helpDefense(def),phys=M.teamPhysique(def),onBall=def.reduce((s,p)=>s+p.onBall,0)/5,pressure=pressureSignal(def,source.options.stealPriorRate).attribute;
    // An independent direct-logit reference: remove tracking activity and
    // source defense physique, retain the exact current offensive context.
    const neutralDef=def.map(p=>({...p,physique:70,defenseExposureMeasurement:{...p.defenseExposureMeasurement,long:{...p.defenseExposureMeasurement.long,rate:0},short:{...p.defenseExposureMeasurement.short,rate:0}}}));
    for(let i=0;i<own.length;i++){
     const p=own[i],context=measuredContext(own,i),sum=sums.get(p.playerId)??{seconds:0,energy:0,n:{long:0,mid:0,short:0},weighted:{long:0,mid:0,short:0}},components=[];
     for(let j=0;j<own.length;j++){
      const weight=j===i?plan.rows[i].weight*plan.rows[i].shoot:plan.rows[j].receivers[i];if(weight<=0)continue;
      const opts={assist:j===i?null:own[j].pass,contextScale:source.options.contextScale,contextLongScale:1,contextShortScale:source.options.contextShortScale,turnoverScale:source.options.turnoverScale,turnoverMode:source.options.turnoverMode,pressureAttribute:pressure};
      const q=probability(p,context,{onBall},help,oreb,dreb,phys,opts,def),neutral=oldProbability(p,context,{onBall:70},70,oreb,dreb,70,opts,neutralDef);
      for(const z of zones){
       const d=def.reduce((s,p)=>s+p.freshDefenseMeasurement.logits[z],0),base=neutral.make[z],logit=Math.log(base/(1-base))+d,expected=1/(1+Math.exp(-logit)),limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)];
       close(q.make[z],Math.max(limits[0],Math.min(limits[1],expected)));probabilityChecks++;
      }
      const fresh={...q,zone:p.opportunityMeasurement.freshZone},fouls=observedFoulInputs(fresh,p,source.options,attemptMakeProbability),hazard=Math.min(.95,q.pTovTouch*(source.options.turnoverCategories?source.options.touchTurnoverScale:1));
      components.push({q,mass:weight*(1-hazard)/zones.reduce((n,z)=>n+fresh.zone[z]/fouls[z].recorded,0)});
     }
     const total=components.reduce((n,c)=>n+c.mass,0);assert.ok(total>0);sum.seconds+=s.seconds;sum.energy+=s.seconds*p._eff;
     for(const z of zones){const n=attempts[p.playerId]?.[z]??0;sum.n[z]+=n;sum.weighted[z]+=n*components.reduce((v,c)=>v+c.mass*(c.q.make[z]-p.shootingMeasurement.sourceBase[z]),0)/total;}
     sums.set(p.playerId,sum);
    }
    states++;
   }
  }
 }
 assert.equal(states,ctx.states);assert.equal(stints,ctx.stints);
 const minutes=[...sums.values()].reduce((n,s)=>n+s.seconds,0)/60;close(minutes,ctx.strictMinutes);
 let maxContextError=0;
 for(const z of zones){
  const total=[...sums.values()].reduce((n,s)=>n+s.n[z],0),prior=[...sums.values()].reduce((n,s)=>n+s.weighted[z],0)/total,pseudo=60*total/minutes;
  assert.equal(total,shot.totals[z]);close(prior,ctx.priors['rotation-space'][z]);close(pseudo,ctx.priorAttempts['rotation-space'][z]);
  for(const[id,card]of Object.entries(ctx.cards)){
   const s=sums.get(Number(id)),n=s?.n[z]??0,expected=((s?.weighted[z]??0)+pseudo*prior)/(n+pseudo);close(card.contexts['rotation-space'][z],expected);maxContextError=Math.max(maxContextError,Math.abs(card.contexts['rotation-space'][z]-expected));
   assert.equal(card.sourceZoneAttempts[z],n);assert.equal(card.strictSeconds,s?.seconds??0);if(s?.seconds)close(card.meanSourceShootingMultiplier,s.energy/s.seconds);
  }
 }
 results.push({season,states,stints,players:unique.size,maxContextError});console.log(JSON.stringify(results.at(-1)));
}
assert.equal(teamCards,2581);assert.equal(uniqueCards,2262);assert.equal(totalStates,270090);
const files=[...Object.keys(protocol.hashes),root+'/context-protocol.json',root+'/verify-contexts.mjs',...['2022-23','2023-24','2024-25','2025-26'].map(s=>`${root}/${s}-contexts.json`)];
const out={passed:true,structureOnly,teamCards,uniqueCards,totalStates,probabilityChecks,sourceCountsMinutesEnergyAndOtherFieldsExactlyPreserved:true,fullIndependentWeightedReconstruction:!structureOnly,results,scope:'Same source games and outcomes, no prospective or causal claim. Independent streaming source reconstruction and direct logit probability reference; shared frozen foul and energy helpers.',hashes:Object.fromEntries(files.map(p=>[p,sha(p)]))};
fs.writeFileSync(root+(structureOnly?'/context-structure-verification.json':'/context-verification.json'),JSON.stringify(out,null,2));console.log(JSON.stringify({passed:true,structureOnly,teamCards,uniqueCards,totalStates,probabilityChecks}));

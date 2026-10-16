import fs from 'node:fs';
import assert from 'node:assert/strict';
import {loadInput,loadSourceInput} from './input.mjs';
import {loadSourceInput as oldSource} from '../player-impact-v42/input.mjs';
import {fineSourcePlan,fineZones,coarseOf,collapseZone} from './model.mjs';
import {spaceProbability,transferredFineMake} from './space-model.mjs';
import {spaceProbability as oldSpace} from '../player-impact-v42/space-model.mjs';
import {logit,logistic} from '../player-impact-v44/space-model.mjs';
import {impactEngine} from './engine.mjs';
import {fineCollector} from './fine-collector.mjs';
const root='reports/player-impact-v45',read=p=>JSON.parse(fs.readFileSync(p)),checks=[],selected=process.argv.slice(2);
const seasons=selected.length?selected:read(root+'/protocol.json').seasons;
const near=(a,b)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-10,`${a} != ${b}`);
for(const season of seasons){
 const before=oldSource(season),after=loadSourceInput(season),old=read(`reports/player-impact-v42/${season}-contexts.json`),ctx=read(`${root}/${season}-contexts.json`),exp=read(`${root}/${season}-exposures.json`);
 let players=0;
 for(let t=0;t<before.league.teams.length;t++)for(let i=0;i<before.league.teams[t].roster.length;i++){
  const a=structuredClone(after.league.teams[t].roster[i]),b=before.league.teams[t].roster[i];
  delete a.fineDefenseMeasurement;assert.deepEqual(a.freshDefenseMeasurement.logits,{long:0,mid:0,short:0});a.freshDefenseMeasurement.logits=b.freshDefenseMeasurement.logits;assert.deepEqual(a,b);players++;
 }
 assert.equal(ctx.states,old.states);assert.equal(ctx.stints,old.stints);
 const counts=Object.fromEntries(fineZones.map(z=>[z,0]));
 for(const[id,c]of Object.entries(ctx.cards)){
  assert.equal(c.strictSeconds,old.cards[id].strictSeconds);assert.equal(c.meanSourceShootingMultiplier,old.cards[id].meanSourceShootingMultiplier);
  assert.equal(c.sourceZoneAttempts.ra+c.sourceZoneAttempts.paint,old.cards[id].sourceZoneAttempts.short);
  assert.equal(c.sourceZoneAttempts.corner+c.sourceZoneAttempts.arc,old.cards[id].sourceZoneAttempts.long);
  assert.equal(c.sourceZoneAttempts.mid,old.cards[id].sourceZoneAttempts.mid);
  for(const z of fineZones){counts[z]+=c.sourceZoneAttempts[z];assert.ok(Number.isFinite(c.contexts['rotation-space'][z]));}
 }
 assert.deepEqual(counts,exp.totals);checks.push({season,players,sourceAttributesPreserved:true,oldBaselineDefenseZeroed:true,sourceMinutesEnergyAttemptsPreserved:true});
}
let transferChecks=0,distributionChecks=0;
for(const base of [.25,.4,.6,.75])for(const delta of [-.12,0,.12]){
 const p={make:{long:base,mid:base,short:base},finePlan:{makeEta:Object.fromEntries(fineZones.map(z=>[z,-.25+delta]))}},player={fineDefenseMeasurement:{contexts:{test:Object.fromEntries(fineZones.map(z=>[z,logit(base)]))}}};
 for(const v of Object.values(transferredFineMake(p,player,'test')))near(v,logistic(-.25+delta));transferChecks++;
}
const b=loadInput('2025-26'),opt={...b.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:read('reports/player-impact-v7/2025-26-center.json').fullCenter};
for(let t=0;t<30;t++)for(const player of b.league.teams[t].roster){
 const ds=b.league.teams[(t+1)%30].roster.slice(0,5),plan=fineSourcePlan(player,ds),p={make:{long:.35,mid:.42,short:.57},zone:{long:.4,mid:.15,short:.45},defensiveZone:collapseZone(plan.zone),finePlan:plan,pFoul:.1,pTovTouch:.1,ftPct:.8};
 near(Object.values(plan.zone).reduce((s,x)=>s+x,0),1);for(const v of Object.values(plan.zone))assert.ok(v>0&&v<1);
 const q=spaceProbability(p,player,false,opt),shot=1-q.pFoul-q.pTovTouch;
 for(const z of ['long','mid','short']){
  const zs=fineZones.filter(k=>coarseOf[k]===z);near(q.zone[z]*q.make[z],zs.reduce((s,k)=>s+plan.zone[k]*q.finePlan.make[k],0));
 }
 near(q.ev,shot*fineZones.reduce((s,z)=>s+plan.zone[z]*q.finePlan.make[z]*(coarseOf[z]==='long'?3:2),0)+q.pFoul*2*q.ftPct);
 assert.deepEqual(spaceProbability(p,player,true,opt),oldSpace(p,player,true,opt));distributionChecks++;
}
const run=await impactEngine('rotation-space',{game:true});let games=0,observedShots=0;
for(let i=0;i<30;i+=3){
 const options={...opt,seed:20261012+i},a=run(b.league.teams[i],b.league.teams[(i+1)%30],options),events=[],collector=fineCollector(i);
 const c=run(b.league.teams[i],b.league.teams[(i+1)%30],{...options,onCourtObserver:e=>{events.push(e);collector.event(e);}});
 assert.ok(a.complete&&c.complete);for(const side of ['A','B']){assert.deepEqual(a['stat'+side],c['stat'+side]);const s=a['stat'+side];assert.equal(s.pts,2*s.fgm+s.fg3m+s.ftm);assert.equal(s.fga,s.fg3a+s.mida+s.rima);}
 const fresh=events.filter(e=>['FGM','FGX'].includes(e.type)&&!e.putback);observedShots+=fresh.length;
 for(const e of fresh){assert.ok(e.finePlan);near(Object.values(e.finePlan.zone).reduce((s,x)=>s+x,0),1);for(const p of Object.values(e.finePlan.make))assert.ok(p>0&&p<1);}
 assert.equal(events.filter(e=>e.type==='GAME_END').length,1);games++;
}
const seasonRun=await impactEngine('rotation-space'),fine=fineCollector(45001);let freshAttempts=0,freshMakes=0;
const mini=seasonRun(b.league,b.exposure,{seed:45001,options:{...opt,onCourtObserver:e=>{fine.event(e);if(['FGM','FGX'].includes(e.type)&&!e.putback){freshAttempts++;freshMakes+=Number(e.type==='FGM');}}},audit:false,replay:false,indices:[0,1,2]});
const fineResult=fine.finish(mini.teams);assert.equal(fineResult.games,3);assert.equal(fineResult.total.fga,freshAttempts);assert.equal(fineResult.total.fgm,freshMakes);
const result={passed:true,checks,transferChecks,distributionChecks,gameChecks:games,observedFreshShots:observedShots,observerScoreAndBoxParity:true,putbacksUnchanged:true,fineCollectorGameChecks:3,fineCollectorFreshCountAndFivePlayerLedgersPassed:true};
fs.writeFileSync(`${root}/${selected.length?selected.join('-')+'-':''}verification.json`,JSON.stringify(result,null,2));console.log(JSON.stringify(result));

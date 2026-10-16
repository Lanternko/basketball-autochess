import fs from 'node:fs';
import assert from 'node:assert/strict';
import {loadInput} from './choice-input.mjs';
import {loadInput as previousInput} from '../player-impact-v47/input.mjs';
import {impactEngine} from './choice-engine.mjs';
import {impactEngine as previousEngine} from '../player-impact-v47/engine.mjs';
import {offensiveChoicePlan} from './choice-model.mjs';
import {offenseCollector} from './offense-collector.mjs';
import {fineCollector} from '../player-impact-v45/fine-collector.mjs';
const read=p=>JSON.parse(fs.readFileSync(p)),checks=[];
for(const season of read('reports/player-impact-v48/protocol.json').seasons){
 const a=previousInput(season),b=loadInput(season);let entries=0;
 for(let t=0;t<a.league.teams.length;t++)for(let i=0;i<a.league.teams[t].roster.length;i++){const q=structuredClone(b.league.teams[t].roster[i]);delete q.offensiveChoiceMeasurement;assert.deepEqual(q,a.league.teams[t].roster[i]);entries++;}
 checks.push({season,entries,onlyOffensiveLineupDescriptorAdded:true});
}
const old=previousInput('2025-26'),b=loadInput('2025-26'),game=await impactEngine('rotation-space',{game:true}),legacy=await previousEngine('rotation-space',{game:true}),opt={...b.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:read('reports/player-impact-v7/2025-26-center.json').fullCenter};
let games=0;
for(let i=0;i<10;i++){
 const options={...opt,seed:48000+i},a=legacy(old.league.teams[i],old.league.teams[i+1],options),c=game(old.league.teams[i],old.league.teams[i+1],options);for(const side of ['A','B'])assert.deepEqual(a['stat'+side],c['stat'+side]);
 const d=game(b.league.teams[i],b.league.teams[i+1],options),e=game(b.league.teams[i],b.league.teams[i+1],{...options,onCourtObserver:()=>{}});assert.ok(d.complete);for(const side of ['A','B'])assert.deepEqual(d['stat'+side],e['stat'+side]);games++;
}
const os=b.league.teams[0].roster.slice(0,5),p={finePlan:{zone:{ra:.2,paint:.2,mid:.2,corner:.1,arc:.3},makeEta:{ra:1,paint:2,mid:3,corner:4,arc:5}}},q=offensiveChoicePlan(p,os[0],os,false);
assert.equal(q.finePlan.zone.corner,p.finePlan.zone.corner);assert.equal(q.finePlan.zone.arc,p.finePlan.zone.arc);assert.deepEqual(q.finePlan.makeEta,p.finePlan.makeEta);assert.ok(Math.abs(q.finePlan.zone.ra+q.finePlan.zone.paint+q.finePlan.zone.mid-.6)<1e-12);assert.equal(offensiveChoicePlan(p,os[0],os,true),p);
for(const branch of ['paintGivenTwo','raGivenPaint']){const delta=os[0].offensiveChoiceMeasurement.shooterDelta[branch]+os.slice(1).reduce((s,p)=>s+p.offensiveChoiceMeasurement.teammateLogits[branch],0),actual=branch==='paintGivenTwo'?(q.finePlan.zone.ra+q.finePlan.zone.paint)/.6:q.finePlan.zone.ra/(q.finePlan.zone.ra+q.finePlan.zone.paint),old=branch==='paintGivenTwo'?2/3:.5;assert.ok(Math.abs(Math.log(actual/(1-actual))-Math.log(old/(1-old))-delta)<1e-12);}

const run=await impactEngine('rotation-space'),offense=offenseCollector(48001),defense=fineCollector(48001),r=run(b.league,b.exposure,{seed:48001,options:{...opt,onCourtObserver:e=>{offense.event(e);defense.event(e);}},audit:false,replay:false,indices:[0,1,2]});const a=offense.finish(r.teams),d=defense.finish(r.teams);assert.deepEqual(a.total,d.total);assert.equal(a.games,3);
const result={passed:true,checks,legacyNoDescriptorGameParity:games,candidateObserverGameParity:games,otherFourExcludesShooter:true,cornerArcAndPutbacksUnchanged:true,offensiveDefensiveFineLabelsAndLedgersMatch:true,fineGames:3};fs.writeFileSync('reports/player-impact-v48/choice-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));

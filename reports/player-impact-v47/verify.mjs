import fs from 'node:fs';
import assert from 'node:assert/strict';
import {loadInput} from './input.mjs';
import {loadInput as previousInput} from '../player-impact-v46/input.mjs';
import {impactEngine} from './engine.mjs';
import {impactEngine as previousEngine} from '../player-impact-v45/engine.mjs';
import {measuredFreeThrowPercentage,withMeasuredFreeThrow} from './ft-model.mjs';
import {fineCollector} from '../player-impact-v45/fine-collector.mjs';
const read=p=>JSON.parse(fs.readFileSync(p)),checks=[];
for(const season of read('reports/player-impact-v46/protocol.json').seasons){
 const old=previousInput(season),next=loadInput(season);let entries=0;
 for(let t=0;t<old.league.teams.length;t++)for(let i=0;i<old.league.teams[t].roster.length;i++){
  const a=old.league.teams[t].roster[i],b=structuredClone(next.league.teams[t].roster[i]),m=b.freeThrowAccuracyMeasurement;
  const expected=Math.max(.30,Math.min(.98,m.probability));assert.ok(Math.abs(measuredFreeThrowPercentage(b)-expected)<1e-12);
  assert.ok(measuredFreeThrowPercentage({...b,ft:b.ft+2})>=expected-1e-12);
  delete b.freeThrowAccuracyMeasurement;assert.deepEqual(b,a);entries++;
 }
 checks.push({season,entries,onlyFTDescriptorChanged:true});
}
const old=previousInput('2025-26'),next=loadInput('2025-26'),game=await impactEngine('rotation-space',{game:true}),legacy=await previousEngine('rotation-space',{game:true});
const opt={...old.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:read('reports/player-impact-v7/2025-26-center.json').fullCenter};
let smoke=0;
for(let i=0;i<10;i++){
 const options={...opt,seed:47000+i},a=legacy(old.league.teams[i],old.league.teams[i+1],options),b=game(old.league.teams[i],old.league.teams[i+1],options);
 for(const side of ['A','B'])assert.deepEqual(a['stat'+side],b['stat'+side]);
 const c=game(next.league.teams[i],next.league.teams[i+1],options),d=game(next.league.teams[i],next.league.teams[i+1],{...options,onCourtObserver:()=>{}});assert.ok(c.complete);
 for(const side of ['A','B']){assert.deepEqual(c['stat'+side],d['stat'+side]);const s=c['stat'+side];assert.equal(s.pts,2*s.fgm+s.fg3m+s.ftm);}smoke++;
}
const player=next.league.teams.flatMap(t=>t.roster).find(p=>p.playerId===201939),legacyP={ftPct:.8,pFoul:.1,ev:1.2};assert.ok(Math.abs(withMeasuredFreeThrow(legacyP,player).ev-(1.2+.2*(measuredFreeThrowPercentage(player)-.8)))<1e-12);
const run=await impactEngine('rotation-space'),fine=fineCollector(47001);let fresh=0;
const r=run(next.league,next.exposure,{seed:47001,options:{...opt,onCourtObserver:e=>{fine.event(e);if(['FGM','FGX'].includes(e.type)&&!e.putback)fresh++;}},audit:false,replay:false,indices:[0,1,2]});const f=fine.finish(r.teams);assert.equal(f.total.fga,fresh);assert.equal(f.games,3);
const result={passed:true,checks,legacyNoDescriptorGameParity:smoke,candidateObserverGameParity:smoke,sourceAttributeDeltaPreserved:true,evLedgerPassed:true,fineConservationGames:3,curry2025:{oldFTProbability:player.freeThrowAccuracyMeasurement.sourceProbability,newFTProbability:measuredFreeThrowPercentage(player),actualFTProbability:player.observed.FTM/player.observed.FTA}};
fs.writeFileSync('reports/player-impact-v47/verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));

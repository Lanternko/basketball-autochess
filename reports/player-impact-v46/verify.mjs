import fs from 'node:fs';
import assert from 'node:assert/strict';
import {loadInput} from './input.mjs';
import {loadInput as previousInput} from '../player-impact-v45/input.mjs';
import {fineSourcePlan} from '../player-impact-v45/model.mjs';
import {impactEngine} from '../player-impact-v45/engine.mjs';
import {fineCollector} from '../player-impact-v45/fine-collector.mjs';
const read=p=>JSON.parse(fs.readFileSync(p)),root='reports/player-impact-v46',checks=[];
for(const season of read(root+'/protocol.json').seasons){
 const old=previousInput(season),next=loadInput(season);let entries=0;
 for(let t=0;t<old.league.teams.length;t++)for(let i=0;i<old.league.teams[t].roster.length;i++){
  const a=old.league.teams[t].roster[i],b=structuredClone(next.league.teams[t].roster[i]),ds=old.league.teams[(t+1)%30].roster.slice(0,5),nd=next.league.teams[(t+1)%30].roster.slice(0,5);
  assert.deepEqual(fineSourcePlan(a,ds).zone,fineSourcePlan(b,nd).zone);
  for(const z of ['ra','paint']){assert.ok(Number.isFinite(b.fineDefenseMeasurement.makeShooter[z])&&Number.isFinite(b.fineDefenseMeasurement.makeDefender[z]));b.fineDefenseMeasurement.makeShooter[z]=a.fineDefenseMeasurement.makeShooter[z];b.fineDefenseMeasurement.makeDefender[z]=a.fineDefenseMeasurement.makeDefender[z];}
  assert.deepEqual(b,a);entries++;
 }
 checks.push({season,rosterEntries:entries,onlyPaintCoefficientsChanged:true,sourceNeutralContextsPreserved:true,sourceChoicePreserved:true});
}
const b=loadInput('2025-26'),game=await impactEngine('rotation-space',{game:true}),opt={...b.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:read('reports/player-impact-v7/2025-26-center.json').fullCenter};let games=0;
for(let i=0;i<30;i+=3){const options={...opt,seed:46000+i},a=game(b.league.teams[i],b.league.teams[(i+1)%30],options),c=game(b.league.teams[i],b.league.teams[(i+1)%30],{...options,onCourtObserver:()=>{}});assert.ok(a.complete);for(const side of ['A','B']){assert.deepEqual(a['stat'+side],c['stat'+side]);const s=a['stat'+side];assert.equal(s.pts,2*s.fgm+s.fg3m+s.ftm);}games++;}
const run=await impactEngine('rotation-space'),collector=fineCollector(46);let fresh=0;const r=run(b.league,b.exposure,{seed:46001,options:{...opt,onCourtObserver:e=>{collector.event(e);if(['FGM','FGX'].includes(e.type)&&!e.putback)fresh++;}},audit:false,replay:false,indices:[0,1,2]});const fine=collector.finish(r.teams);assert.equal(fine.games,3);assert.equal(fine.total.fga,fresh);
const result={passed:true,checks,smokeGames:games,observerBoxParityPassed:true,fineConservationGames:3};fs.writeFileSync(root+'/verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));

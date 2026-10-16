import fs from 'node:fs';
import assert from 'node:assert/strict';
import {loadInput,loadSourceInput} from './input.mjs';
import {loadSourceInput as previousSource} from '../player-impact-v42/input.mjs';
import {spaceProbability,transferredMake,logit,logistic} from './space-model.mjs';
import {spaceProbability as previousSpace} from '../player-impact-v42/space-model.mjs';
import {impactEngine} from './engine.mjs';
const root='reports/player-impact-v44',read=p=>JSON.parse(fs.readFileSync(p)),checks=[];
const selected=process.argv.slice(2),seasons=selected.length?selected:read(root+'/protocol.json').seasons;
for(const season of seasons){
 const old=previousSource(season),next=loadSourceInput(season),a=read(`reports/player-impact-v42/${season}-contexts.json`),b=read(`${root}/${season}-contexts.json`);
 for(let t=0;t<old.league.teams.length;t++)for(let i=0;i<old.league.teams[t].roster.length;i++){
  const p=structuredClone(next.league.teams[t].roster[i]);delete p.sourceMakeTransfer;assert.deepEqual(p,old.league.teams[t].roster[i]);
 }
 assert.equal(a.states,b.states);assert.equal(a.stints,b.stints);
 for(const[id,c]of Object.entries(b.cards)){
  assert.equal(c.strictSeconds,a.cards[id].strictSeconds);assert.deepEqual(c.sourceZoneAttempts,a.cards[id].sourceZoneAttempts);
  assert.equal(c.meanSourceShootingMultiplier,a.cards[id].meanSourceShootingMultiplier);
  for(const x of Object.values(c.contexts['rotation-space']))assert.ok(Number.isFinite(x));
 }
 checks.push({season,sourceAttributesAndDefenseUnchanged:true,sourceMinutesEnergyAttemptsUnchanged:true,cards:Object.keys(b.cards).length});
}
// At a neutral source context the fitted shooter and defender logits must be
// reproduced exactly, and changing one defender must preserve log-odds change.
let transferChecks=0;
for(const base of [.25,.4,.6,.75])for(const d of [-.12,0,.12]){
 const shooter=-.25,neutral=logit(base),p={make:Object.fromEntries(['long','mid','short'].map(z=>[z,logistic(neutral+d)]))};
 const player={sourceMakeTransfer:{shooterLogits:{long:shooter,mid:shooter,short:shooter},contexts:{test:{long:neutral,mid:neutral,short:neutral}}}};
 const q=transferredMake(p,player,'test');for(const z of ['long','mid','short'])assert.ok(Math.abs(q[z]-logistic(shooter+d))<1e-12);transferChecks++;
}
const b=loadInput('2025-26'),run=await impactEngine('rotation-space',{game:true});let games=0;
for(let i=0;i<30;i+=3){
 const opt={...b.options,seed:20261012+i,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:read('reports/player-impact-v7/2025-26-center.json').fullCenter};
 const r=run(b.league.teams[i],b.league.teams[(i+1)%30],opt);assert.ok(r.complete);
 for(const side of ['A','B']){const s=r['stat'+side];assert.equal(s.pts,2*s.fgm+s.fg3m+s.ftm);assert.equal(s.fga,s.fg3a+s.mida+s.rima);}
 games++;
}
const p={make:{long:.35,mid:.42,short:.57},zone:{long:.4,mid:.15,short:.45},pFoul:.1,pTovTouch:.1,ftPct:.8};
assert.deepEqual(spaceProbability(p,b.league.teams[0].roster[0],true,b.options),previousSpace(p,b.league.teams[0].roster[0],true,b.options));
const result={passed:true,checks,transferChecks,gameChecks:games,putbacksUnchanged:true};fs.writeFileSync(root+'/'+(selected.length?selected.join('-')+'-':'')+'verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));

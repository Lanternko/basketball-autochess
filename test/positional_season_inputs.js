import assert from 'node:assert/strict';
import {positionalOvrInput} from '../reports/player-impact-validation/positional-input.mjs';
import {ovrInput} from '../reports/player-impact-v6/ovr-input.mjs';
import {loadInput} from '../reports/player-impact-v6/input.mjs';
import {ATTRIBUTES} from '../src/strength_benchmark.js';
const a=await positionalOvrInput('2025-26'),b=ovrInput();
for(const key of ['players','opponents','profiles','options','roles','roleAudit'])assert.deepEqual(a[key],b[key],key+' changed in generalized protocol');
for(const season of ['2022-23','2023-24','2024-25']){
 const x=await positionalOvrInput(season),source=loadInput(season),cards=new Map(source.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p]));
 for(const p of x.players)for(const k of ATTRIBUTES)assert.equal(p[k],cards.get(p.playerId)[k],season+' '+p.playerId+' '+k);
 assert.equal(x.players.length,cards.size);assert.equal(x.profiles.length,5);
 for(const p of x.profiles){assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/ATTRIBUTES.length-70)<1e-9);for(const k of ['offBall','screen','handle','breakDbl'])assert.equal(p[k],70);}
 console.log(season,x.players.length,'natural role inputs, historical projections and mean70 profiles passed');
}
console.log('Generalized 2025-26 inputs exactly equal frozen benchmark');

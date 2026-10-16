import fs from 'node:fs';import assert from 'node:assert/strict';
import {root,verify,job,pool} from './run.mjs';import {read} from '../../../scripts/defense_io.js';
import {reboundChance,reboundWeights} from './model.mjs';import {reboundChance as oldChance} from '../step4-rebounds-oreb/model.mjs';import {opportunityReboundWeights} from '../../../src/rebound_block_model.js';
verify();const p=read(root+'/protocol.json'),results=[];
for(const s of p.seasons){const c=read(`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`).selected,r=(await pool([job(s,'acquisition',p.seeds[0],c)],{workers:1,quiet:true}))[0].result,o=read(`reports/defense-tenth/step4-rebounds-oreb/runs/${s}-oreb-${p.seeds[0]}.json`);assert.deepEqual(r.matches,o.matches);assert.deepEqual(r.teams,o.teams);results.push({season:s,games:1230,identical:true,trace:r.allocationTrace});console.log('PARITY',s,1230);}
const lineup=['PG','SG','SF','PF','C'].map((pos,i)=>({pos,physique:70,rebound:70,individualOreb:{share:[.001,.01,.03,.06,.15][i]}})),options={individualOrebAllocation:true,individualOrebCard:true,leagueOrbLogit:.27};
for(const zone of ['short','mid','long']){
 for(const side of ['offense','defense'])for(const freeThrow of [true,false]){const s={zone,side,freeThrow,shooterIndex:2},w=reboundWeights(lineup,s,options);assert(Math.abs(w.reduce((s,x)=>s+x,0)-1)<1e-12);if(side==='defense'||freeThrow)assert.deepEqual(w,opportunityReboundWeights(lineup,s));}
 const s={zone,oldChance:.26,shooterIndex:2,options};assert.equal(reboundChance(lineup,lineup,s),oldChance(lineup,lineup,s));
}
assert(reboundWeights(lineup,{zone:'short',side:'offense',freeThrow:false},options)[0]<.06);
const swapped=lineup.map(p=>({...p,courtPosition:'PG'}));assert.deepEqual(reboundWeights(lineup,{side:'offense'},options),reboundWeights(swapped,{side:'offense'},options));
fs.writeFileSync(root+'/parity.json',JSON.stringify({results,invariants:['OFF exact full-season parity','acquisition function re-exported byte-identically','FT and DREB allocation unchanged','one normalized recipient distribution','no PG/C penalty or uniform floor on FG OREB allocation']},null,2)+'\n');

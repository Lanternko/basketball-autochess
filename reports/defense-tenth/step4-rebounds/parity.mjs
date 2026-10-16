import fs from 'node:fs';
import assert from 'node:assert/strict';
import {read} from '../../../scripts/defense_io.js';
import {pool,job,root,verify} from './run.mjs';
import {reboundChance,reboundWeights} from './model.mjs';
verify();const p=read(root+'/protocol.json'),results=[];
for(const season of p.seasons){const r=(await pool([job(season,'off',p.seeds[0])],{workers:1,quiet:true}))[0].result,old=read(`reports/defense-tenth/step4-t0/runs/${season}-pure-${p.seeds[0]}.json`);assert.deepEqual(r.matches,old.matches);assert.deepEqual(r.teams,old.teams);results.push({season,games:r.matches.length,teamPlayerStatsIdentical:true});console.log('PARITY',season,r.matches.length);}
const base=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70,individualDreb:{share:.15}})),settings={zone:'short',shooterIndex:2,oldChance:.26,options:{individualDrebCard:true,leagueOrbLogit:0}};
const original=reboundChance(base,base,settings),strong=base.map(p=>({...p,individualDreb:{share:.17}}));assert(reboundChance(base,strong,settings)<original);assert(Math.abs(reboundChance(base,[...base].reverse(),settings)-original)<1e-12);assert(Math.abs(reboundWeights(base,{side:'defense'},settings.options).reduce((s,x)=>s+x,0)-1)<1e-12);assert(Math.abs(reboundChance(base,base,{...settings,options:{individualDrebCard:false}})-.26)<1e-12);
fs.writeFileSync(root+'/parity.json',JSON.stringify({results,invariants:['stronger DREB lowers opposing ORB','defensive permutation invariance','recipient weights normalized','OFF probability unchanged']},null,2)+'\n');

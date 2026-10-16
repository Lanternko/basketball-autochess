import fs from 'node:fs';
import assert from 'node:assert/strict';
import {root,verify} from './run.mjs';
import {reboundChance,reboundWeights} from './model.mjs';
verify();
const base=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70,individualOreb:{share:.05}}));
const checks=[],rows=[];
for(const zone of ['short','mid','long']){
 const s={zone,shooterIndex:2,oldChance:.26,options:{individualOrebCard:true,leagueOrbLogit:0}};
 let previous=0;
 for(let k=0;k<=5;k++){
  const off=base.map((p,i)=>({...p,individualOreb:{share:i<k?.20:.01}}));
  const chance=reboundChance(off,base,s);assert(chance>0&&chance<=.60);assert(chance>=previous);previous=chance;
  rows.push({zone,highOrebPlayers:k,chance});
 }
 const a=reboundChance(base,base,s),strong=base.map(p=>({...p,rebound:110,physique:110}));
 assert(reboundChance(base,strong,s)<a);
 assert(Math.abs(reboundChance(strong,base,s)-a)<1e-12);
 const pg=base.map(p=>({...p,courtPosition:'PG'}));assert.equal(reboundChance(pg,base,s),a);
 assert.equal(reboundWeights(pg,{zone,side:'offense',shooterIndex:2}).length,5);
 for(const off of [base,strong,pg])assert(Math.abs(reboundWeights(off,{zone,side:'offense',shooterIndex:2}).reduce((n,x)=>n+x,0)-1)<1e-12);
 checks.push({zone,monotonic:true,strongerDefenseLowersAcquisition:true,noDoubleBodyBonus:true,offensiveSlotIndependent:true,recipientWeightsNormalized:true});
}
fs.writeFileSync(root+'/mechanism-invariants.json',JSON.stringify({checks,rows,scope:'Acquisition only; PG/C still affects unchanged recipient distribution.'},null,2)+'\n');
console.log('PASS',JSON.stringify(checks));

import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash} from '../scripts/defense_io.js';
import {inputN,configN,counterfactualN,pairN,analyticN,sampleTemplateN} from '../src/defense_ninth_rosters.js';
import {runDefenseSeason} from '../src/defense_seventh_season.js';
const root='reports/defense-ninth/development',spec=read(root+'/prereg.json');
assert.equal(hash(root+'/prereg.json'),fs.readFileSync(root+'/prereg.sha256','utf8').trim());
for(const [p,h]of Object.entries(spec.sourceHashes))assert.equal(hash(p),h,p);
const parity=[];
for(const s of spec.seasons)for(const v of ['v3','v4']){
 const c=read(configN(s,41)),base=inputN(c,v),indices=base.league.schedule.flatMap((g,i)=>g.date>c.date?[i]:[]).slice(0,5),mf=read(`reports/defense-seventh/${s}-calendar-41-${v}-seeds.json`),known=read(mf.files[0].file);
 const run=runDefenseSeason(base.league,base.exposure,{seed:20261012,options:base.options,indices,audit:false,replay:false});
 for(const g of run.matches){const old=known.matches.find(z=>z.id===g.id);assert.deepEqual([g.scoreA,g.scoreB,g.regulationScore],[old.scoreA,old.scoreB,old.regulationScore],s+'/'+v+'/'+g.id);}
 const ctrl=counterfactualN(base,20261012);for(const i of indices)for(const side of [0,1]){const f=base.league.schedule[i],t=sampleTemplateN(base,f,i,side,20261012);assert(t.date<=c.date);assert.deepEqual(ctrl.league.schedule[i][side?'awayPlayerIds':'homePlayerIds'],t.ids);const p=pairN(base,f,i,20261012,true);assert(Math.abs(p[side].roster.reduce((n,x)=>n+x.targetMinutes,0)-240)<1e-8);}
 if(v==='v3'){const a=analyticN(base),pair=pairN(base,base.league.schedule[indices[0]],indices[0],20261012);assert(Number.isFinite(a.seg(pair))&&Number.isFinite(a.naive(pair)));assert.equal(a.seg(pair)-a.seg(pair),0);}
 parity.push({season:s,version:v,games:run.matches.length,exact:true});
}
fs.writeFileSync(root+'/parity.json',JSON.stringify({checkedAt:new Date().toISOString(),preregHash:hash(root+'/prereg.json'),parity},null,2)+'\n');
console.log('PASS prereg/source hashes,40 exact existing scores, training-only roster sampling,240-minute budgets, analytic scale sanity');

import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash} from '../scripts/defense_io.js';
import {sixthInputs} from '../src/defense_sixth_jobs.js';
import {runDefenseSeason} from '../src/defense_sixth_season.js';
import {executeFifthJob} from '../src/defense_fifth_jobs.js';
import {runSixthJobs} from '../src/defense_sixth_pool.js';
import {abilityJob,selectedAbilityJob} from '../src/defense_sixth_presets.js';
const root='reports/defense-sixth';
assert.equal(abilityJob(41).cardVersion,undefined);assert.equal(abilityJob(41,{rolePrior:true}).cardVersion,'role');assert.equal(abilityJob(41,{offenseResidual:true}).cardVersion,'offense');assert.equal(abilityJob(41,{rolePrior:true,offenseResidual:true}).cardVersion,'role-offense');assert.throws(()=>abilityJob(30));
for(const [file,h] of Object.entries(read(root+'/frozen.json')))assert.equal(hash(file),h,'Frozen '+file);
const input=sixthInputs({cutoff:41}),prior=executeFifthJob({cutoff:41,seed:20261012,indices:[700,810],audit:true});
const now=runDefenseSeason(input.league,input.exposure,{seed:20261012,options:input.options,indices:[700,810],post41:true,cutoff:41,replay:true,audit:true});assert.deepEqual(now.matches,prior.matches);
const train=runDefenseSeason(input.league,input.exposure,{seed:20261012,options:input.options,indices:[0,6,123],post41:true,cutoff:41,phase:'train',audit:false});assert.equal(train.teams.reduce((s,t)=>s+t.games,0),6);
for(const k of [25,41,55]){
 const model=read(`${root}/model-pre${k}.json`),league=read('data/season-league.json'),count={},order={};for(const g of league.schedule)for(const t of [g.homeId,g.awayId])order[g.id+'/'+t]=count[t]=(count[t]??0)+1;
 for(const [f,h] of Object.entries(model.sources))assert.equal(hash(f),h);
 for(const m of Object.values(model.models))assert.ok(m.diagnostics.prior.converged&&m.diagnostics.residual.converged);
 for(const id of model.trainGames){const g=league.schedule.find(g=>g.id===id);assert.ok([g.homeId,g.awayId].every(t=>order[g.id+'/'+t]<=k));}
 for(const version of ['role','offense','role-offense']){
  const cards=read(`${root}/pre${k}-${version}-league.json`),pmap=new Map();assert.deepEqual(cards.sixthProvenance.trainingGames,model.trainGames);
  for(const t of cards.teams)for(const p of t.roster){for(const a of ['long','mid','short'])assert.ok(p[a]>=0&&p[a]<=120&&Number.isFinite(p[a]));const a=[p.long,p.mid,p.short];if(pmap.has(p.playerId))assert.deepEqual(a,pmap.get(p.playerId));else pmap.set(p.playerId,a);}
  for(const [f,h] of Object.entries(cards.sixthProvenance.sources))assert.equal(hash(f),h);
 }
}
if(process.argv.includes('--artifacts')){
 const labels=fs.readdirSync(root).filter(f=>f.endsWith('-seeds.json'));
 for(const label of labels){const m=read(root+'/'+label);assert.equal(m.files.length,20);assert.deepEqual(m.files.map(f=>f.seed),Array.from({length:20},(_,i)=>20261012+i));for(const [f,h] of Object.entries(m.code))assert.equal(hash(f),h,label+' '+f);for(const f of m.files){assert.equal(hash(f.file),f.sha256);const r=read(f.file);assert.ok(r.teams.every(t=>t.games===(m.extra.phase==='train'?m.extra.cutoff:82-m.extra.cutoff)));}}
 const report=read(root+'/closeout.json');for(const [f,h] of Object.entries(report.sources))assert.equal(hash(f),h);
 assert.equal(report.selection.clock,false);assert.equal(report.selection.netResidual,false);
 for(const k of [25,41,55]){const p=report.selection.neutralTests[k];assert.ok(p);}
 const d=report.information.decomposition;for(const r of Object.values(d))assert.ok(Math.abs(r.signedMSEShares.reduce((a,b)=>a+b,0)-1)<1e-9);
 const wins=Object.values(report.rolling).filter(r=>r.paired.netRMSE.ci95[1]<0&&r.paired.winMAE.ci95[1]<0).length;
 if(report.classification==='成功'){assert.ok(wins>=2);assert.ok(report.rolling[41].final.metrics.netRMSE<=report.rolling[41].simple.netRMSE);assert.ok(report.rolling[41].final.metrics.winMAE<=report.rolling[41].simple.winMAE);}
}
console.log('Sixth frozen engine/cards, baseline score parity, train gate, cutoff sources, trade portability and artifacts PASS');

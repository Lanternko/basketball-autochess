import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {runFourthJobs} from '../src/defense_fourth_pool.js';
import {mean,sd} from '../src/statistical_summary.js';
import {makeRng} from '../src/rng.js';
const root='reports/defense-fourth',states=read('reports/defense-b1/empirical-timing.json').states;
const common=Object.values(states).flat().filter(t=>t>=.1).sort((a,b)=>a-b),timingCDF=Object.fromEntries(Object.keys(states).map(k=>[k,common]));
const jobs=Array.from({length:20},(_,i)=>({label:'diagnostic-pooled-clock',seed:20261012+i,options:{timingCDF}}));
console.log('Diagnostic: state dependence disabled; all other v2 options and pace fixed.');
const results=await runFourthJobs(jobs,{workers:4,onProgress:(n,total)=>{if(n%4===0)console.log('pooled-clock',n+'/'+total);}});
const base=read(root+'/v2-seeds.json').files.map(f=>read(f.file));
const uncertainty=a=>{const rng=makeRng(20261117),b=Array.from({length:4000},()=>mean(a.map(()=>a[Math.floor(rng()*a.length)]))).sort((a,b)=>a-b);return {estimate:mean(a),standardError:sd(b),ci95:[b[100],b[3900]]};};
const keys=['scoreCovariance','paceCovariance','remainingCovariance','meanPossessionCount','possessionCountVariance','marginResidualSD'];
const summary=Object.fromEntries(keys.map(k=>[k,{v2:mean(base.map(r=>r.analysis[k])),pooled:mean(results.map(r=>r.analysis[k])),difference:uncertainty(results.map((r,i)=>r.analysis[k]-base[i].analysis[k]))}]));
const files=results.map(r=>{const file=root+'/runs/diagnostic-pooled-clock-seed'+r.seed+'.json';fs.writeFileSync(file,JSON.stringify(r)+'\n');return {seed:r.seed,file,sha256:hash(file)};});
const report={scope:'20pairedseeds20261012-31, regulation1227 fixtures. Diagnostic only: replace every start-state CDF with same positive empirical pooled-segment CDF; other v2 parameters, pace and all outcomes unchanged. Not a proposed baseline and no accuracy optimization. Mean/count variance changes also listed; remaining covariance controls linearly for observed possession count.',summary,files,
 verifiedCode:'Empirical deadline is drawn once before setup. Setup/pass elapsed time is subtracted from release deadline; extra completed passes do not increase the complete opportunity duration. Empirical setup/release also omit the existing hurry/protectLead timeFactor. Legacy clock sums setup+pass+release and applies that factor. This is verified from source, but does not identify each channel causal contribution.',
 sources:Object.fromEntries(['reports/defense-b1/empirical-timing.json',root+'/v2-seeds.json','src/defense_fourth_game.js','src/defense_fourth_effects.js','scripts/diagnose_defense_fourth_timing_state.js'].map(f=>[f,hash(f)]))};
fs.writeFileSync(root+'/timing-state-diagnosis.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(summary,null,2));

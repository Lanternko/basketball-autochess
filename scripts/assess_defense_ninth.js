import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {makeRng} from '../src/rng.js';
import {deltaNamesN,evaluateN,flattenN,aggregateN,fitN,meanN,sdN} from '../src/defense_ninth_statistics.js';
const root='reports/defense-ninth/development',spec=read(root+'/prereg.json'),dataset=read(root+'/dataset.json'),data=dataset.data,B=spec.bootstrap.replicates;
if(dataset.preregHash!==hash(root+'/prereg.json'))throw Error('Prereg changed');
for(const [p,h]of Object.entries(spec.sourceHashes))if(hash(p)!==h)throw Error('Input changed '+p);
const point=evaluateN(data),flat=flattenN(point),series=Object.fromEntries(Object.entries(flat).filter(([,v])=>Number.isFinite(v)).map(([key])=>[key,{values:new Float64Array(B),n:0}])),rng=makeRng(spec.bootstrap.rngSeed),start=Date.now();
for(let b=0;b<B;b++){
 const tw=Array(30).fill(0),sw=Array(20).fill(0);for(let i=0;i<30;i++)tw[Math.floor(rng()*30)]++;for(let i=0;i<20;i++)sw[Math.floor(rng()*20)]++;
 const sample=flattenN(evaluateN(data,sw,tw));for(const [key,s]of Object.entries(series)){const x=sample[key];if(Number.isFinite(x))s.values[s.n++]=x;}
 if((b+1)%1000===0)console.log('BOOT',b+1,B,'seconds',((Date.now()-start)/1000).toFixed(1));
}
const intervals={};for(const [key,s]of Object.entries(series)){const a=s.values.slice(0,s.n).sort(),m=meanN(a);intervals[key]={estimate:flat[key],standardError:Math.sqrt(a.reduce((v,x)=>v+(x-m)**2,0)/a.length),ci95:[a[Math.floor(.025*a.length)],a[Math.floor(.975*a.length)]],ci998:[a[Math.floor(.001*a.length)],a[Math.floor(.999*a.length)]],valid:s.n};}
const diagnostics=data.map(season=>season.map(c=>{const deltas={};for(const v of deltaNamesN){const m=c.ids.map((_,i)=>meanN(c.deltas[v].map(row=>row[i]))),SE=c.ids.map((_,i)=>sdN(c.deltas[v].map(row=>row[i]))/Math.sqrt(20));deltas[v]={teamSD:sdN(m),teamsAbove2SE:m.filter((x,i)=>Math.abs(x)>2*SE[i]).length,meanSeedSE:meanN(SE),medianSeedSE:[...SE].sort((a,b)=>a-b)[15],maxSeedSE:Math.max(...SE),teams:c.ids.map((id,i)=>({id,name:c.names[i],delta:m[i],seedSE:SE[i],above2SE:Math.abs(m[i])>2*SE[i]}))};}return {season:c.season,k:c.k,deltas};}));
const gates=deltaNamesN.filter(v=>v!=='naive').map(v=>{
 const bs=point.folds.filter(f=>f.delta===v&&f.mode==='fit').map(f=>({heldout:f.heldout,b:f.b})),sameSign=bs.every(f=>f.b>0)||bs.every(f=>f.b<0),negativeK=[],nonWorseNaiveK=[];
 for(let k=0;k<3;k++){const m=point.pooled[k].versions;if(m[v+'-fit'].netRMSE<Math.min(m.simple.netRMSE,m.simplecal.netRMSE)){negativeK.push(spec.K[k]);if(m[v+'-fit'].netRMSE<=m['naive-fit'].netRMSE)nonWorseNaiveK.push(spec.K[k]);}}
 const overall=v=>Math.sqrt(meanN(point.pooled.map(c=>c.versions[v+'-fit'].netRMSE**2))),nonWorseNaive=nonWorseNaiveK.length>=2&&overall(v)<=overall('naive');
 return {delta:v,b:bs,sameSign,negativeK,nonWorseNaiveK,overallRMSE:overall(v),naiveOverallRMSE:overall('naive'),nonWorseNaive,continue:sameSign&&negativeK.length>=2&&nonWorseNaive};
});
const allfit=aggregateN(data,Array(20).fill(1),Array(30).fill(1)),developmentConstants=Object.fromEntries(deltaNamesN.map(v=>[v,fitN(allfit,[0,1,2,3],v,Array(30).fill(1))]));
const power=[];
for(const v of deltaNamesN.filter(v=>v!=='naive'))for(const k of spec.K){
 const entries=[0,1,2,3].map(s=>({season:spec.seasons[s],key:`s${s}/K${k}/compare/${v}-fit/net-min`})),one=entries.map(e=>({...e,interval:intervals[e.key]})),three=[];
 for(let omitted=0;omitted<4;omitted++){
  const kept=entries.filter((_,i)=>i!==omitted),noise=Array.from({length:B},(_,b)=>meanN(kept.map(e=>series[e.key].values[b]-flat[e.key]))),SE=sdN(noise);
  three.push({seasons:kept.map(e=>e.season),standardError:SE,power:Object.fromEntries([.15,.4].map(gain=>[gain,noise.filter(x=>x<gain-1.96*SE).length/B]))});
 }
 const approximateCDF=z=>{const t=1/(1+.2316419*Math.abs(z)),a=.3989422804014327*Math.exp(-z*z/2)*t*(.31938153+t*(-.356563782+t*(1.781477937+t*(-1.821255978+t*1.330274429))));return z>=0?1-a:a;};
 power.push({delta:v,k,oneSeason:one.map(e=>({season:e.season,width:e.interval.ci95[1]-e.interval.ci95[0],standardError:e.interval.standardError,power:Object.fromEntries([.15,.4].map(gain=>[gain,{normal:approximateCDF(gain/e.interval.standardError-1.96),empirical:Array.from(series[e.key].values).filter(x=>x-flat[e.key]<gain-1.96*e.interval.standardError).length/B}]))})),threeSeasonPairedPlanning:three,independentThreeSeason:Object.fromEntries([.15,.4].map(gain=>[gain,one.map(e=>approximateCDF(gain/(e.interval.standardError/Math.sqrt(3))-1.96))])),limitation:'Planning using developer seasons and joint-bootstrap noise; future season distribution unknown. Three-season empirical scenario averages centered per-season RMSE contrasts, not an exact pooled-RMSE power analysis. Shared franchise draws retained; no new outcomes inspected.'});
}
fs.writeFileSync(root+'/assessment.json',JSON.stringify({assessedAt:new Date().toISOString(),label:'四季開發季，已看過答案',preregHash:hash(root+'/prereg.json'),datasetHash:hash(root+'/dataset.json'),bootstrap:spec.bootstrap,point,diagnostics,intervals,gates,developmentConstants,power,continue:gates.some(g=>g.continue),conclusion:gates.some(g=>g.continue)?'部分候選符合進入後續盲測的開發季門檻；尚非盲測確認':'現有球員卡無法在簡單對照之上提供可驗證的增量',seconds:(Date.now()-start)/1000},null,2)+'\n');console.log('ASSESS COMPLETE',gates);

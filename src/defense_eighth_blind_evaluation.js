// Precommitted C4 semantics. No blind data are read while defining the rule.
import {makeRng} from './rng.js';
import {mean,sd} from './statistical_summary.js';
import {measureEighth,averageRows} from './defense_eighth_analysis.js';
export function blindVerdict(net,wins){
 const good=x=>x.ci95[1]<0,bad=x=>x.ci95[0]>0;
 return {answer:good(net)||good(wins)?'成立':bad(net)||bad(wins)?'不成立':'分不出',net:good(net)?'改善':bad(net)?'退步':'分不出',wins:good(wins)?'改善':bad(wins)?'退步':'分不出',widths:{netRMSE:net.ci95[1]-net.ci95[0],winMAE:wins.ci95[1]-wins.ci95[0]},tradeoff:(good(net)&&bad(wins))||(good(wins)&&bad(net))};
}
export function combinedMetric(groups,version,seedDraw,teamDraw){
 const ms=groups.map(g=>measureEighth(averageRows(g[version],seedDraw),teamDraw)),keys=['netRMSE','netCorrelation','calibrationSlope','netSDRatio','winMAE','winRMSE'];
 return Object.fromEntries(keys.map(k=>[k,['netRMSE','winRMSE'].includes(k)?Math.sqrt(mean(ms.map(m=>m[k]**2))):mean(ms.map(m=>m[k]))]));
}
export function jointBlindEnvelope(groups,version,{B=5000,rngSeed=20261082}={}){
 const order=groups.map(g=>{const ids=g[version][0].map(t=>t.id).sort((a,b)=>a-b);return Object.fromEntries([version,'simple','shrink'].map(v=>[v,g[v].map(rows=>ids.map(id=>rows.find(t=>t.id===id)))]));});
 const seeds=order[0][version].map((_,i)=>i),teams=order[0][version][0].map((_,i)=>i);
 const delta=(ds,td)=>{const a=combinedMetric(order,version,ds,td),b=combinedMetric(order,'simple',ds,td),c=combinedMetric(order,'shrink',ds,td);return {netRMSE:a.netRMSE-Math.min(b.netRMSE,c.netRMSE),winMAE:a.winMAE-Math.min(b.winMAE,c.winMAE)};};
 const point=delta(seeds,teams),samples={netRMSE:[],winMAE:[]},rng=makeRng(rngSeed);
 for(let n=0;n<B;n++){const td=teams.map(()=>Math.floor(rng()*teams.length)),ds=seeds.map(()=>Math.floor(rng()*seeds.length)),d=delta(ds,td);for(const k of Object.keys(samples))samples[k].push(d[k]);}
 const result=Object.fromEntries(Object.keys(samples).map(k=>{const a=samples[k].sort((a,b)=>a-b);return [k,{estimate:point[k],standardError:sd(a),ci95:[a[Math.floor(.025*B)],a[Math.floor(.975*B)]]}];}));
 result.verdict=blindVerdict(result.netRMSE,result.winMAE);return result;
}
export function jointBlindPair(groups,left,right,{B=5000,rngSeed=20261082}={}){
 const order=groups.map(g=>{const ids=g[left][0].map(t=>t.id).sort((a,b)=>a-b);return Object.fromEntries([left,right].map(v=>[v,g[v].map(rows=>ids.map(id=>rows.find(t=>t.id===id)))]));});
 const seeds=order[0][left].map((_,i)=>i),teams=order[0][left][0].map((_,i)=>i),keys=['netRMSE','netCorrelation','calibrationSlope','netSDRatio','winMAE','winRMSE'];
 const delta=(ds,td)=>{const a=combinedMetric(order,left,ds,td),b=combinedMetric(order,right,ds,td);return Object.fromEntries(keys.map(k=>[k,a[k]-b[k]]));},point=delta(seeds,teams),samples=Object.fromEntries(keys.map(k=>[k,[]])),rng=makeRng(rngSeed);
 for(let n=0;n<B;n++){const td=teams.map(()=>Math.floor(rng()*teams.length)),ds=seeds.map(()=>Math.floor(rng()*seeds.length)),d=delta(ds,td);for(const k of keys)samples[k].push(d[k]);}
 return Object.fromEntries(keys.map(k=>{const x=samples[k].sort((a,b)=>a-b);return [k,{estimate:point[k],standardError:sd(x),ci95:[x[Math.floor(.025*B)],x[Math.floor(.975*B)]]}];}));
}

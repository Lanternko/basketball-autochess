// Evaluation only; this module never feeds statistics back into a predictor.
import {makeRng} from './rng.js';
export const cMetrics=['netRMSE','netCorrelation','calibrationSlope','netSDRatio','residualSD','winMAE','winRMSE','efficiencyBias','oracleRMSE'];
export function prepareCGroup(group){
 const versions=Object.keys(group),ids=group[versions[0]][0].map(t=>t.id).sort((a,b)=>a-b),out={};
 for(const v of versions){if(group[v].length!==20)throw Error('Need20 paired seed rows');out[v]=group[v].map(rows=>ids.map(id=>{const r=rows.find(t=>t.id===id);if(!r)throw Error('Missing franchise '+id);return r;}));}
 return out;
}
function seasonMetrics(g,sw,tw){
 const N=tw.reduce((s,n)=>s+n,0),S=sw.reduce((s,n)=>s+n,0),result={};
 for(const [version,seeds]of Object.entries(g)){
  const hasWins=seeds[0].every(r=>Number.isFinite(r.wins)),hasEvents=seeds[0].every(r=>Number.isFinite(r.points)&&Number.isFinite(r.proxy)),hasResidual=seeds[0].every(r=>r.residualMoment);
  const pn=new Float64Array(30),pw=new Float64Array(30);let pts=0,poss=0,realPts=0,realPoss=0;
  for(let i=0;i<30;i++){
   for(let j=0;j<20;j++)if(sw[j]){const r=seeds[j][i],w=sw[j]/S;pn[i]+=w*r.net;if(hasWins)pw[i]+=w*r.wins;if(hasEvents){pts+=tw[i]*w*r.points;poss+=tw[i]*w*r.proxy;}}
   if(hasEvents){realPts+=tw[i]*seeds[0][i].observed.points;realPoss+=tw[i]*seeds[0][i].observed.proxy;}
  }
  let am=0,pm=0;for(let i=0;i<30;i++){am+=tw[i]*seeds[0][i].observed.net/N;pm+=tw[i]*pn[i]/N;}
  let av=0,pv=0,cov=0,mae=0,mse=0;for(let i=0;i<30;i++){const w=tw[i]/N,a=seeds[0][i].observed.net-am,p=pn[i]-pm;av+=w*a*a;pv+=w*p*p;cov+=w*a*p;if(hasWins){const e=pw[i]-seeds[0][i].observed.wins;mae+=w*Math.abs(e);mse+=w*e*e;}}
  const r=cov/Math.sqrt(av*pv),residual=[];
  if(hasResidual)for(let j=0;j<20;j++)if(sw[j]){let n=0,s=0,s2=0;for(let i=0;i<30;i++){const m=seeds[j][i].residualMoment;n+=tw[i]*m.n;s+=tw[i]*m.sum;s2+=tw[i]*m.sum2;}residual.push(sw[j]/S*Math.sqrt(Math.max(0,s2/n-(s/n)**2)));}
  result[version]={netRMSE:Math.sqrt(Math.max(0,av+pv-2*cov)),netCorrelation:r,calibrationSlope:cov/pv,netSDRatio:Math.sqrt(pv/av),residualSD:hasResidual?residual.reduce((s,x)=>s+x,0):null,winMAE:hasWins?mae:null,winRMSE:hasWins?Math.sqrt(mse):null,efficiencyBias:hasEvents?100*pts/poss-100*realPts/realPoss:null,oracleRMSE:Math.sqrt(av*Math.max(0,1-r*r)),observedNetSD:Math.sqrt(av)};
 }
 return result;
}
export function combinedC(groups,sw=Array(20).fill(1),tw=Array(30).fill(1)){
 const ms=groups.map(g=>seasonMetrics(g,sw,tw)),keys=[...cMetrics,'observedNetSD'];
 return Object.fromEntries(Object.keys(ms[0]).map(v=>[v,Object.fromEntries(keys.map(k=>{const xs=ms.map(m=>m[v][k]);return [k,xs.some(x=>!Number.isFinite(x))?null:['netRMSE','winRMSE','oracleRMSE'].includes(k)?Math.sqrt(xs.reduce((s,x)=>s+x*x,0)/xs.length):xs.reduce((s,x)=>s+x,0)/xs.length];}))]));
}
function difference(metrics,c){const left=metrics[c.left],right=c.envelope?Object.fromEntries(cMetrics.map(k=>[k,k==='netRMSE'||k==='winMAE'||k==='winRMSE'?Math.min(...c.envelope.map(v=>metrics[v][k])):null])):metrics[c.right];return Object.fromEntries(cMetrics.map(k=>[k,(c.netOnly&&['winMAE','winRMSE','residualSD','efficiencyBias'].includes(k))||!Number.isFinite(left[k])||!Number.isFinite(right[k])?null:left[k]-right[k]]));}
export function cVerdict(pair,netOnly=false){const ps=(netOnly?['netRMSE']:['netRMSE','winMAE']).map(k=>pair[k]);const good=x=>x.ci95[1]<0,bad=x=>x.ci95[0]>0;return {answer:ps.some(good)?'成立':ps.some(bad)?'不成立':'分不出',tradeoff:ps.some(good)&&ps.some(bad),widths:Object.fromEntries((netOnly?['netRMSE']:['netRMSE','winMAE']).map(k=>[k,pair[k].ci95[1]-pair[k].ci95[0]]))};}
export function bootstrapC(groups,comparisons,{B=20000,rngSeed=20261082}={}){
 const point=combinedC(groups),deltas=Object.fromEntries(comparisons.map(c=>[c.id,difference(point,c)])),samples=Object.fromEntries(comparisons.map(c=>[c.id,Object.fromEntries(cMetrics.map(k=>[k,[]]))])),rng=makeRng(rngSeed);
 for(let n=0;n<B;n++){const tw=Array(30).fill(0),sw=Array(20).fill(0);for(let i=0;i<30;i++)tw[Math.floor(rng()*30)]++;for(let i=0;i<20;i++)sw[Math.floor(rng()*20)]++;const m=combinedC(groups,sw,tw);for(const c of comparisons){const d=difference(m,c);for(const k of cMetrics)if(Number.isFinite(d[k]))samples[c.id][k].push(d[k]);}}
 const pairs={};for(const c of comparisons){pairs[c.id]={};for(const k of cMetrics){const xs=samples[c.id][k];if(!xs.length){pairs[c.id][k]=null;continue;}xs.sort((a,b)=>a-b);const mu=xs.reduce((s,x)=>s+x,0)/xs.length;pairs[c.id][k]={estimate:deltas[c.id][k],standardError:Math.sqrt(xs.reduce((s,x)=>s+(x-mu)**2,0)/xs.length),ci95:[xs[Math.floor(.025*xs.length)],xs[Math.floor(.975*xs.length)]],ci998:[xs[Math.floor(.001*xs.length)],xs[Math.floor(.999*xs.length)]]};}pairs[c.id].verdict=cVerdict(pairs[c.id],c.netOnly);}
 return {versions:point,pairs,bootstrap:{B,rngSeed}};
}
export function confirmationC(cutoffs,comparison,direction){
 const keys=comparison.netOnly?['netRMSE']:['netRMSE','winMAE'],inDirection=(x,ci)=>direction==='improvement'?x[ci][1]<0:x[ci][0]>0;
 const cells=Object.entries(cutoffs).map(([k,cell])=>({k:Number(k),pair:cell.pairs[comparison.id]})),hits=cells.filter(x=>keys.some(k=>inDirection(x.pair[k],'ci95'))).map(x=>x.k),wide=cells.filter(x=>keys.some(k=>inDirection(x.pair[k],'ci998'))).map(x=>x.k);
 return {grade:hits.length>=2||wide.length?'跨季確認':hits.length===1?'單點成立':'分不出',direction,K95:hits,K998:wide,warning:hits.length===1&&!wide.length?'30多個檢定中預期約1–2個偶然通過':null,endpoints:Object.fromEntries(keys.map(k=>{const h=cells.filter(x=>inDirection(x.pair[k],'ci95')).map(x=>x.k),w=cells.filter(x=>inDirection(x.pair[k],'ci998')).map(x=>x.k);return [k,{grade:h.length>=2||w.length?'跨季確認':h.length===1?'單點成立':'分不出',K95:h,K998:w}];}))};
}

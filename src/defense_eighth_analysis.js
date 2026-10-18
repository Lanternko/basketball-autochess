import {mean,sd} from './statistical_summary.js';
import {slope,compareMetrics} from './defense_scoreboard.js';
import {makeRng} from './rng.js';
export const eighthMetrics=['netRMSE','netCorrelation','netSDRatio','calibrationSlope','winMAE','winRMSE','winSlope','calibrationError','defenseCorrelation','defenseSDRatio','residualSD'];
export function decomposition(actual,predicted){
 const m=compareMetrics(actual,predicted),r=m.correlation,sy=m.observedSD,sx=m.simulatedSD;
 // RMSE^2 = sy^2(1-r^2) + (sx-r sy)^2, population SD, separately centered.
 const rankingMSE=sy*sy*Math.max(0,1-r*r),dispersionMSE=(sx-r*sy)**2;
 const correlationMSE=2*sx*sy*(1-r),sdGapMSE=(sx-sy)**2;
 return {...m,correlationMSE,sdGapMSE,correlationRMSE:Math.sqrt(Math.max(0,correlationMSE)),sdGapRMSE:Math.sqrt(sdGapMSE),rankingMSE,dispersionMSE,rankingRMSE:Math.sqrt(rankingMSE),dispersionRMSE:Math.sqrt(dispersionMSE),oracleShrunkRMSE:Math.sqrt(rankingMSE),oracleMultiplier:slope(predicted,actual),identityError:m.centeredRMSE**2-rankingMSE-dispersionMSE,standardIdentityError:m.centeredRMSE**2-correlationMSE-sdGapMSE};
}
export function measureEighth(teams,draw=teams.map((_,i)=>i)){
 const t=draw.map(i=>teams[i]),a=t.map(x=>x.observed.net),p=t.map(x=>x.net),d=decomposition(a,p),e=t.map(x=>x.wins-x.observed.wins),cal=d.oracleMultiplier;
 const hasDefense=t.every(x=>Number.isFinite(x.defensiveRatingProxy)&&Number.isFinite(x.observed.defensiveRatingProxy));
 const def=hasDefense?compareMetrics(t.map(x=>x.observed.defensiveRatingProxy),t.map(x=>x.defensiveRatingProxy)):null;
 const rv=t.every(x=>x.residualMoment);
 let residualSD=null;
 if(rv){const n=t.reduce((s,x)=>s+x.residualMoment.n,0),m=t.reduce((s,x)=>s+x.residualMoment.sum,0)/n;residualSD=Math.sqrt(Math.max(0,t.reduce((s,x)=>s+x.residualMoment.sum2,0)/n-m*m));}
 return {netRMSE:d.centeredRMSE,netCorrelation:d.correlation,netSDRatio:d.sdRatio,calibrationSlope:cal,calibrationError:Math.abs(cal-1),winMAE:mean(e.map(Math.abs)),winRMSE:Math.sqrt(mean(e.map(x=>x*x))),winSlope:slope(p,t.map(x=>x.wins)),defenseCorrelation:def?.correlation??null,defenseSDRatio:def?.sdRatio??null,residualSD};
}
export function averageRows(seedRows,draws=seedRows.map((_,i)=>i)){
 return seedRows[0].map((row,j)=>({...row,...Object.fromEntries(['net','wins','defensiveRatingProxy'].map(k=>[k,row[k]==null?null:mean(draws.map(i=>seedRows[i][j][k]))]))}));
}
function percentile(xs){const a=xs.filter(Number.isFinite).sort((a,b)=>a-b);return a.length?{standardError:sd(a),ci95:[a[Math.floor(.025*a.length)],a[Math.floor(.975*a.length)]]}:{standardError:null,ci95:[null,null]};}
function combine(ms){return Object.fromEntries(eighthMetrics.map(k=>[k,ms.some(m=>!Number.isFinite(m[k]))?null:(['netRMSE','winRMSE'].includes(k)?Math.sqrt(mean(ms.map(m=>m[k]**2))):mean(ms.map(m=>m[k])))]));}
export function pairedEighth(groups,{B=5000,rngSeed=20261080}={}){
 // Each group is a season at one cutoff. Franchise draw is shared across seasons;
 // means/SD/centering are recomputed within season, then seasons get equal weight.
 const ordered=groups.map(g=>{const ids=g.a[0].map(x=>x.id).sort((a,b)=>a-b);return {...g,a:g.a.map(rows=>ids.map(id=>rows.find(x=>x.id===id))),b:g.b.map(rows=>ids.map(id=>rows.find(x=>x.id===id)))};});
 const all=ordered[0].a[0].map((_,i)=>i),seeds=ordered[0].a.map((_,i)=>i);
 if(ordered.some(g=>g.a.length!==seeds.length||g.b.length!==seeds.length))throw Error('Unpaired seed count');
 const evaluate=(which,teamDraw,seedDraw)=>combine(ordered.map(g=>{
  const rows=averageRows(g[which],seedDraw),m=measureEighth(rows,teamDraw);
  // Aggregate SD is mean per-seed residual SD (same original convention).
  m.residualSD=mean(seedDraw.map(i=>{
   if(!g[which][i][0].residualMoment)return null;
   let n=0,s=0,s2=0;for(const j of teamDraw){const x=g[which][i][j].residualMoment;n+=x.n;s+=x.sum;s2+=x.sum2;}
   return Math.sqrt(Math.max(0,s2/n-(s/n)**2));
  }).filter(Number.isFinite));
  if(!g[which][0].every(x=>x.residualMoment))m.residualSD=null;
  return m;
 }));
 const aa=evaluate('a',all,seeds),bb=evaluate('b',all,seeds),samples=Object.fromEntries(['seed','team','joint'].map(mode=>[mode,Object.fromEntries(eighthMetrics.map(k=>[k,[]]))]));
 for(const mode of ['seed','team','joint']){
  const rng=makeRng(rngSeed+(mode==='seed'?0:mode==='team'?1:2));
  for(let n=0;n<B;n++){
   const td=mode==='seed'?all:all.map(()=>Math.floor(rng()*all.length)),ds=mode==='team'?seeds:seeds.map(()=>Math.floor(rng()*seeds.length));
   const a=evaluate('a',td,ds),b=evaluate('b',td,ds);
   for(const k of eighthMetrics)if(Number.isFinite(a[k])&&Number.isFinite(b[k]))samples[mode][k].push(a[k]-b[k]);
  }
 }
 return Object.fromEntries(eighthMetrics.map(k=>[k,{estimate:Number.isFinite(aa[k])&&Number.isFinite(bb[k])?aa[k]-bb[k]:null,...Object.fromEntries(['seed','team','joint'].map(mode=>[mode,percentile(samples[mode][k])]))}]));
}

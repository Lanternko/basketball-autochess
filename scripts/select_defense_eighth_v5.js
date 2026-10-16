import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {calendarTruth} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
import {mean} from '../src/statistical_summary.js';
import {slope} from '../src/defense_scoreboard.js';
import {bLabel} from './run_defense_eighth_b_point.js';
const root='reports/defense-eighth/b',rules=read(root+'/development-rules.json'),a=read('reports/defense-eighth/a/analysis.json');
if(fs.existsSync(root+'/selection.json'))throw Error('Selection exists; do not revise after validation');
const center=xs=>xs.map(x=>x-mean(xs)),rms=xs=>Math.sqrt(mean(xs.map(x=>x*x))),result={selectedAt:new Date().toISOString(),developmentOnly:true,rulesHash:hash(root+'/development-rules.json'),oracleRatios:{},cutoffs:{},sources:{}};
result.sources['reports/defense-eighth/a/analysis.json']=hash('reports/defense-eighth/a/analysis.json');
for(const season of rules.developmentSeasons)result.oracleRatios[season]=Object.fromEntries(rules.cutoffs.map(k=>{const m=a.seasons[season][k].models,den=m.simple.metrics.calibrationSlope;return [k,{v4:m.v4.metrics.calibrationSlope/den,v3:m.v3.metrics.calibrationSlope/den,definition:'Oracle actual-vs-prediction slope ratios in development data; not forecasts.'}];}));
for(const k of rules.cutoffs){
 const datasets=rules.developmentSeasons.map(season=>{
  const cf=`reports/defense-seventh/${season}/calendar-${k}/config.json`,truth=calendarTruth(read(cf)),rows={},summaries={};
  result.sources[cf]=hash(cf);result.sources[read(cf).root+'/ability-model-forward.json']=hash(read(cf).root+'/ability-model-forward.json');
  for(const c of rules.selection.anchors){const label=c===1?`${season}-calendar-${k}-v4`:bLabel(season,k,c),runs=loadSeventh(label),summary=summarizeFifth(runs,0,runs.map((_,i)=>i),truth);rows[c]=summary.teams.map(t=>t.net);summaries[c]=summary.metrics;const file=`reports/defense-seventh/${label}-seeds.json`;result.sources[file]=hash(file);}
  const observed=truth.teams.map(t=>t.net),target=a.seasons[season][k].models.simple.metrics.calibrationSlope;
  const model=read(read(cf).root+'/ability-model-forward.json'),weights=model.minutes,ws=weights.reduce((s,w)=>s+w,0),weightedSD=xs=>{const mu=xs.reduce((s,x,i)=>s+x*weights[i],0)/ws;return Math.sqrt(xs.reduce((s,x,i)=>s+weights[i]*(x-mu)**2,0)/ws);};
  const abilitySpread={priorOffenseSD:weightedSD(model.models.role.priorOffense),offenseResidualSD:weightedSD(model.models.role.offenseResidual),definition:'Training-minute weighted logPPP spread; size comparison only, not a causal variance decomposition.'};
  const z=center(rows[0]),half=center(rows[.5]),one=center(rows[1]),mid=z.map((v,i)=>(v+one[i])/2),difference=half.map((v,i)=>v-mid[i]),response=one.map((v,i)=>v-z[i]);
  return {season,observed,rows,summaries,target,abilitySpread,nonlinearity:{midpointRMS:rms(difference),endpointResponseRMS:rms(response),relativeMidpointError:rms(difference)/Math.max(1e-12,rms(response)),actualHalfSlope:slope(half,observed),straightEndpointHalfSlope:slope(mid,observed),teamScaleRegression:Object.fromEntries(rules.selection.anchors.map(c=>[c,slope(one,center(rows[c]))]))}};
 });
 const target=mean(datasets.map(d=>d.target));
 const predict=(d,c)=>{const lo=c<=.5?0:.5,hi=c<=.5?.5:1,t=(c-lo)/(hi-lo);return d.rows[lo].map((v,i)=>v+(d.rows[hi][i]-v)*t);},calibration=c=>mean(datasets.map(d=>slope(predict(d,c),d.observed))),loss=c=>Math.abs(calibration(c)-target);
 let best=1,bestLoss=loss(1),mappedMin=Infinity,mappedMax=-Infinity;for(let i=0;i<=10000;i++){const c=i/10000,beta=calibration(c),l=Math.abs(beta-target);mappedMin=Math.min(mappedMin,beta);mappedMax=Math.max(mappedMax,beta);if(l<bestLoss-1e-12||Math.abs(l-bestLoss)<=1e-12&&c>best){best=c;bestLoss=l;}}
 let lo=Math.max(0,best-.0001),hi=Math.min(1,best+.0001),phi=(Math.sqrt(5)-1)/2;
 for(let i=0;i<80;i++){const x=hi-phi*(hi-lo),y=lo+phi*(hi-lo);if(loss(x)<loss(y))hi=y;else lo=x;}
 const refined=(lo+hi)/2;if(loss(refined)<bestLoss)best=refined;
 const c=Number(best.toFixed(6));
 result.cutoffs[k]={c,targetSimpleSlope:target,v4Slope:calibration(1),mappedSelectedSlope:calibration(c),mappingGap:calibration(c)-target,mappedRange:[mappedMin,mappedMax],targetWithinMappedRange:target>=mappedMin&&target<=mappedMax,anchorPooledSlopes:Object.fromEntries(rules.selection.anchors.map(c=>[c,calibration(c)])),mapping:'Piecewise centered team-net response, not c=oracle-ratio.',seasons:datasets};console.log('SELECTED',k,c,'target',target,'mapped',calibration(c));
}
fs.writeFileSync(root+'/selection.json',JSON.stringify(result,null,2)+'\n');

import fs from 'node:fs';
import {read,table,hash} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {calendarTruth,simpleCalendar} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
import {mean} from '../src/statistical_summary.js';
import {slope} from '../src/defense_scoreboard.js';
import {decomposition,measureEighth,pairedEighth,averageRows} from '../src/defense_eighth_analysis.js';
const root='reports/defense-eighth/a',seasons=['2024-25','2025-26'],ks=[25,41,55];fs.mkdirSync(root,{recursive:true});
const cache=fs.existsSync(root+'/analysis.json')?read(root+'/analysis.json'):null;
const cacheValid=cache&&Object.entries(cache.sources).every(([p,h])=>hash(p)===h)&&cache.analysisCodeHash===hash('src/defense_eighth_analysis.js');
function shrinkSimple(c,simple,truth){
 const l=read(c.leagueFile),logs=table(c.paths['data/season-source/team-games.json']),lookup=new Map(logs.map(r=>[r.GAME_ID+'/'+r.TEAM_ID,r])),train=l.schedule.filter(g=>g.date<=c.date),dates=[...new Set(train.map(g=>g.date))].sort(),split=dates[Math.floor((dates.length-1)/2)];
 const stats=l.teams.map(t=>{const gs=train.filter(g=>[g.homeId,g.awayId].includes(t.id)),phase=early=>{const a=gs.filter(g=>(g.date<=split)===early);return {games:a.length,net:mean(a.map(g=>lookup.get(g.id+'/'+t.id).PTS-lookup.get(g.id+'/'+(g.homeId===t.id?g.awayId:g.homeId)).PTS))};};return {id:t.id,early:phase(true),late:phase(false)};});
 const raw=slope(stats.map(t=>t.early.net),stats.map(t=>t.late.net)),multiplier=Math.max(0,Math.min(1,raw));
 const trainTruth=calendarTruth(c,'train'),rows=simple.summary.teams.map(t=>{const pre=trainTruth.teams.find(x=>x.id===t.id),post=truth.teams.find(x=>x.id===t.id);return {id:t.id,name:t.name,net:multiplier*t.net,wins:post.games/(1+(pre.opponent.pts/pre.stats.pts)**(simple.exponent*multiplier)),observed:post};});
 return {rows,metrics:measureEighth(rows),multiplier,rawSlope:raw,split,date:c.date,trainingChecks:stats,method:'League-wide OLS slope of late-training team mean net on early-training mean net, clipped [0,1] for shrinkage only. Split complete dates at training midpoint; fit no intercept after centering. Apply same constant to train net and Pythagorean log scoring ratio; full-training exponent unchanged. Never use holdout results to select constant.'};
}
function seedRows(label,truth){
 const rs=loadSeventh(label),manifest=read('reports/defense-seventh/'+label+'-seeds.json'),league=manifest.extra.cardFile?read(manifest.extra.cardFile):read(manifest.extra.bundle).league;
 // Residuals match the frozen quickVariance definition. Team bootstrap weights
 // each fixed residual by the average multiplicity of its two endpoints.
 const valid=new Set(league.validGameIds??[]);
 return rs.map(r=>{
  const s=summarizeFifth([r],0,[0],truth),gs=r.matches.filter(g=>!valid.size||valid.has(g.id)),sc=new Map(),al=new Map();
  for(const g of gs)for(let i=0;i<2;i++){const id=i?g.awayId:g.homeId;const a=sc.get(id)??[],b=al.get(id)??[];a.push(g.regulationScore[i]);b.push(g.regulationScore[1-i]);sc.set(id,a);al.set(id,b);}
  for(const[id,a]of sc)sc.set(id,mean(a));for(const[id,a]of al)al.set(id,mean(a));const lm=mean([...sc.values()]),mom=new Map(s.teams.map(t=>[t.id,{n:0,sum:0,sum2:0}]));
  for(const g of gs){const e=(g.regulationScore[0]-sc.get(g.homeId)-al.get(g.awayId)+lm)-(g.regulationScore[1]-sc.get(g.awayId)-al.get(g.homeId)+lm);for(const id of [g.homeId,g.awayId]){const m=mom.get(id);m.n+=.5;m.sum+=e*.5;m.sum2+=e*e*.5;}}
  return s.teams.map(t=>({...t,residualMoment:mom.get(t.id)}));
 });
}
const result={stage:'A',B:5000,seeds:Array.from({length:20},(_,i)=>20261012+i),definition:'Population SD and team-centered net RMSE. Pair all versions on same franchise and seeds; team-only and joint seed/team bootstrap5000, franchise draw shared between seasons. Combined seasons are equally weighted, centered within each season; RMSE via average squared error, other metrics average seasonal metric. Fixed fitted models; not refit uncertainty. Joint CI is decision interval. Residual bootstrap reweights frozen adjusted game residuals by endpoint multiplicity; it does not re-estimate game-strength adjustment.',seasons:{},combined:{},sources:{}};
const datasets={};
for(const season of seasons){
 result.seasons[season]={};datasets[season]={};
 for(const k of ks){
  const cf=`reports/defense-seventh/${season}/calendar-${k}/config.json`,c=read(cf),truth=calendarTruth(c),simple=simpleCalendar(c),sh=shrinkSimple(c,simple,truth),simpleRows=simple.summary.teams.map(t=>({id:t.id,name:t.name,net:t.net,wins:t.wins,observed:t.observed})),data={v3:seedRows(`${season}-calendar-${k}-v3`,truth),v4:seedRows(`${season}-calendar-${k}-v4`,truth),simple:Array.from({length:20},()=>simpleRows),shrink:Array.from({length:20},()=>sh.rows)};
  for(const label of ['v1','v3-signals-off'])if(fs.existsSync(`reports/defense-seventh/${season}-eighth-a-calendar-${k}-${label}-seeds.json`))data[label]=seedRows(`${season}-eighth-a-calendar-${k}-${label}`,truth);
  const models=Object.fromEntries(Object.entries(data).map(([key,rows])=>{const averaged=averageRows(rows),metrics=measureEighth(averaged);metrics.residualSD=rows[0].every(t=>t.residualMoment)?mean(rows.map(r=>measureEighth(r).residualSD)):null;return [key,{metrics,decomposition:decomposition(averaged.map(t=>t.observed.net),averaged.map(t=>t.net)),teams:averaged.map(t=>({id:t.id,name:t.name,net:t.net,wins:t.wins,actualNet:t.observed.net,actualWins:t.observed.wins}))}];}));
  const pairs={},keys=Object.keys(data);
  for(let i=0;i<keys.length;i++)for(let j=i+1;j<keys.length;j++){const key=keys[i]+'-minus-'+keys[j];pairs[key]=cacheValid&&cache.seasons[season][k].pairs[key]?cache.seasons[season][k].pairs[key]:pairedEighth([{a:data[keys[i]],b:data[keys[j]]}]);}
  const historical=read(`reports/defense-seventh/${season}-calendar-assessment.json`).cutoffs[k];
  for(const[key,old,reverse]of [['v3-minus-v4',historical.pairedV3,true],['v4-minus-simple',historical.pairedSimple,false]])for(const [m,ci]of Object.entries(old))if(pairs[key]?.[m])pairs[key][m].historicalSeed=reverse?{estimate:-ci.estimate,standardError:ci.standardError,ci95:[-ci.ci95[1],-ci.ci95[0]]}:ci;
  result.seasons[season][k]={date:c.date,models,shrinkRule:{...sh,rows:undefined,metrics:undefined},pairs,strongerBenchmarkByMetric:{netRMSE:models.shrink.metrics.netRMSE<models.simple.metrics.netRMSE?'shrink':'simple',winMAE:models.shrink.metrics.winMAE<models.simple.metrics.winMAE?'shrink':'simple'},benchmarkNote:'Stronger heldout comparator is an evaluation envelope (can differ by metric), not a deployable selection rule; both predictors and all intervals are reported.'};
  datasets[season][k]=data;result.sources[cf]=hash(cf);for(const p of [c.leagueFile,c.paths['data/season-source/team-games.json']])result.sources[p]=hash(p);console.log('ASSESS',season,k,JSON.stringify({oracle:Object.fromEntries(Object.entries(models).map(([name,m])=>[name,m.decomposition.oracleShrunkRMSE])),shrink:sh.multiplier}));
 }
}
for(const k of ks){const keys=['v3','v4','simple','shrink'],pairs={};for(let i=0;i<keys.length;i++)for(let j=i+1;j<keys.length;j++){const key=keys[i]+'-minus-'+keys[j];pairs[key]=cacheValid?cache.combined[k].pairs[key]:pairedEighth(seasons.map(s=>({a:datasets[s][k][keys[i]],b:datasets[s][k][keys[j]]})));}result.combined[k]={pairs};}
for(const s of seasons)for(const k of ks)for(const v of ['v3','v4']){const file=`reports/defense-seventh/${s}-calendar-${k}-${v}-seeds.json`;result.sources[file]=hash(file);}
result.analysisCodeHash=hash('src/defense_eighth_analysis.js');
for(const s of seasons)for(const k of ks)for(const v of ['v1','v3-signals-off']){const p=`reports/defense-seventh/${s}-eighth-a-calendar-${k}-${v}-seeds.json`;if(fs.existsSync(p))result.sources[p]=hash(p);}
fs.writeFileSync(root+'/analysis.json',JSON.stringify(result,null,2)+'\n');

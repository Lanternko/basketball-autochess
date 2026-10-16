import fs from 'node:fs';
import {read,hash,table} from './defense_io.js';
import {scoreboard,actualScoreboardInputs,teamRows,SCOREBOARD_KEYS,compareMetrics,slope,mean,sd} from '../src/defense_scoreboard.js';
import {teamDefenseMetrics} from '../src/defense_validation.js';
import {makeRng} from '../src/rng.js';
const manifests=process.argv.slice(2);if(!manifests.length)throw Error('Supply seed manifests');
const inputs=actualScoreboardInputs(read('data/season-league.json'),table('data/benchmark-source/teams.json'),table('data/diagnostic-source/opponents.json'));
const root='reports/defense-third';fs.mkdirSync(root,{recursive:true});
const cohorts=manifests.map(file=>{const manifest=read(file),runs=manifest.files.map(s=>{if(hash(s.file)!==s.sha256)throw Error('Stale run');return read(s.file);});
  if(runs.length<20)throw Error('Need at least 20 seeds');
  return {file,manifest,runs,board:scoreboard(runs,...Object.values(inputs)),cache:runs.map(teamRows)};});
const fields=['bias','correlation','sdRatio','slope','centeredMAE','centeredRMSE','simulatedPooled','simulatedSD'];
const globalReal=cohorts[0].board.global.observed;
function ensemble(c,indices){
  const averaged=inputs.actualTeams.map((t,j)=>Object.fromEntries(['wins',...SCOREBOARD_KEYS].map(k=>[k,mean(indices.map(i=>c.cache[i].find(r=>r.id===t.id)[k]))])));
  const stats={},op={};for(const i of indices)for(const t of c.runs[i].teams)for(const [k,v] of Object.entries(t.stats))if(Number.isFinite(v)){stats[k]=(stats[k]??0)+v;op[k]=(op[k]??0)+t.opponent[k];}
  const global={...teamDefenseMetrics(stats,op,2460*indices.length),net:0};
  const out={};for(const k of SCOREBOARD_KEYS){const m={...compareMetrics(inputs.actualTeams.map(t=>t[k]),averaged.map(t=>t[k]),{observedCenter:globalReal[k],simulatedCenter:global[k]}),bias:global[k]-globalReal[k],simulatedPooled:global[k]};for(const f of fields)out[k+'.'+f]=m[f];}
  out.winPerNet=slope(averaged.map(t=>t.net),averaged.map(t=>t.wins));out.winMAE=mean(averaged.map((t,j)=>Math.abs(t.wins-inputs.actualTeams[j].wins)));
  for(const k of ['marginSD','residualSD','closeShare','blowoutShare'])out[k]=mean(indices.map(i=>c.board.games.single[i][k]));
  for(const k of ['fg','three','turnovers','possessionsProxy','clockTurnovers','liveTurnovers','startedPossessions'])out['global.'+k]=global[k];
  out['global.liveShare']=stats.liveTov/stats.tov;
  out['global.clockPer100Possessions']=100*stats.clockTov/stats.poss;
  return out;
}
const repetitions=2000,rng=makeRng(20261101),bootstrap=cohorts.map(()=>[]),n=cohorts[0].runs.length;
if(cohorts.some(c=>JSON.stringify(c.board.seeds)!==JSON.stringify(cohorts[0].board.seeds)))throw Error('Paired comparison requires identical seeds');
for(let b=0;b<repetitions;b++){const indices=Array.from({length:n},()=>Math.floor(rng()*n));cohorts.forEach((c,j)=>bootstrap[j].push(ensemble(c,indices)));}
const quantile=(xs,p)=>{const a=xs.slice().sort((a,b)=>a-b);return a[Math.floor((a.length-1)*p)];};
const uncertainty=xs=>({standardError:sd(xs)*Math.sqrt(xs.length/(xs.length-1)),ci95:[quantile(xs,.025),quantile(xs,.975)]});
for(const [j,c] of cohorts.entries()){
  const point=ensemble(c,Array.from({length:n},(_,i)=>i)),single=Array.from({length:n},(_,i)=>ensemble(c,[i]));
  c.board.uncertainty={definition:'Seed-block bootstrap of the full ensemble, 2000 paired resamples. Conditional Monte Carlo uncertainty only; not data/model uncertainty. Single-seed sample SD / sqrt(n) also listed, not substituted for nonlinear ensemble SE.',repetitions,bootstrapSeed:20261101,metrics:Object.fromEntries(Object.keys(point).map(k=>[k,{estimate:point[k],...uncertainty(bootstrap[j].map(r=>r[k])),singleSeedSD:sd(single.map(r=>r[k]))*Math.sqrt(n/(n-1)),singleSeedMeanSE:sd(single.map(r=>r[k]))/Math.sqrt(n-1)}]))};
  c.board.adoption={primary:['net.centeredRMSE','net.correlation','net.sdRatio','winPerNet'],reportedOnly:['winMAE'],clockGates:['efficiencyBias <= 0.5','boxPossBias <= 0.5','TOV/G bias <= 0.2','shot-clock and live turnover share aligned','FG% and 3P% no regression']};
  c.board.provenance={manifest:{file:c.file,sha256:hash(c.file)},sources:Object.fromEntries(['data/season-league.json','data/benchmark-source/teams.json','data/diagnostic-source/opponents.json'].map(f=>[f,hash(f)])),code:Object.fromEntries(['scripts/defense_third_uncertainty.js','src/defense_scoreboard.js','src/statistical_summary.js'].map(f=>[f,hash(f)]))};
  fs.writeFileSync(root+'/scoreboard-'+c.manifest.preset+'-20.json',JSON.stringify(c.board,null,2)+'\n');
  const f=n=>Number.isFinite(n)?n.toFixed(4):'—',u=c.board.uncertainty.metrics;
  const md=['# 二十 seed 計分板：'+c.manifest.preset,'','採用主判準：去均值淨勝分 RMSE、相關、SD 比、每分淨勝分勝場斜率。勝場 MAE 僅列示。',
    '','合併計數聯盟均值；逐隊先平均 seed；母體 SD；SE 為 seed 整季區塊 bootstrap（2000 次）。只代表模擬種子不確定性。','',
    '| 指標 | 偏差 ± SE | 相關 ± SE | SD比 ± SE | 斜率 ± SE | 去均值MAE ± SE | 去均值RMSE ± SE |','|---|---:|---:|---:|---:|---:|---:|',
    ...SCOREBOARD_KEYS.map(k=>'| '+k+' | '+['bias','correlation','sdRatio','slope','centeredMAE','centeredRMSE'].map(v=>f(c.board.metrics[k][v])+' ± '+f(u[k+'.'+v].standardError)).join(' | ')+' |'),'',
    `勝場斜率 ${f(u.winPerNet.estimate)} ± ${f(u.winPerNet.standardError)}；勝場MAE ${f(u.winMAE.estimate)} ± ${f(u.winMAE.standardError)}（非採用判準）。單 seed MAE 範圍 ${c.board.wins.singleMAERange.map(f).join('–')}。`,'',
    '| 指標 | 估計 | SE | 95%區間 | 單seed SD | 單seed均值SE |','|---|---:|---:|---:|---:|---:|',
    ...Object.entries(u).map(([k,v])=>`| ${k} | ${f(v.estimate)} | ${f(v.standardError)} | ${v.ci95.map(f).join('–')} | ${f(v.singleSeedSD)} | ${f(v.singleSeedMeanSE)} |`),''].join('\n');
  fs.writeFileSync(root+'/scoreboard-'+c.manifest.preset+'-20.md',md);
}
if(cohorts.length>1){const result=cohorts.slice(1).map((c,j)=>({baseline:cohorts[0].manifest.preset,candidate:c.manifest.preset,direction:'candidate minus baseline',differences:Object.fromEntries(Object.keys(bootstrap[0][0]).map(k=>[k,{estimate:c.board.uncertainty.metrics[k].estimate-cohorts[0].board.uncertainty.metrics[k].estimate,...uncertainty(bootstrap[j+1].map((r,i)=>r[k]-bootstrap[0][i][k]))}]))}));fs.writeFileSync(root+'/paired-comparison.json',JSON.stringify(result,null,2)+'\n');}
fs.writeFileSync(root+'/paired-comparison-provenance.json',JSON.stringify({seeds:cohorts[0].board.seeds,repetitions,bootstrapSeed:20261101,sources:Object.fromEntries([...manifests,'data/season-league.json','data/benchmark-source/teams.json','data/diagnostic-source/opponents.json'].map(f=>[f,hash(f)])),code:hash('scripts/defense_third_uncertainty.js')},null,2)+'\n');
console.log(cohorts.map(c=>({preset:c.manifest.preset,net:c.board.metrics.net,wins:c.board.wins.winPerNet,winMAE:c.board.wins.expectedMAE})));

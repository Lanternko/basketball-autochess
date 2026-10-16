import fs from 'node:fs';
import {scoreboard,actualScoreboardInputs,SCOREBOARD_KEYS} from '../src/defense_scoreboard.js';
import {read,table,hash} from './defense_io.js';
const args=process.argv.slice(2),outputIndex=args.indexOf('--output');
const output=outputIndex>=0?args[outputIndex+1]:null;
if(outputIndex>=0)args.splice(outputIndex,2);
if(output&&!/^[a-z0-9-]+$/.test(output))throw new Error('Invalid output label');
const files=args;if(!files.length)throw new Error('Usage: node scripts/defense_scoreboard.js [--output LABEL] RUN.json [RUN.json ...]');
const runs=files.map(file=>{const r=read(file);return r.accounting?{seed:r.seed,teams:r.accounting,matches:r.matches,preset:r.version}:r;});
const actual=actualScoreboardInputs(read('data/season-league.json'),table('data/benchmark-source/teams.json'),table('data/diagnostic-source/opponents.json'));
const result=scoreboard(runs,...Object.values(actual));
result.preset=runs[0].preset;result.definitions={means:'Pooled counts across teams and seeds; ratios after pooling.',
  crossTeam:'Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.',
  errors:'Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.',residual:'Each game margin minus own seed season team net difference; not held-out strength.'};
result.provenance={sources:Object.fromEntries([...files,'data/season-league.json','data/benchmark-source/teams.json','data/diagnostic-source/opponents.json'].map(f=>[f,hash(f)])),
  code:Object.fromEntries(['src/defense_scoreboard.js','src/statistical_summary.js','scripts/defense_scoreboard.js'].map(f=>[f,hash(f)]))};
const stem='reports/defense-a/scoreboard-'+(output??runs[0].preset??'custom');fs.mkdirSync(new URL('../reports/defense-a/',import.meta.url),{recursive:true});
fs.writeFileSync(new URL('../'+stem+'.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
const f=n=>Number.isFinite(n)?n.toFixed(3):'—';
const md=['# A1計分板：'+result.preset,'',result.definitions.means,result.definitions.crossTeam,result.definitions.errors,'',
  '| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |',
  '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
  ...SCOREBOARD_KEYS.map(k=>{const m=result.metrics[k];return '| '+k+' | '+[m.simulatedPooled,m.observedPooled,m.bias,m.correlation,m.simulatedSD,m.observedSD,m.sdRatio,m.slope,m.centeredMAE,m.centeredRMSE].map(f).join(' | ')+' |';}),'',
  `期望勝場MAE ${f(result.wins.expectedMAE)}；單seed範圍 ${result.wins.singleMAERange.map(f).join('–')}；每分淨勝分勝場斜率 ${f(result.wins.winPerNet)}（真實${f(result.games.observed.winPerNet)}）。`,'',
  '| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |','|---|---:|---:|---:|---:|---:|---:|',
  '| 真實 | '+['marginSD','residualSD','closeShare','blowoutShare','winPerNet'].map(k=>f(result.games.observed[k])).join(' | ')+' | — |',
  ...result.games.single.map(s=>'| '+s.seed+' | '+['marginSD','residualSD','closeShare','blowoutShare','winPerNet','winMAE'].map(k=>f(s[k])).join(' | ')+' |'),'','## 進攻偏差（僅記錄）','',
  '| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |','|---|---:|---:|---:|',
  ...result.teams.slice().sort((a,b)=>b.offenseCenteredError-a.offenseCenteredError).map(t=>`| ${t.name} | ${f(t.offensiveRatingProxy)} | ${f(t.observed.offensiveRatingProxy)} | ${f(t.offenseCenteredError)} |`),'',
  '同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。',''].join('\n');
fs.writeFileSync(new URL('../'+stem+'.md',import.meta.url),md);console.log(stem);

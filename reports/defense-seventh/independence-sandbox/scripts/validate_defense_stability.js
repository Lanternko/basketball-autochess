import fs from 'node:fs';
import assert from 'node:assert/strict';
import {runDefenseSeason} from '../src/defense_validation.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {loadDefenseInputs,summarizeDefenseRun,saveDefenseSeason,hash,codeFiles,read} from './defense_io.js';
const inputs=loadDefenseInputs(),calibration=read('reports/defense-calibration.json');
for(const [f,h] of Object.entries(calibration.provenance.code))assert.equal(hash(f),h,'Stale normal-rotation calibration');
for(const [k,value] of Object.entries(calibration.selected))assert.equal(NBA_DEFENSE_V1[k],value);
const configs=[
  {id:'reference',label:'正常輪替，舊犯規抽樣',options:{...NBA_DEFENSE_V1,foulConditioning:false}},
  {id:'corrected',label:'正常輪替，修正犯規抽樣',options:{...NBA_DEFENSE_V1}},
  {id:'control',label:'固定曝光診斷',options:{...NBA_DEFENSE_V1,minuteMode:'budget',foulOut:99}}
];
const runs=[];
for(const seed of [20261012,20261013,20261014,20261015]){
  for(const config of configs){
    console.log(config.id+' seed '+seed);
    const run=runDefenseSeason(inputs.league,inputs.exposure,{seed,options:{...config.options,stealPriorRate:inputs.priorRate},replay:config.id==='corrected',
      onProgress:n=>console.log(config.id+' '+seed+' '+n+'/1230')});
    let artifact;
    if(config.id==='corrected')artifact=saveDefenseSeason(run,inputs,'scripts/validate_defense_stability.js');
    const summary=summarizeDefenseRun(run,inputs);runs.push({seed,id:config.id,label:config.label,options:run.options,summary,artifact});
    console.log(JSON.stringify({seed,version:config.id,FG:summary.global.fg,PPG:summary.global.ppg,STL:summary.global.steals,
      defensiveMAE:summary.defensiveRatingMAE,OKC:summary.teams.find(t=>t.id===1610612760).wins}));
  }
  const old=runs.find(r=>r.seed===seed&&r.id==='reference'),updated=runs.find(r=>r.seed===seed&&r.id==='corrected');
  assert.ok(updated.summary.global.fg<old.summary.global.fg,'Recorded FG conditioning must lower inflation');
  assert.ok(Math.abs(updated.summary.global.fg-inputs.target.fg)<Math.abs(old.summary.global.fg-inputs.target.fg),'FG correction should improve accuracy on independent seeds');
}
const result={schemaVersion:1,scope:'Four-seed full-league retrospective stability, not held-out-data accuracy. Identical normal rotation/foul rules compare the shooting correction; synthetic exposure mode is separate.',
  target:inputs.target,runs,provenance:{code:Object.fromEntries([...codeFiles,'scripts/validate_defense_stability.js'].map(f=>[f,hash(f)])),
    sources:Object.fromEntries(['data/season-league.json','data/defense-source/game-exposure.json','reports/defense-calibration.json'].map(f=>[f,hash(f)]))}};
fs.writeFileSync(new URL('../reports/defense-stability.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
const f=n=>Number.isFinite(n)?n.toFixed(2):'—';
const md=['# 防守v1多seed比較','',
  '四組seed、三種條件，每組都是完整1230場／30隊各82場。正常輪替兩版本都使用官方先發與逐場分鐘軟目標、場內疲勞及六犯離場；只有犯規抽樣開關不同。第三種固定曝光條件允許合成換人與停用犯滿，不能直接當真實NBA輪替。','',
  '**新seed只驗證隨機穩定性；建卡仍用同季資料，尚非資料外預測。** 分區情境係數由另一seed的123場FG%、3P%及球權代理誤差選定；時鐘依球權代理選定，勝場不進入選擇。','',
  '| seed | 版本 | FG% | 3P% | 2P% | PPG | STL/G | 球權代理/G | 防守效率代理MAE | 勝場MAE | 雷霆勝場 | 球員PTS36 MAE | 分鐘MAE |',
  '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
  ...runs.map(r=>{const s=r.summary;return `| ${r.seed} | ${r.label} | ${[s.global.fg,s.global.three,s.global.two,s.global.ppg,s.global.steals,s.global.possessionsProxy,s.defensiveRatingMAE,s.winMAE,s.teams.find(t=>t.id===1610612760).wins,s.playerPTS36MAE,s.meanMinuteMAE].map(f).join(' | ')} |`;}),'',
  `真實：FG% ${f(inputs.target.fg)}、3P% ${f(inputs.target.three)}、2P% ${f(inputs.target.two)}、PPG ${f(inputs.target.ppg)}、STL/G ${f(inputs.target.steals)}、球權代理/G ${f(inputs.target.possessionsProxy)}；雷霆64勝。`,'',
  '防守效率代理用雙方FGA−OREB+TOV+0.44FTA平均，不等於官方DefRtg。球員PTS36至少1000真實分鐘；分鐘MAE含模擬與真實延長賽差異。','',
  '正常輪替的修正版已保存四份完整賽季報告，包含全部球員正負值：',
  ...runs.filter(r=>r.id==='corrected').map(r=>`- [seed ${r.seed}](nba-defense-v1-seed${r.seed}.md)`),'',
  '完整來源、程式雜湊及30隊指標見 [JSON](defense-stability.json)。`npm run validate:defense-stability` 重跑。',''].join('\n');
fs.writeFileSync(new URL('../reports/defense-stability.md',import.meta.url),md);
console.log('Saved defense-stability.md/json');

import fs from 'node:fs';
import crypto from 'node:crypto';
import {defensiveMeasurements,runDefenseSeason,teamDefenseMetrics,globalDefenseMetrics,realCountStats} from '../src/defense_validation.js';

const read=file=>JSON.parse(fs.readFileSync(new URL('../'+file,import.meta.url)));
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+file,import.meta.url))).digest('hex');
const table=file=>{const set=read(file).data.resultSets[0];return set.rowSet.map(r=>Object.fromEntries(set.headers.map((k,i)=>[k,r[i]])));};
const rawLeague=read('data/season-league.json'),exposure=read('data/defense-source/game-exposure.json');
if(exposure.games.length!==1230||new Set(exposure.games.map(g=>g.id)).size!==1230)throw new Error('Incomplete exposure data');
for(const s of exposure.sources)if(hash('data/'+s.file)!==s.sha256)throw new Error('Changed official source '+s.file);
const baseline=read('reports/nba-season-2025-26-seed20261012.json');
if(hash('data/season-league.json')!==baseline.provenance.leagueSha256)throw new Error('Stale baseline league');
for(const [file,h] of Object.entries(baseline.provenance.codeHashes))if(hash(file)!==h)throw new Error('Changed baseline code '+file);
const {league,priorRate}=defensiveMeasurements(rawLeague,table('data/benchmark-source/base.json'));
const realTeams=table('data/benchmark-source/teams.json'),opponents=new Map(table('data/diagnostic-source/opponents.json').map(t=>[t.TEAM_ID,t]));
const advanced=new Map(table('data/defense-source/advanced-teams.json').map(t=>[t.TEAM_ID,t]));
const real=realTeams.map(t=>({id:t.TEAM_ID,name:t.TEAM_NAME,wins:t.W,
  ...teamDefenseMetrics(realCountStats(t),realCountStats(opponents.get(t.TEAM_ID),'OPP_')),
  officialDefensiveRating:advanced.get(t.TEAM_ID).DEF_RATING,officialPossessionsPerGame:advanced.get(t.TEAM_ID).POSS/82}));
const totalReal=realTeams.map(t=>realCountStats(t)),sum=key=>totalReal.reduce((n,t)=>n+t[key],0),totals=Object.fromEntries(Object.keys(totalReal[0]).map(k=>[k,sum(k)]));
const target=teamDefenseMetrics(totals,totals,2460);
const paceCalibration=read('reports/defense-pace-calibration.json');
for(const [f,h] of Object.entries(paceCalibration.provenance.codeHashes))if(hash(f)!==h)throw new Error('Stale pace probe; rerun calibrate:defense-pace');
const common={stealPriorRate:priorRate,touchLiveShare:.5};
const budget={...common,minuteMode:'budget',foulOut:99};
const configs=[
  {id:'legacy',label:'原引擎',options:{...common}},
  {id:'minutes',label:'固定分鐘與官方先發',options:{...budget}},
  {id:'split',label:'＋失誤／抄截拆解',options:{...budget,turnoverMode:'split'}},
  {id:'pressure',label:'＋獨立失誤壓迫訊號',options:{...budget,turnoverMode:'pressure'}},
  {id:'foul',label:'＋修正犯規與FGA條件機率',options:{...budget,turnoverMode:'pressure',foulConditioning:true}},
  {id:'context-off',label:'關閉直接命中情境加成',options:{...budget,turnoverMode:'pressure',foulConditioning:true,contextScale:0}},
  {id:'volume',label:'＋實際出手量角色權重',options:{...budget,turnoverMode:'pressure',foulConditioning:true,shotSelection:'volume'}},
  {id:'paced',label:'＋球權代理校準時鐘',options:{...budget,turnoverMode:'pressure',foulConditioning:true,shotSelection:'volume',pace:paceCalibration.selectedPace}}
];
const mean=xs=>xs.reduce((n,x)=>n+x,0)/xs.length;
const correlation=(a,b)=>{
  const am=mean(a),bm=mean(b),num=a.reduce((n,x,i)=>n+(x-am)*(b[i]-bm),0);
  return num/Math.sqrt(a.reduce((n,x)=>n+(x-am)**2,0)*b.reduce((n,x)=>n+(x-bm)**2,0));
};
const rank=xs=>xs.map(x=>xs.filter(y=>y<x).length+(xs.filter(y=>y===x).length-1)/2);
const summaries=[];
fs.mkdirSync(new URL('../reports/defense-runs/',import.meta.url),{recursive:true});
for(const config of configs){
  console.log('Run '+config.id);
  const run=runDefenseSeason(league,exposure,{seed:20261012,options:config.options,baseline:config.id==='legacy'?baseline:null,
    replay:config.id==='paced',onProgress:n=>console.log(config.id+' '+n+'/1230')});
  const file='reports/defense-runs/'+config.id+'-seed20261012.json';
  fs.writeFileSync(new URL('../'+file,import.meta.url),JSON.stringify(run)+'\n');
  const rows=run.teams.map(t=>{const actual=real.find(r=>r.id===t.id);return {id:t.id,name:t.name,wins:t.wins,observedWins:actual.wins,
    ...teamDefenseMetrics(t.stats,t.opponent),minuteMAE:t.minuteError/t.playerGames,regulationTargetMAE:t.regulationMinuteError/t.playerGames,
    observed:actual};});
  summaries.push({...config,file,sha256:hash(file),seed:run.seed,global:globalDefenseMetrics(run),
    meanMinuteMAE:mean(rows.map(r=>r.minuteMAE)),meanRegulationTargetMAE:mean(rows.map(r=>r.regulationTargetMAE)),
    defensiveRatingMAE:mean(rows.map(r=>Math.abs(r.defensiveRatingProxy-r.observed.defensiveRatingProxy))),
    winMAE:mean(rows.map(r=>Math.abs(r.wins-r.observedWins))),
    defensiveRankCorrelation:correlation(rank(rows.map(r=>r.defensiveRatingProxy)),rank(rows.map(r=>r.observed.defensiveRatingProxy))),teams:rows});
  const okc=rows.find(r=>r.id===1610612760);
  console.log(JSON.stringify({version:config.id,FG:summaries.at(-1).global.fg,three:summaries.at(-1).global.three,STL:summaries.at(-1).global.steals,OKC:okc.wins,defMAE:summaries.at(-1).defensiveRatingMAE}));
}
const sourceFiles=['data/season-league.json','data/defense-source/game-exposure.json','data/diagnostic-source/opponents.json','data/benchmark-source/base.json','data/benchmark-source/teams.json','data/defense-source/advanced-teams.json','reports/defense-pace-calibration.json'];
const codeFiles=['src/defense_game.js','src/defense_probability.js','src/minute_budget.js','src/defense_validation.js','src/replay_accounting.js','src/probability_model.js','src/constants.js','src/rebound_block_model.js','src/rng.js','scripts/validate_defense.js'];
const result={schemaVersion:1,season:'2025-26',baselineSeed:20261012,
  scope:'First defense intervention batch. Same-season retrospective diagnostic, not independent prediction or calibrated player OVR. New model opt-in; original remains unchanged.',
  limitations:['Exact exposure uses a synthetic minute decomposition, not observed substitutions. Diagnostic budget mode permits live-clock substitutions and disables foul-out (foulOut=99).',
    'Observed OT minutes are normalized to regulation 240 player-minutes; simulated OT is additional. Exact regulation targets are quantized to 0.1 seconds.',
    'Split-only steals reclassify existing turnovers; no new possessions, fast-break state, or additional turnover pressure. Pressure is a separate intervention.',
    'Defensive-rating proxy uses both teams FGA - OREB + TOV + .44 FTA; not official NBA possession tracking. Same proxy applied to actual and simulated rows.',
    'Full-season abilities, rates and observed minutes are known. No held-out data validation. One full-season seed per ablation.'],
  provenance:{sources:Object.fromEntries(sourceFiles.map(p=>[p,hash(p)])),code:Object.fromEntries(codeFiles.map(p=>[p,hash(p)])),officialSources:exposure.sources},
  parameters:{stealPriorRate:priorRate,touchLiveShare:.5,pressurePriorMinutes:240,pressureCoefficient:.35,pace:paceCalibration.selectedPace},target,real,variants:summaries};
fs.writeFileSync(new URL('../reports/defense-validation.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
const f=n=>Number.isFinite(n)?n.toFixed(2):'—';
const md=['# 防守第一批修正：30隊控制實驗','',result.scope,'',
  '**這是同季回溯診斷，實驗版本尚未成為預設引擎。** 固定分鐘模式只固定曝光量：官方先發、G/F/C或PG/SG/SF/PF/C位置與逐場秒數來自1230份官方box score，換人時段為合成排程，不是真實輪替。為維持曝光，允許非死球換人並停用犯滿離場。','',
  '原版本逐場比分與原1230場基準完全一致。抄截拆解使用獨立記帳亂數；不新增失誤，也不新增反擊收益。每場驗證得分、分鐘、正負值（啟用重播時）、分區投籃與失誤／抄截守恆。','',
  '時鐘pace只以123場、另一seed的球權代理誤差選擇；不使用勝場或雷霆表現選參數。這仍使用同季整季建卡資料，不能稱為資料外預測。','',
  '## 聯盟平均與全隊誤差','',
  '| 版本 | FG% | 3P% | 2P% | PPG | STL/G | TOV/G | FTA/G | 球權代理/G | 防守效率代理MAE | 防守排序相關 | 勝場MAE |',
  '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
  `| 真實 | ${[target.fg,target.three,target.two,target.ppg,target.steals,target.turnovers,target.fta,target.possessionsProxy].map(f).join(' | ')} | — | — | — |`,
  ...summaries.map(v=>`| ${v.label} | ${[v.global.fg,v.global.three,v.global.two,v.global.ppg,v.global.steals,v.global.turnovers,v.global.fta,v.global.possessionsProxy,v.defensiveRatingMAE,v.defensiveRankCorrelation,v.winMAE].map(f).join(' | ')} |`),'',
  '效率代理分母為雙方box score估計球權的平均，真實與模擬使用相同估計式；不是NBA官方DefRtg。JSON另保存官方DefRtg與POSS作參考。勝場不是校準目標。','',
  '## 犯規與記帳命中率','',
  '真實FG%不包含被犯規而投失的出手。原引擎先以FG%抽命中，再排除犯規投失，會再次條件化並灌高FG%。新開關用 raw = recorded × (1 − foul) / (1 − recorded × foul) 校正抽樣，且保留可獨立比較的舊路徑。單元測試驗證逆變換。','',
  '| 版本 | 記帳FG% | 出手時輸入命中機率平均 | 逐場分鐘MAE | 正規時間目標分鐘MAE |','|---|---:|---:|---:|---:|',
  ...summaries.map(v=>`| ${v.label} | ${[v.global.fg,v.global.expectedFG,v.meanMinuteMAE,v.meanRegulationTargetMAE].map(f).join(' | ')} |`),'',
  '逐場分鐘MAE使用原始官方分鐘，包含真實與模擬延長賽不同造成的差異；正規時間目標MAE比較規格化到240分鐘的曝光量。','',
  '## 雷霆','',
  '| 版本 | 勝場 | PPG | 對手PPG | 對手2P% | 對手3P% | STL/G | 迫使TOV/G | 防守效率代理 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|',
  `| 真實 | ${[real.find(t=>t.id===1610612760).wins,...['ppg','opponentPPG','opponentTwo','opponentThree','steals','forcedTurnovers','defensiveRatingProxy'].map(k=>real.find(t=>t.id===1610612760)[k])].map(f).join(' | ')} |`,
  ...summaries.map(v=>{const t=v.teams.find(t=>t.id===1610612760);return `| ${v.label} | ${[t.wins,t.ppg,t.opponentPPG,t.opponentTwo,t.opponentThree,t.steals,t.forcedTurnovers,t.defensiveRatingProxy].map(f).join(' | ')} |`;}),'',
  '## 30隊：原版本／最後一項實驗／真實','',
  '| 球隊 | 勝場 原/新/真 | 防守效率代理 原/新/真 | 對手2P% 原/新/真 | 對手3P% 原/新/真 |','|---|---:|---:|---:|---:|',
  ...real.map(r=>{const a=summaries[0].teams.find(t=>t.id===r.id),b=summaries.at(-1).teams.find(t=>t.id===r.id);
    return `| ${r.name} | ${[a.wins,b.wins,r.wins].map(f).join(' / ')} | ${[a.defensiveRatingProxy,b.defensiveRatingProxy,r.defensiveRatingProxy].map(f).join(' / ')} | ${[a.opponentTwo,b.opponentTwo,r.opponentTwo].map(f).join(' / ')} | ${[a.opponentThree,b.opponentThree,r.opponentThree].map(f).join(' / ')} |`;}),'',
  '## 尚未完成','',
  '- 真實換人區段與活球失誤分類，完整反擊狀態、護框／區域口徑對齊及陣容責任模型。',
  '- 多seed與資料外驗證；本批只能定位機制偏差，不支持把球員正負值殘差直接修成OVR。','',
  '完整指標、參數、30隊及來源／程式雜湊見 [JSON](defense-validation.json)。重跑 `npm run validate:defense`；資料抓取 `npm run defense:fetch`，已取得資料可離線驗證。',''].join('\n');
fs.writeFileSync(new URL('../reports/defense-validation.md',import.meta.url),md);
console.log('Saved defense-validation.md/json');

import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { simulateGame } from '../src/simulation_engine.js';
import { BASELINE, TEAMS } from '../src/teams.js';

// Synthetic benches exercise rotation; never present these as real NBA rosters.
const fixture={name:'Synthetic equal-strength ten-player team',roster:Array.from({length:10},(_,i)=>({
  ...BASELINE.roster[i%5],name:`Synthetic ${i+1}`,targetMinutes:i<5?30:18 }))};
const n=100, games=[];
for(let i=0;i<n;i++)games.push(simulateGame(fixture,fixture,{mode:'timed',seed:20260909+i}));
const mean=values=>values.reduce((a,b)=>a+b,0)/values.length;
const sides=games.flatMap(g=>[g.statA,g.statB]);
const total=k=>sides.reduce((s,row)=>s+row[k],0);
const summary={games:n,complete:games.filter(g=>g.complete).length,
  meanPointsPerTeam:mean(sides.map(s=>s.pts)),meanStartedPossessionsPerTeam:mean(sides.map(s=>s.poss)),
  meanRebounds:mean(sides.map(s=>s.reb)),meanAssists:mean(sides.map(s=>s.ast)),
  meanTurnovers:mean(sides.map(s=>s.tov)),meanFreeThrows:mean(sides.map(s=>s.fta)),
  fgPct:total('fgm')/total('fga'),threePct:total('fg3m')/total('fg3a'),ftPct:total('ftm')/total('fta'),
  overtimeGames:games.filter(g=>g.overtimes>0).length,
  firstSideWins:games.filter(g=>g.winnerA).length,
  minScore:Math.min(...sides.map(s=>s.pts)),maxScore:Math.max(...sides.map(s=>s.pts)),
  meanPlayerMinutes:fixture.roster.map((p,i)=>({name:p.name,minutes:mean(games.map(g=>g.playersA[i].minutes))}))};
const example=simulateGame(TEAMS.GSW,TEAMS.CLE,{mode:'timed',seed:20260909,replay:true});
const data={schemaVersion:1,seedStart:20260909,label:'Structural benchmark, not NBA validation',summary,
  example:{label:'Existing historical five-player cards; no real bench',...example}};
const output=fileURLToPath(new URL('../reports/timed-benchmark.json',import.meta.url));
fs.mkdirSync(fileURLToPath(new URL('../reports/',import.meta.url)),{recursive:true});
fs.writeFileSync(output,JSON.stringify(data,null,2)+'\n');
const fmt=x=>x.toFixed(2);
const md=`# 真實時鐘模式：結構基準報告

這是 100 場合成十人隊伍的結構測試，不是 NBA 2025–26 球季驗證。兩隊能力相同，替補皆為合成資料；seed 從 20260909 起。沒有使用 Hoop Land 或 Basketball GM 引擎產生本報告。

| 項目 | 結果 |
|---|---:|
| 完成場數 | ${summary.complete}/${n} |
| 每隊平均得分 | ${fmt(summary.meanPointsPerTeam)} |
| 每隊平均開始球權數（非官方 possessions 定義） | ${fmt(summary.meanStartedPossessionsPerTeam)} |
| 每隊平均籃板 | ${fmt(summary.meanRebounds)} |
| 每隊平均助攻 | ${fmt(summary.meanAssists)} |
| 每隊平均失誤 | ${fmt(summary.meanTurnovers)} |
| 每隊平均罰球出手 | ${fmt(summary.meanFreeThrows)} |
| FG% / 3P% / FT% | ${fmt(summary.fgPct*100)} / ${fmt(summary.threePct*100)} / ${fmt(summary.ftPct*100)} |
| 延長賽場數 | ${summary.overtimeGames} |
| A 方勝場 | ${summary.firstSideWins} |
| 單隊最低／最高比分 | ${summary.minScore} / ${summary.maxScore} |

## 輪替分鐘（A 方跨場平均）

${summary.meanPlayerMinutes.map(p=>`- ${p.name}: ${fmt(p.minutes)} 分鐘`).join('\n')}

## 現有歷史卡表的完整比賽範例

GSW vs CLE，seed 20260909：${example.scoreA}–${example.scoreB}，${example.gameSeconds/60} 分鐘、${example.overtimes} 次延長賽。各隊仍只有原本五名球員，不能代表完整歷史球隊戰力；犯滿且無替補時會使用最低五人例外。逐事件與球員數據見同目錄 timed-benchmark.json。

## 解讀限制

本階段驗證時鐘、分鐘、比分、助攻、罰球與輪替的一致性。動作耗時、輪替評分、罰球籃板與犯規機率尚未校準；平均比分不可直接當成 NBA 準確度。沒有實際空間、暫停、進攻犯規、比賽中受傷與完整違例處理。既有觀戰頁仍使用短局模式；新事件格式尚未接入動畫。

重跑：npm run benchmark:timed。
`;
fs.writeFileSync(output.replace(/\.json$/,'.md'),md);
console.log(JSON.stringify(summary,null,2));

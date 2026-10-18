import fs from 'node:fs';
import {TEAMS} from '../src/teams.js';
import {buildPer36Report,renderPer36Markdown} from '../src/per36_report.js';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const refs=read('../data/reference-seasons.json'),league=read('../data/league-context.json');
const keys=['CLE','LAL','OKC','NYK'];
const run=(key,options)=>buildPer36Report(TEAMS[key],refs.teams[key],{seasonStyle:true,freeThrowStyle:true,leagueReboundShare:league.contexts.find(c=>c.season===TEAMS[key].season&&c.type==='Regular Season').orebShare,...options});
const score=rows=>rows.flatMap(r=>r.players).reduce((sum,p)=>sum+Math.abs(p.simulated.pts-p.real.pts)/3+Math.abs(p.simulated.tov-p.real.tov)/.7+Math.abs(p.simulated.fta-p.real.fta)/2+Math.abs(p.simulated.twoPct-p.real.twoPct)/.06+(p.real.fg3a>=1?Math.abs(p.simulated.threePct-p.real.threePct)/.06:0),0)/(rows.length*5);
const candidates=[];
for(const contextScale of [.5,.75,1]) for(const turnoverScale of [1,1.4,1.8]) {
 const rows=['CLE','LAL'].map(k=>run(k,{n:120,seed:73001,contextScale,turnoverScale}));
 const candidate={contextScale,turnoverScale,score:score(rows)}; candidates.push(candidate);console.log(JSON.stringify(candidate));
}
candidates.sort((a,b)=>a.score-b.score);const best=candidates[0];
const rows=keys.map(k=>{const r=run(k,{n:1000,seed:20260909,contextScale:best.contextScale,turnoverScale:best.turnoverScale});console.log('validated',k,r.teamResult.pointsPer36);return r;});
const metrics=['pts','oreb','dreb','reb','tov','fta','stl','blk','twoPct','threePct','ftPct'];
const old=read('../reports/per36.json').filter(r=>rows.some(n=>n.team===r.team));
const mae=(rs,k)=>{const ps=rs.flatMap(r=>r.players).filter(p=>Number.isFinite(p.simulated[k])&&Number.isFinite(p.real[k])&&(k!=='threePct'||p.real.fg3a>=1));return ps.reduce((s,p)=>s+Math.abs(p.simulated[k]-p.real[k]),0)/ps.length;};
const usageMAE=rs=>rs.flatMap(r=>r.players).reduce((s,p)=>s+Math.abs(p.error.usageProxyPercentagePoints),0)/(rs.length*5);
const lines=['# 四隊校準實驗結果','', '採用判斷：失誤與FTA改善，但得分誤差未通過不退步條件；不升為正式預設。此為實驗設定，未套用正式卡表。固定全70對手，不是球隊PR50；疲勞關閉。','', '以CLE/LAL各120場比較9組共用係數；以新seed各1000場重跑四隊。OKC/NYK未參與係數選擇，但所有球員出手／罰球傾向均來自同季資料，不能稱為獨立賽季預測。','', '最佳參數：情境加成倍率 '+best.contextScale+'；持球失誤倍率 '+best.turnoverScale+'。罰球命中率曲線不變，FTA/FGA作兩罰事件先驗；尚無and-one、三罰、罰球籃板。','', '| 全20人MAE | 舊版 | 實驗 |','|---|---:|---:|',...metrics.map(k=>'| '+k+' | '+mae(old,k).toFixed(3)+' | '+mae(rows,k).toFixed(3)+' |'),'| usage代理(pp) | '+usageMAE(old).toFixed(3)+' | '+usageMAE(rows).toFixed(3)+' |','','三分命中率僅納入真實per36至少1次三分出手者；率類誤差以0–1表示。舊版與新驗證seed不同，差異包含抽樣誤差。','', ...['訓練隊 CLE/LAL','未參與選參 OKC/NYK'].map((label,i)=>label+'：綜合誤差 '+score(rows.filter(r=>keys.slice(i*2,i*2+2).some(k=>TEAMS[k].name===r.team))).toFixed(3)),''];
fs.writeFileSync(new URL('../reports/four-team-calibration.json',import.meta.url),JSON.stringify({candidates,best,reports:rows},null,2));
fs.writeFileSync(new URL('../reports/four-team-calibration.md',import.meta.url),lines.join('\n')+'\n'+renderPer36Markdown(rows));

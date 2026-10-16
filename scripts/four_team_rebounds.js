import fs from 'node:fs';
import { TEAMS } from '../src/teams.js';
import { buildPer36Report, renderPer36Markdown } from '../src/per36_report.js';
const refs=JSON.parse(fs.readFileSync(new URL('../data/reference-seasons.json',import.meta.url)));
const league=JSON.parse(fs.readFileSync(new URL('../data/league-context.json',import.meta.url)));
const before=JSON.parse(fs.readFileSync(new URL('../reports/per36.json',import.meta.url)));
const style=process.argv.includes('--season-style');
const reports=[];
for(const key of ['CLE','OKC','NYK','LAL']) {
 const team=TEAMS[key], context=league.contexts.find(c=>c.season===team.season&&c.type==='Regular Season');
 if(!context) throw new Error('Missing league season '+team.season);
 const report=buildPer36Report(team,refs.teams[key],{n:1000,seed:20260908,seasonStyle:style,leagueReboundShare:context.orebShare});
 report.leagueSource=context.sources.base;
 reports.push(report);
 console.log(key,report.teamResult.pointsPer36.toFixed(2));
}
const metrics=['pts','oreb','dreb','reb','tov'];
const mae=(rows,k)=>rows.flatMap(r=>r.players).reduce((s,p)=>s+Math.abs(p.simulated[k]-p.real[k]),0)/(rows.length*5);
const old=before.filter(r=>reports.some(n=>n.team===r.team));
const lines=[style ? '# 四隊個人出手傾向實驗' : '# 四隊籃板比例校準','', '固定全屬性70基準，不代表聯盟平均實力；每隊1000場、相同seed、疲勞關閉。舊報表保留不覆蓋。','',
 '球員籃板比例來自同季聯盟 OREB / (OREB + DREB)，包含罰球籃板，因此只作目前 live-FG 模型的近似基準。位置／落點／能力影響相對爭搶機率；尚未模擬衝搶後快攻的代價。','',
 '| 指標 MAE | 修改前 | 修改後 |','|---|---:|---:|',...metrics.map(k=>'| '+k+' | '+mae(old,k).toFixed(3)+' | '+mae(reports,k).toFixed(3)+' |'),''];
if(style) lines.push('實驗使用同季 FG3A/FGA 作為三分出手先驗，不是獨立驗證；命中曲線、罰球、失誤及球權公式未改。只啟用於這份報表，未套用遊戲卡表。','');
for(const r of reports) lines.push(r.team+'：聯盟進攻籃板基準 '+(r.leagueReboundShare*100).toFixed(2)+'%。[NBA來源]('+r.leagueSource.url+')','');
fs.writeFileSync(new URL(style ? '../reports/four-team-shot-style.json' : '../reports/four-team-rebounds.json',import.meta.url),JSON.stringify(reports,null,2));
fs.writeFileSync(new URL(style ? '../reports/four-team-shot-style.md' : '../reports/four-team-rebounds.md',import.meta.url),lines.join('\n')+'\n'+renderPer36Markdown(reports));

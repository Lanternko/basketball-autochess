import fs from 'node:fs';
import crypto from 'node:crypto';
import {simulateSeason} from '../src/season_simulation.js';

const args=process.argv.slice(2);
if (args.some((a,i)=>a!=='--seed'&&args[i-1]!=='--seed')||args.filter(a=>a==='--seed').length>1) throw new Error('Usage: node scripts/simulate_season.js [--seed INTEGER]');
const seed=args.includes('--seed')?Number(args[args.indexOf('--seed')+1]):20261012;
const file=new URL('../data/season-league.json',import.meta.url);
const bytes=fs.readFileSync(file),league=JSON.parse(bytes);
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
for (const source of league.sources) if (sha(fs.readFileSync(new URL('../data/'+source.file,import.meta.url)))!==source.sha256) throw new Error('Stale league snapshot: '+source.file);
const base=new URL(`../reports/nba-season-2025-26-seed${seed}`,import.meta.url);
fs.mkdirSync(new URL('../reports/',import.meta.url),{recursive:true});
const boxes=new URL(base.href+'-games.jsonl'),partial=new URL(boxes.href+`.partial-${process.pid}`);
const descriptor=fs.openSync(partial,'w');
let report;
try {
  report=simulateSeason(league,{seed,
    onGame:game=>fs.writeSync(descriptor,JSON.stringify(game)+'\n'),
    onProgress:(n,total)=>console.log(`Season ${n}/${total}`)});
} finally {fs.closeSync(descriptor);}
fs.renameSync(partial,boxes);
report.provenance={leagueSha256:sha(bytes),sources:league.sources,methodology:league.methodology,
  boxScoresSha256:sha(fs.readFileSync(boxes)),codeHashes:Object.fromEntries([
    'src/season_simulation.js','src/simulation_engine.js','src/timed_game.js','src/probability_model.js',
    'src/rebound_block_model.js','src/constants.js','src/rng.js','scripts/build_season_league.js','scripts/simulate_season.js'
  ].map(p=>[p,sha(fs.readFileSync(new URL('../'+p,import.meta.url)))]))};
const references=new Map(league.teams.map(t=>[t.id,t]));
const pct=(m,a)=>a?100*m/a:null;
report.comparison=report.standings.map(t=>{
  const r=references.get(t.id).observed;
  return {id:t.id,name:t.name,conference:references.get(t.id).conference,
    wins:t.wins,observedWins:r.W,winDelta:t.wins-r.W,
    simulatedPPG:t.pointsFor/82,observedPPG:r.PTS/82,
    simulatedOpponentPPG:t.pointsAgainst/82,observedOpponentPPG:(r.PTS-r.PLUS_MINUS)/82,
    simulatedFGPct:pct(t.stats.fgm,t.stats.fga),observedFGPct:pct(r.FGM,r.FGA),
    simulatedThreePct:pct(t.stats.fg3m,t.stats.fg3a),observedThreePct:pct(r.FG3M,r.FG3A)};
});
const mean=xs=>xs.reduce((n,x)=>n+x,0)/xs.length;
const sides=report.standings;
report.summary={games:report.matches.length,completed:report.matches.length,
  wins:sides.reduce((n,t)=>n+t.wins,0),losses:sides.reduce((n,t)=>n+t.losses,0),
  overtimeGames:report.matches.filter(g=>g.overtimes>0).length,
  meanPointsPerTeamGame:mean(sides.map(t=>t.pointsFor/82)),
  meanStartedPossessionsPerTeamGame:mean(sides.map(t=>t.stats.poss/82)),
  meanReboundsPerTeamGame:mean(sides.map(t=>(t.stats.oreb+t.stats.dreb)/82)),
  meanAssistsPerTeamGame:mean(sides.map(t=>t.stats.ast/82)),
  meanTurnoversPerTeamGame:mean(sides.map(t=>t.stats.tov/82)),
  meanFreeThrowAttemptsPerTeamGame:mean(sides.map(t=>t.stats.fta/82)),
  fgPct:pct(sides.reduce((n,t)=>n+t.stats.fgm,0),sides.reduce((n,t)=>n+t.stats.fga,0)),
  threePct:pct(sides.reduce((n,t)=>n+t.stats.fg3m,0),sides.reduce((n,t)=>n+t.stats.fg3a,0)),
  winMAE:mean(report.comparison.map(t=>Math.abs(t.winDelta))),
  ppgMAE:mean(report.comparison.map(t=>Math.abs(t.simulatedPPG-t.observedPPG))),
  interpretation:'One realized simulated season using same-season ability, tendencies and observed participant pools. Comparison errors are descriptive, not held-out prediction scores.'};
report.observedPlayers=league.teams.flatMap(t=>t.roster.map(p=>({teamId:t.id,playerId:p.playerId,...p.observed})));
fs.writeFileSync(new URL(base.href+'.json'),JSON.stringify(report,null,2)+'\n');
const f=x=>x===null?'—':x.toFixed(2);
const standings=report.standings.map((t,i)=>{
  const c=report.comparison.find(r=>r.id===t.id);
  return `| ${i+1} | ${t.name} | ${c.conference} | ${t.wins}–${t.losses} | ${t.homeWins}–${t.homeGames-t.homeWins} | ${t.awayWins}–${t.awayGames-t.awayWins} | ${t.neutralWins}–${t.neutralGames-t.neutralWins} | ${c.observedWins}–${82-c.observedWins} | ${c.winDelta>0?'+':''}${c.winDelta} | ${f(c.simulatedPPG)} / ${f(c.observedPPG)} | ${f(c.simulatedOpponentPPG)} / ${f(c.observedOpponentPPG)} |`;
});
const leaders=report.players.filter(p=>p.games>=20).sort((a,b)=>b.stats.pts/b.games-a.stats.pts/a.games).slice(0,20);
const md=[`# NBA 2025–26：30 隊 × 82 場回溯賽季模擬`,'',
  `seed=${seed}。使用官方實際賽程、${report.validation.uniquePlayers} 位球員、${report.validation.playerCards} 個球員在隊版本；完成 ${report.summary.completed}/1230 場，每隊82場。${report.validation.neutralGames} 場中立場另計，不強制41主場與41客場。NBA Cup冠軍賽、附加賽及季後賽不納入。`,'',
  '**此為回溯條件模擬，不是賽前預測或獨立準確度驗證。** 能力和出手傾向使用整季資料；每場只使用官方紀錄中實際出賽的球員。已知交易／缺席因此反映在候選池，但沒有DNP替補、官方先發或逐場傷病決策。分鐘目標採在隊整季MPG，重新分配240分鐘；沒有輸入該場真實分鐘或比分。','',
  '時鐘使用現有 timed-v1，含四節／延長賽、疲勞、輪替及犯規。未將固定五人的 stable-v1 強行套入；目前缺少主場優勢、跨場疲勞、旅行與暫停模型。四項未量測能力設70，缺防守tracking者另標記中性先驗。排名同勝場按分差與球隊ID排序，不是NBA季後賽種子或正式同戰績規則。','',
  '| 檢查 / 統計 | 結果 |','|---|---:|',
  `| 完成場數 | ${report.summary.completed} |`,`| 總勝 / 總敗 | ${report.summary.wins} / ${report.summary.losses} |`,
  `| 球員／球隊記帳、五人分鐘、節數比分守恆 | 全場通過 |`,
  `| 每隊每場平均得分 | ${f(report.summary.meanPointsPerTeamGame)} |`,
  `| 每隊每場開始球權數（非官方possessions） | ${f(report.summary.meanStartedPossessionsPerTeamGame)} |`,
  `| 每隊每場籃板 / 助攻 / 失誤 | ${f(report.summary.meanReboundsPerTeamGame)} / ${f(report.summary.meanAssistsPerTeamGame)} / ${f(report.summary.meanTurnoversPerTeamGame)} |`,
  `| FG% / 3P% | ${f(report.summary.fgPct)} / ${f(report.summary.threePct)} |`,
  `| 延長賽場數 | ${report.summary.overtimeGames} |`,
  `| 與同季真實勝場的MAE | ${f(report.summary.winMAE)} 場 |`,
  `| 與同季真實場均得分的MAE | ${f(report.summary.ppgMAE)} 分 |`,'',
  '## 30隊戰績與同季描述比較','',
  '| 排序 | 球隊 | 分區 | 模擬W–L | 主場W–L | 客場W–L | 中立W–L | 真實W–L | 勝場差 | 場均得分 模/真 | 場均失分 模/真 |',
  '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|',...standings,'',
  '## 模擬得分榜（至少20場有上場分鐘）','',
  '| 球員 | 上場數 | 候選場數 | MPG | PPG | RPG | APG |','|---|---:|---:|---:|---:|---:|---:|',
  ...leaders.map(p=>`| ${p.name} | ${p.games} | ${p.eligibleGames} | ${f(p.stats.seconds/60/p.games)} | ${f(p.stats.pts/p.games)} | ${f((p.stats.oreb+p.stats.dreb)/p.games)} | ${f(p.stats.ast/p.games)} |`),'',
  '交易球員跨隊統計按player ID合併；完整JSON另保存各在隊版本。候選場数是實際出賽紀錄的場數；模擬輪替未必讓每位候選都上場，因此模擬GP可能較少。','',
  '## 重跑及完整輸出','',
  '`npm run season:build` 離線從'+league.sources.length+'份官方快照重建；`npm run test:season` 驗證賽程、來源與核心記帳；`npm run simulate:season -- --seed '+seed+'` 重跑。','',
  `- 完整賽季：[JSON](${base.pathname.split('/').at(-1)}.json)。包含30隊、全部球員、1230場結果與來源／程式雜湊。`,
  `- 逐場球員box score：[JSONL](${boxes.pathname.split('/').at(-1)})。每行一場。`,
  '- 一個seed只有一季，尚無重複球季區間；真實比分和戰績僅用於本報告比較，不進入引擎決策。',''].join('\n');
fs.writeFileSync(new URL(base.href+'.md'),md);
console.log(JSON.stringify(report.summary,null,2));

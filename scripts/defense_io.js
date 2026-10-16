import fs from 'node:fs';
import crypto from 'node:crypto';
import {defensiveMeasurements,realCountStats,teamDefenseMetrics,globalDefenseMetrics} from '../src/defense_validation.js';
export const read=f=>JSON.parse(fs.readFileSync(new URL('../'+f,import.meta.url)));
export const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+f,import.meta.url))).digest('hex');
export const table=f=>{const s=read(f).data.resultSets[0];return s.rowSet.map(r=>Object.fromEntries(s.headers.map((k,i)=>[k,r[i]])));};
export const codeFiles=['src/defense_game.js','src/defense_probability.js','src/defense_validation.js','src/defense_presets.js',
  'src/minute_budget.js','src/replay_accounting.js','src/probability_model.js','src/constants.js','src/rebound_block_model.js','src/rng.js','scripts/defense_io.js'];
export function loadDefenseInputs(){
  const raw=read('data/season-league.json'),exposure=read('data/defense-source/game-exposure.json');
  for(const s of [...raw.sources,...exposure.sources])if(hash('data/'+s.file)!==s.sha256)throw new Error('Stale source '+s.file);
  if(exposure.games.length!==1230)throw new Error('Incomplete exposure');
  const {league,priorRate}=defensiveMeasurements(raw,table('data/benchmark-source/base.json'));
  const opponents=new Map(table('data/diagnostic-source/opponents.json').map(t=>[t.TEAM_ID,t]));
  const actualTeams=table('data/benchmark-source/teams.json');
  const actual=actualTeams.map(t=>({id:t.TEAM_ID,name:t.TEAM_NAME,wins:t.W,
    ...teamDefenseMetrics(realCountStats(t),realCountStats(opponents.get(t.TEAM_ID),'OPP_'))}));
  const stats=actualTeams.map(t=>realCountStats(t)),all=Object.fromEntries(Object.keys(stats[0]).map(k=>[k,stats.reduce((n,t)=>n+t[k],0)]));
  return {league,exposure,priorRate,actual,target:teamDefenseMetrics(all,all,2460)};
}
export function summarizeDefenseRun(run,inputs){
  const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
  const teams=run.teams.map(t=>({id:t.id,name:t.name,wins:t.wins,losses:t.games-t.wins,
    ...teamDefenseMetrics(t.stats,t.opponent),observed:inputs.actual.find(r=>r.id===t.id),
    minuteMAE:t.minuteError/t.playerGames,regulationTargetMAE:t.regulationMinuteError/t.playerGames}));
  const errors=[];
  for(const t of run.teams)for(const p of t.players){
    const observed=inputs.league.teams.find(q=>q.id===t.id).roster.find(q=>q.playerId===p.playerId).observed;
    if(observed.MIN>=1000&&p.stats.seconds>0)errors.push(Math.abs(p.stats.pts/(p.stats.seconds/60)*36-observed.PTS/observed.MIN*36));
  }
  return {global:globalDefenseMetrics(run),defensiveRatingMAE:mean(teams.map(t=>Math.abs(t.defensiveRatingProxy-t.observed.defensiveRatingProxy))),
    winMAE:mean(teams.map(t=>Math.abs(t.wins-t.observed.wins))),playerPTS36MAE:mean(errors),meanMinuteMAE:mean(teams.map(t=>t.minuteMAE)),
    meanRegulationTargetMAE:mean(teams.map(t=>t.regulationTargetMAE)),teams};
}
export function saveDefenseSeason(run,inputs,caller='scripts/simulate_defense_season.js'){
  const summary=summarizeDefenseRun(run,inputs),file='reports/nba-defense-v1-seed'+run.seed;
  const report={schemaVersion:1,version:'nba-defense-v1',season:'2025-26',seed:run.seed,options:run.options,
    interpretation:'Same-season retrospective simulation with observed appearances, official starters and observed game minute targets. Legal dead-ball/period heuristic substitutions, six-foul disqualification, in-game fatigue. Soft minutes, not exact game exposures; no independent prediction claim.',
    provenance:{sources:Object.fromEntries(['data/season-league.json','data/defense-source/game-exposure.json','data/benchmark-source/base.json','data/diagnostic-source/opponents.json','reports/defense-calibration.json'].map(f=>[f,hash(f)])),
      code:Object.fromEntries([...codeFiles,caller].map(f=>[f,hash(f)]))},summary,
    standings:[...summary.teams].sort((a,b)=>b.wins-a.wins||(b.ppg-b.opponentPPG)-(a.ppg-a.opponentPPG)),
    accounting:run.teams,matches:run.matches};
  fs.writeFileSync(new URL('../'+file+'.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
  const f=n=>Number.isFinite(n)?n.toFixed(2):'—';
  const md=['# NBA防守v1：30隊 × 82場','',
    `seed=${run.seed}。完成1230場，各隊82場。官方逐場名單、先發／位置與分鐘目標；正常犯滿與死球／節間輪替。此模式分鐘是軟目標，不使用固定曝光診斷排程。`,'',
    '**同季回溯模擬，尚非獨立預測驗證。** 能力、抄截率、出手量與分鐘使用整季或逐場已知資料；活球失誤只有分類記帳，尚無反擊狀態。中立場保留原賽程A/B，不當作場地優勢。','',
    '| 指標 | 模擬 | 真實 |','|---|---:|---:|',
    ...[['FG%','fg'],['3P%','three'],['2P%','two'],['PPG','ppg'],['STL/G','steals'],['TOV/G','turnovers'],['FTA/G','fta'],['球權代理/G','possessionsProxy']].map(([label,k])=>`| ${label} | ${f(summary.global[k])} | ${f(inputs.target[k])} |`),'',
    `30隊防守效率代理MAE ${f(summary.defensiveRatingMAE)}；勝場MAE ${f(summary.winMAE)}。效率分母為雙方FGA−OREB+TOV+0.44FTA平均，真實與模擬同口徑，不等於官方DefRtg。`,
    `逐場分鐘MAE ${f(summary.meanMinuteMAE)}；正規時間目標MAE ${f(summary.meanRegulationTargetMAE)}。至少1000真實分鐘的球員PTS36 MAE ${f(summary.playerPTS36MAE)}。`,'',
    '| 球隊 | 模擬W–L | 真實W–L | PPG 模/真 | 失分 模/真 | 防守效率代理 模/真 |','|---|---:|---:|---:|---:|---:|',
    ...report.standings.map(t=>`| ${t.name} | ${t.wins}–${t.losses} | ${t.observed.wins}–${82-t.observed.wins} | ${f(t.ppg)} / ${f(t.observed.ppg)} | ${f(t.opponentPPG)} / ${f(t.observed.opponentPPG)} | ${f(t.defensiveRatingProxy)} / ${f(t.observed.defensiveRatingProxy)} |`),'',
    `完整球員在隊統計、正負值、逐場比分及來源／程式雜湊見 [JSON](nba-defense-v1-seed${run.seed}.json)。`,
    '`npm run simulate:season:defense -- --seed '+run.seed+'` 重跑。完整機制拆解見 [防守控制實驗](defense-validation.md) 與 [多seed比較](defense-stability.md)。',''].join('\n');
  fs.writeFileSync(new URL('../'+file+'.md',import.meta.url),md);return {file:file+'.json',sha256:hash(file+'.json')};
}

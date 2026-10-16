import fs from 'node:fs';
import crypto from 'node:crypto';
import {simulateGame} from '../src/simulation_engine.js';
import {lineupForGame} from '../src/season_simulation.js';
import {replayAccounting} from '../src/replay_accounting.js';

const read=file=>JSON.parse(fs.readFileSync(new URL('../'+file,import.meta.url)));
const table=file=>{const doc=read(file),s=doc.data.resultSets[0];return s.rowSet.map(r=>Object.fromEntries(s.headers.map((k,i)=>[k,r[i]])));};
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+file,import.meta.url))).digest('hex');
const report=read('reports/nba-season-2025-26-seed20261012.json'),league=read('data/season-league.json');
if (hash('data/season-league.json')!==report.provenance.leagueSha256) throw new Error('Stale season report');
for (const [file,h] of Object.entries(report.provenance.codeHashes)) if(hash(file)!==h)throw new Error('Stale engine: '+file);
const teams=new Map(league.teams.map(t=>[t.id,t]));
const realTeams=new Map(table('data/benchmark-source/teams.json').map(r=>[r.TEAM_ID,r]));
const realStints=new Map(league.teams.flatMap(t=>table('data/benchmark-source/team-'+t.id+'.json').map(p=>[t.id+'/'+p.PLAYER_ID,p])));
const realLogs=Map.groupBy(table('data/season-source/player-games.json'),r=>r.GAME_ID+'/'+r.TEAM_ID);
const accumulated=new Map(league.teams.map(t=>[t.id,{players:new Map(t.roster.map(p=>[p.playerId,{plusMinus:0,seconds:0}])),
  opponent:{},bench:Object.fromEntries(Array.from({length:6},(_,i)=>[i,{seconds:0,plusMinus:0,pointsFor:0,pointsAgainst:0}])),
  shai:{on:{seconds:0,plusMinus:0},off:{seconds:0,plusMinus:0}}}]));
for (const [i,fixture] of league.schedule.entries()) {
  const pair=[lineupForGame(teams.get(fixture.homeId),fixture.homePlayerIds),lineupForGame(teams.get(fixture.awayId),fixture.awayPlayerIds)];
  const game=simulateGame(...pair,{mode:'timed',seed:report.matches[i].seed,replay:true});
  if (game.scoreA!==report.matches[i].homeScore||game.scoreB!==report.matches[i].awayScore) throw new Error('Replay changed outcome');
  const accounting=replayAccounting(game,pair);
  for (const side of [0,1]) {
    const row=accumulated.get(pair[side].id);
    accounting.players[side].forEach((p,j)=>{
      const total=row.players.get(pair[side].roster[j].playerId);total.plusMinus+=p.plusMinus;total.seconds+=p.seconds;
    });
    const opposite=game[side===0?'statB':'statA'];
    for (const k of ['pts','fgm','fga','fg3m','fg3a','fta','oreb','tov','stl']) row.opponent[k]=(row.opponent[k]??0)+opposite[k];
    for (const k of Object.keys(row.bench)) for (const key of Object.keys(row.bench[k])) row.bench[k][key]+=accounting.buckets[side][k][key];
    for (const k of ['on','off']) for (const key of ['seconds','plusMinus']) row.shai[k][key]+=accounting.shai[side][k][key];
  }
  if ((i+1)%200===0) console.log(`Replay accounting ${i+1}/1230`);
}
const per48=(pm,seconds)=>seconds>0?pm/seconds*2880:null;
const players=league.teams.flatMap(t=>t.roster.map(p=>{
  const actual=realStints.get(t.id+'/'+p.playerId),sim=report.standings.find(r=>r.id===t.id).players.find(r=>r.playerId===p.playerId);
  const plus=accumulated.get(t.id).players.get(p.playerId);
  const realPM=actual.PLUS_MINUS;
  const simPM48=per48(plus.plusMinus,plus.seconds),realPM48=per48(realPM,actual.MIN*60);
  return {teamId:t.id,team:t.name,playerId:p.playerId,name:p.name,observedGP:actual.GP,simulatedGP:sim.games,
    observedMinutes:actual.MIN,simulatedMinutes:plus.seconds/60,observedMPG:actual.MIN/actual.GP,simulatedMPG:plus.seconds/60/sim.games,
    observedPlusMinus:realPM,simulatedPlusMinus:plus.plusMinus,observedPM48:realPM48,simulatedPM48:simPM48,
    pmResidual48:simPM48===null||realPM48===null?null:simPM48-realPM48,
    observedPPG:actual.PTS/actual.GP,simulatedPPG:sim.stats.pts/sim.games,
    observedPTS36:actual.PTS/actual.MIN*36,simulatedPTS36:sim.stats.pts/(plus.seconds/60)*36};
}));
const okcId=1610612760, okc=report.standings.find(t=>t.id===okcId),actual=realTeams.get(okcId),op=accumulated.get(okcId).opponent;
const opponents=new Map(table('data/diagnostic-source/opponents.json').map(r=>[r.TEAM_ID,r]));
const realOp=opponents.get(okcId);
const pct=(m,a)=>100*m/a;
const sum=(rows,key)=>rows.reduce((n,r)=>n+r[key],0);
const simTotals=report.standings.map(t=>t.stats),realTotals=[...realTeams.values()];
const leagueComparison={simulatedFG:pct(sum(simTotals,'fgm'),sum(simTotals,'fga')),observedFG:pct(sum(realTotals,'FGM'),sum(realTotals,'FGA')),
  simulatedThree:pct(sum(simTotals,'fg3m'),sum(simTotals,'fg3a')),observedThree:pct(sum(realTotals,'FG3M'),sum(realTotals,'FG3A')),
  simulatedTwo:pct(sum(simTotals,'fgm')-sum(simTotals,'fg3m'),sum(simTotals,'fga')-sum(simTotals,'fg3a')),
  observedTwo:pct(sum(realTotals,'FGM')-sum(realTotals,'FG3M'),sum(realTotals,'FGA')-sum(realTotals,'FG3A')),
  simulatedSteals:sum(simTotals,'stl')/2460,observedSteals:sum(realTotals,'STL')/2460};
const okcComparison={simulatedWins:okc.wins,observedWins:actual.W,
  simulatedPPG:okc.pointsFor/82,observedPPG:actual.PTS/82,
  simulatedOpponentPPG:op.pts/82,observedOpponentPPG:realOp.OPP_PTS/82,
  simulatedSteals:okc.stats.stl/82,observedSteals:actual.STL/82,
  simulatedForcedTOV:op.tov/82,observedForcedTOV:realOp.OPP_TOV/82,
  simulatedOppFG:pct(op.fgm,op.fga),observedOppFG:pct(realOp.OPP_FGM,realOp.OPP_FGA),
  simulatedOppThree:pct(op.fg3m,op.fg3a),observedOppThree:pct(realOp.OPP_FG3M,realOp.OPP_FG3A),
  simulatedOppTwo:pct(op.fgm-op.fg3m,op.fga-op.fg3a),observedOppTwo:pct(realOp.OPP_FGM-realOp.OPP_FG3M,realOp.OPP_FGA-realOp.OPP_FG3A)};

// Paired target-minute experiment. This changes only rotation targets; it is
// not an exact-minute scheduler, and therefore cannot rule rotation out.
const experiments=[];
for (const seed of [20261012,20261013,20261014,20261015]) {
  const variants=[{label:'season-average targets',wins:0,margin:0,minuteError:0,playerGames:0},
    {label:'observed game-minute targets (soft)',wins:0,margin:0,minuteError:0,playerGames:0}];
  for (const [index,fixture] of league.schedule.entries()) {
    if (![fixture.homeId,fixture.awayId].includes(okcId)) continue;
    const pair=[lineupForGame(teams.get(fixture.homeId),fixture.homePlayerIds),lineupForGame(teams.get(fixture.awayId),fixture.awayPlayerIds)];
    const side=fixture.homeId===okcId?0:1, observed=realLogs.get(fixture.id+'/'+okcId);
    const observedMinutes=new Map(observed.map(p=>[p.PLAYER_ID,p.MIN]));
    for (const [v,variant] of variants.entries()) {
      const lineup=v===0?pair[side]:{...pair[side],roster:pair[side].roster.map(p=>({...p}))};
      if(v===1){
        let lo=0,hi=240/.0001;
        for(let n=0;n<80;n++){const scale=(lo+hi)/2;
          if(lineup.roster.reduce((s,p)=>s+Math.min(48,Math.max(.0001,observedMinutes.get(p.playerId))*scale),0)<240)lo=scale;else hi=scale;}
        for(const p of lineup.roster)p.targetMinutes=Math.min(48,Math.max(.0001,observedMinutes.get(p.playerId))*(lo+hi)/2);
      }
      const input=[...pair];input[side]=lineup;
      const game=simulateGame(...input,{mode:'timed',seed:(seed+Math.imul(index+1,7919))>>>0});
      const scored=side===0?game.scoreA:game.scoreB,allowed=side===0?game.scoreB:game.scoreA;
      variant.wins+=Number(scored>allowed);variant.margin+=scored-allowed;
      game[side===0?'playersA':'playersB'].forEach((p,i)=>{
        variant.minuteError+=Math.abs(p.minutes-observedMinutes.get(lineup.roster[i].playerId));variant.playerGames++;
      });
    }
  }
  experiments.push({seed,variants:variants.map(v=>({...v,marginPerGame:v.margin/82,minuteMAE:v.minuteError/v.playerGames}))});
  console.log('Minute target experiment',seed,variants.map(v=>v.wins));
}
const qualifiers=players.filter(p=>p.observedMinutes>=1000&&p.simulatedMinutes>=600&&Number.isFinite(p.pmResidual48));
const home=table('data/diagnostic-source/home.json'),road=table('data/diagnostic-source/road.json');
const result={schemaVersion:1,baselineSeed:report.seed,provenance:{baselineReport:hash('reports/nba-season-2025-26-seed20261012.json'),
  league:hash('data/season-league.json'),code:{'src/replay_accounting.js':hash('src/replay_accounting.js'),'scripts/diagnose_season.js':hash('scripts/diagnose_season.js')},
  diagnostics:Object.fromEntries(['opponents','home','road','cup-east','cup-west'].map(n=>[n,{url:read('data/diagnostic-source/'+n+'.json').url,sha256:hash('data/diagnostic-source/'+n+'.json')}]))},
  interpretation:'Plus-minus residuals describe model/context mismatch, not isolated player ability or causal wins. Minutes are normalized by exposure. Bench is input first-five versus reserves, not observed NBA starters.',
  league:leagueComparison,okc:okcComparison,okcPlayers:players.filter(p=>p.teamId===okcId),players,
  largestPositiveResiduals:[...qualifiers].sort((a,b)=>b.pmResidual48-a.pmResidual48).slice(0,20),
  largestNegativeResiduals:[...qualifiers].sort((a,b)=>a.pmResidual48-b.pmResidual48).slice(0,20),
  okcBench:Object.entries(accumulated.get(okcId).bench).map(([count,b])=>({reserveCount:Number(count),...b,netPer48:per48(b.plusMinus,b.seconds)})),
  okcShai:Object.entries(accumulated.get(okcId).shai).map(([status,b])=>({status,...b,netPer48:per48(b.plusMinus,b.seconds)})),
  minuteExperiments:experiments,officialLocation:league.teams.map(t=>({id:t.id,name:t.name,
    home:home.find(r=>r.TEAM_ID===t.id)?.GP??0,road:road.find(r=>r.TEAM_ID===t.id)?.GP??0,
    neutral:82-(home.find(r=>r.TEAM_ID===t.id)?.GP??0)-(road.find(r=>r.TEAM_ID===t.id)?.GP??0)}))};
fs.writeFileSync(new URL('../reports/season-diagnostics.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
const f=n=>Number.isFinite(n)?n.toFixed(2):'—';
const playerTable=ps=>['| 球員 | 球隊 | MPG 模/真 | PPG 模/真 | +/-48 模/真 | +/-48殘差 |',
  '|---|---|---:|---:|---:|---:|',...ps.map(p=>`| ${p.name} | ${p.team} | ${f(p.simulatedMPG)} / ${f(p.observedMPG)} | ${f(p.simulatedPPG)} / ${f(p.observedPPG)} | ${f(p.simulatedPM48)} / ${f(p.observedPM48)} | ${f(p.pmResidual48)} |`)];
const md=['# 賽季診斷：雷霆防守、輪替與球員正負值','',
  '同seed重播1230場，比分與原報告逐場一致。由每次得分時的場上五人計算正負值；每隊球員正負值合計等於五倍球隊分差，重播分鐘與引擎分鐘一致。','',
  '**殘差不是球員真實能力評分，也不能換算成某人造成幾場勝差。** 隊友、對手、陣容、分鐘及整體模型誤差會共同影響正負值。以下每48分鐘消除總曝光差，但沒有完成RAPM或陣容條件匹配。','',
  '| 雷霆指標 | 模擬 | 真實 |','|---|---:|---:|',
  ...[['勝場','simulatedWins','observedWins'],['PPG','simulatedPPG','observedPPG'],['對手PPG','simulatedOpponentPPG','observedOpponentPPG'],['STL/G','simulatedSteals','observedSteals'],['迫使對手TOV/G','simulatedForcedTOV','observedForcedTOV'],['對手FG%','simulatedOppFG','observedOppFG'],['對手3P%','simulatedOppThree','observedOppThree'],['對手2P%','simulatedOppTwo','observedOppTwo']].map(([label,a,b])=>`| ${label} | ${f(okcComparison[a])} | ${f(okcComparison[b])} |`),'',
  '## 聯盟共同偏差','',
  `全聯盟FG% 模/真 ${f(leagueComparison.simulatedFG)} / ${f(leagueComparison.observedFG)}；2P% ${f(leagueComparison.simulatedTwo)} / ${f(leagueComparison.observedTwo)}；3P% ${f(leagueComparison.simulatedThree)} / ${f(leagueComparison.observedThree)}；STL/G ${f(leagueComparison.simulatedSteals)} / ${f(leagueComparison.observedSteals)}。雷霆偏差含全局命中率與抄截記帳問題，不能全歸因於雷霆球員評分。`,'',
  '## 雷霆球員曝光與正負值','',...playerTable(result.okcPlayers),'',
  '## 全聯盟正殘差最大的在隊版本（真實至少1000分鐘、模擬至少600分鐘）','',...playerTable(result.largestPositiveResiduals.slice(0,10)),'',
  '## 全聯盟負殘差最大的在隊版本','',...playerTable(result.largestNegativeResiduals.slice(0,10)),'',
  '## 雷霆模擬輪替時段','',
  '替補定義為輸入陣容前五人以外的球員，不是官方先發／替補。沒有同口徑真實陣容區段，因此不能以這張表直接判定真實替補被低估。','',
  '| 場上替補數 | 累計分鐘 | 淨分/48 |','|---|---:|---:|',...result.okcBench.map(b=>`| ${b.reserveCount} | ${f(b.seconds/60)} | ${f(b.netPer48)} |`),'',
  ...result.okcShai.map(b=>`SGA ${b.status}: ${f(b.seconds/60)}分鐘，淨分/48 ${f(b.netPer48)}。`),'',
  'SGA off包含整場未出賽時段，不等於只在SGA出賽場次的替補帶隊段；尚無同口徑真實on/off作比較。','',
  '## 同seed分鐘目標控制實驗','',
  '只修改雷霆球員的目標分鐘，改用當場真實分鐘比例；引擎仍是軟目標，非完全鎖分鐘。四組seed為探索診斷，未調參，也沒有獨立驗證效果。分鐘MAE比較的是逐場gamelog的取整分鐘。','',
  '| seed | 原目標勝場 | 真實分鐘目標勝場 | 原淨分/G | 新淨分/G | 原分鐘MAE | 新分鐘MAE |','|---|---:|---:|---:|---:|---:|---:|',
  ...experiments.map(e=>`| ${e.seed} | ${e.variants[0].wins} | ${e.variants[1].wins} | ${f(e.variants[0].marginPerGame)} | ${f(e.variants[1].marginPerGame)} | ${f(e.variants[0].minuteMAE)} | ${f(e.variants[1].minuteMAE)} |`),'',
  '## 中立與主客','',
  '官方Location=Home/Road另查：馬刺40主場、41客場、1中立；雷霆41主場、40客場、1中立。NBA Cup半決賽v3 box score指定雷霆為帳面homeTeam、馬刺為awayTeam，但不代表官方Home/Road篩選會將中立場合併。不能因馬刺只有40主場就把這場勝利指定為馬刺主場。','',
  '如採「帳面指定主客」展示，可另列馬刺40主／42客、雷霆42主／40客，並保留neutral標記；這不改變82場總戰績。','',
  '完整582球員的661個在隊版本及資料來源見 [JSON](season-diagnostics.json)。',''].join('\n');
fs.writeFileSync(new URL('../reports/season-diagnostics.md',import.meta.url),md);
console.log(JSON.stringify({okc:okcComparison,positive:result.largestPositiveResiduals.slice(0,5),negative:result.largestNegativeResiduals.slice(0,5),bench:result.okcBench,shai:result.okcShai,experiments},null,2));

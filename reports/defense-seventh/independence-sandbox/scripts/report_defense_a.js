import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {SCOREBOARD_KEYS} from '../src/defense_scoreboard.js';
const labels=['legacy','nba-defense-v1','a-accounting','a-rebounds','a-accounting-clock','a-rebounds-clock'];
const boards=Object.fromEntries(labels.map(k=>[k,read('reports/defense-a/scoreboard-'+k+'.json')]));
const base=boards['nba-defense-v1'],candidate=boards['a-accounting-clock'];
const audit=read('reports/defense-a/rebound-audit.json'),variance=read('reports/defense-a/variance.json');
const clock=read('reports/defense-a/clock-calibration.json'),full=read('reports/defense-a/a-accounting-clock-seeds.json');
const fast=read('reports/defense-a/v1-seeds.json'),twenty=read('reports/defense-a/scoreboard-a-accounting-clock-20.json');
const gates={efficiencyBias:Math.abs(candidate.metrics.offensiveRatingProxy.bias)<=.5,
  fg:Math.abs(candidate.global.simulated.fg-base.global.observed.fg)<=Math.abs(base.global.simulated.fg-base.global.observed.fg),
  three:Math.abs(candidate.global.simulated.three-base.global.observed.three)<=Math.abs(base.global.simulated.three-base.global.observed.three),
  turnovers:Math.abs(candidate.global.simulated.turnovers-base.global.observed.turnovers)<=Math.abs(base.global.simulated.turnovers-base.global.observed.turnovers)};
const adopted=Object.values(gates).every(Boolean);
const countsFor=name=>{
  const runs=[12,13,14,15].map(s=>read(name==='nba-defense-v1'?'reports/nba-defense-v1-seed202610'+s+'.json':'reports/defense-a/runs/'+name+'-seed202610'+s+'.json'));
  const counts={};for(const key of ['fga','fgm','fta','ftm','oreb','dreb','teamOreb','teamDreb','deadFtReb','clockTov'])
    counts[key]=runs.reduce((n,r)=>n+(r.accounting??r.teams).reduce((m,t)=>m+(t.stats[key]??0),0),0)/9840;
  return {...counts,fgMiss:counts.fga-counts.fgm,ftMiss:counts.fta-counts.ftm};
};
const reboundCounts=Object.fromEntries(labels.filter(k=>k!=='legacy').map(k=>[k,countsFor(k)]));
const realCounts={fgMiss:audit.box.fgMiss/audit.box.teamGames,ftMiss:audit.box.ftMiss/audit.box.teamGames,
  oreb:audit.box.playerOff/audit.box.teamGames,dreb:audit.box.playerDef/audit.box.teamGames,
  teamOreb:audit.box.teamOff/audit.box.richTeamGames,teamDreb:audit.box.teamDef/audit.box.richTeamGames,
  deadFtReb:audit.buckets.ftOther.misses/audit.box.teamGames};
const baselineVariance=variance.runs.find(r=>r.variant==='baseline');
const result={schemaVersion:1,scope:'Stage A complete; no B implementation; all new rebound variants remain experimental.',
  seeds:[20261012,20261013,20261014,20261015],scoreboards:boards,
  adoption:{candidate:'a-accounting-clock',gates,adopted,reason:adopted?'All specified A3 gates passed':'TOV error increased; retain v1 baseline, expose correction only as experimental preset.'},
  reboundAudit:{coverage:audit.coverage,realCounts,simulatedCounts:reboundCounts,
    additionalTeamEventsOutsideRecordedMissBuckets:audit.teamEvents-Object.values(audit.buckets).reduce((n,b)=>n+b.teamOff+b.teamDef,0),
    boxMinusPBPPlayerRebounds:{oreb:audit.box.playerOff-Object.values(audit.buckets).reduce((n,b)=>n+b.playerOff,0),dreb:audit.box.playerDef-Object.values(audit.buckets).reduce((n,b)=>n+b.playerDef,0)}},
  parallel:{fast:{seeds:fast.seeds,seconds:fast.elapsedSeconds,workers:fast.workers},full:{seeds:full.seeds,seconds:full.elapsedSeconds,workers:full.workers},
    verification:'Fresh sequential and parallel 40-game subsets on legacy/v1/A, complete 1230-game legacy baseline parity and complete two-seed v1 parity against frozen sequential artifacts.'},
  twentySeedValidation:twenty,variance:variance.runs.map(({results,...r})=>r),
  limitations:['仍為同季回溯，沒有完成資料外預測驗證。',
    '逐球率估計排除3場CDN比分不一致資料；與box球員籃板合計差7次，另有1個重複的投失／籃板連結。',
    '團隊籃板採抽象死球結果，尚非完整出界、開球及時鐘規則模型；原始box團隊籃板還含Heave等一般記帳投失以外的事件。',
    '123場時鐘校準選出pace 1.16，但全季球權代理仍高於目標，A3未通過全部門檻。',
    'A4僅使用一組相同的真實太陽名單；獨立回合理論值來自引擎本身，沒有直接量到真實NBA回合協方差。',
    '領先時先發曝光是描述性結果；尚未證明垃圾時間輪替能解釋多少NBA殘差差距。'],
  provenance:{sources:Object.fromEntries([...labels.map(k=>'reports/defense-a/scoreboard-'+k+'.json'),'reports/defense-a/rebound-audit.json',
    'reports/defense-a/clock-calibration.json','reports/defense-a/variance.json','reports/defense-a/v1-seeds.json','reports/defense-a/a-accounting-clock-seeds.json',
    'reports/defense-a/scoreboard-a-accounting-clock-20.json'].map(f=>[f,hash(f)])),code:{'scripts/report_defense_a.js':hash('scripts/report_defense_a.js')}}};
const f=(n,d=3)=>Number.isFinite(n)?n.toFixed(d):'—';
const md=['# 防守第二批：A階段結果','',
  '**A1–A4完成，停在A階段。A3候選未通過完整驗收；原版與nba-defense-v1保持原樣。B階段沒有開始，也沒有修改球員OVR。**','',
  '## 口徑','',
  '全聯盟均值、偏差及去均值誤差以合併計數後的聯盟指標為基準。30隊先逐隊平均seed，相關、標準差比與模擬對真實斜率使用母體定義。殘差SD逐seed扣除兩隊自身賽季淨勝分差；同季描述不等於資料外實力估計。','',
  '原版與v1均使用seed 20261012–15各完整1230場；原版四seed已補跑。主要壓縮數字與重現關卡一致；新表的去均值誤差使用合併聯盟均值，和前次單純去30隊算術均值略有差別。','',
  '## A1：第一批有沒有改善鑑別度','',
  '| 指標 | 原版相關 | v1相關 | 原版SD比 | v1SD比 | 原版去均值MAE | v1去均值MAE | 原版去均值RMSE | v1去均值RMSE |',
  '|---|---:|---:|---:|---:|---:|---:|---:|---:|',
  ...SCOREBOARD_KEYS.map(k=>{const a=boards.legacy.metrics[k],b=base.metrics[k];return `| ${k} | ${[a.correlation,b.correlation,a.sdRatio,b.sdRatio,a.centeredMAE,b.centeredMAE,a.centeredRMSE,b.centeredRMSE].map(n=>f(n)).join(' | ')} |`;}),'',
  `防守相關 ${f(boards.legacy.metrics.defensiveRatingProxy.correlation)}→${f(base.metrics.defensiveRatingProxy.correlation)}，確有改善；SD比 ${f(boards.legacy.metrics.defensiveRatingProxy.sdRatio)}→${f(base.metrics.defensiveRatingProxy.sdRatio)}，防守強弱更被壓縮。去均值誤差僅小幅改善，不能把全局效率平移當作完整防守修復。`,
  `期望勝場MAE：原版${f(boards.legacy.wins.expectedMAE)}、v1 ${f(base.wins.expectedMAE)}；每分淨勝分勝場斜率：原版${f(boards.legacy.wins.winPerNet)}、v1 ${f(base.wins.winPerNet)}、真實${f(base.games.observed.winPerNet)}。`,
  '各版本完整偏差、SD、斜率、每seed分差／接戰比例及30隊進攻殘差見 [原版計分板](scoreboard-legacy.md) 和 [v1計分板](scoreboard-nba-defense-v1.md)。進攻端只記錄，沒有調整能力。','',
  '## A2：平行模式','',
  `快速模式兩seed實測${f(fast.elapsedSeconds,2)}秒；20seed完整模式實測${f(full.elapsedSeconds,2)}秒（${full.workers} workers）。這是本機本輪測量，不是任意主機的時間保證。`,
  '測試驗證：循序與平行的原版／v1／A候選40場子集合，完整回傳統計相同；兩seed v1的全部2460場比分與既有循序產物完全相同；原版seed 20261012的1230場亦與凍結基準一致。20seed每隊82場及總勝場守恆也通過。',
  `20seed A3候選效率偏差${f(twenty.metrics.offensiveRatingProxy.bias)}、TOV／場${f(twenty.global.simulated.turnovers)}、期望勝場MAE ${f(twenty.wins.expectedMAE)}，見 [20seed計分板](scoreboard-a-accounting-clock-20.md)。這不替代四seed同口徑比較。`,'',
  '## A3：籃板推測與修正','',
  `已檢查${audit.coverage.games}場比分一致的官方逐球紀錄；排除${audit.coverage.excluded.map(r=>r.id).join('、')}三場CDN比分不一致資料。FG投失後團隊籃板比例：三分${f(100*audit.rates.long.teamProbability,2)}%、中距離${f(100*audit.rates.mid.teamProbability,2)}%、近射${f(100*audit.rates.short.teamProbability,2)}%；末次可搶罰球投失為${f(100*audit.rates.ftFinal.teamProbability,2)}%。`,
  `非末次／技術等不可搶罰球投失的${audit.buckets.ftOther.misses}次事件均記團隊進攻籃板，球員籃板為0。另有${result.reboundAudit.additionalTeamEventsOutsideRecordedMissBuckets}個團隊事件不在一般記帳投失分類內，含Heave與其他記帳；不能把原始box score團隊OREB都當作延續活球。`,
  '因此「每個可搶投失都分給球員」的記帳偏差成立。球權代理中的OREB現在仍只用球員OREB，與官方統計同義；團隊留球、團隊失球、非末次罰球死球記帳另列。團隊事件的開球／14秒重置採抽象規則，尚未逐條重現真實裁判事件。','',
  '| 籃板／投失每隊每場 | v1四seed | A3分類＋時鐘四seed | 真實核對樣本 |',
  '|---|---:|---:|---:|',
  ...['fgMiss','ftMiss','oreb','dreb','teamOreb','teamDreb','deadFtReb'].map(k=>`| ${k} | ${f(reboundCounts['nba-defense-v1'][k])} | ${f(reboundCounts['a-accounting-clock'][k])} | ${f(realCounts[k])} |`),'',
  '真實FG／FT／球員籃板使用1227場；原始團隊籃板僅2374個具完整欄位的team-game，而且teamOreb含死球及其他事件，不能與候選的teamOreb留球計數直接相減。逐球球員籃板與box合計差3個OREB、4個DREB，另有1個重複連結，均保留為資料限制。','',
  '| 版本（四seed） | 進攻／防守代理 | 與真實偏差 | FG% | 3P% | TOV／場 | 球權代理／場 |',
  '|---|---:|---:|---:|---:|---:|---:|',
  ...labels.filter(k=>k!=='legacy').map(k=>{const b=boards[k];return `| ${k} | ${[b.global.simulated.offensiveRatingProxy,b.metrics.offensiveRatingProxy.bias,b.global.simulated.fg,b.global.simulated.three,b.global.simulated.turnovers,b.global.simulated.possessionsProxy].map(n=>f(n)).join(' | ')} |`;}),
  `| 真實 | ${f(base.global.observed.offensiveRatingProxy)} | 0 | ${f(base.global.observed.fg)} | ${f(base.global.observed.three)} | ${f(base.global.observed.turnovers)} | ${f(base.global.observed.possessionsProxy)} |`,'',
  `時鐘依123場合併球權代理校準，選出pace ${clock.selected['a-accounting']}；不以效率、勝場或雷霆作選擇目標。全季球權代理仍多${f(candidate.global.simulated.possessionsProxy-base.global.observed.possessionsProxy)}／場，說明樣本校準未完全對齊全季。`,
  `**驗收：效率偏差≤±0.5 ${gates.efficiencyBias?'通過':'未通過'}；FG ${gates.fg?'通過':'退步'}；3P ${gates.three?'通過':'退步'}；TOV ${gates.turnovers?'通過':'退步'}。整體未通過，沒有取代v1。**`,
  `候選時鐘失誤／場 ${f(reboundCounts['a-accounting-clock'].clockTov)}，v1 ${f(reboundCounts['nba-defense-v1'].clockTov)}。新團隊留球路徑缺乏即刻補籃、需重新組織進攻，可能與14秒限制耦合；這是待拆解原因，不以額外降低失誤參數補到過關。`,
  '分類開關與分區球員籃板先驗分開：a-accounting只加入團隊／死球分類；a-rebounds再替換分區球員OREB先驗；各自另有clock候選。沒有改防守屬性。','',
  '## A4：單場變異拆解（不修改正式模型）','',
  `兩邊均複製Phoenix Suns同一場官方名單（${baselineVariance.fixture}），每條件2000組相同seed。基準最終分差SD ${f(baselineVariance.finalSD)}，正規時間${f(baselineVariance.regulationSD)}；依同模型回合得分分布、假設獨立的理論SD ${f(baselineVariance.theoreticalIndependentSD)}。該理論是內部反事實，不是NBA實測。`,
  '| 關閉項目 | 最終SD | 正規SD | 獨立理論SD | SD降低量 | 變異降低量 | 配對平方分差降低95%區間 |',
  '|---|---:|---:|---:|---:|---:|---:|',
  ...variance.runs.map(r=>`| ${r.variant} | ${[r.finalSD,r.regulationSD,r.theoreticalIndependentSD,r.sdReductionVsBaseline,r.varianceReductionVsBaseline].map(n=>f(n)).join(' | ')} | ${r.pairedSquaredMarginReduction95.map(n=>f(n)).join('～')} |`),'',
  '正值表示關閉後變異降低；負值表示關閉後增加。單項效果不能相加。疲勞、犯滿與分鐘目標的配對區間跨0，不能認定其中一項是主因；終場策略關閉反而顯著增加變異。全部關閉也沒有回到14。固定五人仍接近獨立理論值，差距不只來自輪替。',
  `基準領先≥20時，先發佔場上時間${f(100*baselineVariance.starterExposure.leading20.share,2)}%；接戰≤5時${f(100*baselineVariance.starterExposure.close5.share,2)}%。輪替價值函式沒有領先分數輸入，未見大比分領先自動撤主力的機制；這是缺少負回饋的證據，但尚無其造成NBA殘差差距的因果量。`,
  '建議B2先用真實回合序列估計得分協方差與比分狀態的效率／耗時、垃圾時間輪替，再測可解釋的負回饋。保留現有終場策略；不直接縮放分差、不另加勝場斜率補丁。單一相同陣容結果不能完全代表30隊異質對戰。','',
  '## 仍不確定與停止點','',
  ...result.limitations.map(s=>'- '+s),'',
  'B1防守訊號、B2變異修法、B3球隊節奏／反擊、B4前後41場資料外驗證均未開始。A階段已停下，下一步需依這些結果重新決定B的機制與驗收。','',
  '## 重跑','',
  '```sh',
  'npm run defense:a:seeds -- --preset v1 --mode fast',
  'npm run defense:a:seeds -- --preset a-accounting-clock --mode full',
  'npm run defense:a:scoreboard -- reports/nba-defense-v1-seed20261012.json reports/nba-defense-v1-seed20261013.json reports/nba-defense-v1-seed20261014.json reports/nba-defense-v1-seed20261015.json',
  'npm run defense:a:variance',
  'npm run test:defense-a','```','',
  '快速預設2seed；完整預設20seed；可用--seeds與--workers覆寫。計分板接受v1報告及A runner的完整產物；--output可另存20seed比較。所有A候選均為實驗版本。完整數據、來源與程式雜湊見 [A階段JSON](stage-a.json)。',''].join('\n');
fs.writeFileSync(new URL('../reports/defense-a/stage-a.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
fs.writeFileSync(new URL('../reports/defense-a/stage-a.md',import.meta.url),md);
console.log(JSON.stringify({adopted,gates,fastSeconds:fast.elapsedSeconds,fullSeconds:full.elapsedSeconds,twentyBias:twenty.metrics.offensiveRatingProxy.bias,twentyTov:twenty.global.simulated.turnovers}));

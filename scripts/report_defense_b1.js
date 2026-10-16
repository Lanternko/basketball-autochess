import fs from 'node:fs';
import {read,hash} from './defense_io.js';
const root='reports/defense-b1',names=['v1','a-accounting-clock','c-empirical'],boards=names.map(n=>read(root+'/scoreboard-'+n+'-20.json'));
const [baseline,a3,candidate]=boards,prep=read(root+'/preparation.json'),samples=read(root+'/defensive-samples.json'),timing=read(root+'/empirical-timing.json'),types=read(root+'/turnover-types.json'),variance=read(root+'/variance-sources.json'),four=read(root+'/four-point-diagnosis.json'),paired=read(root+'/paired-comparison.json');
const contains=(ci,x)=>ci[0]<=x&&x<=ci[1],u=candidate.uncertainty.metrics,real=baseline.global.observed;
const gates={efficiency:{estimate:candidate.metrics.offensiveRatingProxy.bias,limit:.5,passed:Math.abs(candidate.metrics.offensiveRatingProxy.bias)<=.5},possessions:{estimate:candidate.metrics.possessionsProxy.bias,limit:.5,passed:Math.abs(candidate.metrics.possessionsProxy.bias)<=.5},turnovers:{estimate:candidate.global.simulated.turnovers-real.turnovers,limit:.2,passed:Math.abs(candidate.global.simulated.turnovers-real.turnovers)<=.2},
  clockRate:{estimate:u['global.clockPer100Possessions'].estimate,target:timing.clockViolationPerPossession*100,ci95:u['global.clockPer100Possessions'].ci95,passed:contains(u['global.clockPer100Possessions'].ci95,timing.clockViolationPerPossession*100)},
  liveShare:{estimate:u['global.liveShare'].estimate,target:prep.liveTurnoverShare,ci95:u['global.liveShare'].ci95,passed:contains(u['global.liveShare'].ci95,prep.liveTurnoverShare)},
  fg:{candidateError:Math.abs(candidate.global.simulated.fg-real.fg),baselineError:Math.abs(baseline.global.simulated.fg-real.fg),passed:Math.abs(candidate.global.simulated.fg-real.fg)<=Math.abs(baseline.global.simulated.fg-real.fg)},
  three:{candidateError:Math.abs(candidate.global.simulated.three-real.three),baselineError:Math.abs(baseline.global.simulated.three-real.three),passed:Math.abs(candidate.global.simulated.three-real.three)<=Math.abs(baseline.global.simulated.three-real.three)}};
const adopted=Object.values(gates).every(g=>g.passed);if(adopted)throw Error('Adoption requires a separately reviewable production change; this report does not mutate presets');
const sources=[...names.map(n=>root+'/scoreboard-'+n+'-20.json'),root+'/paired-comparison.json',root+'/preparation.json',root+'/defensive-samples.json',root+'/stint-schema.json',root+'/stint-zones.jsonl',root+'/empirical-timing.json',root+'/turnover-types.json',root+'/variance-sources.json',root+'/four-point-diagnosis.json',root+'/clock-calibration.json',root+'/c-empirical-seeds.json',...['v1-instrumented','a-instrumented','c-independent','c-time-only','c-empirical'].map(n=>root+'/'+n+'-diagnosis.json')];
sources.push(root+'/paired-comparison-provenance.json');
const result={schemaVersion:1,stage:'A closeout plus B1 data preparation',complete:true,adopted:false,production:'nba-defense-v1 remains unchanged',seeds:baseline.seeds,adoption:{primary:['centered net RMSE','net correlation','net SD ratio','winPerNet'],winMAE:'Report only, no acceptance gate',rateAlignmentDiagnostic:'Candidate 20-seed bootstrap 95% interval covers the observed target. No new user tolerance imposed; efficiency and TOV failures already independently block adoption.',gates},
  clockConclusion:'Uniform setup/pass/release clock overflow generates excess violations and directly preempts touch turnovers. Expected direct lost steals ~0.11/G in frozen v1, too small to explain ~1.0/G steal gap. Independent-clock ablation supports a small effect; altered possession chains make it non-exact causal attribution. Empirical candidate fails overall efficiency/TOV/live-share gates without any turnover coefficient adjustment.',
  varianceGap:variance.gap,dataCompleteness:{lineupGames:samples.lineupValidatedGames,strictGames:samples.strictUsableGames,stints:samples.stints,strictStints:samples.strictStints,samples:samples.strict.distribution},
  nextMechanisms:['B2: first verify separate and-one frequencies by zone, then model score/time-dependent rotation and possession outcome coupling. No variance correction implemented in this batch.','Turnovers need identifiable passing, handling, offensive foul and violation outcomes. Do not add observed category rates on top of unclassified dead touch turnovers without checking overlap.','B1 defense estimation remains pending. Use strict stint quality masks and team-centered shrinkage for low exposure; no attribute or OVR estimated here.'],
  limitations:['Same-season retrospective, not held-out predictive validation.','Seed-block errors measure simulation uncertainty only; no season/source/measurement uncertainty included.','Variance decomposition uses one full v1 seed and game-block intervals with fitted team centers held fixed; remainder is not uniquely identifiable score feedback.','3 missing PBP final-score validation failures, 7 lineup failures, 8 possession-anomaly games, 25 games with official-vs-PBP counters inconsistent; overlapping exclusions produce 1188 strict games.','Empirical timing uses positive game-clock durations; zero-time bookkeeping excluded and all draws conditional on the remaining clock. Rebound flight/inbound abstraction still affects the calibrated clock.','The v1 run manifest was expanded from fast two seeds to full twenty; the historical A report retains the older manifest fingerprint. Frozen engine/presets and original per-seed season artifacts are unchanged.'],
  provenance:{sources:Object.fromEntries(sources.map(f=>[f,hash(f)])),code:hash('scripts/report_defense_b1.js')}};
fs.writeFileSync(root+'/closeout.json',JSON.stringify(result,null,2)+'\n');
const f=n=>Number.isFinite(n)?n.toFixed(3):'—',pct=n=>f(n*100)+'%',estimate=(b,k)=>f(b.uncertainty.metrics[k].estimate)+' ± '+f(b.uncertainty.metrics[k].standardError);
const primary=[['淨勝分去均值RMSE','net.centeredRMSE'],['淨勝分相關','net.correlation'],['淨勝分SD比','net.sdRatio'],['每分淨勝分勝場斜率','winPerNet'],['期望勝場MAE（僅列示）','winMAE']];
const sims=boards.map(b=>b.global.simulated),diagnoses=['v1-instrumented','a-instrumented','c-independent','c-time-only','c-empirical'].map(n=>read(root+'/'+n+'-diagnosis.json'));
const md=['# A 階段收尾＋B1 資料準備','',
  '**四項工作完成，停在資料準備與診斷。時鐘候選未通過，因此不取代 v1；沒有調失誤係數，也沒有改防守屬性或 OVR。**','',
  '## 二十 seed 與採用判準','',
  '三組都用 seed 20261012–20261031；各 seed 30 隊 × 82 場，共 1,230 場。表內 ± 是 SE，採整季 seed 區塊 bootstrap 2,000 次；另列單 seed SD／均值SE及95%區間。聯盟均值用合併計數，球隊指標先逐隊平均seed，SD用母體定義。','',
  '| 主指標 | v1 | A3 記帳＋時鐘 | 經驗時鐘候選 |','|---|---:|---:|---:|',...primary.map(([label,k])=>'| '+label+' | '+boards.map(b=>estimate(b,k)).join(' | ')+' |'),'',
  `真實每分淨勝分勝場斜率 ${f(baseline.games.observed.winPerNet)}。勝場MAE不再作採用判準。A3 相對 v1 的淨勝分RMSE差 ${f(paired[0].differences['net.centeredRMSE'].estimate)}，95%區間 ${paired[0].differences['net.centeredRMSE'].ci95.map(f).join('～')}，沒有證據顯示改善。`,'',
  '[v1完整計分板](scoreboard-v1-20.md) · [A3完整計分板](scoreboard-a-accounting-clock-20.md) · [時鐘完整計分板](scoreboard-c-empirical-20.md) · [成對差異與區間](paired-comparison.json)','',
  '## 時鐘、失誤類型與驗收','',
  `有效逐球 ${prep.sourceGames} 場；違例 ${prep.totals.clockTov} 次，即 ${f(prep.clockViolationPerTeamGame)} 次／隊／場、${f(timing.clockViolationPerPossession*100)} 次／100 真實逐球回合。活球定義為失誤事件含官方 stealPersonId，占 ${pct(prep.liveTurnoverShare)}。`,'',
  '| 真實失誤類型 | 次／隊／場 | 占全部失誤 | 其中活球次／場 |','|---|---:|---:|---:|',...Object.entries(types.groups).map(([k,g])=>`| ${k} | ${f(g.perTeamGame)} | ${pct(g.share)} | ${f(g.livePerTeamGame)} |`),'',
  '模擬能直接辨識傳球抄截、touch活球、泛稱dead touch和時鐘違例。進攻犯規與其他違例沒有獨立機制；dead touch無法直接分類成真實傳球、持球、犯規，不拿兩者當成相同欄位。','',
  '| 同口徑／可識別部分 | 真實 | v1 二十seed | A3 二十seed | 經驗時鐘二十seed |','|---|---:|---:|---:|---:|',
  ...[['TOV/G',prep.turnoversPerTeamGame,'turnovers'],['STL/G',prep.totals.liveTov/(prep.sourceGames*2),'steals'],['時鐘違例/G',prep.clockViolationPerTeamGame,'clockTurnovers'],['傳球活球/G',types.groups.passing.livePerTeamGame,'passSteals'],['持球／touch活球/G（近似類別）',types.groups.handling.livePerTeamGame,'touchSteals']].map(([label,target,key])=>`| ${label} | ${f(target)} | ${sims.map(s=>f(s[key])).join(' | ')} |`),'',
  '| 機制開關診斷，seed20261012 | TOV/G | 時鐘違例/G | STL/G |','|---|---:|---:|---:|',...diagnoses.map(r=>`| ${r.preset} | ${f(r.totals.tov/2460)} | ${f(r.totals.clockTov/2460)} | ${f(r.totals.stl/2460)} |`),'',
  `已證實：原引擎setup、pass、release均勻亂數相加撞限產生違例，且先於觸球失誤檢定返回。v1影子機率計數估計略過觸球失誤 ${f(diagnoses[0].totals.clockExpectedTouch/2460)}／場，其中預期抄截 ${f(diagnoses[0].totals.clockExpectedLive/2460)}／場。這個直接效應不足以解釋全部STL缺口；只改獨立違例的消融實驗也只有小幅STL改善。`,'',
  '新候選將團隊籃板記帳、經驗耗時、獨立違例各保留開關。耗時依對手得分後、防守籃板後、失誤後、進攻籃板／團隊留球後抽樣；不使用球隊ID、勝場或球隊節奏。CDF條件抽樣限制在剩餘進攻時限，違例由獨立亂數結果決定。','',
  `全季校準每次均 ${read(root+'/clock-calibration.json').trials[0].games} 場，15個試驗，只選球權代理偏差最小，pace=${read(root+'/clock-calibration.json').selected.pace}；校準seed731019，驗收另用上述20seed。`,'',
  '| 二十seed驗收 | 結果 | SE／比較 | 判定 |','|---|---:|---|---|',
  `| 效率偏差 | ${f(gates.efficiency.estimate)} | SE ${f(u['offensiveRatingProxy.bias'].standardError)}，要求±0.5 | 未過 |`,
  `| 球權代理偏差 | ${f(gates.possessions.estimate)} | SE ${f(u['global.possessionsProxy'].standardError)}，要求±0.5 | ${gates.possessions.passed?'通過':'未過'} |`,
  `| TOV/G偏差 | ${f(gates.turnovers.estimate)} | SE ${f(u['global.turnovers'].standardError)}，要求±0.2 | 未過 |`,
  `| 違例／100逐球回合 | ${f(gates.clockRate.estimate)} | 真實${f(gates.clockRate.target)}；95%區間${gates.clockRate.ci95.map(f).join('～')} | 接近，但95%未涵蓋目標 |`,
  `| 活球比例 | ${pct(gates.liveShare.estimate)} | 真實${pct(gates.liveShare.target)} | 未對齊 |`,
  `| FG%絕對偏差 | ${f(gates.fg.candidateError)}pp | v1 ${f(gates.fg.baselineError)}pp | ${gates.fg.passed?'改善':'未過'} |`,
  `| 3P%絕對偏差 | ${f(gates.three.candidateError)}pp | v1 ${f(gates.three.baselineError)}pp；版本差95%跨0 | 點估計小幅退步，未證實差異 |`,'',
  '獨立違例移除了原本補償其他失誤的假失誤，暴露原有失誤分類缺口。不能直接把真實進攻犯規、違例數加回去，因泛稱dead touch可能重疊。沒有調TOV參數讓候選過關，v1維持原樣。','',
  '## 真實變異拆解','',
  `共同1227場、正規時間，使用同一分析函式。v1獨立回合理論SD ${f(variance.simulation.independentSD)}、實際殘差SD ${f(variance.simulation.marginResidualSD)}；真實理論SD ${f(variance.real.independentSD)}、殘差SD ${f(variance.real.marginResidualSD)}。沒有把A4單一同隊名單的16.79與全NBA季賽混在同一分解。`,'',
  '| 變異差來源：模擬減真實 | 分數平方 | 占總差 |','|---|---:|---:|',...Object.entries(variance.gap.components).map(([k,v])=>`| ${k} | ${f(v)} | ${pct(variance.gap.shares[k])} |`),`| 合計 | ${f(variance.gap.marginVariance)} | 100% |`,'',
  '單回合分布解釋約28%；其餘同場比分共變異約32%；球權數合計約−3.5%，並非主要來源；剩餘約43%含隊內序列相關、名單／對戰異質性和實力估計。這是可加總的統計分解，不是唯一因果拆解；不能把最後43%直接歸給領先負回饋。','',
  `四分回合真實${four.real.four}、模擬${four.simulation.four}；其中三分加罰命中分別${four.real.threePlusOne}、${four.simulation.threePlusOne}（場數1227／1230）。已確認模擬四分回合的主要來源是三分加罰。這說明全局FG%對齊仍可能存在犯規結果分布偏差，B2應先驗證分區and-one頻率。`,'',
  `領先≥20時先發曝光：真實${pct(variance.real.scoreBuckets['>=20'].starterShare)}、v1 ${pct(variance.simulation.scoreBuckets['>=20'].starterShare)}。前三節分差對第四節分差變化相關：真實${f(variance.real.q3Q4Correlation)}、v1 ${f(variance.simulation.q3Q4Correlation)}。需控制球隊／時間／對戰後才能估計領先策略的因果貢獻；本批沒有修B2。`,'',
  '[完整分布、隊內得分變異、共變異、球權拆解、比分分桶與區間](variance-sources.md)','',
  '## B1 五人區段與防守樣本','',
  `${samples.lineupValidatedGames}/1227有效逐球場通過五人與逐人分鐘驗證（全1230場覆蓋${pct(samples.lineupCoverage)}）；${samples.stints}個區段。${samples.minuteValidation.playerGameRows}筆球員場次分鐘，MAE ${f(samples.minuteValidation.meanAbsoluteSeconds)}秒，最大誤差${f(samples.minuteValidation.maxAbsoluteSeconds)}秒；容許1.1秒，只容納官方分鐘四捨五入，沒有用box分鐘解陣容。`,'',
  '區段含雙方五人、起迄時間、對手三分／中投／禁區出手與命中、罰球、活球與時鐘失誤、個人／團隊籃板、真實籃板機會、回合終止數及按時計的分數防守回合。零秒區段保留當時罰球／換人事件。區段事件計數逐場加總核對原始逐球，差異為0。','',
  `另有25場的40筆PBP計數與官方box不同、8場回合歸屬異常。嚴格資料遮罩一併排除後，${samples.strictUsableGames}場、${samples.strictStints}區段可用；不把原始來源差異強行平帳。`,'',
  '| 嚴格樣本，每位球員跨隊合計 | 防守回合 |','|---|---:|',...['min','p10','p25','median','p75','p90','max'].map(k=>`| ${k} | ${f(samples.strict.distribution[k])} |`),'',
  `共582位球員，581位有嚴格樣本；低於100／500／1000回合分別${samples.strict.distribution.under100}／${samples.strict.distribution.under500}／${samples.strict.distribution.under1000}位。Darius Brown II嚴格樣本為0，保留名列，不補成聯盟70或估防守屬性。`,'',
  '| 無法驗證五人區段 | 原因 |','|---|---|',...samples.lineupFailed.map(g=>`| ${g.id} | ${[...new Set(g.errors.map(e=>e.reason))].join(', ')} |`),'',
  `缺少可用逐球：${samples.missingPbp.map(g=>g.id).join('、')}（CDN終場比分不一致）。`,'',
  '更細的NBA原始出手分區另有 restricted area、paint non-RA、midrange、左右底角、弧頂與backcourt／unknown；用game ID、period、startIndex、endIndex接回區段。原始分區出手加總亦逐區段與FGA核對一致。注意欄位opponent.dreb指此五名防守者所屬球隊的防守籃板，搭配opponent.oreb（對手進攻籃板）計算防守籃板率；完整語意見schema。','',
  '[每球員樣本、嚴格遮罩及所有失敗／差異清單](defensive-samples.json) · [五人區段JSONL](stints.jsonl) · [原始分區JSONL](stint-zones.jsonl) · [欄位語意](stint-schema.json) · [逐人分鐘核對JSONL](minute-checks.jsonl)','',
  '## 重跑與限制','',
  'Windows參數範例直接用node，避免本機npm轉送命名旗標遺失。','',
  '```powershell','node scripts/run_defense_a_seeds.js --preset v1 --mode full','node scripts/prepare_defense_b1.js','node scripts/validate_defense_stints.js','node scripts/prepare_defense_stint_zones.js','node scripts/classify_defense_turnovers.js','node scripts/diagnose_defense_clock.js','node scripts/calibrate_defense_clock.js','node scripts/run_defense_clock_seeds.js --preset c-empirical --mode full','node scripts/defense_scoreboard_uncertainty.js reports/defense-a/v1-seeds.json reports/defense-a/a-accounting-clock-seeds.json reports/defense-b1/c-empirical-seeds.json','node scripts/report_defense_variance_sources.js','node scripts/diagnose_defense_four_points.js','node scripts/report_defense_b1.js','node test/defense_b1.js','```','',
  ...result.limitations.map(s=>'- '+s),'','原版、v1、A3引擎／preset都保留。B1尚未估防守屬性，B2/B3尚未實作，B4資料外驗證尚未開始。',''].join('\n');
fs.writeFileSync(root+'/closeout.md',md);console.log({complete:true,adopted:false,gates,data:result.dataCompleteness});

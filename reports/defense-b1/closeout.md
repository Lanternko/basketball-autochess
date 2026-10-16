# A 階段收尾＋B1 資料準備

**四項工作完成，停在資料準備與診斷。時鐘候選未通過，因此不取代 v1；沒有調失誤係數，也沒有改防守屬性或 OVR。**

## 二十 seed 與採用判準

三組都用 seed 20261012–20261031；各 seed 30 隊 × 82 場，共 1,230 場。表內 ± 是 SE，採整季 seed 區塊 bootstrap 2,000 次；另列單 seed SD／均值SE及95%區間。聯盟均值用合併計數，球隊指標先逐隊平均seed，SD用母體定義。

| 主指標 | v1 | A3 記帳＋時鐘 | 經驗時鐘候選 |
|---|---:|---:|---:|
| 淨勝分去均值RMSE | 3.547 ± 0.065 | 3.656 ± 0.080 | 3.725 ± 0.072 |
| 淨勝分相關 | 0.821 ± 0.008 | 0.807 ± 0.010 | 0.805 ± 0.011 |
| 淨勝分SD比 | 0.722 ± 0.011 | 0.715 ± 0.012 | 0.666 ± 0.012 |
| 每分淨勝分勝場斜率 | 1.793 ± 0.030 | 1.847 ± 0.026 | 1.861 ± 0.032 |
| 期望勝場MAE（僅列示） | 6.813 ± 0.162 | 7.157 ± 0.172 | 6.893 ± 0.182 |

真實每分淨勝分勝場斜率 2.165。勝場MAE不再作採用判準。A3 相對 v1 的淨勝分RMSE差 0.110，95%區間 -0.089～0.286，沒有證據顯示改善。

[v1完整計分板](scoreboard-v1-20.md) · [A3完整計分板](scoreboard-a-accounting-clock-20.md) · [時鐘完整計分板](scoreboard-c-empirical-20.md) · [成對差異與區間](paired-comparison.json)

## 時鐘、失誤類型與驗收

有效逐球 1227 場；違例 1653 次，即 0.674 次／隊／場、0.666 次／100 真實逐球回合。活球定義為失誤事件含官方 stealPersonId，占 58.009%。

| 真實失誤類型 | 次／隊／場 | 占全部失誤 | 其中活球次／場 |
|---|---:|---:|---:|
| shotClock | 0.674 | 4.643% | 0.000 |
| passing | 6.902 | 47.569% | 5.137 |
| handling | 4.222 | 29.097% | 3.280 |
| offensiveFoul | 1.474 | 10.161% | 0.000 |
| otherViolation | 0.910 | 6.269% | 0.000 |
| outOfBoundsUnclassified | 0.328 | 2.261% | 0.000 |

模擬能直接辨識傳球抄截、touch活球、泛稱dead touch和時鐘違例。進攻犯規與其他違例沒有獨立機制；dead touch無法直接分類成真實傳球、持球、犯規，不拿兩者當成相同欄位。

| 同口徑／可識別部分 | 真實 | v1 二十seed | A3 二十seed | 經驗時鐘二十seed |
|---|---:|---:|---:|---:|
| TOV/G | 14.509 | 14.400 | 14.949 | 12.368 |
| STL/G | 8.416 | 7.384 | 7.394 | 7.421 |
| 時鐘違例/G | 0.674 | 2.751 | 3.299 | 0.637 |
| 傳球活球/G | 5.137 | 3.127 | 3.137 | 3.085 |
| 持球／touch活球/G（近似類別） | 3.280 | 4.257 | 4.257 | 4.336 |

| 機制開關診斷，seed20261012 | TOV/G | 時鐘違例/G | STL/G |
|---|---:|---:|---:|
| v1-instrumented | 14.452 | 2.738 | 7.417 |
| a-instrumented | 15.017 | 3.346 | 7.350 |
| c-independent | 12.525 | 0.652 | 7.443 |
| c-time-only | 12.780 | 0.000 | 8.027 |
| c-empirical | 13.318 | 0.670 | 7.964 |

已證實：原引擎setup、pass、release均勻亂數相加撞限產生違例，且先於觸球失誤檢定返回。v1影子機率計數估計略過觸球失誤 0.226／場，其中預期抄截 0.113／場。這個直接效應不足以解釋全部STL缺口；只改獨立違例的消融實驗也只有小幅STL改善。

新候選將團隊籃板記帳、經驗耗時、獨立違例各保留開關。耗時依對手得分後、防守籃板後、失誤後、進攻籃板／團隊留球後抽樣；不使用球隊ID、勝場或球隊節奏。CDF條件抽樣限制在剩餘進攻時限，違例由獨立亂數結果決定。

全季校準每次均 1230 場，15個試驗，只選球權代理偏差最小，pace=0.836；校準seed731019，驗收另用上述20seed。

| 二十seed驗收 | 結果 | SE／比較 | 判定 |
|---|---:|---|---|
| 效率偏差 | 3.109 | SE 0.039，要求±0.5 | 未過 |
| 球權代理偏差 | 0.141 | SE 0.031，要求±0.5 | 通過 |
| TOV/G偏差 | -2.142 | SE 0.016，要求±0.2 | 未過 |
| 違例／100逐球回合 | 0.655 | 真實0.666；95%區間0.647～0.662 | 接近，但95%未涵蓋目標 |
| 活球比例 | 60.004% | 真實58.009% | 未對齊 |
| FG%絕對偏差 | 0.201pp | v1 0.293pp | 改善 |
| 3P%絕對偏差 | 0.634pp | v1 0.594pp；版本差95%跨0 | 點估計小幅退步，未證實差異 |

獨立違例移除了原本補償其他失誤的假失誤，暴露原有失誤分類缺口。不能直接把真實進攻犯規、違例數加回去，因泛稱dead touch可能重疊。沒有調TOV參數讓候選過關，v1維持原樣。

## 真實變異拆解

共同1227場、正規時間，使用同一分析函式。v1獨立回合理論SD 17.680、實際殘差SD 17.557；真實理論SD 16.859、殘差SD 14.027。沒有把A4單一同隊名單的16.79與全NBA季賽混在同一分解。

| 變異差來源：模擬減真實 | 分數平方 | 占總差 |
|---|---:|---:|
| singlePossessionVariance | 31.296 | 28.070% |
| meanPossessionCount | -3.035 | -2.722% |
| sharedPaceNet | -0.895 | -0.802% |
| remainingSameGameCovariance | 35.806 | 32.115% |
| withinTeamSerialAndHeterogeneity | 48.322 | 43.340% |
| 合計 | 111.494 | 100% |

單回合分布解釋約28%；其餘同場比分共變異約32%；球權數合計約−3.5%，並非主要來源；剩餘約43%含隊內序列相關、名單／對戰異質性和實力估計。這是可加總的統計分解，不是唯一因果拆解；不能把最後43%直接歸給領先負回饋。

四分回合真實382、模擬3154；其中三分加罰命中分別314、3053（場數1227／1230）。已確認模擬四分回合的主要來源是三分加罰。這說明全局FG%對齊仍可能存在犯規結果分布偏差，B2應先驗證分區and-one頻率。

領先≥20時先發曝光：真實41.808%、v1 61.279%。前三節分差對第四節分差變化相關：真實-0.105、v1 0.024。需控制球隊／時間／對戰後才能估計領先策略的因果貢獻；本批沒有修B2。

[完整分布、隊內得分變異、共變異、球權拆解、比分分桶與區間](variance-sources.md)

## B1 五人區段與防守樣本

1220/1227有效逐球場通過五人與逐人分鐘驗證（全1230場覆蓋99.187%）；39669個區段。42612筆球員場次分鐘，MAE 0.002秒，最大誤差0.500秒；容許1.1秒，只容納官方分鐘四捨五入，沒有用box分鐘解陣容。

區段含雙方五人、起迄時間、對手三分／中投／禁區出手與命中、罰球、活球與時鐘失誤、個人／團隊籃板、真實籃板機會、回合終止數及按時計的分數防守回合。零秒區段保留當時罰球／換人事件。區段事件計數逐場加總核對原始逐球，差異為0。

另有25場的40筆PBP計數與官方box不同、8場回合歸屬異常。嚴格資料遮罩一併排除後，1188場、38623區段可用；不把原始來源差異強行平帳。

| 嚴格樣本，每位球員跨隊合計 | 防守回合 |
|---|---:|
| min | 0.000 |
| p10 | 137.337 |
| p25 | 612.080 |
| median | 1946.573 |
| p75 | 3243.411 |
| p90 | 4379.679 |
| max | 5867.439 |

共582位球員，581位有嚴格樣本；低於100／500／1000回合分別46／132／196位。Darius Brown II嚴格樣本為0，保留名列，不補成聯盟70或估防守屬性。

| 無法驗證五人區段 | 原因 |
|---|---|
| 0022500449 | nonmonotone-clock |
| 0022500458 | ambiguous-period-start |
| 0022500521 | ambiguous-period-start, not-five-after-substitution |
| 0022500637 | ambiguous-period-start, not-five-after-substitution |
| 0022500955 | ambiguous-period-start, not-five-after-substitution |
| 0022501029 | ambiguous-period-start, not-five-after-substitution |
| 0022501031 | nonmonotone-clock |

缺少可用逐球：0022500029、0022501230、0022501229（CDN終場比分不一致）。

更細的NBA原始出手分區另有 restricted area、paint non-RA、midrange、左右底角、弧頂與backcourt／unknown；用game ID、period、startIndex、endIndex接回區段。原始分區出手加總亦逐區段與FGA核對一致。注意欄位opponent.dreb指此五名防守者所屬球隊的防守籃板，搭配opponent.oreb（對手進攻籃板）計算防守籃板率；完整語意見schema。

[每球員樣本、嚴格遮罩及所有失敗／差異清單](defensive-samples.json) · [五人區段JSONL](stints.jsonl) · [原始分區JSONL](stint-zones.jsonl) · [欄位語意](stint-schema.json) · [逐人分鐘核對JSONL](minute-checks.jsonl)

## 重跑與限制

Windows參數範例直接用node，避免本機npm轉送命名旗標遺失。

```powershell
node scripts/run_defense_a_seeds.js --preset v1 --mode full
node scripts/prepare_defense_b1.js
node scripts/validate_defense_stints.js
node scripts/prepare_defense_stint_zones.js
node scripts/classify_defense_turnovers.js
node scripts/diagnose_defense_clock.js
node scripts/calibrate_defense_clock.js
node scripts/run_defense_clock_seeds.js --preset c-empirical --mode full
node scripts/defense_scoreboard_uncertainty.js reports/defense-a/v1-seeds.json reports/defense-a/a-accounting-clock-seeds.json reports/defense-b1/c-empirical-seeds.json
node scripts/report_defense_variance_sources.js
node scripts/diagnose_defense_four_points.js
node scripts/report_defense_b1.js
node test/defense_b1.js
```

- Same-season retrospective, not held-out predictive validation.
- Seed-block errors measure simulation uncertainty only; no season/source/measurement uncertainty included.
- Variance decomposition uses one full v1 seed and game-block intervals with fitted team centers held fixed; remainder is not uniquely identifiable score feedback.
- 3 missing PBP final-score validation failures, 7 lineup failures, 8 possession-anomaly games, 25 games with official-vs-PBP counters inconsistent; overlapping exclusions produce 1188 strict games.
- Empirical timing uses positive game-clock durations; zero-time bookkeeping excluded and all draws conditional on the remaining clock. Rebound flight/inbound abstraction still affects the calibrated clock.
- The v1 run manifest was expanded from fast two seeds to full twenty; the historical A report retains the older manifest fingerprint. Frozen engine/presets and original per-seed season artifacts are unchanged.

原版、v1、A3引擎／preset都保留。B1尚未估防守屬性，B2/B3尚未實作，B4資料外驗證尚未開始。

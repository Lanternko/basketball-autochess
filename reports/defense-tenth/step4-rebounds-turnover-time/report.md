# 活球／死球失誤耗時拆分

耗時辨識改善，但準確度沒有顯著改善，不升為新基準。 本批只拆失誤後的耗時分布，聯盟 pace 只用官方球權代理校準；球員卡、投籃／犯規／失誤／抄截／籃板機率與補籃機制均沿用。四季全部已看過答案。

## 二十 seed 準確度

季內去均值、四季等權合併；每版先平均二十 seed 再評分。差值是新候選減上一版 calibrated。95% 為 franchise＋seed 聯合配對重抽，20,000 次。

| 指標 | 上一版 calibrated | 新 split | 差值與聯合 95% 區間 |
|---|---:|---:|---|
| netRMSE | 2.5544 | 2.5553 | +0.0009 [-0.143, +0.150] |
| Pearson | 0.8830 | 0.8829 | -0.0001 [-0.016, +0.017] |
| Spearman | 0.8604 | 0.8440 | -0.0164 [-0.052, +0.021] |
| SDRatio | 0.8415 | 0.8415 | -0.0000 [-0.031, +0.030] |
| calibrationSlope | 1.0493 | 1.0492 | -0.0001 [-0.042, +0.046] |
| winsMAE | 5.0525 | 4.9375 | -0.1150 [-0.496, +0.268] |
| winsRMSE | 6.3819 | 6.3239 | -0.0581 [-0.440, +0.328] |
| winSlope | 1.8440 | 1.8415 | -0.0025 [-0.058, +0.053] |
| OREB_RMSE | 0.5844 | 0.5951 | +0.0107 [-0.042, +0.059] |
| DREB_RMSE | 1.3154 | 1.3099 | -0.0055 [-0.071, +0.060] |

次要比較（相對快速補籃之前 allocation）：

| 指標 | 差值 | 聯合 95% |
|---|---:|---|
| netRMSE | -0.0151 | [-0.177, +0.145] |
| winsMAE | -0.1058 | [-0.475, +0.290] |
| OREB_RMSE | +0.0024 | [-0.050, +0.054] |
| DREB_RMSE | -0.0073 | [-0.069, +0.051] |

## 各季與聯盟漂移

| 球季 | net RMSE 舊→新 | wins MAE 舊→新 | 效率偏差 | 球權代理偏差 | TOV／場偏差 | STL／場偏差 | FG% 偏差 pp | 3P% 偏差 pp |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2022-23 | 2.578→2.644 | 4.670→4.627 | -0.053 | +0.097 | -0.624 | -0.428 | -0.320 | +0.251 |
| 2023-24 | 1.998→1.878 | 4.747→4.383 | +0.195 | +0.156 | -0.626 | -0.501 | -0.416 | +0.270 |
| 2024-25 | 2.674→2.719 | 4.900→5.030 | +0.044 | +0.042 | -0.578 | -0.450 | -0.203 | +0.389 |
| 2025-26 | 2.883→2.866 | 5.893→5.710 | +0.013 | +0.054 | -0.021 | +0.053 | -0.057 | +0.708 |

每季各指標的成對區間、排名失敗隊及攻防誤差詳見 analysis.json 與 joint-intervals.json。不用球隊 net／勝場調任何常數。

## 時間機制是否修對

單位秒；同上一批事件起點與終點定義。第一事件含出手、失誤、普通防守犯規、一般罰球或終止球權的防守籃板。完整球權尾段可跨多次進攻籃板。三 seed 診斷，不當二十 seed 準確度評測。

| 起始狀態／終點 | 真實 | 上一版 | 新版 | 新版−上一版與聯合 95% | 絕對誤差變化與聯合 95% |
|---|---:|---:|---:|---|---|
| liveTurnover / first | 6.461 | 10.426 | 7.847 | -2.579 [-2.620, -2.539] | -2.579 [-2.620, -2.539] |
| liveTurnover / full | 8.344 | 11.545 | 8.967 | -2.578 [-2.627, -2.532] | -2.578 [-2.627, -2.532] |
| deadTurnover / first | 13.252 | 10.377 | 14.037 | +3.659 [+3.599, +3.709] | -2.090 [-2.475, -1.711] |
| deadTurnover / full | 15.623 | 11.522 | 15.202 | +3.680 [+3.614, +3.746] | -3.680 [-3.746, -3.614] |

其他狀態：

| 起點 | 真實第一事件 | 新版第一事件 | 新版−上一版 |
|---|---:|---:|---:|
| made | 15.425 | 16.398 | +0.029 |
| dreb | 9.040 | 10.508 | +0.006 |
| playerOreb | 2.555 | 3.073 | -0.002 |
| teamOreb | 4.042 | 4.566 | +0.016 |
| ftOreb | 5.378 | 4.441 | +0.027 |
| foulRetained | 9.455 | 5.004 | +0.049 |

## OREB 後事件副作用

| 指標 | 真實 | 上一版 | 新版 |
|---|---:|---:|---:|
| immediateProxy | 31.7002 | 30.5226 | 30.4289 |
| meanSeconds | 2.5525 | 3.0675 | 3.0657 |
| earlyLoss | 5.1428 | 6.5124 | 6.5607 |
| laterLoss | 2.6094 | 3.6037 | 3.5331 |
| foul | 9.7751 | 12.8648 | 12.9723 |
| fgPct | 51.9239 | 50.3321 | 50.1593 |
| firstFgPointsPerOreb | 0.9391 | 0.8443 | 0.8405 |

事件比例的聯合區間見 event-joint-intervals.json；不採用 diagnose.py 的 game 正態近似作結論。這批沒有調整 OREB 後犯規、失球或出手分區。firstFgPointsPerOreb 只算第一個 FG 得分，不含罰球與後續再搶板；不是完整 PPP，不能直接視為進攻籃板價值。

## 校準、凍結與資料稽核

| 球季 | 原 pace | 新 pace | 校準輪數 | 最後校準球權偏差 | 收斂 | 活球 CDF 數／均值 | 死球 CDF 數／均值 |
|---|---:|---:|---:|---:|---|---|---|
| 2022-23 | 0.904602 | 0.902103 | 2 | +0.087 | True | 17627 / 7.740 | 16569 / 14.842 |
| 2023-24 | 0.899354 | 0.899354 | 1 | +0.135 | True | 18113 / 7.862 | 14973 / 14.904 |
| 2024-25 | 0.892678 | 0.888090 | 4 | +0.010 | True | 19938 / 7.786 | 14886 / 14.834 |
| 2025-26 | 0.891795 | 0.884721 | 4 | +0.072 | True | 20370 / 7.790 | 14852 / 14.767 |

## 拆分與 pace 校準的歸因診斷

僅相同三個診斷 seed 的點估計，不替代二十 seed 的聯合區間，不據此宣稱準確度改善。rawsplit 固定舊 pace；split 使用預先登記的聯盟球權校準。

| 版本 | net RMSE | wins MAE | 球權代理偏差 |
|---|---:|---:|---:|
| calibrated | 2.728 | 5.472 | +0.430 |
| rawsplit | 2.721 | 5.267 | +0.295 |
| split | 2.816 | 5.328 | +0.090 |

拆分與校準都影響球權均值，所以不能把球權偏差縮小全部歸因於拆分。2023–24 新舊 pace 相同，三個 seed 的 rawsplit／split 比分、完整統計與耗時資料逐筆一致（3,690 場）。

聯盟事件偏差仍存在：歷史季 TOV／STL 偏低、部分球季 3P% 偏高；本批沒有用這些誤差再調參，表中如實列示。這些是未解決項，不因本批球權對齊而視為通過整套引擎驗收。


已驗證：新兩個 CDF 合併後逐值等於各季 frozen turnover CDF。既有支援最小 .1 秒，因此零長區段仍排除；下載與規則未更換。當季全季資料適用本次重現，不能宣稱是資料外預測。

開關 OFF 四季共 4,920 場逐場比分、完整球員／球隊統計與 OREB 事件分類完全一致。正式評測 80 季、98,400 場；每季 82 場／隊。能力卡與事件機率保持不變；耗時仍可能改變場上分鐘、事件數、疲勞、迫近時限與後續 RNG 路徑，不能宣稱最終統計必然不變。

protocol SHA-256：`3f3bdd930871a5b5aa0fed2aa643430295c48d2ba79477da800aad585e4a0f5c`；登記 UTC 2026-10-14T21:56:47.948950+00:00。CDF 支援補充登記與來源雜湊見 cdf-support-supplement.*、source-registration.json。
保護 4423 份既有檔案，變動 0 份；未修改 frozen v1–v5、T0 或任何先前報告。

執行紀錄：file job 只回傳完成摘要、完整結果仍寫檔，降低主程序記憶體；輔助事件分析原複用 putback 對照，已修正為預先登記的 calibrated 對照，主二十 seed 比較與候選對真實結果不變。詳見 execution-serialization.json、event-comparator-correction.json。

## 已驗證、推測、失敗分列

已驗證：OFF parity 通過；兩個耗時絕對誤差同時減少=True；符合本批機制候選門檻=True。

推測：若耗時改善但 net／勝場不改善，原因可能是本批只修了反擊的時間，仍沒有修反擊的得分效率與陣容相性；這需要獨立資料與實驗，不能拿本批結果當因果證明。

失敗／未證實：漂移未通過季 無；顯著退步項 無；沒有顯著改善的主指標 ['netRMSE', 'winsMAE']。

保留限制：犯規留球仍與籃板共用 retained；CDF 到球權結束與引擎抽到出手時刻的口徑落差仍在。沒有藉本批同時修掉，也未使用球隊 ID、net 或勝場補丁。

## 重跑指令

```powershell
node reports/defense-tenth/step4-rebounds-turnover-time/build-cdf.mjs
node reports/defense-tenth/step4-rebounds-turnover-time/calibrate.mjs
node reports/defense-tenth/step4-rebounds-turnover-time/run.mjs
node reports/defense-tenth/step4-rebounds-turnover-time/analyze.mjs
python reports/defense-tenth/step4-rebounds-turnover-time/bootstrap.py
python reports/defense-tenth/step4-rebounds-turnover-time/timing-analysis.py
python reports/defense-tenth/step4-rebounds-turnover-time/diagnose.py
python reports/defense-tenth/step4-rebounds-turnover-time/event-joint.py
node reports/defense-tenth/step4-rebounds-turnover-time/attribution.mjs
python reports/defense-tenth/step4-rebounds-turnover-time/attribution-analysis.py
python reports/defense-tenth/step4-rebounds-turnover-time/same-pace-check.py
python reports/defense-tenth/step4-rebounds-turnover-time/finish.py
```

既有校準與模擬輸出會跳過；不得為了通過而改規則或重選參數。本批到此停止。

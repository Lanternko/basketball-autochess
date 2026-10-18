# v48：隊友陣容與兩分出手區域

狀態：未通過全部採用條件，保留為候選；正式量測進攻基準仍為 v47。遊戲預設及 OVR 未切換。

## 變更與證據

只修改新鮮兩分出手的籃下／其他油漆區／中距離分配。聯合估計投籃人與其他四位隊友的條件選擇係數，保留原本防守係數；三分選擇、所有命中率、罰球、補籃與角色設定不變。沒有姓名特例。

較早三季、整場五折交叉驗證選出共用 sigma=0.1；2025–26 不參與選擇。這是同季資料重建，不是預測未來賽季。最初測試的命中率係數僅保留來源資料原型，未混入本候選。

## 全體誤差

四季等權平均；百分比指標為百分點。隊友細區使用 strict PBP、新鮮出手共同樣本；個人與球隊使用完整賽季。

| 指標 | v47 | v48 |
|---|---:|---:|
| teammateTwoFGmae | 1.3049 | 1.2455 |
| teammateRAshareMAE | 2.0514 | 1.4409 |
| teamPPGmae | 2.3232 | 2.3532 |
| pts36mae | 0.7355 | 0.7381 |
| onshortFGpct | 1.0706 | 1.0486 |
| onlongFGpct | 1.2159 | 1.2586 |

| 球季 | 隊友兩分 MAE v47→v48 | 隊友籃下占兩分 MAE | 球隊 PPG MAE |
|---|---|---|---|
| 2022-23 | 1.3072 → 1.2325 | 2.0327 → 1.4752 | 2.3580 → 2.3699 |
| 2023-24 | 1.2841 → 1.2443 | 1.9985 → 1.3950 | 2.6953 → 2.7196 |
| 2024-25 | 1.2975 → 1.2300 | 2.1207 → 1.4338 | 2.1343 → 2.1500 |
| 2025-26 | 1.3306 → 1.2754 | 2.0536 → 1.4599 | 2.1051 → 2.1730 |

## Curry 2025–26

| 新鮮出手指標 | 實際 | v47 | v48 |
|---|---:|---:|---:|
| two:on | 61.055 | 57.846 | 57.664 |
| two:off | 52.811 | 58.063 | 56.895 |
| two:teammates | 61.874 | 58.532 | 57.952 |
| ra:on:shareWithinTwo | 54.302 | 46.144 | 48.586 |
| ra:off:shareWithinTwo | 40.716 | 51.186 | 50.434 |
| ra:teammates:shareWithinTwo | 59.178 | 48.853 | 51.920 |
| ra:teammates:FGpct | 72.017 | 73.333 | 71.655 |
| paint:teammates:FGpct | 50.476 | 48.534 | 46.119 |
| mid:teammates:FGpct | 40.741 | 37.875 | 38.228 |

出手組成有所改善，不代表隊友命中率已修好。原 v47 的隊友兩分誤差 −3.34pp，依投籃人×區域分解，組成項約 −3.26pp；固定真實出手與陣容時，預期隊友兩分為 60.34%，完整模擬卻為 58.53%。這指出完整流程的投籃人、區域及同場分配仍有問題。

目前使用實際每場出賽、先發與分鐘目標，但啟發式換人不保證實際同場陣容。Payton II 等球員在 Curry 上下場時的出手分配有明顯落差；尚不能判定全部來自換人，也不能把條件陣容係數稱作已量測的因果空間能力。

## 位置、細區與亂數

個人 ALL/G/F/C、得分／助攻／失誤／三分／罰球及種子結果見 [scores.json](scores.json)；五區防守見 [fine-scores.json](fine-scores.json)。全體逐人新鮮進攻、Curry 投籃人×區域分解、三種子範圍見 [candidate-offense-scores.json](candidate-offense-scores.json)，比較基準見 [baseline-offense-scores.json](baseline-offense-scores.json)。三種子範圍描述模擬波動，不是真實資料信賴區間。

## 事先列出的採用條件

| 條件 | 結果 |
|---|---|
| nonzeroOlderThreeSelection | 通過 |
| teammateTwoFGmaeImproved | 通過 |
| teammateRAshareMAEimproved | 通過 |
| teamPPGmeanNonRegression | 未通過 |
| individualPTS36within002 | 通過 |
| coarseDefenseWithin005pp | 通過 |
| fitVerified | 通過 |
| runtimeVerified | 通過 |
| olderThreeHeldoutNLLimproved | 通過 |

條件取自 [choice-protocol.json](choice-protocol.json)，未因 Curry 個案放寬。驗證見 [results-verification.json](results-verification.json)。

## 同場時間：獨立觀測

另外重跑 v47 的 2025–26 strict 三種子，只在引擎每段真正計入球員秒數的位置觀測同場時間，未改換人。比賽與全部隊伍／個人統計與原 v47 完全相同。原始 stint 與模擬秒數都限定 Curry 有出賽的共同場次。

| 球員 | Curry 狀態 | 實際同場分鐘 | 模擬分鐘 | 實際籃下次數/36 | 模擬籃下次數/36 |
|---|---|---:|---:|---:|---:|
| Gary Payton II | on | 413.77 | 215.08 | 6.44 | 5.24 |
| Gary Payton II | off | 53.89 | 305.12 | 2.00 | 5.74 |
| Jimmy Butler III | on | 568.10 | 659.73 | 6.21 | 4.53 |
| Jimmy Butler III | off | 418.34 | 286.32 | 4.13 | 5.95 |

Payton II 與 Curry 同場時間明顯不足，反而被大量排到 Curry 下場時；Butler 的方向相反。這已證實輪替分配有偏差，但每 36 分鐘的條件出手率也有落差，因此不能說輪替是唯一原因。下一個修正應先改善通用同場輪替，再評估空間與投籃人分配，避免能力係數補償錯誤陣容。完整結果見 [pair-scores.json](pair-scores.json)。

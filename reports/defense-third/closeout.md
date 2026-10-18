# 防守第三批：事件分布校準與 B1 離線估計

**結果：未通過全項驗收，保留 nba-defense-v1；不接防守新屬性、不改 OVR。**

二十 seed 20261012–20261031，完整30隊×82場。合併計數聯盟均值，逐隊先平均seed，母體SD；相關／RMSE的區間為成對seed整季bootstrap。勝場MAE僅列示。

## 1. 犯規條件分布與驗收

| 出手區 | 命中且犯規／機會 | 投失且犯規／機會 | 命中時犯規機率 | 投失時未計FGA的犯規機率 |
|---|---:|---:|---:|---:|
| short | 4.2234% | 13.8701% | 8.5239% | 27.2966% |
| mid | 1.8726% | 8.0494% | 4.5625% | 13.6529% |
| long | 0.2672% | 1.0275% | 0.7506% | 1.5954% |

v1原本獨立抽犯規與命中，另加andOne。新機制先抽命中，再用qMake或qMiss抽犯規，移除額外andOne；p.zone是記帳FGA分區，先依記帳率反推機會分區，避免漏算犯規投失。

`m = r / [r + (1-r)(1-qMiss)]`，因此 `r = m(1-qMiss)/(1-m*qMiss)`；qMake不影響FGA分母。

1227場；38筆射球犯規的罰球分類不完整而排除，118筆禁區犯規投失已記FGA，另列且不當成未記FGA機會。球員抽樣仍以個人FTA/FGA調整聯盟區域條件率；這項混合仍有偏差，不能稱為完全校準。

| 單回合得分 | 真實 | 候選20seed | 差異（百分點） |
|---|---:|---:|---:|
| 0 | 48.8659% | 48.5313% | -0.3345 |
| 1 | 3.4093% | 3.4970% | 0.0877 |
| 2 | 32.5137% | 31.9558% | -0.5579 |
| 3 | 15.0444% | 15.8592% | 0.8148 |
| 4 | 0.1546% | 0.1396% | -0.0150 |

單回合變異數 1.4301，目標1.41±0.03。

## 2. 失誤分類

5.42是「非24秒違例的死球失誤」，包括進攻犯規及其他違例。dead touch按實測類別拆帳；出界原因不明保留unmapped，未硬分到傳球或持球。進攻犯規加在進攻球員PF，不加防守隊bonus。

| 類別／隊／場 | 真實 | 候選20seed |
|---|---:|---:|
| liveTov | 8.4165 | 8.4862 |
| deadNoClock | 5.4189 | 5.3195 |
| clockTov | 0.6736 | 0.6842 |
| offensiveFoulTov | 1.4743 | 1.4428 |
| otherViolationTov | 0.9095 | 0.8989 |
| passOutTov | 1.7653 | 1.7285 |
| handlingOutTov | 0.9417 | 0.9273 |
| unmappedDeadTov | 0.3280 | 0.3221 |
| passSteals | 5.1365 | 5.1945 |
| touchSteals | 3.2800 | 3.2917 |

傳球／持球活球比例：真實 74.4229%／77.6931%，候選 75.0331%／78.0210%。活球數量比由v1約3.1:4.3改善至候選 5.1945:3.2917，目標5.14:3.28。

dead touch類別是校準的事件結果；傳球出界並未模擬球飛出界的物理路徑，其他違例也不是獨立場上時空判定。每類可追蹤，但不宣稱已有完整規則引擎。

## 3. 候選與逐項開關

| preset | 去均值淨勝分RMSE | 相關 | SD比 | 每分勝場 | 效率偏差 | 球權偏差 | TOV | STL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v1 | 3.5467 | 0.8205 | 0.7216 | 1.7928 | 2.4500 | -0.7762 | 14.4004 | 7.3845 |
| accounting | 3.6562 | 0.8066 | 0.7154 | 1.8470 | 0.0408 | 1.1267 | 14.9486 | 7.3943 |
| independent | 3.6983 | 0.8061 | 0.6809 | 1.7977 | 3.1017 | 0.2602 | 12.4267 | 7.4390 |
| empirical | 3.7248 | 0.8050 | 0.6663 | 1.8612 | 3.1090 | 0.1414 | 12.3684 | 7.4215 |
| fouls | 3.6958 | 0.8168 | 0.6363 | 1.8792 | 2.7396 | -3.1117 | 12.3060 | 7.3741 |
| combined | 3.4403 | 0.8444 | 0.6722 | 1.8770 | 0.4125 | -2.0919 | 14.2112 | 8.3264 |
| combined-grid | 3.5576 | 0.8225 | 0.6992 | 1.8296 | 0.3666 | -0.1889 | 14.4899 | 8.4862 |
| season-minutes | 3.7278 | 0.7976 | 0.7083 | 1.7930 | 2.4390 | -0.7455 | 14.3703 | 7.3838 |

accounting=團隊籃板＋原時鐘重校準；independent再加獨立違例；empirical再換經驗耗時（pace0.836）；fouls再改條件犯規；combined初始校準點0.8797377；combined-grid是完整賽季網格選到pace0.90。season-minutes僅v1分鐘輸入對照。以上每個機制都能以boolean獨立關閉。

| 相對v1（候選−v1） | 差異 | 成對95%區間 |
|---|---:|---:|
| net.centeredRMSE | 0.0110 | -0.1585～0.1700 |
| net.correlation | 0.0020 | -0.0190～0.0228 |
| net.sdRatio | -0.0224 | -0.0508～0.0100 |
| winPerNet | 0.0367 | -0.0250～0.1008 |

| 驗收 | 結果 | 通過 |
|---|---|---|
| efficiencyBias | 0.3666；目標 ±0.5 | 是 |
| boxPossBias | -0.1889；目標 ±0.5 | 是 |
| TOV/G | 14.4899；目標 14.510162601626016 ±0.2 | 是 |
| STL/G | 8.4862；目標 8.419918699186992 ±0.3 | 是 |
| clockViolation/G | 0.6842；目標 real0.673594; within0.02 | 是 |
| netRMSE | {"estimate":0.010966411280768362,"standardError":0.08488660389871969,"ci95":[-0.15853465426387192,0.17003905290771293]}；目標 paired95CI not significantly worse | 是 |
| netCorrelation | {"estimate":0.002042996170570688,"standardError":0.010957381504855479,"ci95":[-0.019035608901540102,0.02275471692543407]}；目標 paired95CI not significantly worse | 是 |
| netSDRatio | 0.6992；目標 >=v1 0.7216075622145449 | 否 |
| possessionPoints0 | 0.4853；目標 0.488658717245064 ±0.005 | 是 |
| possessionPoints1 | 0.0350；目標 0.034092656903935044 ±0.005 | 是 |
| possessionPoints2 | 0.3196；目標 0.3251370101432029 ±0.005 | 否 |
| possessionPoints3 | 0.1586；目標 0.15044401810071967 ±0.005 | 否 |
| possessionPoints4 | 0.0014；目標 0.001546170596854231 ±0.005 | 是 |
| possessionVariance | 1.4301；目標 1.41 ±0.03 | 是 |
| FG% | 46.7879；目標 absolute bias <=v1 | 否 |
| 3P% | 36.5838；目標 absolute bias <=v1 | 否 |
| FTR | 0.2836；目標 absolute bias <=v1 | 否 |

不存在顯著變差不等於證明非劣；本表依使用者指定「不得顯著劣於」判準列示。違例率沒有指定數值容忍度，明列採±0.02／隊／場，未將其包裝為等價性檢定。

FG%／3P%的「不退步」按點估計判定；其絕對偏差僅增加約0.020／0.025個百分點，不能當成已證實的顯著退步。另列相同seed的絕對偏差差異區間：

| 絕對偏差 候選−v1 | 差異 | 成對95%區間 |
|---|---:|---:|
| fg（百分點） | 0.0201 | -0.0658～0.1066 |
| three（百分點） | 0.0254 | -0.0739～0.1201 |
| FTR（比例） | 0.0150 | 0.0140～0.0160 |

| 逐項切換 | SD比變化 | 成對95%區間 |
|---|---:|---:|
| v1 → accounting | -0.0062 | -0.0351～0.0203 |
| accounting → independent | -0.0345 | -0.0625～-0.0023 |
| independent → empirical | -0.0146 | -0.0504～0.0224 |
| empirical → fouls | -0.0300 | -0.0615～-0.0021 |
| fouls → combined-grid | 0.0629 | 0.0329～0.0915 |

這是同seed順序開關的效果，含各步已列出的時鐘重校準及交互作用；不是唯一因果分攤。先前0.722→0.666的路徑中，由記帳到獨立違例的點估計下降最大，經驗耗時再下降一部分。舊耗時撞限失誤帶有球員傳球／持球能力差異，是可檢查的機制解釋；但開關效應本身不證明被移除的差異都是合理防守訊號，也需看上述區間。

## 4. 耗時與上一批兩表差異

上一批開關表c-empirical用pace1，二十seed用校準後pace0.836。已用同seed20261012完整賽季重跑，詳見diagnostics.json：並非同設定下的抽樣誤差。

time-audit.json量出每種起始狀態的原始均值、截斷後抽樣均值及縮放截止時間；diagnostics.json逐项對帳setup／pass／release／flight／inbound／violation／other，合計等於全場活時計秒數。

pace0.836是經驗時鐘的補償係數：原始CDF含超過24秒與跨犯規重置的長段，截斷會縮短均值；傳球抄截與非投籃犯規會提早終止抽到的截止時間；發球和籃板飛行另加時間。這些方向相反，係數不是NBA實測節奏，也不能歸因於一塊「額外時間」。

整秒CDF在21/23.9≈0.87866附近有支持集跳點。原比例校準0.87717→0.87974會新納入21秒耗時，球權數反向跳降。改用完整1230場網格0.89／0.90／0.91／0.915，以球權代理選0.90，未用勝場／球隊ID選參數。這個離散抽樣的非單調性仍存在，未偷偷更改CDF。

## 5. 變異拆解（候選診斷，沒有新基準）

候選20seed平均殘差SD 16.9423，真實 14.0275；獨立理論SD 16.8880。

| 先前28%／32%／43%來源 | 先前差（分數平方） | 候選剩餘差 ± seed SE | 剩餘／先前 |
|---|---:|---:|---:|
| singlePossessionVariance | 31.2960 | 3.6796 ± 0.0857 | 11.7575% |
| remainingSameGameCovariance | 35.8058 | 60.5805 ± 1.7506 | 169.1918% |
| withinTeamSerialAndHeterogeneity | 48.3216 | 29.3414 ± 1.8764 | 60.7211% |

候選二十seed與真實同1227場；「剩餘比例」分母沿用上一批單seed v1拆解。分數平方可加，SD不可加；序列與異質性餘項不硬歸為比分耦合。詳細分項、區間與各seed列於closeout.json。

## 6. 分鐘輸入診斷

Frozen v1 other mechanisms. Same observed active players, starter order and bench order. In-team season MPG targets rescaled to240 with48 cap; only minute targets replaced. Whole-season MPG remains future information, so this isolates outcome-dependent per-game minutes, not all possible leakage. Score variances use final scores including OT; residualSD in scoreboard uses final scores and same retrospective team-strength fit.

| 指標 | v1逐場分鐘 | 賽季MPG目標 | 差異95%區間 |
|---|---:|---:|---:|
| net.correlation | 0.8205 | 0.7976 | -0.0471～-0.0005 |
| net.sdRatio | 0.7216 | 0.7083 | -0.0381～0.0150 |
| residualSD | 17.4077 | 17.4412 | -0.1541～0.2161 |
| 單隊單場得分隊內變異 | 186.6360 | 187.1024 | -2.1978～3.5150 |

每隊30列隊內變異、SE與差異區間完整列於closeout.json。這是曝光輸入敏感度診斷；保留實測出賽、先發、替補排序及全季卡片，不能據此宣稱已排除所有洩漏。

## 7. B1離線模型

Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.

Chronological schedule date+ID, individual team game index <=41. Training requires BOTH teams in first41, excluding crossover games to avoid same-game train/test leakage. Test uses each defender team index >41, only true later lineups and opportunity weights; no later outcomes fitted.

Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=41 checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

嚴格1188場；兩隊均前41的訓練574場，測試614場。模型同時放進攻五人／防守五人，個人STL／BLK／DREB／PF與位置作先驗。每一CV折重算box先驗，不把驗證場box混進先驗；場次grouped三折決定收縮強度。後半季只用真實陣容與觀測機會加權，並不更新係數。

FTA模型保留所有標籤。罰球之間換人的零秒區段會有FTA卻無回合終點，另用零回合區段截距估計每區段計數；其餘按回合終點作曝光。這是條件區段計數模型，尚未把每顆罰球歸回犯規發生時的五人，不能直接宣稱取得可接引擎的防守犯規因果屬性。

| 指標 | 現行訊號 r / SD比 / RMSE | 先驗 | 新模型 | 新−現行RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6538 / 0.5889 / 0.0195 | 0.6712 / 0.5016 / 0.0195 | 0.8356 / 0.6260 / 0.0151 | -0.0055～-0.0021 |
| opp3 | -0.2657 / 0.9137 / 0.0241 | -0.1276 / 0.1734 / 0.0164 | -0.3243 / 0.3710 / 0.0185 | -0.0064～-0.0033 |
| liveTOVRate | 0.1658 / 0.0624 / 0.0095 | 0.6010 / 1.0214 / 0.0086 | 0.6334 / 0.9394 / 0.0080 | -0.0029～0.0001 |
| DREBRate | 0.2109 / 0.2448 / 0.0243 | 0.5458 / 0.3399 / 0.0215 | 0.7208 / 0.5338 / 0.0178 | -0.0081～-0.0037 |
| FTR | 0.4798 / 0.2828 / 0.0250 | 0.7153 / 0.5235 / 0.0201 | 0.7049 / 0.8268 / 0.0200 | -0.0078～-0.0009 |

RMSE單位為比例，例如0.01是一個百分點。禁區／中距離／三分出手比例與命中率也各列於offline-model.md。後半季比較不能宣稱全項合格：三分相關、SD比與只用先驗的比較仍須看完整表；顯著RMSE改善也可能只是把不穩定訊號收縮回均值。離線係數保留，這批不接引擎。

## 8. 已驗證與仍不確定

- 已驗證：v1犯規／命中獨立、四分回合過量來源；相同seed的pace差異；整秒CDF支持集跳點；單機／worker比分一致；分類帳、分鐘240與48上限；離線各模型收斂。
- 聯盟分區犯規率再以球員總FTA/FGA縮放，可能重複計入分區與造犯規能力的相關；FTR仍偏高，未用命中率或OVR補丁遮掩。
- 三分得分回合仍偏多。既有分區出手選擇與重複籃板機會可能有貢獻，但本批尚未證實各自原因。
- 分鐘輸入只作敏感度診斷，沒有排除替補排序或全季卡片資訊，也不能證明實測逐場分鐘是外生輸入。
- 離線測試場bootstrap固定已估係數；尚未重訓以估計模型不確定性，也尚未跨賽季驗證。
- 訓練要求兩隊均在前41，比單隊前41更嚴格。現行追蹤訊號使用各隊前41的官方資料，仍含被嚴格區段篩選排除的前半季場次。
- 本批未修改比分相依輪替、同場共變異或球隊節奏，也未用球隊ID／勝場補丁。

offline-model.json/md是正式前41追蹤＋完整CV＋全FTA對照；fullsignal、coarse-cv與positive-fta檔為保留的中間診斷，不作本批結論。

重跑用直接node命令，Windows npm轉送旗標容易被剝除：`node scripts/run_defense_third_seeds.js combined-grid`、`node scripts/audit_defense_third_seeds.js combined-grid`、`python scripts/estimate_defense_third.py`。

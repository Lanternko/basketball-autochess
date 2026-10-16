# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.5155 / 0.5658 / 0.0183 | 0.3464 / 0.4785 / 0.0202 | 0.5753 / 0.5422 / 0.0175 | [-0.003, 0.0013] |
| opp3 | 0.0603 / 0.6096 / 0.0198 | -0.0462 / 0.2210 / 0.0180 | -0.0381 / 0.2830 / 0.0183 | [-0.0031, 0.0004] |
| liveTOVRate | -0.1503 / 0.1470 / 0.0088 | 0.5142 / 1.0110 / 0.0084 | 0.5898 / 0.9560 / 0.0075 | [-0.0026, 0.0005] |
| DREBRate | 0.2225 / 0.2733 / 0.0201 | 0.3695 / 0.5391 / 0.0194 | 0.5147 / 0.7149 / 0.0181 | [-0.005, 0.0013] |
| FTR | 0.6793 / 0.2618 / 0.0226 | 0.6698 / 0.6949 / 0.0199 | 0.5956 / 0.9132 / 0.0231 | [-0.0041, 0.0047] |
| shortShare | 0.0655 / 0.1546 / 0.0231 | 0.4965 / 0.4262 / 0.0201 | 0.6180 / 0.8245 / 0.0187 | [-0.0083, -0.0001] |
| midShare | 0.2490 / 0.2418 / 0.0109 | 0.5002 / 0.2312 / 0.0102 | 0.7678 / 0.9111 / 0.0074 | [-0.0063, -0.0007] |
| threeShare | 0.1288 / 0.1508 / 0.0225 | 0.4156 / 0.3937 / 0.0206 | 0.6506 / 1.0187 / 0.0191 | [-0.0082, 0.001] |
| shortFG | 0.4972 / 0.5630 / 0.0213 | 0.3571 / 0.4656 / 0.0230 | 0.5018 / 0.5186 / 0.0211 | [-0.0027, 0.002] |
| midFG | -0.2290 / 0.1335 / 0.0417 | -0.0687 / 0.2764 / 0.0424 | 0.2461 / 0.2901 / 0.0390 | [-0.0048, 0.0003] |

訓練 726 場；測試 365 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

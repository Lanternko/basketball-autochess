# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.4723 / 0.8896 / 0.0184 | 0.5679 / 0.7138 / 0.0157 | 0.6155 / 0.8252 / 0.0154 | [-0.0046, -0.0002] |
| opp3 | 0.2345 / 0.6788 / 0.0207 | -0.0511 / 0.1719 / 0.0198 | 0.1210 / 0.1937 / 0.0192 | [-0.0039, 0.001] |
| liveTOVRate | 0.4452 / 0.2092 / 0.0089 | 0.6509 / 0.7292 / 0.0073 | 0.6617 / 0.7283 / 0.0072 | [-0.0026, -0.0004] |
| DREBRate | 0.2569 / 0.2164 / 0.0167 | 0.6391 / 0.5316 / 0.0134 | 0.7728 / 0.8109 / 0.0110 | [-0.0074, -0.0015] |
| FTR | 0.5215 / 0.3881 / 0.0209 | 0.8218 / 0.8715 / 0.0139 | 0.8397 / 0.9835 / 0.0136 | [-0.0105, -0.0018] |
| shortShare | 0.4282 / 0.2244 / 0.0209 | 0.4397 / 0.4072 / 0.0202 | 0.6166 / 0.8550 / 0.0185 | [-0.0057, 0.0004] |
| midShare | 0.2616 / 0.2958 / 0.0113 | 0.0742 / 0.3630 / 0.0122 | 0.6715 / 0.9030 / 0.0091 | [-0.0054, -0.0003] |
| threeShare | 0.4551 / 0.2826 / 0.0239 | 0.4281 / 0.3759 / 0.0239 | 0.6249 / 0.7516 / 0.0208 | [-0.0066, -0.0003] |
| shortFG | 0.5281 / 0.9496 / 0.0211 | 0.5891 / 0.7360 / 0.0183 | 0.5890 / 0.8632 / 0.0190 | [-0.0043, 0.0006] |
| midFG | 0.0342 / 0.0860 / 0.0294 | 0.3472 / 0.2465 / 0.0277 | 0.3426 / 0.2576 / 0.0277 | [-0.0033, 0.0007] |

訓練 532 場；測試 547 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

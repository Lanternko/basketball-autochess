# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=41 checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6599 / 0.5522 / 0.0194 | 0.8299 / 0.5526 / 0.0160 | 0.9612 / 0.7948 / 0.0083 | [-0.011, -0.0068] |
| opp3 | -0.2625 / 0.4432 / 0.0189 | 0.3643 / 0.2190 / 0.0149 | 0.7200 / 0.2921 / 0.0129 | [-0.006, -0.0038] |
| liveTOVRate | 0.2769 / 0.0501 / 0.0094 | 0.9262 / 0.9613 / 0.0036 | 0.9592 / 0.9345 / 0.0027 | [-0.0069, -0.0041] |
| DREBRate | 0.1425 / 0.2238 / 0.0247 | 0.8004 / 0.4786 / 0.0169 | 0.9693 / 0.7931 / 0.0075 | [-0.0173, -0.0116] |
| FTR | 0.5143 / 0.2631 / 0.0248 | 0.8558 / 0.6488 / 0.0155 | 0.9701 / 0.8859 / 0.0071 | [-0.0186, -0.0118] |
| shortShare | 0.2408 / 0.1573 / 0.0276 | 0.4828 / 0.3536 / 0.0250 | 0.9731 / 0.8062 / 0.0080 | [-0.0211, -0.0152] |
| midShare | 0.4461 / 0.2038 / 0.0119 | 0.7078 / 0.3634 / 0.0101 | 0.9608 / 0.8957 / 0.0037 | [-0.01, -0.0049] |
| threeShare | 0.2972 / 0.1496 / 0.0233 | 0.2306 / 0.2684 / 0.0235 | 0.9566 / 0.7958 / 0.0080 | [-0.0179, -0.0116] |
| shortFG | 0.6862 / 0.6108 / 0.0187 | 0.8669 / 0.5896 / 0.0146 | 0.9771 / 0.8282 / 0.0066 | [-0.011, -0.0065] |
| midFG | 0.4060 / 0.1983 / 0.0271 | 0.3973 / 0.2362 / 0.0269 | 0.7668 / 0.3527 / 0.0221 | [-0.0056, -0.0019] |

訓練 1188 場；測試 614 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

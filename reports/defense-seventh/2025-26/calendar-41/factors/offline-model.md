# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6359 / 0.6082 / 0.0196 | 0.6607 / 0.5088 / 0.0194 | 0.8273 / 0.6438 / 0.0150 | [-0.0057, -0.0022] |
| opp3 | -0.3057 / 0.8605 / 0.0251 | -0.0500 / 0.2033 / 0.0172 | -0.2762 / 0.3489 / 0.0191 | [-0.0068, -0.0035] |
| liveTOVRate | 0.1961 / 0.0631 / 0.0097 | 0.6033 / 0.9823 / 0.0086 | 0.6317 / 0.9131 / 0.0081 | [-0.0029, -0.0] |
| DREBRate | 0.2154 / 0.2458 / 0.0242 | 0.5341 / 0.3454 / 0.0214 | 0.6971 / 0.5345 / 0.0182 | [-0.0077, -0.0034] |
| FTR | 0.4789 / 0.2908 / 0.0244 | 0.7446 / 0.5297 / 0.0190 | 0.7126 / 0.8512 / 0.0194 | [-0.0083, -0.001] |
| shortShare | 0.1016 / 0.1407 / 0.0276 | 0.2525 / 0.3576 / 0.0269 | 0.5946 / 0.6454 / 0.0223 | [-0.0083, -0.0023] |
| midShare | 0.3314 / 0.1688 / 0.0120 | 0.5508 / 0.2749 / 0.0110 | 0.6952 / 0.8401 / 0.0092 | [-0.0051, -0.0006] |
| threeShare | 0.1261 / 0.1154 / 0.0241 | 0.0574 / 0.2934 / 0.0249 | 0.3949 / 0.6804 / 0.0234 | [-0.0044, 0.0015] |
| shortFG | 0.6621 / 0.6821 / 0.0193 | 0.6246 / 0.5579 / 0.0201 | 0.8137 / 0.6749 / 0.0154 | [-0.0052, -0.0013] |
| midFG | 0.3691 / 0.1743 / 0.0264 | 0.2701 / 0.3578 / 0.0268 | 0.3062 / 0.4049 / 0.0266 | [-0.002, 0.0024] |

訓練 588 場；測試 600 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.4885 / 0.6693 / 0.0167 | 0.3166 / 0.5471 / 0.0183 | 0.5428 / 0.6679 / 0.0159 | [-0.0026, 0.0014] |
| opp3 | -0.0120 / 0.8241 / 0.0189 | -0.0700 / 0.3070 / 0.0154 | -0.0961 / 0.3810 / 0.0160 | [-0.0042, -0.0002] |
| liveTOVRate | 0.0623 / 0.2556 / 0.0085 | 0.6490 / 0.9460 / 0.0068 | 0.6432 / 0.9296 / 0.0068 | [-0.0028, -0.0001] |
| DREBRate | 0.0686 / 0.2865 / 0.0170 | 0.2968 / 0.7084 / 0.0173 | 0.4445 / 0.9226 / 0.0169 | [-0.004, 0.0027] |
| FTR | 0.7825 / 0.2754 / 0.0202 | 0.8243 / 0.7105 / 0.0145 | 0.7103 / 0.9276 / 0.0185 | [-0.0051, 0.0031] |
| shortShare | -0.0629 / 0.1482 / 0.0228 | 0.3755 / 0.4234 / 0.0207 | 0.4895 / 0.6690 / 0.0199 | [-0.0059, -0.0003] |
| midShare | 0.1675 / 0.2439 / 0.0116 | 0.3177 / 0.2303 / 0.0112 | 0.6375 / 0.8148 / 0.0093 | [-0.0045, -0.0003] |
| threeShare | 0.1270 / 0.1038 / 0.0230 | 0.3530 / 0.3691 / 0.0217 | 0.6692 / 0.7414 / 0.0173 | [-0.0086, -0.0023] |
| shortFG | 0.5131 / 0.6978 / 0.0179 | 0.3580 / 0.5304 / 0.0194 | 0.5480 / 0.6341 / 0.0171 | [-0.003, 0.0015] |
| midFG | -0.2672 / 0.1184 / 0.0412 | 0.0450 / 0.3588 / 0.0416 | 0.0468 / 0.3587 / 0.0416 | [-0.0022, 0.0029] |

訓練 539 場；測試 552 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

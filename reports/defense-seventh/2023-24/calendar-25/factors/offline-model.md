# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.4631 / 1.0215 / 0.0179 | 0.6554 / 0.7498 / 0.0130 | 0.6656 / 0.8974 / 0.0133 | [-0.0062, -0.0016] |
| opp3 | 0.2651 / 1.2054 / 0.0168 | 0.0926 / 0.4880 / 0.0134 | 0.2604 / 0.5926 / 0.0128 | [-0.0055, -0.0009] |
| liveTOVRate | 0.2564 / 0.1446 / 0.0058 | 0.5406 / 1.7592 / 0.0088 | 0.5732 / 1.6847 / 0.0082 | [0.0004, 0.0037] |
| DREBRate | 0.1070 / 0.4045 / 0.0164 | 0.4356 / 0.6182 / 0.0145 | 0.5084 / 0.8961 / 0.0149 | [-0.0043, 0.0014] |
| FTR | 0.5910 / 0.3223 / 0.0213 | 0.6307 / 0.7798 / 0.0198 | 0.6130 / 0.9906 / 0.0219 | [-0.0032, 0.0042] |
| shortShare | -0.0352 / 0.1660 / 0.0207 | 0.4797 / 0.3779 / 0.0179 | 0.6808 / 1.0998 / 0.0171 | [-0.0071, 0.0002] |
| midShare | 0.1603 / 0.3506 / 0.0100 | 0.2501 / 0.4658 / 0.0099 | 0.6546 / 0.8091 / 0.0077 | [-0.0035, -0.0003] |
| threeShare | 0.1388 / 0.1381 / 0.0240 | 0.4217 / 0.3603 / 0.0221 | 0.7217 / 0.9749 / 0.0179 | [-0.0092, -0.0027] |
| shortFG | 0.4570 / 1.1069 / 0.0202 | 0.6251 / 0.7195 / 0.0144 | 0.5721 / 0.8612 / 0.0160 | [-0.0064, -0.0015] |
| midFG | 0.3783 / 0.2375 / 0.0184 | 0.3832 / 0.5463 / 0.0184 | 0.2660 / 0.8295 / 0.0219 | [-0.0018, 0.0064] |

訓練 322 場；測試 741 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.4568 / 1.0779 / 0.0170 | 0.6843 / 0.8100 / 0.0116 | 0.7407 / 0.8639 / 0.0107 | [-0.0076, -0.0022] |
| opp3 | 0.2072 / 1.1685 / 0.0201 | -0.0249 / 0.3892 / 0.0159 | 0.1880 / 0.4861 / 0.0150 | [-0.0066, -0.0018] |
| liveTOVRate | 0.3371 / 0.3048 / 0.0085 | 0.4469 / 0.7905 / 0.0086 | 0.4530 / 0.7821 / 0.0086 | [-0.0009, 0.001] |
| DREBRate | -0.0215 / 0.2170 / 0.0168 | 0.7117 / 0.6020 / 0.0116 | 0.7073 / 0.8016 / 0.0116 | [-0.0068, -0.0018] |
| FTR | 0.6742 / 0.2946 / 0.0188 | 0.6887 / 0.9185 / 0.0172 | 0.7686 / 1.0557 / 0.0159 | [-0.0066, 0.0014] |
| shortShare | 0.3679 / 0.4068 / 0.0196 | 0.5563 / 0.4037 / 0.0178 | 0.7019 / 0.8493 / 0.0154 | [-0.0071, -0.0015] |
| midShare | 0.5034 / 0.2327 / 0.0092 | 0.1800 / 0.4830 / 0.0105 | 0.6377 / 1.1169 / 0.0092 | [-0.0029, 0.0019] |
| threeShare | 0.3961 / 0.3941 / 0.0223 | 0.3589 / 0.2946 / 0.0228 | 0.6045 / 0.7818 / 0.0199 | [-0.0055, -0.0001] |
| shortFG | 0.4947 / 1.0286 / 0.0203 | 0.6248 / 0.7183 / 0.0157 | 0.6340 / 0.7537 / 0.0156 | [-0.0063, -0.0013] |
| midFG | 0.0267 / 0.2949 / 0.0279 | -0.0523 / 0.4932 / 0.0307 | -0.0949 / 0.5540 / 0.0321 | [0.0006, 0.0065] |

訓練 315 場；測試 764 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

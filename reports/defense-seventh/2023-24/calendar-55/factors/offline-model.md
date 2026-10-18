# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.3903 / 0.9046 / 0.0192 | 0.4720 / 0.6284 / 0.0163 | 0.5947 / 0.8058 / 0.0151 | [-0.0057, -0.0008] |
| opp3 | 0.3421 / 0.7930 / 0.0179 | 0.1086 / 0.2311 / 0.0172 | 0.1596 / 0.4585 / 0.0177 | [-0.0024, 0.0023] |
| liveTOVRate | 0.2817 / 0.2414 / 0.0070 | 0.5112 / 1.0764 / 0.0075 | 0.5659 / 1.0242 / 0.0068 | [-0.0017, 0.0013] |
| DREBRate | 0.1546 / 0.2867 / 0.0201 | 0.3486 / 0.3456 / 0.0189 | 0.3599 / 0.5048 / 0.0191 | [-0.0038, 0.0017] |
| FTR | 0.6051 / 0.3415 / 0.0240 | 0.7625 / 0.7015 / 0.0186 | 0.8072 / 0.8529 / 0.0169 | [-0.0096, -0.0018] |
| shortShare | -0.1382 / 0.1884 / 0.0244 | 0.2031 / 0.3194 / 0.0230 | 0.6521 / 0.8501 / 0.0183 | [-0.0091, -0.0013] |
| midShare | 0.1673 / 0.2613 / 0.0120 | 0.3585 / 0.3991 / 0.0113 | 0.7065 / 0.8560 / 0.0088 | [-0.0056, -0.0003] |
| threeShare | -0.0868 / 0.1017 / 0.0286 | 0.2823 / 0.3301 / 0.0270 | 0.7428 / 0.7949 / 0.0189 | [-0.0128, -0.0051] |
| shortFG | 0.3035 / 1.0743 / 0.0225 | 0.4138 / 0.7020 / 0.0175 | 0.5184 / 0.8815 / 0.0170 | [-0.0071, -0.0014] |
| midFG | 0.1841 / 0.0808 / 0.0351 | 0.2879 / 0.2423 / 0.0340 | 0.1950 / 0.2951 / 0.0350 | [-0.0025, 0.0021] |

訓練 715 場；測試 348 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

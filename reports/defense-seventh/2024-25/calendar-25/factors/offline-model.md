# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.4676 / 0.9495 / 0.0164 | 0.3122 / 0.7793 / 0.0173 | 0.4961 / 0.8372 / 0.0152 | [-0.0032, 0.0013] |
| opp3 | 0.1903 / 0.9881 / 0.0141 | 0.0758 / 0.5278 / 0.0122 | 0.1072 / 0.5327 / 0.0120 | [-0.0038, 0.0011] |
| liveTOVRate | 0.3173 / 0.3224 / 0.0073 | 0.6605 / 1.1990 / 0.0071 | 0.6693 / 1.2024 / 0.0070 | [-0.0018, 0.0013] |
| DREBRate | 0.2212 / 0.2464 / 0.0153 | 0.4767 / 0.7375 / 0.0144 | 0.4772 / 0.9656 / 0.0157 | [-0.0024, 0.0032] |
| FTR | 0.7054 / 0.2589 / 0.0205 | 0.7449 / 0.8190 / 0.0164 | 0.7196 / 0.9304 / 0.0178 | [-0.0053, 0.0009] |
| shortShare | -0.0331 / 0.2238 / 0.0186 | 0.3760 / 0.4065 / 0.0167 | 0.3763 / 0.9779 / 0.0199 | [-0.0023, 0.0038] |
| midShare | 0.1574 / 0.1940 / 0.0115 | 0.2910 / 0.2481 / 0.0111 | 0.7235 / 0.7300 / 0.0080 | [-0.0049, -0.0018] |
| threeShare | -0.0139 / 0.1096 / 0.0210 | 0.2862 / 0.3423 / 0.0200 | 0.5420 / 0.9491 / 0.0194 | [-0.0052, 0.0017] |
| shortFG | 0.4337 / 0.9232 / 0.0184 | 0.3051 / 0.7441 / 0.0188 | 0.4342 / 0.7801 / 0.0173 | [-0.0034, 0.0014] |
| midFG | 0.0001 / 0.2954 / 0.0354 | 0.1628 / 0.5872 / 0.0364 | 0.2274 / 0.5887 / 0.0352 | [-0.0033, 0.0034] |

訓練 319 場；測試 772 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

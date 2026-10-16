# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6169 / 0.6955 / 0.0187 | 0.5926 / 0.6118 / 0.0190 | 0.6655 / 0.7520 / 0.0177 | [-0.0025, 0.001] |
| opp3 | -0.1669 / 1.2678 / 0.0229 | 0.2939 / 0.3395 / 0.0126 | -0.0561 / 0.4794 / 0.0149 | [-0.0087, -0.0052] |
| liveTOVRate | 0.1645 / 0.0404 / 0.0094 | 0.5129 / 1.0231 / 0.0094 | 0.5148 / 0.9707 / 0.0091 | [-0.0015, 0.0011] |
| DREBRate | 0.3286 / 0.2827 / 0.0209 | 0.4532 / 0.3956 / 0.0198 | 0.5518 / 0.5741 / 0.0185 | [-0.0045, -0.0002] |
| FTR | 0.4993 / 0.3020 / 0.0221 | 0.5402 / 0.6065 / 0.0210 | 0.6044 / 0.7629 / 0.0202 | [-0.0048, 0.0011] |
| shortShare | 0.1366 / 0.1651 / 0.0250 | 0.2918 / 0.3741 / 0.0242 | 0.6272 / 0.7667 / 0.0199 | [-0.0079, -0.0021] |
| midShare | 0.3566 / 0.3028 / 0.0110 | 0.5015 / 0.3488 / 0.0103 | 0.6892 / 0.9313 / 0.0089 | [-0.0041, -0.0002] |
| threeShare | -0.1474 / 0.0992 / 0.0222 | 0.0644 / 0.3163 / 0.0225 | 0.5987 / 0.7759 / 0.0179 | [-0.0073, -0.0017] |
| shortFG | 0.6683 / 0.7591 / 0.0179 | 0.5792 / 0.6555 / 0.0196 | 0.6604 / 0.7943 / 0.0183 | [-0.002, 0.0023] |
| midFG | 0.0729 / 0.2803 / 0.0247 | 0.3548 / 0.4627 / 0.0228 | 0.3697 / 0.4608 / 0.0226 | [-0.0039, 0.0012] |

訓練 366 場；測試 822 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

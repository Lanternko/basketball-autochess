# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6154 / 0.5652 / 0.0223 | 0.6938 / 0.4878 / 0.0211 | 0.8018 / 0.6400 / 0.0175 | [-0.006, -0.0021] |
| opp3 | 0.0400 / 0.5909 / 0.0215 | 0.2625 / 0.1800 / 0.0182 | 0.2404 / 0.1827 / 0.0183 | [-0.0048, -0.0004] |
| liveTOVRate | 0.0879 / 0.0870 / 0.0103 | 0.6573 / 0.9784 / 0.0085 | 0.6622 / 0.9488 / 0.0083 | [-0.0034, -0.0001] |
| DREBRate | 0.2006 / 0.2222 / 0.0275 | 0.6766 / 0.3930 / 0.0222 | 0.6364 / 0.6934 / 0.0217 | [-0.009, -0.0013] |
| FTR | 0.4284 / 0.3153 / 0.0244 | 0.7346 / 0.6564 / 0.0183 | 0.7180 / 0.9916 / 0.0200 | [-0.0082, 0.0003] |
| shortShare | 0.0802 / 0.1206 / 0.0296 | 0.3897 / 0.3380 / 0.0274 | 0.7549 / 0.6848 / 0.0196 | [-0.0136, -0.006] |
| midShare | 0.5468 / 0.1432 / 0.0121 | 0.6667 / 0.3145 / 0.0108 | 0.7307 / 0.8374 / 0.0090 | [-0.0064, -0.0003] |
| threeShare | 0.1101 / 0.1062 / 0.0268 | 0.1839 / 0.2723 / 0.0266 | 0.6808 / 0.6775 / 0.0197 | [-0.0115, -0.0032] |
| shortFG | 0.6462 / 0.6250 / 0.0216 | 0.6911 / 0.5050 / 0.0211 | 0.7882 / 0.6606 / 0.0178 | [-0.0053, -0.0009] |
| midFG | 0.3143 / 0.1958 / 0.0326 | 0.2245 / 0.2887 / 0.0333 | 0.2615 / 0.3200 / 0.0329 | [-0.0019, 0.0026] |

訓練 796 場；測試 392 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

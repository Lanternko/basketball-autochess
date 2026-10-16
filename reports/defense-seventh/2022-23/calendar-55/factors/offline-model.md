# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.3350 / 0.7294 / 0.0209 | 0.4277 / 0.6751 / 0.0192 | 0.5648 / 0.7890 / 0.0175 | [-0.0053, -0.0] |
| opp3 | 0.5015 / 0.5969 / 0.0175 | 0.1906 / 0.1835 / 0.0197 | 0.5729 / 0.3724 / 0.0169 | [-0.0026, 0.0017] |
| liveTOVRate | 0.3896 / 0.2355 / 0.0089 | 0.6714 / 0.7670 / 0.0071 | 0.6782 / 0.7734 / 0.0071 | [-0.0029, -0.0002] |
| DREBRate | 0.2712 / 0.1913 / 0.0194 | 0.6608 / 0.4663 / 0.0156 | 0.6087 / 0.7641 / 0.0163 | [-0.0064, 0.0006] |
| FTR | 0.5536 / 0.3883 / 0.0236 | 0.7343 / 0.7528 / 0.0189 | 0.7213 / 0.8756 / 0.0197 | [-0.0082, 0.0009] |
| shortShare | 0.3100 / 0.2001 / 0.0247 | 0.4497 / 0.3962 / 0.0230 | 0.6019 / 0.7877 / 0.0211 | [-0.0076, 0.0003] |
| midShare | 0.1153 / 0.2753 / 0.0139 | -0.0472 / 0.3889 / 0.0150 | 0.5803 / 0.8650 / 0.0119 | [-0.0058, 0.0004] |
| threeShare | 0.4326 / 0.2446 / 0.0268 | 0.3609 / 0.3236 / 0.0271 | 0.6452 / 0.7340 / 0.0224 | [-0.009, -0.0011] |
| shortFG | 0.4178 / 0.7872 / 0.0231 | 0.5031 / 0.6828 / 0.0208 | 0.6080 / 0.8176 / 0.0193 | [-0.0059, 0.0] |
| midFG | -0.2698 / 0.0481 / 0.0350 | 0.3113 / 0.2062 / 0.0330 | 0.3390 / 0.2203 / 0.0327 | [-0.0033, 0.0003] |

訓練 725 場；測試 354 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

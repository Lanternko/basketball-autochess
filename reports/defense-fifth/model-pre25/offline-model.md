# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前25場，測試依防守球隊截止25後場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first25 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6131 / 0.7204 / 0.0188 | 0.6384 / 0.6389 / 0.0181 | 0.6948 / 0.7753 / 0.0171 | [-0.0036, 0.0002] |
| opp3 | -0.2168 / 1.3409 / 0.0245 | 0.2804 / 0.3862 / 0.0129 | -0.0535 / 0.5306 / 0.0154 | [-0.0097, -0.0064] |
| liveTOVRate | 0.0823 / 0.0535 / 0.0094 | 0.4837 / 0.9990 / 0.0096 | 0.4884 / 0.9507 / 0.0094 | [-0.0015, 0.0012] |
| DREBRate | 0.3166 / 0.2902 / 0.0209 | 0.4697 / 0.3957 / 0.0195 | 0.5578 / 0.5722 / 0.0183 | [-0.0047, -0.0001] |
| FTR | 0.4889 / 0.3058 / 0.0223 | 0.5752 / 0.6081 / 0.0205 | 0.6082 / 0.7601 / 0.0202 | [-0.0047, 0.0007] |
| shortShare | 0.1689 / 0.1685 / 0.0250 | 0.3195 / 0.3638 / 0.0241 | 0.6328 / 0.7871 / 0.0201 | [-0.0076, -0.0021] |
| midShare | 0.3916 / 0.2783 / 0.0109 | 0.5019 / 0.3530 / 0.0103 | 0.6914 / 0.8869 / 0.0088 | [-0.0041, -0.0002] |
| threeShare | -0.0006 / 0.1015 / 0.0223 | 0.1032 / 0.3200 / 0.0226 | 0.6099 / 0.7929 / 0.0180 | [-0.0071, -0.0014] |
| shortFG | 0.6462 / 0.7921 / 0.0186 | 0.6363 / 0.6764 / 0.0185 | 0.6915 / 0.8147 / 0.0175 | [-0.0033, 0.0013] |
| midFG | 0.1378 / 0.2699 / 0.0243 | 0.3197 / 0.4716 / 0.0234 | 0.3541 / 0.4867 / 0.0230 | [-0.0038, 0.0018] |

訓練 352 場；測試 836 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

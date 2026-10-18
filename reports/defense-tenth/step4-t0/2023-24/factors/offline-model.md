# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| opp3 | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| liveTOVRate | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| DREBRate | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| FTR | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| shortShare | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| midShare | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| threeShare | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| shortFG | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |
| midFG | nan / nan / 0.0000 | nan / nan / 0.0000 | nan / nan / 0.0000 | [0.0, 0.0] |

訓練 1063 場；測試 0 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

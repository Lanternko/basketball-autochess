# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前55場，測試依防守球隊截止55後場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first55 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6259 / 0.5629 / 0.0220 | 0.7166 / 0.4822 / 0.0207 | 0.8303 / 0.6344 / 0.0166 | [-0.0064, -0.0023] |
| opp3 | -0.0409 / 0.5682 / 0.0233 | 0.2644 / 0.1841 / 0.0193 | 0.2225 / 0.1810 / 0.0194 | [-0.0053, -0.0009] |
| liveTOVRate | 0.0404 / 0.0919 / 0.0103 | 0.6394 / 0.9816 / 0.0086 | 0.6421 / 0.9563 / 0.0085 | [-0.0032, -0.0] |
| DREBRate | 0.2460 / 0.2258 / 0.0283 | 0.6772 / 0.3778 / 0.0232 | 0.6352 / 0.6967 / 0.0226 | [-0.0095, -0.0017] |
| FTR | 0.4496 / 0.2990 / 0.0251 | 0.7369 / 0.6152 / 0.0190 | 0.7197 / 0.9493 / 0.0203 | [-0.0089, 0.0001] |
| shortShare | 0.0684 / 0.1209 / 0.0295 | 0.3418 / 0.3507 / 0.0277 | 0.7495 / 0.7168 / 0.0195 | [-0.0131, -0.0057] |
| midShare | 0.5420 / 0.1531 / 0.0120 | 0.6495 / 0.3097 / 0.0108 | 0.7206 / 0.8227 / 0.0091 | [-0.0061, -0.0006] |
| threeShare | 0.0546 / 0.1105 / 0.0264 | 0.1403 / 0.2899 / 0.0264 | 0.6770 / 0.7039 / 0.0194 | [-0.0112, -0.0032] |
| shortFG | 0.6451 / 0.6192 / 0.0218 | 0.6935 / 0.4953 / 0.0213 | 0.8091 / 0.6477 / 0.0174 | [-0.0059, -0.0013] |
| midFG | 0.3372 / 0.2107 / 0.0295 | 0.3403 / 0.3155 / 0.0292 | 0.3873 / 0.3536 / 0.0287 | [-0.0028, 0.0017] |

訓練 781 場；測試 407 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

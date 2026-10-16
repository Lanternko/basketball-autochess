# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=cutoff checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.4273 / 0.7842 / 0.0193 | 0.5453 / 0.5799 / 0.0166 | 0.6582 / 0.7052 / 0.0150 | [-0.0056, -0.0014] |
| opp3 | 0.1758 / 0.9829 / 0.0196 | -0.0485 / 0.4273 / 0.0170 | 0.0019 / 0.4816 / 0.0170 | [-0.0043, 0.0004] |
| liveTOVRate | 0.3961 / 0.3043 / 0.0060 | 0.5433 / 1.3449 / 0.0075 | 0.5699 / 1.2782 / 0.0070 | [-0.0007, 0.0021] |
| DREBRate | -0.0410 / 0.3091 / 0.0188 | 0.4159 / 0.4213 / 0.0161 | 0.4196 / 0.6268 / 0.0165 | [-0.0046, 0.0004] |
| FTR | 0.6611 / 0.3092 / 0.0226 | 0.7237 / 0.6905 / 0.0189 | 0.7074 / 0.9744 / 0.0206 | [-0.0059, 0.0025] |
| shortShare | 0.0949 / 0.2138 / 0.0221 | 0.3127 / 0.3181 / 0.0209 | 0.5867 / 1.0079 / 0.0201 | [-0.006, 0.0019] |
| midShare | 0.2651 / 0.2450 / 0.0117 | 0.2785 / 0.4141 / 0.0118 | 0.7592 / 0.8431 / 0.0080 | [-0.0054, -0.0012] |
| threeShare | 0.0814 / 0.1007 / 0.0273 | 0.3604 / 0.2976 / 0.0256 | 0.6933 / 0.8631 / 0.0202 | [-0.0102, -0.0035] |
| shortFG | 0.4344 / 0.9482 / 0.0207 | 0.5222 / 0.6533 / 0.0173 | 0.6124 / 0.7771 / 0.0161 | [-0.0061, -0.0012] |
| midFG | 0.4204 / 0.0785 / 0.0254 | 0.3065 / 0.3104 / 0.0249 | 0.1800 / 0.3786 / 0.0263 | [-0.0017, 0.0028] |

訓練 530 場；測試 533 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

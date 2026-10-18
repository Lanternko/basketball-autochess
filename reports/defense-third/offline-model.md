# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=41 checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.6538 / 0.5889 / 0.0195 | 0.6712 / 0.5016 / 0.0195 | 0.8356 / 0.6260 / 0.0151 | [-0.0055, -0.0021] |
| opp3 | -0.2657 / 0.9137 / 0.0241 | -0.1276 / 0.1734 / 0.0164 | -0.3243 / 0.3710 / 0.0185 | [-0.0064, -0.0033] |
| liveTOVRate | 0.1658 / 0.0624 / 0.0095 | 0.6010 / 1.0214 / 0.0086 | 0.6334 / 0.9394 / 0.0080 | [-0.0029, 0.0001] |
| DREBRate | 0.2109 / 0.2448 / 0.0243 | 0.5458 / 0.3399 / 0.0215 | 0.7208 / 0.5338 / 0.0178 | [-0.0081, -0.0037] |
| FTR | 0.4798 / 0.2828 / 0.0250 | 0.7153 / 0.5235 / 0.0201 | 0.7049 / 0.8268 / 0.0200 | [-0.0078, -0.0009] |
| shortShare | 0.0847 / 0.1405 / 0.0282 | 0.2592 / 0.3560 / 0.0275 | 0.5925 / 0.6362 / 0.0228 | [-0.0085, -0.0024] |
| midShare | 0.3491 / 0.1595 / 0.0123 | 0.5205 / 0.2714 / 0.0114 | 0.6789 / 0.8354 / 0.0097 | [-0.0053, -0.0004] |
| threeShare | 0.0956 / 0.1208 / 0.0240 | 0.0854 / 0.3018 / 0.0246 | 0.4232 / 0.6884 / 0.0227 | [-0.005, 0.0011] |
| shortFG | 0.6837 / 0.6698 / 0.0187 | 0.6368 / 0.5521 / 0.0198 | 0.8257 / 0.6596 / 0.0150 | [-0.0052, -0.0009] |
| midFG | 0.4106 / 0.1634 / 0.0273 | 0.3260 / 0.3570 / 0.0273 | 0.3185 / 0.3966 / 0.0275 | [-0.0019, 0.0026] |

訓練 574 場；測試 614 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

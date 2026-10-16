# B1 離線時間切分估計

嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。
Existing onBall/help tracking cards are full-season; no pre41 closest-defender tracking cache exists. Current baseline is an optimistic full-season-signal comparator, with train-only mapping coefficients, NOT a clean temporal baseline. Other methods use training games only, including CV box priors recomputed excluding validation games.

| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |
|---|---:|---:|---:|---:|
| opp2 | 0.7770 / 0.6556 / 0.0164 | 0.6712 / 0.5016 / 0.0195 | 0.8679 / 0.7155 / 0.0133 | [-0.0046, -0.0003] |
| opp3 | 0.6762 / 0.6428 / 0.0117 | -0.1276 / 0.1734 / 0.0164 | -0.2903 / 0.2268 / 0.0172 | [0.0022, 0.0062] |
| liveTOVRate | 0.1871 / 0.1192 / 0.0094 | 0.6010 / 1.0214 / 0.0086 | 0.6334 / 0.9394 / 0.0080 | [-0.0028, 0.0001] |
| DREBRate | 0.3294 / 0.3066 / 0.0235 | 0.5458 / 0.3399 / 0.0215 | 0.7208 / 0.5338 / 0.0178 | [-0.0073, -0.0028] |
| FTR | 0.5909 / 0.3634 / 0.0233 | 0.7462 / 0.5169 / 0.0196 | 0.7317 / 0.8248 / 0.0191 | [-0.0072, 0.0] |
| shortShare | -0.0435 / 0.1664 / 0.0289 | 0.2592 / 0.3560 / 0.0275 | 0.5755 / 0.6307 / 0.0232 | [-0.0086, -0.003] |
| midShare | 0.4124 / 0.1891 / 0.0121 | 0.5205 / 0.2714 / 0.0114 | 0.6747 / 0.7000 / 0.0095 | [-0.0048, -0.0007] |
| threeShare | -0.0897 / 0.1540 / 0.0247 | 0.0854 / 0.3018 / 0.0246 | 0.4350 / 0.6734 / 0.0224 | [-0.0057, 0.0002] |
| shortFG | 0.8332 / 0.7427 / 0.0143 | 0.6368 / 0.5521 / 0.0198 | 0.8643 / 0.7767 / 0.0131 | [-0.0036, 0.0019] |
| midFG | 0.3682 / 0.2349 / 0.0271 | 0.3260 / 0.3570 / 0.0273 | 0.3293 / 0.3657 / 0.0273 | [-0.0018, 0.0024] |

訓練 574 場；測試 614 場，各隊有效後半場數詳見 JSON。未接引擎。
Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA per possession. Offense five and defense five simultaneous sparse player effects (averaged 1/5). Ridge residuals around learned box+position prior; 200-possession feature smoothing. Three game-grouped folds select 10/100/1000 prior precision. Three zone probabilities renormalized.
Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.

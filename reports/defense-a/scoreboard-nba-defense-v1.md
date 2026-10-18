# A1計分板：nba-defense-v1

Pooled counts across teams and seeds; ratios after pooling.
Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.
Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.

| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| net | 0.000 | 0.000 | 0.000 | 0.809 | 4.443 | 6.114 | 0.727 | 0.588 | 3.224 | 3.631 |
| offensiveRatingProxy | 115.156 | 112.728 | 2.428 | 0.813 | 3.441 | 3.157 | 1.090 | 0.886 | 1.756 | 2.035 |
| defensiveRatingProxy | 115.156 | 112.728 | 2.428 | 0.657 | 1.956 | 3.433 | 0.570 | 0.374 | 2.105 | 2.605 |
| opponentTwo | 54.816 | 55.004 | -0.188 | 0.709 | 1.404 | 2.203 | 0.637 | 0.452 | 1.203 | 1.561 |
| opponentThree | 36.638 | 35.965 | 0.674 | 0.780 | 0.578 | 0.962 | 0.600 | 0.469 | 0.490 | 0.626 |
| forcedTOVRate | 14.205 | 14.149 | 0.056 | 0.413 | 0.441 | 1.239 | 0.356 | 0.147 | 0.940 | 1.131 |
| defensiveReboundPct | 73.647 | 74.005 | -0.358 | 0.388 | 0.824 | 1.633 | 0.504 | 0.196 | 1.191 | 1.517 |
| opponentFTR | 0.258 | 0.264 | -0.006 | 0.037 | 0.006 | 0.021 | 0.303 | 0.011 | 0.018 | 0.022 |
| possessionsProxy | 101.743 | 102.554 | -0.812 | -0.098 | 0.727 | 2.052 | 0.354 | -0.035 | 1.967 | 2.243 |

期望勝場MAE 6.400；單seed範圍 6.733–7.267；每分淨勝分勝場斜率 1.723（真實2.165）。

| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |
|---|---:|---:|---:|---:|---:|---:|
| 真實 | 16.404 | 14.040 | 0.245 | 0.228 | 2.165 | — |
| 20261012 | 18.763 | 17.591 | 0.188 | 0.290 | 1.690 | 7.267 |
| 20261013 | 18.987 | 17.830 | 0.189 | 0.308 | 1.740 | 7.267 |
| 20261014 | 18.546 | 17.332 | 0.203 | 0.288 | 1.864 | 6.933 |
| 20261015 | 19.416 | 18.276 | 0.184 | 0.315 | 1.580 | 6.733 |

## 進攻偏差（僅記錄）

| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |
|---|---:|---:|---:|
| Milwaukee Bucks | 116.797 | 110.337 | 4.033 |
| Minnesota Timberwolves | 119.563 | 113.754 | 3.381 |
| Orlando Magic | 116.670 | 111.950 | 2.292 |
| Los Angeles Lakers | 120.016 | 115.408 | 2.180 |
| Brooklyn Nets | 110.210 | 105.931 | 1.851 |
| Memphis Grizzlies | 114.039 | 109.859 | 1.751 |
| Indiana Pacers | 112.413 | 108.270 | 1.715 |
| Denver Nuggets | 123.636 | 119.571 | 1.637 |
| Dallas Mavericks | 112.589 | 108.555 | 1.606 |
| Atlanta Hawks | 117.088 | 113.257 | 1.404 |
| San Antonio Spurs | 120.416 | 116.607 | 1.382 |
| Oklahoma City Thunder | 119.609 | 115.988 | 1.193 |
| Toronto Raptors | 116.089 | 112.882 | 0.780 |
| Sacramento Kings | 111.445 | 108.588 | 0.429 |
| Utah Jazz | 113.827 | 111.263 | 0.136 |
| Philadelphia 76ers | 114.425 | 112.147 | -0.149 |
| Phoenix Suns | 114.253 | 112.077 | -0.251 |
| Miami Heat | 115.421 | 113.786 | -0.793 |
| New Orleans Pelicans | 112.674 | 111.277 | -1.031 |
| LA Clippers | 115.598 | 114.265 | -1.095 |
| Cleveland Cavaliers | 117.004 | 116.073 | -1.497 |
| Golden State Warriors | 112.802 | 112.003 | -1.629 |
| Washington Wizards | 108.807 | 108.137 | -1.758 |
| New York Knicks | 117.259 | 116.687 | -1.856 |
| Charlotte Hornets | 116.094 | 115.727 | -2.061 |
| Detroit Pistons | 114.643 | 114.415 | -2.200 |
| Boston Celtics | 117.303 | 117.208 | -2.333 |
| Chicago Bulls | 110.346 | 110.372 | -2.454 |
| Houston Rockets | 114.022 | 115.088 | -3.494 |
| Portland Trail Blazers | 109.151 | 111.029 | -4.306 |

同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。

# A1計分板：a-rebounds

Pooled counts across teams and seeds; ratios after pooling.
Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.
Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.

| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| net | 0.000 | 0.000 | 0.000 | 0.835 | 4.457 | 6.114 | 0.729 | 0.609 | 2.975 | 3.427 |
| offensiveRatingProxy | 113.029 | 112.728 | 0.301 | 0.825 | 3.248 | 3.157 | 1.029 | 0.849 | 1.565 | 1.896 |
| defensiveRatingProxy | 113.029 | 112.728 | 0.301 | 0.733 | 2.073 | 3.433 | 0.604 | 0.443 | 1.942 | 2.376 |
| opponentTwo | 54.870 | 55.004 | -0.135 | 0.690 | 1.494 | 2.203 | 0.678 | 0.468 | 1.231 | 1.594 |
| opponentThree | 36.613 | 35.965 | 0.649 | 0.607 | 0.621 | 0.962 | 0.645 | 0.391 | 0.624 | 0.766 |
| forcedTOVRate | 14.650 | 14.149 | 0.501 | 0.490 | 0.435 | 1.239 | 0.351 | 0.172 | 0.901 | 1.094 |
| defensiveReboundPct | 72.911 | 74.005 | -1.094 | 0.417 | 0.834 | 1.633 | 0.510 | 0.213 | 1.178 | 1.492 |
| opponentFTR | 0.259 | 0.264 | -0.004 | -0.384 | 0.005 | 0.021 | 0.246 | -0.094 | 0.019 | 0.023 |
| possessionsProxy | 102.952 | 102.554 | 0.397 | -0.108 | 0.659 | 2.052 | 0.321 | -0.035 | 1.926 | 2.222 |

期望勝場MAE 7.033；單seed範圍 6.867–8.467；每分淨勝分勝場斜率 1.766（真實2.165）。

| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |
|---|---:|---:|---:|---:|---:|---:|
| 真實 | 16.404 | 14.040 | 0.245 | 0.228 | 2.165 | — |
| 20261012 | 18.888 | 17.698 | 0.194 | 0.283 | 1.644 | 8.467 |
| 20261013 | 18.443 | 17.257 | 0.194 | 0.281 | 1.902 | 6.867 |
| 20261014 | 18.894 | 17.487 | 0.191 | 0.285 | 1.711 | 7.933 |
| 20261015 | 18.513 | 17.466 | 0.208 | 0.273 | 1.815 | 7.333 |

## 進攻偏差（僅記錄）

| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |
|---|---:|---:|---:|
| Milwaukee Bucks | 114.659 | 110.337 | 4.021 |
| Indiana Pacers | 111.485 | 108.270 | 2.915 |
| Minnesota Timberwolves | 116.648 | 113.754 | 2.593 |
| Orlando Magic | 114.628 | 111.950 | 2.377 |
| Toronto Raptors | 115.282 | 112.882 | 2.099 |
| Brooklyn Nets | 108.157 | 105.931 | 1.925 |
| Denver Nuggets | 121.712 | 119.571 | 1.840 |
| Dallas Mavericks | 110.020 | 108.555 | 1.165 |
| Los Angeles Lakers | 116.609 | 115.408 | 0.901 |
| Sacramento Kings | 109.768 | 108.588 | 0.879 |
| Memphis Grizzlies | 110.892 | 109.859 | 0.732 |
| San Antonio Spurs | 117.530 | 116.607 | 0.623 |
| Oklahoma City Thunder | 116.822 | 115.988 | 0.533 |
| Atlanta Hawks | 113.872 | 113.257 | 0.315 |
| LA Clippers | 114.317 | 114.265 | -0.249 |
| Miami Heat | 113.754 | 113.786 | -0.333 |
| Philadelphia 76ers | 111.941 | 112.147 | -0.506 |
| Washington Wizards | 107.822 | 108.137 | -0.616 |
| Utah Jazz | 110.822 | 111.263 | -0.742 |
| New Orleans Pelicans | 110.808 | 111.277 | -0.770 |
| Cleveland Cavaliers | 115.465 | 116.073 | -0.909 |
| Phoenix Suns | 111.439 | 112.077 | -0.938 |
| Detroit Pistons | 113.436 | 114.415 | -1.280 |
| Charlotte Hornets | 114.541 | 115.727 | -1.487 |
| New York Knicks | 115.348 | 116.687 | -1.640 |
| Chicago Bulls | 108.577 | 110.372 | -2.096 |
| Golden State Warriors | 110.146 | 112.003 | -2.157 |
| Boston Celtics | 114.469 | 117.208 | -3.040 |
| Houston Rockets | 112.009 | 115.088 | -3.380 |
| Portland Trail Blazers | 107.430 | 111.029 | -3.899 |

同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。

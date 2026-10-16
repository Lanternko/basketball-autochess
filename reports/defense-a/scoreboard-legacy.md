# A1計分板：legacy

Pooled counts across teams and seeds; ratios after pooling.
Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.
Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.

| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| net | 0.000 | 0.000 | 0.000 | 0.686 | 5.528 | 6.114 | 0.904 | 0.621 | 3.914 | 4.642 |
| offensiveRatingProxy | 123.347 | 112.728 | 10.619 | 0.775 | 4.403 | 3.157 | 1.395 | 1.081 | 2.218 | 2.793 |
| defensiveRatingProxy | 123.347 | 112.728 | 10.619 | 0.572 | 2.447 | 3.433 | 0.713 | 0.408 | 2.219 | 2.856 |
| opponentTwo | 60.734 | 55.004 | 5.729 | 0.578 | 1.590 | 2.203 | 0.722 | 0.417 | 1.388 | 1.825 |
| opponentThree | 41.208 | 35.965 | 5.244 | 0.762 | 0.588 | 0.962 | 0.612 | 0.466 | 0.491 | 0.640 |
| forcedTOVRate | 15.044 | 14.149 | 0.895 | 0.222 | 0.444 | 1.239 | 0.358 | 0.079 | 0.990 | 1.220 |
| defensiveReboundPct | 73.483 | 74.005 | -0.523 | 0.301 | 0.874 | 1.633 | 0.535 | 0.161 | 1.252 | 1.604 |
| opponentFTR | 0.249 | 0.264 | -0.014 | -0.190 | 0.007 | 0.021 | 0.332 | -0.063 | 0.019 | 0.023 |
| possessionsProxy | 94.428 | 102.554 | -8.126 | -0.218 | 0.684 | 2.052 | 0.333 | -0.073 | 1.999 | 2.300 |

期望勝場MAE 8.183；單seed範圍 7.933–8.667；每分淨勝分勝場斜率 1.851（真實2.165）。

| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |
|---|---:|---:|---:|---:|---:|---:|
| 真實 | 16.404 | 14.040 | 0.245 | 0.228 | 2.165 | — |
| 20261012 | 18.691 | 17.230 | 0.217 | 0.284 | 1.978 | 8.133 |
| 20261013 | 18.744 | 17.049 | 0.207 | 0.286 | 1.758 | 7.933 |
| 20261014 | 18.410 | 16.334 | 0.198 | 0.287 | 1.808 | 8.533 |
| 20261015 | 18.669 | 16.984 | 0.215 | 0.293 | 1.844 | 8.667 |

## 進攻偏差（僅記錄）

| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |
|---|---:|---:|---:|
| Denver Nuggets | 136.523 | 119.571 | 6.332 |
| Los Angeles Lakers | 131.635 | 115.408 | 5.608 |
| Milwaukee Bucks | 126.432 | 110.337 | 5.476 |
| Orlando Magic | 125.895 | 111.950 | 3.325 |
| Indiana Pacers | 121.989 | 108.270 | 3.100 |
| San Antonio Spurs | 129.764 | 116.607 | 2.538 |
| Minnesota Timberwolves | 126.573 | 113.754 | 2.200 |
| Brooklyn Nets | 118.488 | 105.931 | 1.938 |
| Memphis Grizzlies | 121.483 | 109.859 | 1.004 |
| Sacramento Kings | 119.590 | 108.588 | 0.383 |
| Dallas Mavericks | 119.553 | 108.555 | 0.379 |
| LA Clippers | 125.160 | 114.265 | 0.276 |
| Toronto Raptors | 123.443 | 112.882 | -0.058 |
| Cleveland Cavaliers | 126.424 | 116.073 | -0.269 |
| Oklahoma City Thunder | 126.222 | 115.988 | -0.385 |
| Utah Jazz | 121.183 | 111.263 | -0.699 |
| New Orleans Pelicans | 120.748 | 111.277 | -1.148 |
| Philadelphia 76ers | 121.565 | 112.147 | -1.201 |
| Atlanta Hawks | 122.594 | 113.257 | -1.283 |
| New York Knicks | 126.022 | 116.687 | -1.284 |
| Charlotte Hornets | 124.891 | 115.727 | -1.455 |
| Phoenix Suns | 121.152 | 112.077 | -1.544 |
| Miami Heat | 122.752 | 113.786 | -1.653 |
| Chicago Bulls | 118.852 | 110.372 | -2.140 |
| Detroit Pistons | 122.878 | 114.415 | -2.156 |
| Boston Celtics | 125.147 | 117.208 | -2.680 |
| Golden State Warriors | 119.083 | 112.003 | -3.540 |
| Houston Rockets | 121.962 | 115.088 | -3.746 |
| Portland Trail Blazers | 117.675 | 111.029 | -3.973 |
| Washington Wizards | 113.992 | 108.137 | -4.765 |

同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。

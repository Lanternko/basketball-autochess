# A1計分板：a-rebounds-clock

Pooled counts across teams and seeds; ratios after pooling.
Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.
Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.

| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| net | 0.000 | 0.000 | 0.000 | 0.839 | 4.659 | 6.114 | 0.762 | 0.640 | 2.928 | 3.357 |
| offensiveRatingProxy | 113.020 | 112.728 | 0.292 | 0.833 | 3.483 | 3.157 | 1.103 | 0.919 | 1.637 | 1.943 |
| defensiveRatingProxy | 113.020 | 112.728 | 0.292 | 0.735 | 2.054 | 3.433 | 0.598 | 0.440 | 1.894 | 2.375 |
| opponentTwo | 54.805 | 55.004 | -0.199 | 0.741 | 1.337 | 2.203 | 0.607 | 0.450 | 1.119 | 1.509 |
| opponentThree | 36.550 | 35.965 | 0.585 | 0.763 | 0.652 | 0.962 | 0.678 | 0.517 | 0.461 | 0.628 |
| forcedTOVRate | 14.536 | 14.149 | 0.387 | 0.466 | 0.401 | 1.239 | 0.323 | 0.151 | 0.925 | 1.111 |
| defensiveReboundPct | 72.930 | 74.005 | -1.075 | 0.358 | 0.881 | 1.633 | 0.540 | 0.193 | 1.211 | 1.554 |
| opponentFTR | 0.258 | 0.264 | -0.006 | -0.219 | 0.006 | 0.021 | 0.298 | -0.065 | 0.019 | 0.023 |
| possessionsProxy | 103.427 | 102.554 | 0.873 | -0.080 | 0.774 | 2.052 | 0.377 | -0.030 | 1.941 | 2.251 |

期望勝場MAE 6.300；單seed範圍 6.267–7.133；每分淨勝分勝場斜率 1.772（真實2.165）。

| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |
|---|---:|---:|---:|---:|---:|---:|
| 真實 | 16.404 | 14.040 | 0.245 | 0.228 | 2.165 | — |
| 20261012 | 17.937 | 16.669 | 0.196 | 0.270 | 1.652 | 6.933 |
| 20261013 | 18.427 | 16.793 | 0.203 | 0.290 | 1.770 | 6.267 |
| 20261014 | 18.660 | 17.584 | 0.193 | 0.284 | 1.847 | 7.133 |
| 20261015 | 17.972 | 16.679 | 0.210 | 0.279 | 1.756 | 6.800 |

## 進攻偏差（僅記錄）

| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |
|---|---:|---:|---:|
| Milwaukee Bucks | 114.500 | 110.337 | 3.871 |
| Denver Nuggets | 122.249 | 119.571 | 2.386 |
| Indiana Pacers | 110.882 | 108.270 | 2.321 |
| Orlando Magic | 114.483 | 111.950 | 2.241 |
| Minnesota Timberwolves | 116.235 | 113.754 | 2.189 |
| Brooklyn Nets | 108.385 | 105.931 | 2.162 |
| Sacramento Kings | 110.583 | 108.588 | 1.702 |
| San Antonio Spurs | 118.512 | 116.607 | 1.614 |
| Los Angeles Lakers | 117.149 | 115.408 | 1.449 |
| Toronto Raptors | 114.593 | 112.882 | 1.419 |
| Atlanta Hawks | 114.454 | 113.257 | 0.905 |
| Oklahoma City Thunder | 117.089 | 115.988 | 0.809 |
| Memphis Grizzlies | 110.642 | 109.859 | 0.491 |
| Cleveland Cavaliers | 116.714 | 116.073 | 0.349 |
| LA Clippers | 114.581 | 114.265 | 0.024 |
| Dallas Mavericks | 108.675 | 108.555 | -0.172 |
| Phoenix Suns | 112.174 | 112.077 | -0.195 |
| Miami Heat | 113.762 | 113.786 | -0.316 |
| Philadelphia 76ers | 111.836 | 112.147 | -0.603 |
| Utah Jazz | 110.950 | 111.263 | -0.605 |
| New York Knicks | 115.494 | 116.687 | -1.485 |
| New Orleans Pelicans | 109.881 | 111.277 | -1.688 |
| Washington Wizards | 106.664 | 108.137 | -1.765 |
| Chicago Bulls | 108.812 | 110.372 | -1.852 |
| Golden State Warriors | 110.354 | 112.003 | -1.941 |
| Detroit Pistons | 112.736 | 114.415 | -1.971 |
| Charlotte Hornets | 113.749 | 115.727 | -2.270 |
| Houston Rockets | 112.347 | 115.088 | -3.034 |
| Boston Celtics | 114.233 | 117.208 | -3.267 |
| Portland Trail Blazers | 107.315 | 111.029 | -4.006 |

同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。

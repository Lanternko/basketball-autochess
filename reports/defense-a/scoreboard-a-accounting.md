# A1計分板：a-accounting

Pooled counts across teams and seeds; ratios after pooling.
Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.
Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.

| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| net | 0.000 | 0.000 | 0.000 | 0.819 | 4.490 | 6.114 | 0.735 | 0.601 | 3.020 | 3.547 |
| offensiveRatingProxy | 112.675 | 112.728 | -0.053 | 0.798 | 3.333 | 3.157 | 1.056 | 0.842 | 1.621 | 2.071 |
| defensiveRatingProxy | 112.675 | 112.728 | -0.053 | 0.753 | 2.063 | 3.433 | 0.601 | 0.452 | 1.847 | 2.319 |
| opponentTwo | 54.872 | 55.004 | -0.133 | 0.700 | 1.511 | 2.203 | 0.686 | 0.480 | 1.162 | 1.573 |
| opponentThree | 36.588 | 35.965 | 0.623 | 0.676 | 0.541 | 0.962 | 0.562 | 0.380 | 0.557 | 0.717 |
| forcedTOVRate | 14.541 | 14.149 | 0.393 | 0.448 | 0.432 | 1.239 | 0.349 | 0.156 | 0.926 | 1.115 |
| defensiveReboundPct | 73.740 | 74.005 | -0.265 | 0.348 | 0.659 | 1.633 | 0.403 | 0.140 | 1.180 | 1.534 |
| opponentFTR | 0.259 | 0.264 | -0.005 | -0.348 | 0.007 | 0.021 | 0.318 | -0.111 | 0.020 | 0.024 |
| possessionsProxy | 103.092 | 102.554 | 0.537 | -0.131 | 0.713 | 2.052 | 0.348 | -0.045 | 1.971 | 2.259 |

期望勝場MAE 7.533；單seed範圍 7.267–8.333；每分淨勝分勝場斜率 1.732（真實2.165）。

| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |
|---|---:|---:|---:|---:|---:|---:|
| 真實 | 16.404 | 14.040 | 0.245 | 0.228 | 2.165 | — |
| 20261012 | 19.011 | 17.589 | 0.186 | 0.280 | 1.759 | 8.333 |
| 20261013 | 18.086 | 16.969 | 0.201 | 0.266 | 1.897 | 7.267 |
| 20261014 | 18.347 | 17.075 | 0.197 | 0.288 | 1.745 | 8.133 |
| 20261015 | 19.042 | 17.874 | 0.211 | 0.294 | 1.492 | 8.267 |

## 進攻偏差（僅記錄）

| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |
|---|---:|---:|---:|
| Milwaukee Bucks | 114.700 | 110.337 | 4.417 |
| Indiana Pacers | 111.593 | 108.270 | 3.376 |
| Minnesota Timberwolves | 116.290 | 113.754 | 2.589 |
| Brooklyn Nets | 108.348 | 105.931 | 2.470 |
| Denver Nuggets | 121.565 | 119.571 | 2.047 |
| Memphis Grizzlies | 111.818 | 109.859 | 2.012 |
| Orlando Magic | 113.763 | 111.950 | 1.866 |
| Toronto Raptors | 114.514 | 112.882 | 1.686 |
| Los Angeles Lakers | 116.623 | 115.408 | 1.269 |
| Dallas Mavericks | 109.332 | 108.555 | 0.831 |
| Atlanta Hawks | 113.794 | 113.257 | 0.591 |
| Sacramento Kings | 108.775 | 108.588 | 0.240 |
| San Antonio Spurs | 116.715 | 116.607 | 0.162 |
| Miami Heat | 113.865 | 113.786 | 0.132 |
| Oklahoma City Thunder | 115.982 | 115.988 | 0.047 |
| Utah Jazz | 111.178 | 111.263 | -0.032 |
| Cleveland Cavaliers | 115.753 | 116.073 | -0.267 |
| LA Clippers | 113.829 | 114.265 | -0.383 |
| Washington Wizards | 107.547 | 108.137 | -0.537 |
| Phoenix Suns | 111.158 | 112.077 | -0.865 |
| Charlotte Hornets | 114.794 | 115.727 | -0.879 |
| Philadelphia 76ers | 111.179 | 112.147 | -0.914 |
| Detroit Pistons | 113.264 | 114.415 | -1.097 |
| Chicago Bulls | 108.572 | 110.372 | -1.747 |
| New York Knicks | 114.593 | 116.687 | -2.040 |
| Golden State Warriors | 109.739 | 112.003 | -2.210 |
| New Orleans Pelicans | 108.621 | 111.277 | -2.603 |
| Boston Celtics | 114.537 | 117.208 | -2.618 |
| Houston Rockets | 110.884 | 115.088 | -4.151 |
| Portland Trail Blazers | 106.432 | 111.029 | -4.544 |

同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。

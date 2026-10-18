# A1計分板：a-accounting-clock

Pooled counts across teams and seeds; ratios after pooling.
Mean each team metric across seeds first; population SD; simulated on observed regression with intercept.
Both MAE and RMSE subtract the corresponding pooled league metric, for observed and simulated vectors separately.

| 指標 | 模擬合併 | 真實合併 | 偏差 | 相關 | 模擬SD | 真實SD | SD比 | 斜率 | 去均值MAE | 去均值RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| net | 0.000 | 0.000 | 0.000 | 0.815 | 4.705 | 6.114 | 0.770 | 0.627 | 3.153 | 3.555 |
| offensiveRatingProxy | 112.772 | 112.728 | 0.044 | 0.842 | 3.399 | 3.157 | 1.077 | 0.906 | 1.562 | 1.858 |
| defensiveRatingProxy | 112.772 | 112.728 | 0.044 | 0.723 | 1.908 | 3.433 | 0.556 | 0.402 | 2.011 | 2.441 |
| opponentTwo | 54.829 | 55.004 | -0.175 | 0.741 | 1.405 | 2.203 | 0.638 | 0.473 | 1.144 | 1.497 |
| opponentThree | 36.576 | 35.965 | 0.611 | 0.438 | 0.599 | 0.962 | 0.623 | 0.273 | 0.641 | 0.883 |
| forcedTOVRate | 14.398 | 14.149 | 0.249 | 0.378 | 0.403 | 1.239 | 0.325 | 0.123 | 0.932 | 1.149 |
| defensiveReboundPct | 73.780 | 74.005 | -0.225 | 0.211 | 0.812 | 1.633 | 0.497 | 0.105 | 1.271 | 1.663 |
| opponentFTR | 0.258 | 0.264 | -0.005 | -0.250 | 0.006 | 0.021 | 0.276 | -0.069 | 0.019 | 0.023 |
| possessionsProxy | 103.643 | 102.554 | 1.089 | -0.059 | 0.760 | 2.052 | 0.370 | -0.022 | 1.952 | 2.230 |

期望勝場MAE 7.050；單seed範圍 6.800–7.933；每分淨勝分勝場斜率 1.833（真實2.165）。

| seed | 分差SD | 殘差SD | ≤5分比例 | ≥20分比例 | 勝場斜率 | 勝場MAE |
|---|---:|---:|---:|---:|---:|---:|
| 真實 | 16.404 | 14.040 | 0.245 | 0.228 | 2.165 | — |
| 20261012 | 18.802 | 17.603 | 0.184 | 0.303 | 1.798 | 7.933 |
| 20261013 | 18.264 | 17.038 | 0.210 | 0.267 | 1.905 | 6.800 |
| 20261014 | 18.076 | 16.822 | 0.196 | 0.267 | 1.914 | 7.800 |
| 20261015 | 19.018 | 17.561 | 0.197 | 0.294 | 1.712 | 6.867 |

## 進攻偏差（僅記錄）

| 球隊 | 模擬進攻代理 | 真實 | 去均值殘差 |
|---|---:|---:|---:|
| Milwaukee Bucks | 114.462 | 110.337 | 4.081 |
| Orlando Magic | 114.825 | 111.950 | 2.830 |
| Brooklyn Nets | 108.287 | 105.931 | 2.312 |
| Minnesota Timberwolves | 115.964 | 113.754 | 2.166 |
| Indiana Pacers | 110.271 | 108.270 | 1.957 |
| Denver Nuggets | 121.406 | 119.571 | 1.791 |
| Memphis Grizzlies | 111.430 | 109.859 | 1.526 |
| Los Angeles Lakers | 116.969 | 115.408 | 1.517 |
| Dallas Mavericks | 109.733 | 108.555 | 1.134 |
| San Antonio Spurs | 117.748 | 116.607 | 1.098 |
| Toronto Raptors | 114.014 | 112.882 | 1.088 |
| Oklahoma City Thunder | 116.574 | 115.988 | 0.542 |
| Atlanta Hawks | 113.720 | 113.257 | 0.419 |
| Cleveland Cavaliers | 116.407 | 116.073 | 0.290 |
| Phoenix Suns | 112.224 | 112.077 | 0.103 |
| Sacramento Kings | 108.483 | 108.588 | -0.150 |
| Miami Heat | 113.495 | 113.786 | -0.335 |
| LA Clippers | 113.954 | 114.265 | -0.356 |
| Utah Jazz | 110.834 | 111.263 | -0.473 |
| Charlotte Hornets | 114.965 | 115.727 | -0.806 |
| Washington Wizards | 106.758 | 108.137 | -1.423 |
| New York Knicks | 115.294 | 116.687 | -1.436 |
| Philadelphia 76ers | 110.675 | 112.147 | -1.516 |
| New Orleans Pelicans | 109.638 | 111.277 | -1.684 |
| Golden State Warriors | 110.084 | 112.003 | -1.963 |
| Detroit Pistons | 111.941 | 114.415 | -2.518 |
| Chicago Bulls | 107.881 | 110.372 | -2.535 |
| Houston Rockets | 112.425 | 115.088 | -2.707 |
| Boston Celtics | 114.394 | 117.208 | -2.858 |
| Portland Trail Blazers | 107.829 | 111.029 | -3.243 |

同季回溯；殘差SD使用每個seed自身賽季淨勝分估計實力；球權為FGA−OREB+TOV+0.44FTA代理，非官方逐球POSS。比例以0–1表示。

# 真實與 v1 的變異來源

Same 1227 fixtures; one full frozen-v1 seed 20261012. Regulation only; original A4 identical-roster IID17.604 and final SD16.792 are reference values, not mixed into this decomposition.

| 指標 | 真實 | v1 |
|---|---:|---:|
| games | 1227.0000 | 1227.0000 |
| pointVariance | 1.4115 | 1.5692 |
| teamCenteredPointVariance | 1.4105 | 1.5676 |
| meanCombinedPossessions | 201.3545 | 199.2029 |
| independentSD | 16.8587 | 17.6801 |
| teamCenteredIndependentSD | 16.8526 | 17.6712 |
| withinTeamScoreVariance | 149.0137 | 177.1670 |
| withinTeamScoreCovariance | 28.8249 | 17.0187 |
| strengthAdjustedScoreVariance | 126.3508 | 170.9164 |
| scoreCovariance | 27.9661 | 16.7847 |
| paceCovariance | 7.2869 | 14.0084 |
| remainingCovariance | 20.6792 | 2.7763 |
| possessionCountVariance | 24.9488 | 8.7030 |
| marginResidualSD | 14.0275 | 17.5574 |
| q3Q4Correlation | -0.1054 | 0.0236 |

| 單回合進攻得分 | 真實比例 | v1比例 |
|---|---:|---:|
| 0 | 0.4887 | 0.5037 |
| 1 | 0.0341 | 0.0178 |
| 2 | 0.3251 | 0.2961 |
| 3 | 0.1504 | 0.1691 |
| 4 | 0.0015 | 0.0129 |
| 5 | 0.0001 | 0.0003 |
| 6 | 0.0000 | 0.0001 |

| 模擬減真實的變異差來源 | 分數平方 | 占總差 |
|---|---:|---:|
| singlePossessionVariance | 31.2960 | 28.0697% |
| meanPossessionCount | -3.0348 | -2.7219% |
| sharedPaceNet | -0.8947 | -0.8024% |
| remainingSameGameCovariance | 35.8058 | 32.1146% |
| withinTeamSerialAndHeterogeneity | 48.3216 | 43.3401% |
| 合計 | 111.4940 | 100% |

**統計拆解，不是唯一因果分解。** 最後一項沒有被強行歸為比分耦合。SD不能直接相加。

| 領先分桶 | 真實PPP | v1PPP | 真實秒/回合 | v1秒/回合 | 真實先發比例 | v1先發比例 |
|---|---:|---:|---:|---:|---:|---:|
| -5..5 | 1.1461 | 1.1812 | 14.3475 | 14.5023 | 0.6951 | 0.6087 |
| -9..-6 | 1.1558 | 1.1610 | 14.3171 | 14.3547 | 0.6205 | 0.5919 |
| 6..9 | 1.1377 | 1.1754 | 14.2131 | 14.4669 | 0.6164 | 0.5989 |
| -19..-10 | 1.1362 | 1.1546 | 14.1204 | 14.3432 | 0.5755 | 0.5988 |
| 10..19 | 1.1394 | 1.1685 | 14.5790 | 14.5920 | 0.5855 | 0.6063 |
| <=-20 | 1.1409 | 1.1578 | 13.9710 | 14.1903 | 0.4406 | 0.5979 |
| >=20 | 1.1189 | 1.1736 | 14.3061 | 14.6363 | 0.4181 | 0.6128 |

嚴格排除 8 場回合異常後：真實殘差SD 14.0228，v1 17.5006。

Y_A = regulation points_A - season own points mean_A - season opponent allowed mean_B + league mean. Y_B symmetric. Var(Y_A-Y_B)=Var(Y_A)+Var(Y_B)-2Cov(Y_A,Y_B). Score covariance uses actual team scores including opposing technical FTs; within-team variance is the game-count-weighted population variance across each team, with per-team values supplied.

Shared N=(N_A+N_B)/2. Linear score projections on N partition covariance into beta_A*beta_B*Var(N) and residual covariance. Statistical partition, not intervention causality.

Mean combined regulation possession count times within-team signed possession point variance. Technical opposing points remain signed only for margin IID theory; ordinary offensive point distribution also shown.

Remainder after IID, marginal pace variance and both covariance components. Contains within-team serial dependence, remaining schedule/lineup heterogeneity and strength fitting effects; cannot identify garbage time causally.

Components in points squared, not additive SD. Replacing simulation terms with real terms yields the observed variance exactly. Own vs opponent technical bookkeeping is retained, not forced into 0–4.

本批只診斷，尚未實作B2。

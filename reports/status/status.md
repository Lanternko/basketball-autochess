# 審查表（2026-10-18）

模擬版本 v53。由 `reports/status/status_snapshot.py` 產生。

## 個人準確度（RAPM，pooledPoss ≥ 5000）

| 層 | 人數 | 淨值 ρ | 防守 ρ | 備註 |
|---|---:|---:|---:|---|
| 模擬板 v53（原始） | 414 | 0.362 | 0.256 |  |
| 模擬板 v53（收縮修正版） | 414 | 0.398 | 0.276 |  |
| 卡片 OVR（遊戲現用） | 414 | 0.374 | 0.205 |  |
| 卡片 OVR（混合 α=0.5） | 414 | 0.500 | 0.288 | 目標含 RAPM，樣本內 ρ 偏高；留出 ρ 見 ovr-blended-2025-26/summary.json |

## 球隊準確度（30 隊、全季）

| 版本 | 勝場 MAE | 淨分 RMSE | 得分 MAE | 來源 |
|---|---:|---:|---:|---|
| v14 | 5.73 | 2.912 | 2.25 | model-evolution-20261016 |
| v17 | 5.91 | 3.008 | 2.45 | model-evolution-20261016 |
| v19 | 6.71 | 3.170 | 2.44 | model-evolution-20261016 |
| v20 | 7.64 | 3.496 | 2.40 | model-evolution-20261016 |
| v21 | 8.02 | 3.689 | 2.36 | model-evolution-20261016 |
| v22 | 7.84 | 3.616 | 2.16 | model-evolution-20261016 |
| v23 | 7.96 | 3.624 | 2.36 | model-evolution-20261016 |
| v24 | 7.96 | 3.624 | 2.36 | model-evolution-20261016 |
| v25 | 6.62 | 3.377 | 2.40 | model-evolution-20261016 |
| v26 | 7.31 | 3.505 | 2.59 | model-evolution-20261016 |
| v28 | 7.22 | 3.459 | 2.58 | model-evolution-20261016 |
| v30 | 6.91 | 3.391 | 2.55 | model-evolution-20261016 |
| v31 | 7.18 | 3.384 | 2.60 | model-evolution-20261016 |
| v34 | 6.40 | 3.061 | 2.47 | model-evolution-20261016 |
| v35 | 6.89 | 3.324 | 2.53 | model-evolution-20261016 |
| v36 | 6.78 | 3.372 | 2.39 | model-evolution-20261016 |
| v37 | 6.87 | 3.166 | 2.33 | model-evolution-20261016 |
| v39 | 6.91 | 3.391 | 2.55 | model-evolution-20261016 |
| v41 | 6.67 | 2.876 | 2.42 | model-evolution-20261016 |
| v46 | 5.24 | 2.302 | — | player-impact-v46 |
| v47 | 5.38 | 2.313 | — | player-impact-v47 |
| v48 | 4.98 | 2.174 | — | player-impact-v48 |
| v49 | 6.24 | 2.723 | — | player-impact-v49 |
| v53 | — | — | — | 未跑全季球隊驗證 |

## 卡片 OVR 前 20（RAPM 名次在 415 人中）

| # | 球員 | 位置 | OVR | 分鐘 | 模擬名次 | RAPM 名次 | 旗標 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Shai Gilgeous-Alexander | PG | 110.4 | 2259 | 1 | 2 |  |
| 2 | Luka Dončić | PG | 106.1 | 2289 | 6 | 16 |  |
| 3 | Chet Holmgren | PF | 105.0 | 1997 | 14 | 8 | 長人 |
| 4 | Victor Wembanyama | C | 99.1 | 1866 | 5 | 5 | 長人 |
| 5 | Karlo Matković | PF | 99.0 | 912 | 33 | 212 | 低分鐘、RAPM 差距大、長人 |
| 6 | Giannis Antetokounmpo | PF | 98.1 | 1039 | 3 | 3 | 長人 |
| 7 | Jamal Murray | PG | 96.7 | 2652 | 105 | 211 | RAPM 差距大 |
| 8 | Evan Mobley | PF | 96.4 | 2074 | 10 | 47 | 長人 |
| 9 | Javon Small | PG | 96.2 | 830 | 29 | — | 低分鐘、RAPM 樣本不足 |
| 10 | Kawhi Leonard | SF | 93.5 | 2085 | 2 | 4 |  |
| 11 | Luka Garza | C | 92.5 | 1118 | 112 | 174 | RAPM 差距大、長人 |
| 12 | Ty Jerome | PG | 92.5 | 339 | 4 | 136 | 低分鐘、RAPM 差距大 |
| 13 | Stephen Curry | PG | 91.2 | 1329 | 92 | 24 |  |
| 14 | Nikola Jokić | C | 91.2 | 2265 | 8 | 1 | 長人 |
| 15 | Ryan Rollins | PG | 91.1 | 2375 | 26 | 155 | RAPM 差距大 |
| 16 | Isaiah Stewart | PF | 90.3 | 1317 | 32 | 261 | RAPM 差距大、長人 |
| 17 | Marvin Bagley III | C | 90.2 | 1201 | 77 | 289 | RAPM 差距大、長人 |
| 18 | Charles Bassey | PF | 89.2 | 153 | 36 | 353 | 低分鐘、RAPM 差距大、長人 |
| 19 | Jalen Duren | C | 88.1 | 1976 | 16 | 180 | RAPM 差距大、長人 |
| 20 | Donovan Mitchell | SG | 87.3 | 2342 | 66 | 17 |  |

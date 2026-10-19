# 審查表（2026-10-19）

模擬版本 v54。由 `reports/status/status_snapshot.py` 產生。

## 個人準確度（RAPM，pooledPoss ≥ 5000）

| 層 | 人數 | 淨值 ρ | 防守 ρ | 備註 |
|---|---:|---:|---:|---|
| 模擬板 v53（原始） | 414 | 0.362 | 0.256 |  |
| 模擬板 v53（收縮修正版） | 414 | 0.398 | 0.276 |  |
| 模擬板 v54（原始） | 414 | 0.389 | 0.289 |  |
| 模擬板 v54（收縮修正版） | 414 | 0.424 | 0.303 | 已收束；球隊層 2025-26 勝場 MAE 變差，未切換對局資料，卡片板仍為 v53 校準 |
| 卡片 OVR（正式卡片板） | 414 | 0.500 | 0.288 | 替補可靠度收縮已依預註冊跑完但不採用（G1、G2 未過，見 ovr-blended-bench-shrinkage/report.md），本板維持不變 |
| 卡片 OVR（舊版，sim-only） | 414 | 0.374 | 0.205 |  |
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
| v53 | 4.56 | 2.019 | — | player-impact-v53-team（壓迫係數為樣本內） |
| v54 | 6.29 | 2.703 | — | player-impact-v54-team（未採用） |

## 卡片 OVR 前 20（RAPM 名次在 415 人中）

| # | 球員 | 位置 | OVR | 分鐘 | 模擬名次 | RAPM 名次 | 旗標 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Shai Gilgeous-Alexander | PG | 111.6 | 2259 | 1 | 2 |  |
| 2 | Luka Dončić | PG | 104.3 | 2289 | 7 | 16 |  |
| 3 | Victor Wembanyama | C | 102.3 | 1866 | 5 | 5 | 長人 |
| 4 | Chet Holmgren | PF | 100.9 | 1997 | 21 | 8 | 長人 |
| 5 | Evan Mobley | PF | 99.0 | 2074 | 11 | 47 | 長人 |
| 6 | Giannis Antetokounmpo | PF | 96.2 | 1039 | 3 | 3 | 長人 |
| 7 | Karlo Matković | PF | 95.4 | 912 | 20 | 212 | 低分鐘、RAPM 差距大、長人 |
| 8 | Nikola Jokić | C | 95.3 | 2265 | 6 | 1 | 長人 |
| 9 | Jamal Murray | PG | 94.7 | 2652 | 130 | 211 | RAPM 差距大 |
| 10 | Kawhi Leonard | SF | 93.6 | 2085 | 2 | 4 |  |
| 11 | Kevin Durant | SF | 91.4 | 2840 | 56 | 35 |  |
| 12 | Ryan Rollins | PG | 90.7 | 2375 | 26 | 155 | RAPM 差距大 |
| 13 | Stephen Curry | PG | 89.9 | 1329 | 115 | 24 |  |
| 14 | Javon Small | PG | 89.9 | 830 | 55 | — | 低分鐘、RAPM 樣本不足 |
| 15 | Aaron Gordon | PF | 89.3 | 1005 | 204 | 21 | 長人 |
| 16 | Donovan Mitchell | SG | 89.2 | 2342 | 70 | 17 |  |
| 17 | Joel Embiid | C | 88.3 | 1201 | 254 | 10 | 長人 |
| 18 | Jimmy Butler III | SF | 88.2 | 1182 | 23 | 12 |  |
| 19 | Scottie Barnes | PF | 88.1 | 2681 | 28 | 101 | RAPM 差距大、長人 |
| 20 | Ty Jerome | PG | 87.3 | 339 | 4 | 136 | 低分鐘、RAPM 差距大 |

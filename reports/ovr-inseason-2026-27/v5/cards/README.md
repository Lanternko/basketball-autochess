# v5 答案卡：D1（2023-24）、D2（2024-25）

依 `preregistration-v5.md` §R.3 重建。**只換 RAPM 檔**；管線（`card-H1-m0/summary.json`）、prior（season-cards 能力值）、球員名單、分鐘數全部照 v4 `build_cards_v4.py`。v4 舊卡（`v4/cards/<season>.csv`）原樣保留，沒有覆蓋。

## 季集更正

| 起點 | 目標季 | v4 答案用 RAPM | v5 答案用 RAPM | 檔案 |
|---|---|---|---|---|
| D1 | 2023-24 | 2021-22..2022-23（不含目標季） | **2020-21..2023-24**（四季） | `v5/data/rapm-2020-21_2023-24.csv` |
| D2 | 2024-25 | 2021-22..2023-24（不含目標季） | **2021-22..2024-25**（四季） | `v4/data/rapm-2021-22_2024-25.csv` |

- 規則：目標季（含）往前最多四季。§R.3 原文寫「最早 2021-22」，是因為當時本機沒有 2020-21 資料；使用者 2026-10-27 指示補抓 2020-21，D1 因此改成完整四季。先前的三季版（2021-22..2023-24）保留為對照，見下方「三季版對照」。
- RAPM 方法沒變：`v4/tools/rapm_v4.build` → `tools/rapm_2022_25.py`（ridge，CV 選 λ，網格 100..30000）。三組都選到 λ=3000（四季 D1、四季 D2、三季對照）。
- `v5/tools/rapm_answer_v5.py` 會依有 stint 的季決定季集：2024-25 的 RAPM 從本機 stint 重跑，和 `v4/data/rapm-2021-22_2024-25.csv` **逐位相同**（最大差 0.0）。2020-21_2023-24 是新的季集，沒有既有檔可比，所以正式檔就是這次重跑的結果。季集、SHA、stint SHA 與 2020-21 來源記在 `v5/data/rapm-answer-v5.json`；三季版的紀錄在 `rapm-answer-v5-3season.json`。

### 2020-21 stint 的來源與管線差異

2020-21 的 stint 檔不是 repo 的 cdn liveData 管線產出的。它來自另一項工作：從 shufinskiy/nba_data 鏡像的 stats.nba.com playbyplayv2 存檔重建，路徑是 `v5/history/stints/stints-2020-21.jsonl.gz`，連同 `preparation-2020-21.json` 和 `v5/history/validation-onoff.json` 一起 commit。RAPM 讀它解壓後的版本 `reports/defense-seventh/2020-21/stints/stints.jsonl`。只有 RAPM 用到的欄位（`id`、`seconds`、`teams[].players/teamId/defensivePossessions/opponent.points`）與 cdn 管線相同。

| | cdn 管線（2021-22..2024-25） | 2020-21 重建 |
|---|---|---|
| 來源 | cdn.nba.com liveData pbp | stats.nba.com playbyplayv2 存檔 |
| 回合數 | 按時鐘分攤 | 回合結束的整數計數 |
| 排除規則的分鐘容許誤差 | 1.1 秒 | 2.1 秒 |
| 場次 | — | 1080 場中 1066 場可用 |

驗證：整季得分效率比值 1.002。用同一套方法重建 2022-23、2023-24，再和 repo 的 onoff.csv（≥2000 回合）比對：在場淨效率 r=0.966／0.978，on-off 差 r=0.945／0.943。結論是兩套管線大致一致，但不是逐位相同，所以 D1 的四季 RAPM 混用了兩種管線。
- 被交易球員分鐘數仍不跨隊加總（照 v4）。§R.7 第 1 條使用者尚未定案，定案後要再重建一次。

## 檔案

| 檔案 | 內容 |
|---|---|
| `2023-24-v5.csv`、`2024-25-v5.csv` | 新答案卡（欄位同 v4 卡；2023-24 為四季版） |
| `2023-24-v5-3season.csv`／`.json` | 2023-24 三季版（2021-22..2023-24），僅供對照，不是答案 |
| `diff-3season-4season-2023-24.csv` | 2023-24 三季版 vs 四季版的逐人差異 |
| `diff-v4-v5-2023-24-3season.csv` | 舊的 v4 vs 三季版差異（對照用） |
| `2023-24-v5.json`、`2024-25-v5.json` | 建卡檢查、RAPM/prior/summary SHA、取代的 v4 檔 |
| `diff-v4-v5-<season>.csv` | 每位球員 v4 vs v5 OVR、名次（全卡內 OVR 由高到低）、變化（`dRank` 正數＝名次上升） |
| `diff-summary-v5.json` | 相關係數、變動統計、前 10 名、對 2K27／同期 2K 的 rank ρ 與中位數；2023-24 另有 `vs3season` 區塊 |
| `../tools/build_answer_cards_v5.py` | 產生以上檔案 |

自我檢查：同一支腳本先用 v4 的 RAPM 檔重建，和 `v4/cards/<season>.csv` 位元相同（`reproducesV4WithV4Rapm: true`），所以差異只來自 RAPM 季集。兩季的 v4 建卡檢查（≥500 人、ρ_OVR≥0.90、|中位差|≤1.0、能力值 ρ≥0.90）都通過。

## 差異摘要

| | 2023-24 全部 | 2023-24 MIN≥500 | 2024-25 全部 | 2024-25 MIN≥500 |
|---|---|---|---|---|
| 人數 | 572 | 360 | 569 | 375 |
| v4–v5 OVR Pearson | 0.945 | 0.934 | 0.972 | 0.965 |
| v4–v5 OVR Spearman | 0.939 | 0.928 | 0.966 | 0.958 |
| 平均 ΔOVR（v5−v4） | +0.09 | −0.00 | +0.53 | +0.80 |
| 平均 \|ΔOVR\| | 2.34 | 3.04 | 1.61 | 2.14 |
| \|ΔOVR\|>3 人數 | 165 | 134 | 112 | 98 |
| 最大 \|ΔOVR\| | 18.7 | 18.7 | 21.2 | 21.2 |
| OVR 中位數 v4 → v5 | 67.85 → 68.18 | 71.64 → 71.52 | 65.89 → 66.54 | 68.57 → 70.13 |
| 平均 \|Δ名次\| | 34.9 | 42.0 | 23.9 | 28.7 |

2023-24 欄是 v4 對四季版。

### 對 2K 的 rank ρ 與中位數（§R.3 要求並列）

| 季 | 參照 | 子集 | n | ρ v4 | ρ v5 | 卡−2K 中位數 v4 | v5 |
|---|---|---|---|---|---|---|---|
| 2023-24 | 2K27 | 全部 | 377 | **0.532** | 0.532 | −5.78 | −5.83 |
| 2023-24 | 2K27 | MIN≥500 | 299 | **0.528** | 0.523 | −5.56 | −5.85 |
| 2023-24 | 2K24（同期） | 全部 | 376 | **0.543** | 0.519 | −5.27 | −5.31 |
| 2023-24 | 2K24（同期） | MIN≥500 | 299 | **0.573** | 0.533 | −5.34 | −5.60 |
| 2024-25 | 2K27 | 全部 | 457 | 0.534 | **0.548** | −8.46 | −7.20 |
| 2024-25 | 2K27 | MIN≥500 | 343 | **0.568** | 0.561 | −8.66 | −7.06 |
| 2024-25 | 2K25（同期） | 全部 | 456 | 0.527 | **0.545** | −7.48 | −6.80 |
| 2024-25 | 2K25（同期） | MIN≥500 | 342 | **0.596** | 0.591 | −7.59 | −6.75 |

- 2K 以姓名比對（去重音、去 Jr./II 等），比不到的球員不計。2K27 是 2026-27 版本，對舊季只是參考；舊季退役球員不在 2K27 名單。
- 對 2K 的 ρ 變化都在 ±0.04 內，沒有一致方向。2023-24 四季版對 2K27 和 v4 持平，對同期 2K24 下降 0.02–0.04。驗收不設 OVR 範圍（§R.3）。

### 變動最大前 10（全部球員）

**2023-24**（v4 → 四季）：Gary Payton II +18.7、Toumani Camara +15.2、Frank Ntilikina +14.0、Jimmy Butler III +14.0、James Wiseman −13.6、Marcus Smart +12.8、Andre Drummond −12.6、P.J. Tucker −12.5、Andrew Wiggins −12.0、Kris Murray +11.5。

**2024-25**：Lonzo Ball +21.2、AJ Green +15.9、Dorian Finney-Smith +13.7、Keon Ellis +11.9、Kris Dunn +11.5、Dante Exum +10.2、Andrew Nembhard +9.9、OG Anunoby −9.5、Anthony Black +9.4、Day'Ron Sharpe +9.4。

完整名單（含 MIN≥500 子集）見 `diff-summary-v5.json`。變動大的多半是前一季沒有或很少 RAPM 樣本的人：2023-24 新秀（Camara、Kris Murray、Ausar Thompson）、缺陣季（Lonzo Ball 2022-23、2023-24 全休；Bridges 2022-23 全休），v4 答案卡只看到舊季或看不到 RAPM，v5 改成含目標季後才反映。

## 三季版對照（2023-24）

三季版是 2021-22..2023-24 的 RAPM，四季版是 2020-21..2023-24 的 RAPM。兩者都含目標季，差別只在有沒有加入 2020-21。

| | 全部 | MIN≥500 |
|---|---|---|
| 人數 | 572 | 360 |
| 三季–四季 OVR Pearson | 0.980 | 0.983 |
| 三季–四季 OVR Spearman | 0.977 | 0.983 |
| 平均 \|ΔOVR\| | 1.22 | 1.38 |
| \|ΔOVR\|>3 人數 | 66 | 41 |
| 最大 \|ΔOVR\| | 14.6 | 14.6 |
| OVR 中位數 三季 → 四季 | 68.33 → 68.18 | 71.35 → 71.52 |

| 參照 | 子集 | n | ρ 三季 | ρ 四季 | 卡−2K 中位數 三季 | 四季 |
|---|---|---|---|---|---|---|
| 2K27 | 全部 | 377 | **0.550** | 0.532 | −5.70 | −5.83 |
| 2K27 | MIN≥500 | 299 | **0.544** | 0.523 | −5.66 | −5.85 |
| 2K24 | 全部 | 376 | **0.522** | 0.519 | −5.14 | −5.31 |
| 2K24 | MIN≥500 | 299 | 0.531 | **0.533** | −5.50 | −5.60 |

變動最大前 10（全部球員）：Anthony Edwards −14.6、Frank Ntilikina +14.0、Patty Mills +11.5、Devonte' Graham +10.6、Evan Fournier −10.5、P.J. Tucker −10.4、Svi Mykhailiuk −10.2、Reggie Bullock Jr. +10.0、Derrick Rose +10.0、Juan Toscano-Anderson +9.9。

MIN≥500 子集：Anthony Edwards −14.6、Evan Fournier −10.5、Clint Capela +8.6、Jimmy Butler III +7.9、Danuel House Jr. −7.7、Jusuf Nurkić +7.6、De'Anthony Melton +6.9、Dean Wade −6.3、Reggie Jackson +6.1、Mike Muscala +6.1。

加入 2020-21 後，變動集中在當季樣本多、之後角色變很多的球員。例如 Edwards 2020-21 是新秀，淨效率差；Ntilikina 和 Mills 則是 2020-21 的數字較好。對 2K 的 ρ 小幅下降（2K27 約 −0.02），但驗收不以 2K 為準。

## 影響

- §R.4：D1、D2 的 A、B、C3 誤差必須用這兩張新卡重算（D1 用四季版 `2023-24-v5.csv`）；v4 的 D1、D2 數字只能標「v4 舊答案」並列。三季版只做敏感度對照。
- 新卡 SHA：見 `<season>-v5.json` 的 `sha256`；之後任何預測誤差都以這兩個 SHA 為準。

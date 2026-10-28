# 實驗登記（experiments）

模擬版本、卡片版本、預註冊、回測與量測。讀寫規則見 [README.md](README.md)。逐份細節在 `reports/<資料夾>/`。

欄位（固定）：
- **ID**：`E-001` 起，只追加。
- **日期**
- **內容**：在試什麼。
- **設定**：版本、資料、人群、seed、預註冊檔；跑在哪（本機／5090）。
- **結果**：量到的數字與判定。
- **狀態**：`採用`｜`不採用`｜`停止`｜`參考`｜`進行中`。改狀態時括號註明日期與原因。
- **相關**：其他 ID。
- **來源**：commit、報告路徑。

範例：

```
### E-999
- 日期：2026-10-28
- 內容：賽中 OVR C4 回測
- 設定：preregistration-v5（凍結）、起點 Y5／Y6
- 結果：V1、V2 通過
- 狀態：採用
- 相關：F-019
- 來源：commit 560ddcc
```

2026-10-28 建立時由 git log 與報告搬入；只寫到能從 commit 訊息與 `reports/status/status.md` 確認的程度，細節以報告為準。防守批次（E-003、E-008–E-010）沒有獨立 commit（都在 b8dabc6 一次歸檔），日期取自報告檔的修改日期。

---

### E-001
- 日期：2026-09-05
- 內容：數值模型 v0.4：機率模型、模擬引擎、51 項驗證、OVR 逆推。
- 設定：本機。
- 結果：51 項驗證；踩過的坑見 L-001–L-012。
- 狀態：採用
- 相關：L-001–L-012
- 來源：commit 8d18901

### E-002
- 日期：2026-10-16
- 內容：模型 v14–v51 研究歸檔（球權、防守、輪替、進攻罰球等）。
- 設定：`reports/model-evolution-20261016/`；`docs/*-v45.md`…`*-v51.md`。
- 結果：球隊勝場 MAE v14 5.73 … v41 6.67（`reports/status/status.md` 球隊表）。
- 狀態：參考
- 相關：無
- 來源：commit b8dabc6

### E-003
- 日期：2026-10-12
- 內容：防守第 1–6 批（defense-runs、a、b1、third…sixth）。
- 設定：`reports/defense-*`；`npm run test:defense*`、`test:ability-sixth`。
- 結果：見各批報告。
- 狀態：參考
- 相關：E-008
- 來源：`reports/defense-runs/`…`reports/defense-sixth/`

### E-004
- 日期：2026-10-16
- 內容：OVR 第 1 步：v47 位置基準事後校正。
- 設定：`reports/ovr-v47-2025-26/`、`ovr-2025-26-positional/`。
- 結果：見報告。
- 狀態：參考
- 相關：E-005
- 來源：commit 000359f

### E-005
- 日期：2026-10-16
- 內容：OVR 第 2 步：可靠度收縮與本機加樣本驗證腳本。
- 設定：本機。
- 結果：見報告。
- 狀態：參考
- 相關：E-004
- 來源：commit 7254a33

### E-006
- 日期：2026-10-16
- 內容：期望產出 OVR 原型（2025-26）。
- 設定：`reports/ovr-expected-2025-26/`。
- 結果：見報告。
- 狀態：參考
- 相關：E-007
- 來源：commit 5b7b520

### E-007
- 日期：2026-10-16
- 內容：模擬校準的能力值 OVR（4 組種子）；新增「創造」能力值。
- 設定：`reports/ovr-calibrated-2025-26/`。
- 結果：查明中距離與持球防守不值分的原因（F-024）。
- 狀態：參考
- 相關：F-024、L-024
- 來源：commit d0b4b07、018c023、62a8be0

### E-008
- 日期：2026-10-12
- 內容：防守第七批：校準收尾、2024-25 跨季盲測、前季先驗。
- 設定：單一日曆截止日、25／41／55 切分、相同 20 seed；`npm run ability:seventh:*`、`npm run test:ability-seventh`。
- 結果：v4 收尾驗收未過，2024-25 改善未穩定重現；前季先驗沒有可靠改善。正式基準維持 v3。
- 狀態：不採用
- 相關：F-017、E-009
- 來源：`reports/defense-seventh/closeout.md`

### E-009
- 日期：2026-10-12
- 內容：防守第八批 A（重新分析與控制組）與 B（固定殘差倍率 c(25)=0.500000、c(41)=0.424513、c(55)=0，v5 凍結規格）。
- 設定：`reports/defense-eighth/a/closeout.md`、`b/closeout.md`、`b/v5-freeze.json`；`npm run test:ability-eighth-a`、`test:ability-eighth-b`。
- 結果：倍率在已看過答案的開發季選出，不算盲測（L-026）；simple 目標斜率超出預定範圍，未完成分散校準。
- 狀態：參考
- 相關：E-010、L-026
- 來源：README「已知限制」

### E-010
- 日期：2026-10-12
- 內容：防守第八批 C：兩個盲測季（2023-24、2022-23）。
- 設定：嚴格可用 1063／1079 場；共同日曆 25／41／55、每版本 20 seed；跨季配對 franchise＋seed 聯合重抽 20,000 次 95%／99.8% 區間；`npm run test:ability-eighth-c`。
- 結果：只有 v4cal 對 v4 的 net RMSE 改善跨季確認；v4 對 v3 在 K25 確認退步；v5 對 v4、v4cal 對 simple／simplecal 分不出。正式基準維持 v3。完成後停下，未開始下一批。
- 狀態：不採用
- 相關：F-017、R-010
- 來源：`reports/defense-eighth/c/closeout.md`

### E-011
- 日期：2026-10-16
- 內容：真實影響力驗收：在場／不在場與 RAPM 腳本。
- 設定：本機；`reports/impact-rapm/`、`reports/player-impact-validation/`。
- 結果：RAPM 結果見報告。
- 狀態：採用（RAPM 成為驗收參考）
- 相關：E-012
- 來源：commit 0757b71、cee0a67

### E-012
- 日期：2026-10-16
- 內容：以 RAPM 校準 box score OVR（RAPM 支援 box score 先驗），最終 OVR 第一版。
- 設定：`reports/ovr-rapm-calibrated-2025-26/`、`ovr-final-2025-26/`。
- 結果：修正 box score 先驗未收縮的錯誤。
- 狀態：參考
- 相關：E-011、E-013
- 來源：commit f4d2804、0bf073c、1f7377e

### E-013
- 日期：2026-10-16
- 內容：卡片 OVR 公式：以能力值預測最終 OVR。
- 設定：`reports/ovr-card-2025-26/`。
- 結果：見報告。
- 狀態：參考
- 相關：E-012
- 來源：commit f0dccee

### E-014
- 日期：2026-10-16
- 內容：v52 外線防守診斷。
- 設定：`reports/player-impact-v52/`。
- 結果：持球防守接回效果小（F-022）。
- 狀態：參考
- 相關：F-022
- 來源：commit e0ae5dc

### E-015
- 日期：2026-10-16
- 內容：四因素 RAPM：量測哪些防守是可重現的個人能力。
- 設定：`reports/impact-rapm/`。
- 結果：見報告（F-023）。
- 狀態：參考
- 相關：F-023
- 來源：commit e2a5038、db2d55a、3aeccb9

### E-016
- 日期：2026-10-17
- 內容：v53 防守壓力：逼出抄截以外的失誤、放大命中率壓制；期望分差用運氣記帳降雜訊。
- 設定：先 4 組種子判斷不了，再 8 組種子；平均運氣用群集標準誤。
- 結果：機制 1 有效、機制 2 不需要；v53 採用，卡片能力值改以 v53 期望分差校準，新增「壓迫」。
- 狀態：採用
- 相關：L-024、E-017
- 來源：commit 9b8aea9、a2ec37a、f690fc7、9558520、936ae3f、bd70818、63fb7af

### E-017
- 日期：2026-10-18
- 內容：v53 全季球隊量測。
- 設定：30 隊全季；`reports/player-impact-v53-team/`。
- 結果：2025-26 勝場 MAE 4.56、淨分 RMSE 2.019（壓迫係數樣本內）。
- 狀態：採用
- 相關：F-012
- 來源：commit a764cdb

### E-018
- 日期：2026-10-18
- 內容：卡片 OVR 混合目標（sim＋RAPM），預註冊。
- 設定：`reports/ovr-blended-2025-26/`。
- 結果：α=0.5 通過關卡，正式板改用（選項 B）；ρRAPM 因此部分樣本內。
- 狀態：採用（2026-10-20 由 E-026 取代）
- 相關：L-022、E-026
- 來源：commit 36c82a1、f4bbb8c

### E-019
- 日期：2026-10-18
- 內容：混合版卡片 OVR 的替補可靠度收縮，預註冊。
- 設定：`reports/ovr-blended-bench-shrinkage/`。
- 結果：G1、G2 未通過（G2 是平方誤差，不是 Brier，L-025）。
- 狀態：不採用
- 相關：L-025
- 來源：commit 1559e6b、964e814、e2a0e29

### E-020
- 日期：2026-10-18
- 內容：卡片屬性小樣本收縮，預註冊。
- 設定：`reports/ovr-shrinkage-2025-26/`。
- 結果：關卡 3 未過。
- 狀態：不採用
- 相關：無
- 來源：commit ac4b1a7

### E-021
- 日期：2026-10-18
- 內容：v53 模擬板可靠度收縮。
- 設定：`reports/ovr-v53-shrinkage-2025-26/`。
- 結果：第一版不採用；修正版（先發不收縮）採用。v53 收縮修正版樣本外 ρ 0.356／0.246。
- 狀態：採用（修正版）
- 相關：E-016
- 來源：commit 8061da5

### E-022
- 日期：2026-10-18
- 內容：v54：三分／禁區命中率改用可靠度加權收縮（EB），球員層與球隊層模擬（5090 遠端）。
- 設定：`reports/ovr-v54-*`、`reports/player-impact-v54-team/`。
- 結果：個人 ρ 提高，但球隊 2025-26 勝場 MAE 變差（F-013）；收束，卡片板仍為 v53 校準。
- 狀態：不採用（收束）
- 相關：F-013
- 來源：commit 896e132、5364ab8、23bc68e

### E-023
- 日期：2026-10-19
- 內容：v55 板凳屬性建構（多季加權＋角色條件先驗）。
- 設定：`reports/ovr-v55-bench-prior-2025-26/`。
- 結果：AC 通過預設門檻，但替補 AC 樣本外補驗不通過。
- 狀態：不採用
- 相關：無
- 來源：commit 71b9c29、23bc68e

### E-024
- 日期：2026-10-19
- 內容：v55 卡片修正三方向：B（吃餅長人禁區出手來源，B1／B2／B12）、C1（originShare 第 16 屬性）、D1（屬性建構層 long 去膨脹 `--attr-deflate`）。
- 設定：預設關閉；`reports/ovr-v55-finisher-fix-2025-26/`、`ovr-v55-card-origin-attr-2025-26/`、`ovr-v55-attr-deflate-2025-26/`；7 人驗收表。
- 結果：B12／C1／D1 樣本外 ρ 約 0.455–0.458，Karlo 掉名未過；C1 係數 0.031（SE 0.079）與 0 無法區分（L-023）。
- 狀態：不採用
- 相關：L-023、F-014
- 來源：commit 7393f8f、2f729a2、17cac74、e78dee1

### E-025
- 日期：2026-10-19
- 內容：2K27 評分＋2K19–27 逐年總評 × 卡片 OVR × v54 模擬板 × RAPM 對照。
- 設定：`reports/ovr-v55-2k27-compare/`。
- 結果：吃餅長人高估（F-014）；2K 成為外部基準。
- 狀態：參考
- 相關：F-014
- 來源：commit c85ea85

### E-026
- 日期：2026-10-20
- 內容：v55 卡片修正 E 系列：低分鐘收縮（E1）、吃餅折扣（E2）、合併（E3）。
- 設定：`reports/ovr-v55-card-E-2025-26/`；E2-λ0.4＝只打折 `short`：`effective_short = 70 + (short−70) × (s̃ + 0.4×(1−s̃))`，s̃＝自創禁區出手比例；PF/C 且 `creation` 在 [55,65] 斜坡內折扣線性減弱，≥65 幾乎不打折（固定規則，非回歸係數）。
- 結果：E2-λ0.4 首次同時過 Karlo 掉名與 ρ 門檻（樣本外 0.457／0.245、2K 0.478）；副作用 Gobert 第 91（F-015）。
- 狀態：採用（2026-10-21 由 E-029 取代）
- 相關：F-015、R-001、R-006
- 來源：commit 1609313、ef11e80

### E-027
- 日期：2026-10-20
- 內容：v56：在 E2-λ0.4 上疊加 PF/C 防守加分修正 Gobert 防守低估。
- 設定：`reports/ovr-v56-card-defense-2025-26/`；F2 γ=0.5（用 RAPM pooledD）。
- 結果：樣本外 ρ 0.474／0.273、2K 0.488。
- 狀態：採用（之後由 E-028、E-029 取代）
- 相關：F-015、R-006
- 來源：commit e483017

### E-028
- 日期：2026-10-20
- 內容：v57 G3 卡片（γ=1.0、δ=0.25）。
- 設定：`reports/ovr-v57-card-2025-26/`。
- 結果：樣本內 ρRAPM 0.843／0.697；樣本外 0.555／0.401；2K 0.530。
- 狀態：參考（v58 在它上面加封頂）
- 相關：E-029、L-016
- 來源：`reports/status/status.md`

### E-029
- 日期：2026-10-21
- 內容：v58 H1-m0：v57 G3＋2K 名次封頂（封頂只讀 RAPM），加入 RAPM 分半樣本外驗收。
- 設定：`reports/ovr-v58-holdout-2025-26/`、`ovr-v58-codex/`、`ovr-v58-ds-high/`。
- 結果：19/19 硬門檻全過；樣本外 0.563／0.391、2K 0.537；前十長人只有 Wemby／Giannis／Jokić／Chet。
- 狀態：採用（目前正式卡片）
- 相關：F-011、R-012
- 來源：commit f2f2bbb

### E-030
- 日期：2026-10-21
- 內容：補量測：模擬板與舊卡片層補樣本外 ρ 與對 2K27 ρ，新增卡片球隊指標與版本趨勢。
- 設定：`reports/ovr-metrics-backfill-2025-26/`。
- 結果：見 `reports/status/status.md`。
- 狀態：採用
- 相關：F-011
- 來源：commit bb9e8e4

### E-031
- 日期：2026-10-27
- 內容：v5 §R.3：重建 D1／D2 答案卡，RAPM 改為含目標季、最多四季；2023-24 答案卡重建；主卡恢復三季 D1。
- 設定：`reports/ovr-inseason-2026-27/v5/`。
- 結果：見報告。
- 狀態：採用
- 相關：E-033
- 來源：commit 9bee696、c8d3d48、6ff3a9b

### E-032
- 日期：2026-10-28
- 內容：v5 延伸回測資料：2010-11～2023-24 box 與 stint 歷史檔。
- 設定：`v5/history`（PR #5）。
- 結果：2021-22 stint 來源與 cdn 版不同（F-021）。
- 狀態：採用
- 相關：F-021
- 來源：commit ce2bff6

### E-033
- 日期：2026-10-28
- 內容：v5 Path A 賽中 OVR 判定：C4（單調收縮）vs C3（λ 混合）vs A（上季卡）。
- 設定：`preregistration-v5.md` §2–§3、`preregistration-v5-errata-c4.md`（凍結）、`disclosure-pointwise-ovr.md`；主判定 Y5、Y6，敏感度 Y3，次要 D1–D3。
- 結果：C4 與 C3 都通過，照 errata 順序上線 C4。Y3 因 |E_eff|=1 降為敏感度（L-019）。
- 狀態：採用
- 相關：F-019、F-020、L-019、R-008
- 來源：commit 560ddcc；`reports/ovr-inseason-2026-27/v5/pathA/README.md`

### E-034
- 日期：2026-10-28
- 內容：賽中 RAPM（C4R）。
- 設定：`v5/pathA/preregistration-rapm-inseason.md`（凍結，使用者核可）；`v5/tools/rapm_inseason_pathA.py`。
- 結果：R1 先決檢定 Y6 N=82 不過（最大 |net| 差 1.268、onlyRef=2），照 §4 整輪停止；G1–G3 沒算，沒看任何 C4R 誤差數字。
- 狀態：停止
- 相關：F-021、L-018、R-008
- 來源：commit 560ddcc；`reports/ovr-inseason-2026-27/v5/pathA/README-rapm-inseason.md`

### E-035
- 日期：2026-10-16（git log，b8dabc6；報告未寫日期）
- 內容：防守第九批步驟 1 提案：以真實強度為底、加上陣容差（Δ陣容）。
- 設定：只有提案，未實作；偏好選項見 proposal.md。
- 結果：規劃估計淨分 RMSE 降約 0.15–0.40、勝場 MAE 降約 0.15–0.50，報告明寫是規劃估計、未量測。
- 狀態：參考
- 相關：E-036、F-026
- 來源：reports/defense-ninth/proposal.md；commit b8dabc6

### E-036
- 日期：prereg 2026-10-13T00:39:47.300Z（報告內文）；檔案入庫 2026-10-16
- 內容：防守第九批步驟 2：四季開發診斷（Δsim-v3、Δsim-v4、Δseg、Δnaive）。
- 設定：四季全部已看過答案；K25/K41/K55；聯合 95% 區間（球隊＋種子 bootstrap 20000）；SHA 3b6261c7…5954e。
- 結果：三 K 合併 RMSE 對 naive 4.182：sim-v3 4.142、sim-v4 3.951、seg 3.675。Δseg 對最小者差 K25 -0.501 [-0.825,-0.128]、K41 -0.595 [-0.978,-0.128]、K55 -0.506 [-0.973,-0.023]。符合開發門檻：sim-v3、sim-v4、seg；尚非盲測確認。解讀檔建議 Δseg 為唯一主盲測候選，只有它的 95% 聯合區間在 0 以下，99.8% 區間跨 0。
- 狀態：參考
- 相關：E-035、E-037、F-026
- 來源：reports/defense-ninth/development/closeout.md、interpretation.md；commit b8dabc6

### E-037
- 日期：2026-10-16（git log）
- 內容：防守第九批盲測資料可行性探測（2021-22、2018-19、2017-18 端點 HEAD）。
- 設定：CDN 回 403／403，Stats 15 秒逾時；對照用已知可用網址也回 403。沒有下載任何資料。
- 結果：「三季盲測可行性仍有條件」；探測無法分辨「不存在」與「被擋」。
- 狀態：參考
- 相關：F-027
- 來源：reports/defense-ninth/development/feasibility.md；commit b8dabc6

### E-038
- 日期：2026-10-16（git log）
- 內容：防守第十批步驟 1：「純球員卡」向性稽核。
- 設定：只量測，步驟 2、3 未跑。
- 結果：凍結 v3 的近框保護與防守籃板主路徑被區段防守訊號取代，不符合新「純球員卡」定義；四個方向欄位皆 70。
- 狀態：參考
- 相關：E-039
- 來源：reports/defense-tenth/step1/report.md；commit b8dabc6

### E-039
- 日期：2026-10-16（git log）
- 內容：防守第十批步驟 2：純卡四季診斷（240 補跑 = 4 季 x 3 K x 20 種子，種子 20261012–31）。
- 設定：純卡 vs v3 vs v1 vs simple；四季皆已看過答案。
- 結果：淨分 RMSE（純卡/v3/v1/simple）K25 4.933/4.526/4.917/4.225、K41 5.014/4.766/4.998/4.294、K55 5.370/4.977/5.497/4.555。純卡減 simple：K25 0.708 [-0.087,1.453]、K41 0.719 [0.046,1.434]、K55 0.815 [0.149,1.573]。勝場 MAE 三 K 點估計都較差但聯合區間含 0。關掉區段訊號使防守 RMSE 三 K 顯著升高。結論：不採用純卡取代 simple。
- 狀態：不採用
- 相關：F-025、E-038
- 來源：reports/defense-tenth/step2/report.md；commit b8dabc6

### E-040
- 日期：規則 2026-10-13T04:18:13.407Z（報告內文）
- 內容：防守第十批步驟 3-A：跨季純卡，半盲（protocol tenth-cross-personal-v1）。
- 設定：SHA 8296c18e…5bd；三季皆已看過答案，只稱半盲，未改凍結版本。
- 結果：prior minutes 對均值回歸對照：淨分 RMSE 差 0.956 [0.022,1.957]（顯著較差）、勝場 MAE 差 1.353 [-0.287,3.157]。真實分鐘診斷：淨分 -0.384 [-1.293,0.587]、勝場 -0.928 [-2.455,0.724]，皆不可分辨。
- 狀態：不採用
- 相關：F-025
- 來源：reports/defense-tenth/step3-a/report.md:7；commit b8dabc6

### E-041
- 日期：登記 2026-10-13T05:22:10.790Z、曲線鎖定 05:24:01.159Z（報告內文）
- 內容：防守第十批步驟 3-A2：分層診斷與年齡曲線（L1/L2/L3、P3）。
- 設定：SHA fa301dfa…67cd；P3 是唯一只用前季個人資料的新預測版本，仍屬已看過答案的半盲。
- 結果：2025-26 淨分 L2−L1 -0.475 [-1.020,0.111]、L3−L2 0.080 [-0.367,0.489]、P3−A -0.053 [-0.398,0.304]；勝場 MAE -1.063 [-2.003,-0.070]、0.077 [-0.700,0.927]、0.150 [-0.615,0.868]。淨分三項皆不可分辨。「完成A2即停下，B/C未開始。」
- 狀態：參考
- 相關：E-040
- 來源：reports/defense-tenth/step3-a2/report.md；commit b8dabc6

### E-042
- 日期：T0 2026-10-13T07:39:42.310Z、T1 06:34:58.236Z、T2 06:56:53.816Z（報告內文）
- 內容：防守第十批步驟 4 的 T0/T1/T2 診斷（t2-supplement、t2b 只是球員描述表，無獨立結論）。
- 設定：T0 純卡排名線；T1 凍結 v3/v1/A2 排名線；T2 防守來源端點（575 個成功，嚴格覆蓋 86.42–96.59%）。
- 結果：T0：純卡 1/4 季通過淨分排名線（各季淨分 RMSE 2.857、2.470、3.061、3.647），含區段訊號的 v3 也是 1/4。T1：2025–26 凍結 v3 通過兩條排名線；v1 不通過；A2 的 L1、L2 三季皆未過。T2：直接防守事件與近框壓制最值得作新卡來源；官方個人防守效率、原始在場效率、三分命中率差不適合直接當可攜防守能力。
- 狀態：參考
- 相關：E-039、E-043
- 來源：reports/defense-tenth/step4-t0、step4-t1、step4-t2 的 report.md；commit b8dabc6

### E-043
- 日期：2026-10-14（登記時間戳，步驟 4 rebounds 系列 05:43–08:55）
- 內容：防守籃板與進攻籃板的前置稽核：dreb（pure-dreb-rate-1）、body、opportunity、components（oreb-components-offline-1）、context、talent。
- 設定：四季皆已看過答案、20 種子、樣本內。
- 結果：dreb 未達後續研究條件，維持 T0 純卡基準（淨分 RMSE 差 -0.180 [-0.380,+0.039]；DREB RMSE 差 -0.659 [-0.807,-0.468] pp）。body：身高體重可分開保留，現有來源不足以估力量、彈跳、觸球高度。opportunity：守恆成立，缺口是位置標籤代替機會。components：三個候選皆未過門檻，不接入引擎（2025–26 OREB/36 MAE：carry-over 0.3338、加機會 0.3200、加取得率 0.3178、兩者 0.3187）。context：角色與隊友代理都沒有可確認的 OREB 價值（0.35151 對 0.35391–0.35512）。talent：沒有證據把選秀體測寫進卡或引擎。
- 狀態：不採用
- 相關：E-044
- 來源：reports/defense-tenth/step4-rebounds*/report.md（本體、-body、-opportunity、-components、-context、-talent）；commit b8dabc6

### E-044
- 日期：2026-10-14（git log；報告時間戳未逐份核對）
- 內容：OREB 取得率候選（step4-rebounds-oreb）與個人分配（-allocation）。
- 設定：四季、20 種子、樣本內。
- 結果：oreb：OREB 率去均值 MAE 2.0695→0.4600 pp（差 -1.6095 [-1.8982,-1.2832]）；淨分 RMSE 3.0748→2.5546（差 -0.5202 [-0.8236,-0.2047]）；勝場 MAE 5.5500→5.0575（差 -0.4925 [-0.9921,+0.0058]，區間跨 0）。allocation：個人 OREB36 MAE 0.4605→0.0956（-0.3650 [-0.3902,-0.3312]）；淨分 RMSE 2.5546→2.5704（+0.0158，區間跨 0）。兩者保留為獨立開關。
- 狀態：採用
- 相關：E-043、E-047
- 來源：reports/defense-tenth/step4-rebounds-oreb、-allocation 的 report.md；commit b8dabc6

### E-045
- 日期：2026-10-14 至 10-15（登記時間戳，nonshoot-foul 為 2026-10-15T01:51:06.728994）
- 內容：OREB 之後的診斷與單因子試驗：after、paths、zone-reader、state-time、possession-value、putback-risk、turnover-types、nonshoot-foul。
- 設定：多為量測；單因子試驗皆不改基準。
- 結果：after 量測：模擬補籃近框出手 15.121 對真實 31.700；到下一個結果的時間 4.528s 對 2.552s。zone-reader：10,767 筆矛盾中距離標籤改為近框、969 筆未知。putback-risk、turnover-types：不採用。nonshoot-foul：「局部修正有效，保留為獨立候選；基準不變」。
- 狀態：參考
- 相關：E-044、E-046
- 來源：reports/defense-tenth/step4-rebounds-{after,paths,zone-reader,state-time,possession-value,putback-risk,turnover-types,nonshoot-foul}/report.md；commit b8dabc6

### E-046
- 日期：2026-10-14T20:09 至 2026-10-15T03:39（登記時間戳；clock-competing 為 2026-10-15T03:39:51.367263）
- 內容：補籃時間與時鐘系列：putback-time、clock、turnover-time、clock14、rim-calibration、clock-sources、clock-state、rim-clock、clock-competing。
- 設定：單因子；clock-competing SHA 101e648f…d4e。
- 結果：putback-time 不採用（淨分 RMSE 2.5704→2.5263，差 -0.0441 [-0.1808,+0.0978]）。clock 未過候選門檻（2.5704/2.5263/2.5544）。turnover-time：時序辨識改善、準確度未顯著（2.5544→2.5553，勝場 MAE 5.0525→4.9375）。clock14：推翻「把 0.73% 補成新的 14 秒違例」，時間相容只有 12–19%。rim-calibration：pEffective=0.211278187，未過驗收，不升基準。clock-sources 只找到 2 例官方重播；clock-state 現有資料無法辨識碰框，不改引擎。clock-competing：計數、漂移、無退步閘門過，時序診斷未過，保留實驗選項、基準不升。
- 狀態：不採用
- 相關：E-045、E-047
- 來源：reports/defense-tenth/step4-rebounds-{putback-time,clock,turnover-time,clock14,rim-calibration,clock-sources,clock-state,rim-clock,clock-competing}/report.md；commit b8dabc6

### E-047
- 日期：2026-10-15（git log 最後入庫 2026-10-16，b8dabc6）
- 內容：防守第十批收束（step4-rebounds-closeout）。
- 設定：預設組合 `pure-oreb-turnover-time-1`。
- 結果：可選時鐘淨分 RMSE 2.5553→2.5592（+0.0039 [-0.1199,+0.1321]）、勝場 MAE 4.9375→4.9775，故不入預設。「本輪已收束」；「不再為時鐘開新一輪」；補籃／重攻是下一個候選，「目前未證實收益，不自動開始」。四季皆已看過答案，是重現成績，不是事前或換隊預測。
- 狀態：停止
- 相關：E-044、E-046、F-026
- 來源：reports/defense-tenth/step4-rebounds-closeout/report.md:63-68；commit b8dabc6

### E-048
- 日期：2026-10-28（報告內文用 seed 20261028；comparison.json 修改時間 2026-10-28 17:28）
- 內容：v59 第一階段：3PT 拉回目標改為「依出手頻率預測的三分%」。
- 設定：擬合只用 2010-11～2023-24；回測為 2025-26 前 41 場特徵對後 41 場 3P%，後 41 場 3PA>=50 共 313 人；配對 bootstrap 2000 次。
- 結果：勝出 (b) 只用出手頻率（k=407.396）；3PA 加權中位絕對誤差 3.37→3.21 pp，改善 0.16 pp，但 90% 區間 [-0.50, 0.25] pp 含 0，證據偏弱。(c) 加罰球% 為 3.28 pp，未比 (b) 低 0.05 pp，不採用 (c)。Portis 3PT 98.5→85.6、排名第 2→第 9。報告沒有寫是否升為正式卡。
- 狀態：參考
- 相關：E-033
- 來源：reports/ovr-v59-3pt-prior-2025-26/report.md:3-5；未追蹤（.gitignore）

### E-049
- 日期：2026-10-27（S1-report.md 內文，第 2 輪）
- 內容：賽中 OVR S1：2024-25 先驗重建。
- 設定：preregistration §2.2、§6.2；依使用者裁決改 sanity 判準後重跑，先驗內容與第 1 輪完全相同。
- 結果：S1 全數通過。569 人（要求 >=550）；15 項覆蓋率 100%；與 personal-cards 9 項 box 能力值 Spearman 0.9908–1.0000；撤掉參考檔校準後逐項中位絕對差最大 2.430（short，門檻 <=5）。
- 狀態：參考
- 相關：E-050
- 來源：reports/ovr-inseason-2026-27/S1-report.md；未追蹤（.gitignore）

### E-050
- 日期：2026-10-27（backtest/report.md 內文）
- 內容：賽中 OVR v1 回測 S2–S6（預註冊 preregistration.md，日期 2026-10-26）：收縮版 C 對先驗 A 與觀測 B。
- 設定：k 由 2022-25 季內分半信度反解；N=3/5/10/20。
- 結果：§4.4 判「未勝出」，五條門檻第 3、4 條過，第 1、2、5 條未過。C 在 4 個 N 的 ρ 都贏 A；N=10 輸 B（ρ 0.8044 對 0.8054、OVR MAE 5.669 對 5.712）；N=20 輸更多（0.8253 對 0.8456、5.459 對 5.159）。80% 區間覆蓋率 0.42／0.55。正式維持先驗，不發布區間，S7 不做。
- 狀態：不採用
- 相關：E-051
- 來源：reports/ovr-inseason-2026-27/backtest/report.md:1-12；未追蹤（.gitignore）

### E-051
- 日期：2026-10-27（preregistration-v2.md 與 v2/report.md 內文）
- 內容：賽中 OVR v2：k 含跨季漂移 δ²，加 OVR 區間與 A/B 退路（種子 20261026，未做 S7）。
- 設定：只用 2023-24→2024-25 的 δ²；2025-26 只在 S4 之後當答案。
- 結果：不採用 C_v2；五條門檻第 1、2、5 條未過，§2.5 退化條款（Σδ² <= 0.05·Σσ²）成立，走 §4.4 退路，一律顯示 A（A/B 退路）。
- 狀態：不採用
- 相關：E-050、E-052
- 來源：reports/ovr-inseason-2026-27/v2/report.md；preregistration-v2.md；未追蹤（.gitignore）

### E-052
- 日期：2026-10-27（preregistration-v3.md 與 v3/report.md 內文）
- 內容：賽中 OVR v3：逐能力值逐 N 的今年訊號權重 w_a(N)＋多起點 expanding window 回測（補抓 2021-22）。
- 設定：種子 20261026；候選依 §2.5 選 C2；2021-22 的 mid/short/creation 層不可行（§4.3）。
- 結果：不採用 v3，維持 v2 退路（一律顯示 A）。§7 指標 1 有 3 格失敗（D2 N=3、D2 N=10、D3 N=3）；指標 2 全過；80% 覆蓋率 0.46／0.49 遠低於 [0.70,0.90]，ε_ovr raw 13.70／8.77／6.68 > 3.0，不發布區間。
- 狀態：不採用
- 相關：E-051、E-053
- 來源：reports/ovr-inseason-2026-27/v3/report.md；未追蹤（.gitignore）

### E-053
- 日期：2026-10-27（preregistration-v4.md、v4/report.md 內文；檔案修改 2026-10-27 06:25）
- 內容：賽中 OVR v4：收縮候選 C3（λ 混合）＋座標補回 2021-22 mid＋經驗分位區間（P0→P7）。
- 設定：種子 20261026；λ 依 §2.3 機械選出，每步連跑兩次比對 SHA。
- 結果：G3 = false。D2 N=3 C3 4.4647 > A 4.4596；N=5 4.5321 > 4.5262；N=10 4.8021 > 4.4596；D3 N=3 5.9522 > 5.8366；其餘 4 格過。C3 在 D2 反而輸給 A 與 v3 的 C2。F0 未執行，`v4/frozen/params-2026-27.json` 與 `FROZEN.sha256` 不存在。後續由 v5 勘誤（preregistration-v4-errata-v5.md，2026-10-28）改答案 RAPM 欄。
- 狀態：不採用
- 相關：E-052、E-031、E-033
- 來源：reports/ovr-inseason-2026-27/v4/report.md:24,81,86；未追蹤（.gitignore）

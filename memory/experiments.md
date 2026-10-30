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
- 狀態：不採用（2026-10-28，改善在雜訊內且 Giannis 掉出前十；使用者改走 v62，見 E-056）
- 相關：E-033、E-056
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

### E-054
- 日期：2026-10-28
- 內容：v60 切入 A 階段：卡片 `drive` 拆成 `foulDraw`（原 FTA/FGA 百分位）與新 `drive`（非助攻突破，PBP descriptor 類別加權近似）。只改卡片，模擬未拆。
- 設定：2025-26 前 41 場切點（每隊約 38.3 場，engine-signals 574 場）；v58 H1-m0 校準流程與 evaluate.mjs 19 項門檻。
- 結果：Gobert 切入第 3→第 196（drive 53.8、foulDraw 99），SGA 18→2、Brunson 98→14。OVR 對 v58 ρ 0.9999、最大變動 0.7，Gobert OVR 維持 84.9。evaluate 19/19。App 重跑 ranking 雜湊 79D0CB17… 吻合。回歸裡新 drive 係數 −0.013（SE 0.072），價值歸 foulDraw（+0.074/10 點），見 TODO.md。
- 狀態：參考（待使用者決定是否升正式卡；模擬端拆分屬 B 階段）
- 相關：E-029、R-015、R-016
- 來源：reports/ovr-v60-drive-split-2025-26/；未追蹤（.gitignore）

### E-055
- 日期：2026-10-28
- 內容：v61 低分鐘球員膨脹修正：比率型屬性（rebound、pass、tovSkill、foulDraw、drive 等）改為往球員自己的歷史（上季）拉回，沒有歷史才往聯盟平均拉回。不設最少出場分鐘篩選（R-014）。
- 設定：派工 20261028-173721-31b6f1（role-card、worker 帳號）；long 欄應與 v60 相同。
- 結果：rebound、pass、tovSkill、foulDraw、drive、mid、short、ft 八欄先往本人前 3 季歷史拉回（k、λ、kh 各欄擬合；歷史季回測，2025-26 前 41→後 41 為測試）。測試集 MAE 八欄都是「往本人歷史」最低，對聯盟平均版的區間全不含 0；對另一候選在 drive、mid 含 0。long 與 v60 逐人相同（lead 重算 582 人 0 差）。evaluate 19/19；16 名長人達標 15/16（v60 16/16）；對 2K27 ρ 0.5376→0.5092（樣本外訊號，變差）；對 RAPM ρ 0.8520→0.8685（樣本內，R-007 不算證據）。抽查：Darius Brown II 籃板 99→53.5、名次 172→359；Colby Jones 107→316；但 N'Faly Dante 513→222（歷史好）、Taj Gibson 293→513；MIN<100 的 79 人名次中位 369→316、前 200 人數 12→8。傷停明星組只有 Holiday（27→27），樣本不足。ranking.csv sha256 6238984a…a62c，子 session 重跑一致、lead 重算一致。子 session 另加 kh 參數（spec 外）；2024-25 用本機存檔。
- 狀態：參考（2026-10-28，等使用者 G5 抽查；2K27 ρ 下降要判斷）
- 相關：E-054、R-014
- 來源：reports/ovr-v61-shrink-history-2025-26/

### E-056
- 日期：2026-10-28
- 內容：v62 3PT 第二階段（卡片端）：研究投籃難度（持球自投／接球、防守距離）與出手量對 3PT 屬性的影響。
- 設定：派工 20261028-173433-e327a1（role-card、worker 帳號）；資料抓不到就回報失敗，不硬做。
- 結果：資料取自 stats.nba.com CatchShoot／PullUp＋最近防守者距離四段，manifest 1101 筆，2025-26 切點與 seventh-base 30/30 相同。擬合季選法勝出 (b)（v59 方法）；難度調整 (c)、(c)+出手量 (d) 都沒比 (b) 低 0.05 pp。測試集中位誤差 (a) 3.387、(b) 3.155、(c) 3.362、(d) 3.381 pp，中位差的 90% 區間全含 0；(b)−(a) MAE −0.178 [−0.32, −0.05] 是唯一有訊號的比較。控制難度後出手量沒有額外預測力。直覺驗收未過：(b) 下 Curry 13、Edwards 26、Knueppel 2、LaMelo 52；(c) 下 27／7／5／72；加「承擔分數」旋鈕 w 0–40 都無法四人同時進前 15（LaMelo 實際 36.8%、期望 34.9%）。前十長人門檻未過（Giannis 掉出）。子 session 撞 max_turns 60 截斷，但 report.md 已產出；雜湊未由 lead 重跑。
- 狀態：參考（2026-10-28，直覺驗收未過；等使用者決定 3PT 的定義是「命中能力」還是「投射威脅／承擔」）
- 相關：E-048、R-017
- 來源：reports/ovr-v62-3pt-difficulty-2025-26/

### E-057
- 日期：2026-10-28
- 內容：`card 0.1.1+E057` 三分價值（預註冊，公式在派工前凍結）：卡片顯示的 3PT 與 OVR 改用新屬性 `threeValue`，模擬用的 `long` 不動（模擬已用 `shotProfile.threeRate` 決定出手量，`long` 混入出手量會重複計算）。
- 設定：準度 acc = v62 方法 (c) 的 abilityC（2025-26 全季、依出手類型調整難度、k=294.667，`reports/ovr-v62-3pt-difficulty-2025-26/new-long.json`）；出手量 vol = v62 `Ds.feat('r36')`（每 36 分鐘 3PA，含偽分鐘拉回）；替補水準 rep = 聯盟三分命中率 mu − 0.03；value = vol × (acc − rep)；`threeValue` = value 在 MIN≥500 池內的百分位，套用卡片既有的 `attr()`（40–99）。基準卡 = card 0.1.1（`reports/ovr-v61-shrink-history-2025-26/ranking.csv`）。主要版本：OVR 迴歸裡用 `threeValue` 取代 `long`；次要版本（參考）：兩者並列。rep ±0.02 只當敏感度參考，不得用來挑版本（L-026）。
- 驗收（事先訂定）：(1) Curry、Edwards、Knueppel、LaMelo 在 MIN≥500 池的 threeValue 名次都 ≤15；(2) Portis 的名次比基準卡 `long` 名次後退（不設門檻，R-020）；(3) 主要版本 OVR 對 2K27 的 Spearman 高於基準 0.5092（樣本外，決定 MINOR 或 PATCH，R-019）；(4) 前十長人門檻與 evaluate.mjs 其他門檻不比基準差；(5) `npm test` 過。
- 結果：App 內 sonnet 子代理執行；lead 抽查 evaluation.json 與 ranking.csv 數字相符。驗收 5 項過 3 項：(1) 過，threeValue 池內 Curry 1、Knueppel 2–3（同分排序差異）、Edwards 7、LaMelo 10；(2) 過，Portis long 第 2 → threeValue 第 18（Kennard 1→25）；(3) 未過，主要版本（取代 long）2K27 ρ 0.4956 < 0.5092；(4) 未過，noMobleyTop10 失敗（Mobley 進 OVR 第 10，前十長人 4→5 人），其餘 18 門檻持平；(5) 過，npm test 57/0。次要版本（並列）2K27 ρ 0.5175、19/19 門檻，但它是看結果前就標為參考的版本，不能事後改當主要版本（L-026）。RAPM ρ 0.8785／0.8684 為樣本內。對照重跑 v61 位元組相同（sanity-v61-repro/）。
- 狀態：不採用進 OVR（2026-10-28，主要版本驗收未過）；threeValue 本身可作為顯示用屬性，並列版需另行預註冊樣本外檢驗
- 相關：E-056、R-017、R-019、R-020
- 來源：使用者 2026-10-28

### E-058
- 日期：2026-10-28
- 內容：`card 0.1.1+E058` 單防／協防拉回（預註冊）：`onBall`（最近防守者時對手三分命中率差，`leaguedashptdefend` 3 Pointers）與 `help`（6 呎內）現在用 k=200 往 0 拉回（`scripts/.seventh-base-2025-26-25.js:24`），雜訊太大。例：Luka 128 次被防三分、對手低 4.8 pp（約 1.1 個抽樣標準差；更正：正式卡是全季 418 次、約 2 個標準差，見 L-029）→ onBall 83、全聯盟第 9；他的 pooledD 是 478 人第 246。
- 設定：方法 (a) 現行 k=200 往 0；(b) 往 0、k 用擬合季最大概似估計；(c) 往本人前兩季（衰減 λ 擬合或固定 0.5，二選一寫明）、k 與 kh 擬合；(d) 先驗中心 = 本人前一季以前的 pooledD 換算值、k 擬合（會汙染 RAPM ρ，只看 2K27 ρ）。擬合季 2023-24、2024-25：每隊第 41 場前預測之後的對手命中率（按被防出手數加權的 log-likelihood）；測試季 2025-26 同切法。選擇規則：擬合季分數最好者勝，與更簡單的方法差距 < 0.5% 相對 log-lik 時選簡單的（a<b<c<d）。只用一次測試季，不得看測試季再換方法（L-026）。卡片用 2025-26 全季（正式卡的窗，`scripts/build_season_league.js:100-106`，輸入 `data/benchmark-source/defense-long.json`／`defense-rim.json`）＋勝出方法重算 onBall／help，基準卡 = card 0.1.1。（2026-10-28 更正：原寫「前 25 場」是 lead 把回測卡 `.seventh-base-2025-26-25.js` 誤當正式卡，見 L-029；回測設計不變。）另附參考表：Luka 與 pooledD 前 15 名的 FREQ（被防三分出手佔對手三分出手比）對同位置隊友，只作參考，不進驗收。
- 驗收（事先訂定）：(1) 勝出方法在測試季的加權 log-lik 優於 (a)，附 bootstrap 90% 區間；(2) OVR 對 2K27 Spearman 不低於基準 0.5092 − 0.005；高於 0.5092 才算變準（R-019）；(3) evaluate.mjs 其他門檻不比基準差；(4) 直覺抽查：Luka onBall 池內（MIN≥500）名次 > 30；(5) `npm test` 過。
- 結果（2026-10-28，`reports/card-0.1.1+E058-defense-shrink/`，lead 已核對 evaluation.json、fit_results.json）：擬合季 log-lik 合計 (a) −1.31526、(b) −1.31462（long k≈2081／short k≈98）、(c) −1.31415（λ=0.5 固定；long k≈2195 kh≈1618、short k≈147 kh≈155）；(d) 不可用（rapm.csv 沒有逐季窗）。依選擇規則差距 < 0.5% → 主勝出 (a)＝現行，驗收 (1)(4) 不過。備選 (c) 測試季勝過 (a) +0.00128 [0.00098, 0.00160]，主要來自 rim；2K27 ρ 0.5007（不過 (2)），RAPM ρ 0.8697（樣本內），19/19 閘，Luka onBall 9→39。關鍵發現：三分區測試季所有方法都不贏「人人聯盟平均」（null），(c) 只是輸得最少 → 對手三分命中差幾乎沒有可預測的個人成分。偏離：2023-24 只有前一季歷史（沒抓 2021-22）；FREQ 用 NBA 定義（被防出手中 3PA 比例），無隊內對手 3PA 總數。
- 狀態：不採用（2026-10-28，主勝出＝現行、備選 (c) 2K27 ρ 未過）；選擇規則的 0.5% 門檻設計有誤，見 L-030
- 相關：E-055、R-019
- 來源：使用者 2026-10-28

### E-059
- 日期：2026-10-28
- 內容：`card 0.1.1+E059` onBall 改成看可延續的行為（預註冊）：E-058 顯示對手三分命中差在測試季沒有任何方法贏過「人人聯盟平均」，現行 onBall 基本是雜訊。改用 defense-tenth step4-t2 的建議：三分干擾／36（換隊相鄰季 r 0.72）、對位負擔（PARTIAL_POSS 加權對手 USG，r 0.65），加上使用者提的「被針對程度」（對手透過對位選擇打他的程度）。help 不動。
- 設定：資料用 `reports/defense-tenth/step4-t2/raw/<season>/`（hustle、matchups，四季全季，已有 sha256）。三個分量：(i) C3＝CONTESTED_SHOTS_3PT/36，往同位置組（G／F／C，取主位置）平均拉回、k=500 分鐘；(ii) B＝對位負擔，往全聯盟平均拉回、k=1000 PARTIAL_POSS；(iii) T＝被針對＝對位 FGA／100 PARTIAL_POSS 減同位置組平均，k=1000 拉回，越高越差。T 先過穩定性門檻才納入：只用擬合季（2022-23→2023-24、2023-24→2024-25 相鄰季，兩季各 ≥500 分鐘）r ≥ 0.5，不過就丟掉、不再找替代。合成：onBall_z＝z(C3, 同位置組內)＋z(B)－z(T)（T 不過時只用前兩項），等權、不擬合權重；再用正式卡同一個百分位池與 attr() 對應到 40–99。卡片窗＝2025-26 全季（`scripts/build_season_league.js`），基準卡＝card 0.1.1，OVR 依 v61 流程重擬。只改卡片，模擬端 onBall 語意另列 TODO。
- 驗收（事先訂定）：(0) 新 onBall 在擬合季的相鄰季 r ≥ 0.5（同時列舊 onBall 的 r 對照），不過就停，不建卡；(1) OVR 對 2K27 Spearman ≥ 0.5092 − 0.005；高於 0.5092 才算變準（R-019）；(2) evaluate.mjs 其他門檻不比基準差（基準 19/19）；(3) 直覺抽查：Luka onBall 池內（MIN≥500）名次 > 30；(4) `npm test` 過。另列參考（不進驗收）：onBall 新舊前 15、pooledD 前 15 的新名次、OVR 前 20 差異、RAPM 樣本內 ρ。只看一次 2025-26，不得看結果再改分量、k 或權重（L-026）。
- 結果（2026-10-28，`reports/card-0.1.1+E059-onball-contest/`，lead 已核對 evaluation.json、stability.json，並自己重做 2K27 ρ 配對 bootstrap）：(0) 新 onBall 相鄰季 r 0.770／0.746（舊 onBall 0.067／0.105）；T 的 r 0.822／0.790，納入。(1) 2K27 ρ 0.5124（基準 0.5092，+0.0032；lead 配對 bootstrap 2000 次 90% 區間 [−0.0036, +0.0106]，P(差≤0)=0.22，在雜訊內）。(2) 19/19（bigPass 14/16，基準 15/16）。(3) Luka onBall 9→269。(4) npm test 57 過。不換 onBall 的重跑與 v61 byte-identical。樣本內 RAPM ρ 0.8657（基準 0.8685）。抽查問題：Wembanyama onBall 14→373（分在 F 組；T 的 z +3.26。原先 lead 說是「協防出手被算進對位」，查欄位後更正：matchups 有獨立的 HELP_FGA，MATCHUP_FGA 不含協防；真正原因是他被列 F 卻守中鋒，T 拿 F 組平均 20.3 比，而他守的中鋒本來就每回合出手多，C 組平均 26.5，他 27.2），Embiid 186→339、Gobert 215→312；外線防守者 Caruso 254→20、Herbert Jones 113→5、Ausar Thompson 214→6、Dyson Daniels 第 2。偏離 10 點見 report.md（位置取 PLAYER_POSITION 首字母、7 人缺分量給 70 等）。
- 狀態：預註冊驗收全過（2026-10-28）；+0.0032 是否算 R-019 的「變準」與 Wembanyama 的 T 問題，待使用者裁定
- 相關：E-058、R-019、L-029、L-030
- 來源：使用者 2026-10-28 GO

### E-060
- 日期：2026-10-28
- 內容：`card 0.1.1+E060` 修正 E-059 的「被針對」T（預註冊）。E-059 的 T＝對位 FGA／100 回合減同位置組平均，位置組錯置時會誤判：Wembanyama 被列 F 卻守中鋒，onBall 14→373。改成和位置無關的定義：T＝實際對位 FGA 減「這些對手平常的出手率」預期值，也就是對手在他面前是不是比平常更愛出手。
- 設定：沿用 E-059 的資料、C3、B、合成方式（z(C3)＋z(B)－z(T)）、k、百分位池與 attr()，只換 T。對每位防守者 d：預期 FGA＝Σ_o PARTIAL_POSS(d,o)×r_o；r_o＝進攻者 o 當季所有對位的 ΣMATCHUP_FGA／ΣPARTIAL_POSS，計算時排除 d 自己的那幾列（leave-one-out）。T_raw＝100×(實際 FGA－預期 FGA)／ΣPARTIAL_POSS(d)，往 0 拉回，k=1000 回合；z 的母體＝當季 MIN≥500。T 照樣先過擬合季相鄰季 r ≥ 0.5 才納入，不過就只用 z(C3)＋z(B)。lead 預註冊前已看過 E-059 的 Wembanyama 數字，所以下面 (5) 屬於看過問題才設的抽查，只當必要條件，不當變準的證據。
- 驗收（事先訂定）：(0) 新 onBall 擬合季相鄰季 r ≥ 0.5；(1) 2K27 ρ ≥ 0.5092 − 0.005；「變準」要對基準 card 0.1.1 做配對 bootstrap（2000 次、以球員重抽），90% 區間下界 > 0 才算（L-031）；(2) evaluate.mjs 其他門檻不比基準差（19/19）；(3) Luka onBall 池內（MIN≥500）名次 > 30；(4) `npm test` 過；(5) Wembanyama、Gobert、Embiid 的 onBall 池內名次都 ≤ 200。另列參考：與 E-059 並排的 onBall 前 15、pooledD 前 15、OVR 前 20 差異。只看一次 2025-26，不得看結果再改（L-026）。
- 結果（`reports/card-0.1.1+E060-onball-targeting/`，lead 已核對 evaluation.json、bootstrap.json）：(0) 過，新 onBall 相鄰季 r 0.808／0.785，T r 0.905／0.884；(1) 過，2K27 ρ 0.5181，差 +0.0089，bootstrap 90% 區間 [+0.0003, +0.0181]，P(差≤0)=0.045，按 L-031 算「變準」但很勉強；(2) 過，19/19；(3) 過，Luka onBall 9→276；(4) 過；(5) **不過**：Wembanyama 344、Gobert 356、Embiid 368（zT 各 +2.54、+2.12、+1.33），Holmgren 63→332、Brook Lopez 141→371。OVR：Luka 3→8、Kawhi 10→4、Wembanyama 維持 5。v61 重現逐位元相同。
- 診斷（lead 事後看，不算證據）：長人的超額出手主要來自守其他長人：Wembanyama 對 Draymond Green 106 回合 33 次出手（平常 13/100）、Nurkić 103 回合 28 次（平常 15/100）、Adebayo 60 回合 25 次。長人在籃下對位，對手的補籃與禁區出手都記在他頭上；對手的「平常出手率」大多是被外線防守者守時量到的，所以長人永遠顯得「被針對」。Caruso 則是 −3.5/100。T 這個概念對外線有用，對內線是結構偏差，不是能力。
- 狀態：不採用（2026-10-28，預註冊驗收 (5) 不過）→ 採用（2026-10-28，使用者裁定 (5) 與 onBall 定義矛盾，見 R-022）
- 相關：E-059、L-031、R-019
- 來源：使用者 2026-10-28「先修長人」

### E-061
- 日期：2026-10-28
- 內容：`card 0.1.1+E061` 被針對的 T 只看三分出手（預註冊）。E-060 的 T 算全部出手，長人守長人時對手籃下補籃、禁區出手多，造成結構偏差（Wembanyama 344、Gobert 356）。改成只問「對手在他面前是不是比平常更愛投三分」，衡量外線被針對的程度，籃下出手不計入。
- 設定：除了 T 以外，全部沿用 E-060（資料、C3、B、合成 z(C3)＋z(B)－z(T)、k、百分位池、attr()、leave-one-out）。T3：預期 3PA＝Σ_o PARTIAL_POSS(d,o)×r3_o；r3_o＝進攻者 o 當季所有對位的 ΣMATCHUP_FG3A／ΣPARTIAL_POSS，排除 d 自己的那幾列。T3_raw＝100×(實際 MATCHUP_FG3A－預期)／ΣPARTIAL_POSS(d)，往 0 拉回，k=1000 回合；z 的母體＝當季 MIN≥500。T3 先過擬合季相鄰季 r ≥ 0.5 才納入，不過就只用 z(C3)＋z(B)。lead 預註冊前看過 E-060 長人的全出手分解，沒看過任何人的三分版 T。這是同一問題的第三次嘗試（E-059、E-060、E-061），所以 (1) 的「變準」就算達標，也只記錄、不當 MINOR 的依據，要等另一個樣本外檢驗。
- 驗收（事先訂定）：(0) 新 onBall 擬合季相鄰季 r ≥ 0.5；(1) 2K27 ρ ≥ 0.5092 − 0.005；「變準」以基準 card 0.1.1 做配對 bootstrap（2000 次、以球員重抽、seed 1），90% 區間下界 > 0；同時列出對 E-060 的配對差，只參考；(2) evaluate.mjs 19/19；(3) Luka onBall 池內（MIN≥500）名次 > 30；(4) `npm test` 過；(5) Wembanyama、Gobert、Embiid 的 onBall 池內名次都 ≤ 200（必要條件，看過問題才設）。另列參考：Holmgren、Brook Lopez、Jarrett Allen、Bam Adebayo 名次；和 E-059、E-060 並排的 onBall 前 15、OVR 前 20 差異。只看一次 2025-26，不得看結果再改（L-026）。
- 結果（`reports/card-0.1.1+E061-onball-3pt-targeting/`，lead 已核對 evaluation.json、bootstrap.json）：(0) 過，新 onBall 相鄰季 r 0.799／0.810，T3 r 0.836／0.806（納入）；(1) ρ 門檻過，2K27 ρ 0.5143（+0.0050），但「變準」不過：90% 區間 [−0.0022, +0.0123]，P=0.128；對 E-060 差 −0.0039 [−0.0075, −0.0004]，比 E-060 差；(2) 19/19（bigPass 14/16，基準 15/16）；(3) 過，Luka 9→316；(4) 過；(5) **不過**：Wembanyama 369、Gobert 326、Embiid 361（Wembanyama zT3 +3.24）。Holmgren 299、Brook Lopez 366、Jarrett Allen 357、Adebayo 263。OVR 前 20 名單和 E-060 相同；Luka OVR 回到 3、Wembanyama 5→8。v61 重現逐位元相同。
- 診斷（事後，不算證據）：長人守禁區，對手就改投外線，三分版 T 一樣把「站在籃下」當成「被針對」。E-059～E-061 三版 T 都讓長人掉到 300 名後，問題不在 T 的細節，而是外線單防指標本來就不適用於守禁區的人。
- 狀態：不採用（2026-10-28，預註冊驗收 (5) 與「變準」不過）
- 相關：E-059、E-060、L-026、L-031、R-019
- 來源：使用者 2026-10-28「預註冊 E-061」

### E-062
- 日期：2026-10-28
- 內容：`inseason 0.1.0+E062` 投籃類視窗觀測值的虛擬出手改以球員自己為中心（預註冊）。現行 `shooting()` 先加 100 次聯盟平均虛擬出手，C4 再往 x0 收縮，小樣本時好射手必降（Maxey FT 24/28 → y 71.5、x0 90.9）。
- 設定：`reports/ovr-inseason-2026-27/v5/pathA/preregistration-e062-shooting-center.md`（凍結）。候選 C4s（中心＝forward(x0)、m0=100）、C4r（m0=0）；其他沿用 E-033，δ² 與 c 照凍結程序重估。主判定 Y5、Y6，N=3/5/10/20；(0) 重現 E-033、(1) V1∧V2、(2) 每格 MAE 差 ≤ +0.05、(3) 合併 MAE 差 bootstrap 90% 上界 < 0 才算變準。
- 結果（`reports/ovr-inseason-2026-27/v5/pathA/backtest-e062/`，lead 已核對 verdict.json 與 results.csv）：(0) 過，開關關掉時 results.csv 與 E-033 逐位元相同；(1) 兩候選都過；(2) 兩候選都不過，Y6 全面變差：C4／C4s／C4r MAE Y6 N10 5.589／5.886／5.885、N20 5.147／5.452／5.481（Y5 小幅改善，N20 C4r 5.578）；(3) 合併差 C4s +0.0845 [+0.0104, +0.1633]（顯著變差）、C4r +0.0483 [−0.0287, +0.1294]。重估 c：C4s Y3–Y5 0.7、Y6 0.35；C4r 1.4（D 組 2）。三分位：Y6 高組 C4 本來就高估（+3.22／+2.69），C4s 推到 +3.75／+3.46 → 賽中「好射手偏低」有一大部分是真實的回歸平均，雙重收縮在預測整季卡上是有益的。賽中參考重算（`live/2026-10-27-e062/`，未部署）：C4s 對現行 ΔOVR ≤−1 0 人、≥+1 7 人；Maxey 79.0→80.1、Jerome 80.0→81.3、Kessler 78.6→78.4。偏離預註冊（已揭露）：開關實際裝在 `v4/tools/inseason_common_v4.window_cards`；δ² 由先驗卡→答案卡算、不用視窗 y，所以三版 δ² 相同、只有 c 重估；bootstrap 以每起點重抽球員、8 格等權平均。注意本 ID 與下方「模擬改吃 E-060 onBall」撞號。
- 狀態：不採用（2026-10-28，閘門 (2)(3) 不過；上線維持 C4）
- 相關：E-033、R-009、L-026、L-031、L-032
- 來源：使用者 2026-10-28「預註冊回測」

### E-063
- 日期：2026-10-28
- 內容：（原登記為 E-062，與上方賽中投籃 E-062 撞號，2026-10-28 改號；報告目錄仍為 `reports/player-impact-e062-team/`）模擬改吃 E-060 的 onBall（預註冊）。卡片 v55～0.1.1 一直只改顯示用 OVR，模擬讀的 `data/season-league.json` 還是 v53 時代的 onBall（對手三分命中差）。這次只換 onBall，其他屬性與引擎不動，量球隊準度。
- 設定：沿用 `reports/player-impact-v54-team/` 的整季球隊流程（v47 協定、v53 引擎、壓迫係數、spread scale 1、seed 20261012／13／14、四季 2022-23～2025-26）。在 loadInput 之後把每季名單球員的 onBall 換成該季的 E-060 onBall：attr(percentile(zC3+zB−zT, 該季卡片池))，分量用 `reports/card-0.1.1+E060-onball-targeting/components-<season>.csv`，卡片池定義同 build_card.py（GP≥30 且 MIN/GP≥20，用該季 base）。缺分量的人 onBall 不變（保留原值，不給 70）。基準＝`reports/player-impact-v53-team/runs`（不重跑；另抽一個 v53 run 重跑，需逐位元相同）。
- 驗收（事先訂定）：(1) `npm test` 過；(2) 主指標＝四季合併 winsMAE 差（E062−v53）：每季每 seed 配對，以球隊在季內重抽做 bootstrap（2000 次、seed 1）。90% 區間上界 ≤ +0.25 勝 → 「不比基準差」，接進模擬（PATCH）；區間上界 < 0 → 「變準」，MINOR 候選（R-019）；上界 > +0.25 → 不接；(3) 每季聯盟三分%差 ≤ 0.5 個百分點、每場得分差 ≤ 1.0，否則不接；(4) 2025-26 單季與 netRMSE 另列參考。只跑一次，不得看結果再改（L-026）。
- 接進模擬的做法（驗收過才做）：`scripts/build_season_league.js` 的 onBall 改讀 E-060 2025-26 onBall 的資料檔，重產 `data/season-league.json`，確認和舊檔只差 onBall 欄。
- 結果（`reports/player-impact-e062-team/`，App 內 sonnet 子代理在 5090 執行；lead 核對 scores.json 與 13 個 run 檔）：(1) 過，57/0（未改 src）；(2) 不過，合併 winsMAE 差 +0.378 [−0.053, +0.831]，上界 > +0.25 → 不接；各季 +0.51／+0.69／−0.67／+0.98，netRMSE 四季都變差；(3) 不過，聯盟三分% 四季都高 0.62–0.86 pp（得分差 0.44–0.82 在門檻內）。新 onBall 讓整體外線防守變弱（全聯盟三分% 約 +0.7 pp）。v53 重跑 1 個 run 逐位元相同。偏離（已揭露）：2022-23～2024-25 無 base 檔，卡片池改用 defense-tenth step4-t2 的 advanced 檔 GP／MIN；`freshDefenseMeasurement.sourceOnBall` 未換；5090 環境 `basketball-e062-20261028` 換成本機 src。
- 狀態：不接進模擬（2026-10-28，驗收 (2)(3) 不過）；卡片顯示仍用 E-060 onBall（R-022），模擬維持 v53 onBall
- 相關：E-060、R-019、R-022
- 來源：使用者 2026-10-28「接進模擬並發版」

### E-064
- 日期：2026-10-28
- 內容：`card 0.1.2+E064`／`inseason 0.1.1+E064` OVR 改為每場影響力、含上場時間（預註冊，R-025、R-026）。每 36 的 pred 乘 MPG/36，再用每場錨點（MIN≥500 池 PR1/50/99）映射；基準＝聯盟平均，另列替補水準（PR10）副版。賽中 MPG 用 stamina 的 C4 權重 w 更新。
- 設定：`reports/card-0.1.2+E064-pergame/preregistration.md`（凍結，sha256 c86a2811f57d0ddd34d2dd0ee1b024181e79f4ea1af5973a95697d089dc93985）。卡片：(c0) 重現 0.1.2、(c1) npm test、(c2) RAPM 分半 A→B／B→A，答案＝RAPM_另一半 × MPG_另一半（2025-26 依 gameId 奇偶），ρ(OVR_game)−ρ(OVR_36) 90% 下界 > 0、(c3) ρ(OVR_game)−ρ(MPG) 下界 > 0。賽中：候選 G1（最低樣本 1 場，主）／G5（5 場）／G0（不更新），Y5、Y6 × N=3/5/10/20 對每場答案卡；(0) 重現 E-033、(1) V1∧V2、(2) G1 對 G0 每格 ≤ +0.05、(3) 合併 bootstrap 90% 上界 < 0。
- 結果（App 內 sonnet 子代理執行；lead 核對 verdict.json，並自己從 fitA／fitB pergame-main.csv＋rapm-A/B＋mpg-A/B 重算 ρ，兩方向 game−36 差 +0.0096／+0.0118，對自報 +0.0099／+0.0118）：
  - 卡片端 `reports/card-0.1.2+E064-pergame/` 全過：(c0) ranking.csv sha256 與 0.1.2 相同；(c1) 57/0；(c2) ρ 0.5953 對 0.5844，差 +0.0109 [+0.0011, +0.0205]（勉強過）；(c3) 對 MPG 0.4012 差 +0.1941 [+0.1300, +0.2618]。
  - 卡片端只報告：替補水準副版 ρ 0.6025，對主版差 +0.0072 [−0.0143, +0.0278]（不顯著）；2K27 ρ 主版 0.444、副版 0.695、每 36 0.518、MPG 單獨 0.798。反轉診斷：MIN≥500 池裡 MPG≥20 的人有 77 位低於 MPG<12 組中位數（副版 27 位）。Jerome #47→#64（2025-26 MPG 22.6）、Maxey #70→#44、Kessler #104→#80；前十長人仍 4 位。
  - 賽中端 `v5/pathA/backtest-e064/`：(0) 過（4 位小數逐格相同）；(2)(3) G1、G5 都過，G1 對 G0 合併 −0.314 [上界 −0.182]、G1 對 G5 −0.114 [上界 −0.060]；(1) 三者都不過：G1 V1 N=3 U 0.592（>0.50）、Y5 T_s 0.429，V2 Y5 N10 >10 人數 54 對 A 52；G5 只輸 V2 Y5 N10（54 對 52）；G0 同格 56 對 52 也不過。依凍結規則採 G0（只換單位、不更新上場時間）；退路 G0 本身沒過 (1)，規則沒要求，見 L-035。
  - 賽中參考 `live/2026-10-28-e064/`（G0，未部署；`run_c4_live.py` 加 `E064_MODE`，預設關時與 2026-10-27 頁面逐位元相同）：ΔOVR ≤−1 125 人、≥+1 72 人；Jerome 83.4→79.3、Maxey 79.8→81.4、Kessler 74.6→74.3；Caruso 98.3→85.9；低分鐘新人被拉向 70（Lanier 42.4→59.5、Bronny 40.6→57.0），是平均基準的副作用。
  - 偏離（已揭露 20 條，重點）：賽中錨點池用 3 位小數 predictedPer36；live 的凍結摘要已是 card 0.1.2（另一 session 的 37f7d62，inseason 0.1.2），所以 live 錨點用卡片端主版錨點；子代理沒寫 report.md，內容只在 verdict.json 與回報。
- 狀態：卡片端過關、賽中依規則採 G0（2026-10-29）。2026-10-29 使用者裁定 R-028：改採副版基準＋賽中 G1，版本 card／inseason 0.2.0。2026-10-29 已上線：gh-pages 2870ddb（首頁 inseason 0.2.0a、2025-26.html card 0.2.0），產物 `reports/card-0.2.0/`；lead 抓線上頁核對版號、Jerome 85.4（MPG_hat 29.4）、Maxey 86.9、Caruso 82.3、Jokić 108.4；對前一版 0.1.2a ΔOVR ≤−1 199 人、≥+1 119 人、|Δ|≥5 106 人
- 相關：R-025、R-026、F-029、E-033、E-060、E-062、E-065、L-026、L-031、L-035
- 來源：使用者 2026-10-28「每場，含上場時間」

### E-065
- 日期：2026-10-28
- 內容：OVR 對 R-025 定義的進出勝場測試。模擬器照字面量「球員打 2025-26 場均分鐘＋四個聯盟平均隊友」對「同分鐘換成平均 profile」的每場勝場差（WinImp），對照 card 0.1.2 OVR；另檢驗 defenseBonus 是否高估（White 99.0、Caruso pred0 −0.31＋defenseBonus 3.86→98.9）。
- 設定：`reports/card-0.1.2+E065-inout-wins/preregistration.md`（凍結，sha256 01ff0b679cde0c6fc935f79ab4f11f64697f4b1876bebc5495d99c65eaa68b5e，git HEAD 37f7d62）。答案沿用 E-064 §3.2（RAPM 分半 pooledNet × MPG 另一半，pooledPoss≥2500、兩半各 ≥5 場）。V1：ρ(WinImp)−ρ(OVR) bootstrap 90% 下界 > −0.02 不輸、> 0 較好；V2：前 60 名 defenseBonus≥1 組名次殘差 90% 下界 > 0 → 高估。示範（不作判準）：BOS 拿掉 White、White 加入中位數球隊，對照 Luka／Wemby／Caruso。
- 結果（2026-10-29，lead 自算 `verdict_e065.py` → `verdict.json`；WinImp 由 sonnet 子代理在 5090 跑，baseSeed 20261028、30 對手 × 16 樣本 × 2 邊、379 人，HEAD b660a02，src 與 37f7d62 相同）：
  - V1 不過：ρ(WinImp) 0.414／0.351 對 ρ(OVR 0.1.2) 0.759／0.765（AB n=345／BA n=344），差 −0.345 [−0.421, −0.268]／−0.414 [−0.488, −0.335]。定義版明顯比現行卡差。
  - V2 字面通過：defenseBonus≥1 組殘差 +27.0 [14.4, 39.8]／+19.0 [10.0, 28.5]；但 <1 組也是 +15.7／+16.0（前 60 名整體回歸平均），高減低只有約 +11／+3，預註冊沒設對照，不能算「defenseBonus 高估」的證據。
  - 比較對象有洩漏：OVR 0.1.2 的 align／defenseBonus 用全季 RAPM，對分半答案是樣本內。事後（探索性，不作判準）改用 E-064 fitA／fitB（只用一半 RAPM 擬合的卡）：ρ 0.584／0.596，WinImp 仍輸（差 90% CI [−0.254, −0.083]／[−0.320, −0.162]）；屬性 pred0×MPG 0.534／0.504 也贏 WinImp。fit 卡前 60 名高減低 CI [1.8, 61.6]／[−2.0, 60.2]，方向一致但一邊未過 0。
  - 個人：White 樣本外不被高估（fit 卡池內第 6.5，答案第 4／第 6）；Kenrich 兩方向都高估（fit 71→答案 112、47→109）；Caruso 只有 AB 高估（2.5→116），BA 反而低估（85.5→15）。
  - WinImp 本身：前五 Jokić 16.6、SGA 15.5、Wemby 15.1、Giannis 11.6、Gobert 10.5；White 第 29（6.6±2.6）、Caruso 第 163；偏好長人（Mark Williams OVR 457→WinImp 13、Sengun 241→15）；ρ(WinImp, OVR)=0.543。
  - 示範：White 拿掉 BOS −0.6±1.7 勝、加入中位數隊 PHX +3.1；Luka −6.9／+7.1；Wemby −10.1／+13.0；Caruso +1.0／−0.5（拿掉與加入不對稱，示範只作參考）。
  - 位置版（副表，2026-10-29 事後補記，探索性）：主版四個隊友是同一個全聯盟平均人（不分位置，缺控衛與內線）；位置版隊友＝PG/SG/SF/PF/C 各位置平均 profile（`winimp-core.mjs` variant 'pos'，沿用 v53 workloadTeam）。位置版 ρ 0.291／0.317，比主版 0.414／0.351 更差。主版長人偏差部分來自缺內線：Sengun 8.2→1.3、Mark Williams 8.5→4.4；但位置版仍高估護框長人（Mitchell Robinson OVR 115→第 8、Kalkbrenner 384→第 12）。White 位置版只有 0.6 勝（主版 6.6）。兩種隊友都是「位置平均」，不是使用者說的「各司其職、OVR 70」基準；要測後者需另設計基準陣容。
  - 結論：模擬器照 R-025 字面做的勝場貢獻目前預測力比卡片差、且有長人偏差；在模擬器修好前不能拿來當 OVR。defenseBonus 高估只在個人層看得到（Kenrich、Caruso 單向），群體層證據不足。
- 狀態：完成（H1 否定；H2 未確立）
- 相關：R-025、R-026、F-029、E-064、E-027、L-026、R-007、L-036
- 來源：使用者 2026-10-28「OVR99的球員要有這個強度」「GO」

### E-066
- 日期：2026-10-29
- 內容：卡片能力值兩題合併預註冊（R-029、R-030）。A：同季上半季逐場依日期指數衰減加權（H＝∞／60／30 天），處理 McCain 型季中變化；B：E-055 收縮目標 m 改成依 MPG 分組（<12、12–20、20–28、≥28）的條件平均（B1 本組、B2 一律 MPG<12 組＝往聯盟底層拉），沒有歷史與 drive 缺值的退回值也跟著換。
- 設定：`reports/card-0.2.0+E066-recency-target/preregistration.md`（凍結，sha256 6f940f553fd4dcb13d9d89a4145c5d71de8bfe0025b55c2093bbce3cbdf1747c）。沿用 E-055 回測（前季＋上半季→下半季、MIN_D2、測試 2025-26），候選只用擬合季選、測試季判一次。A：合併相對 MAE 90% 上界 < 0 且每屬性 ≤ +1%；B：無歷史族群合併相對 MAE 90% 上界 < 0、全體 ≤ +0.5%。卡片層 (c0) 重現 card 0.2.0、(c1) npm test、(c2) E-064 RAPM 分半每場 ρ 差 90% 下界 > −0.02、(c3) evaluate 閘數不減；G5 名單含 Topić、McCain、雷霆輪替。
- 結果：兩題都不過，卡片維持 card 0.2.0（`report.md`；role-audit 獨立重算 `audit/audit.md` 結論成立）。
  - A：擬合季選 H\*=60（只好 −0.17%）；測試季 (A1) 合併相對 MAE −0.10%，90% [−0.58%, +0.40%]，不過；(A2) 每屬性 ≤ +0.82%，過。只報告：季對季中途換隊者五項平均好 1.1%、未換隊者差 0.6%；測試季上半季僅 6 人換隊，驗不出交易後加權。
  - B：擬合季 B1 +0.72%、B2 +2.39%，兩個都比現行差，依字面選 B1；(B1) 無歷史族群 mid 15 人、drive 20 人 <30，樣本不足（只報告 +6.6%，變差）；(B2) 全體 +1.98%，90% [+0.77%, +3.23%]，不過。未選的 B2 全體 +3.58%。
  - 卡片層沒做；(c0) 只做回測層重現（開關全關對 `backtest.json` 全同），卡片層 ranking.csv 未驗。
  - audit：點估計獨立吻合；e066 對歷史季上半季也加權（預註冊沒寫），改成只加權當季，A1 上界 +0.0044，判定不變。程序上沒有看測試季後改參數的跡象（L-026）。
- 狀態：完成（不採用，2026-10-29）
- 相關：R-029、R-030、E-055、E-064、L-026、L-037
- 來源：使用者 2026-10-29「寫預註冊」

### E-067
- 日期：2026-10-29
- 內容：長人偏袒檢查的固定量尺。之後卡片或模擬每個版本都用同一支腳本、同一判準。S＝mean(殘差|C) − mean(殘差|PG/SG)，殘差＝答案名次 − 模型名次（正＝高估），答案與人群同 E-064 §3.2；兩方向 90% 下界都 > 0 → 偏袒長人。模擬改版宣稱修掉長人偏袒，須 (b1) 判定不再是偏袒長人、(b2) 兩方向 S 都變小、(b3) WinImp ρ 兩方向平均掉不超過 0.02。
- 設定：`reports/bias-check-E067/preregistration.md`（凍結，sha256 2dc539163a49db8d2d9191ca75f854344cae0fd8427dc698d29794bd6383177d），腳本 `bias_check.py` → `baseline.json`。卡片一律用半季擬合卡（L-036）。
- 結果（基準線，lead 自算）：
  - card 0.1.2 fit 卡：未偵測到偏袒。S +3.0 [−17.6, 23.9]／+13.1 [−7.3, 33.3]；前 20 名 C 的人數：模型 4/3，答案 4。
  - WinImp 主版：偏袒長人。S +81.8 [59.9, 104.3]／+95.2 [71.1, 119.2]；C 組平均高估約 +75 名；前 20 名 C 的人數：模型 11，答案 4。
  - WinImp 位置版：偏袒長人。S +37.5 [9.9, 65.5]／+50.1 [22.5, 77.4]；另外 PG 組大幅低估（−72／−66），等於五個位置平均隊友裡已經有控衛，候選 PG 的邊際價值被壓低。
  - 第二答案 2K27（只列）：三個模型的 S 都更大（fit 卡 +22.6／+17.2，區間含 0），RAPM 答案沒有比 2K27 更偏愛長人。
- 狀態：完成（量尺凍結；模擬改版的驗收目標＝把 WinImp 主版／位置版的 S 壓下來）
- 相關：E-065、E-064、L-036、L-026、R-025
- 來源：使用者 2026-10-29「照這個順序」


### E-068
- 日期：2026-10-29
- 內容：製造犯規（FD）定義比較，探索性、事後（使用者看到 SGA 不在 FD 榜前段才提出），不作採用依據（R-007、L-026）。候選：rate＝FTA/FGA（現行）、vol＝FTA/36、mix＝0.5·z(rate)＋0.5·z(vol)，都取池內百分位（GP≥30 且 MPG≥20，1–99），原始值、未做 v61 歷史拉回。
- 設定：`reports/fd-volume-compare-2025-26/compare_fd.py` → `results.json`、`report.md`。價值檢驗：FD 只用一半比賽（gameId 偶／奇，同 RAPM 分半），答案＝另一半 RAPM pooledNet（pooledPoss≥2500 且在池內，n 242／241），OLS 控制 card 0.2.0 其他 14 屬性（全季值，三候選共用）。
- 結果（lead 自算）：
  - 排行：SGA rate 第 55、vol 第 8、mix 第 17；Luka 59／5／18、Embiid 51／6／14；Gobert 18／103／32、Adams 24／148／46。vol 前 15 名幾乎都是持球主攻，rate 前 15 名多是長人與低出手量的人。池內 Spearman rate~vol 0.868。
  - 穩定度（2024-25→2025-26，n 178）：rate Spearman 0.832、vol 0.844、mix 0.840，差不多。
  - 價值：三個候選都沒有可分辨的增量價值。FD_A→RAPM_B 係數／10 點 rate −0.029（SE 0.052）、vol −0.064（0.065）、mix −0.033（0.057）；FD_B→RAPM_A rate +0.029（0.056）、vol +0.014（0.068）、mix +0.029（0.060）；ΔR² 都 ≤ 0.003。卡片全季 foulDraw 在同一迴歸也是 ≈0（−0.024／−0.007）。
  - 未拉回的原始榜會混進低分鐘的人（Alex Antetokounmpo 1.875 FTA/FGA、27 FTA/36）；正式卡有 v61 拉回，不會這樣。
- 診斷（不算證據）：v60（E-054）回歸給 foulDraw +0.074/10 點，是 calibrate-wing 的樣本內擬合；這裡改成半樣本外、控制其他屬性後消失。資料沒有偏好哪個定義，選 rate 或 vol 是語意問題：rate 量「每次出手換到多少罰球」，vol 量「總共製造多少罰球」。
- 狀態：完成（探索；卡片未改）
- 相關：E-054、R-007、L-026、TODO.md 切入 B 階段
- 來源：使用者 2026-10-29「SGA怎麼沒有在造犯規的排行榜？」→「試做比較」

### E-069
- 日期：2026-10-29
- 內容：handle（控球）依 R-032 量測，並在模擬裡拆分失誤。現況：模擬 handle 全員 70，tovSkill 是總失誤率。第一階段（卡片）：控球失誤 ÷ 持球分鐘，收縮後與持球量（TIME_OF_POSS/36）各占 0.5 合成 handle；傳球失誤率做成 passSec。第二階段（模擬）：失誤拆成控球與傳球兩段，create 與出手品質改用 CRT，包夾脫困改用 handle＋pass。
- 設定：凍結預註冊 `reports/handle-E069/preregistration.md`（sha256 fc6e375e…）。判定：第一階段 (h1)(h2)(h3)；第二階段 (m0)–(m3)，(m3)＝E-067 的 b1–b3。
- 結果（第一階段，role-card 產出，lead 抽查 results.json／handle.csv 相符）：
  - 補充 1（sha256 eb84d28b…）：只看過次數表後，把 out-of-bounds 依 description 拆開，offensive foul 用同刻 foul 的 descriptor=='charge' 判定。對不上比例各季 ≤0.03%。
  - (h1) 通過：方法 c（k 64、λ 0.2、kh 256），測試季 MAE 差 −0.0261，90% CI [−0.0334, −0.0191]，n 361。
  - (h2) 通過：方法 c，MAE 差 −0.00208，90% CI [−0.00260, −0.00162]，n 441。
  - (h3) 通過：card 0.2.0 的 sha256 前後相同。
  - handle 對 2K27 Ball Handle ρ 0.739（池內 n 249）。池內 handle 與 vol 的 ρ 0.85、與穩定度 0.90，vol 與穩定度 0.58。
  - passSec 對 2K27 Pass Accuracy ρ −0.47：每次傳球失誤率最低的是少傳、傳安全球的人（Hauser 99、Gobert 96），最高的是 Luka、Westbrook（40）。適合當模擬的每次傳球風險，不適合當卡片上的「傳球好壞」。
  - G5：Brunson 99、SGA 98.8、Luka 96.9、Pritchard 96.4、Westbrook 95、White 94.3、Jokić 82.6、Caruso 79.9、McCain 77.3、Hauser 69.2、Gobert 45.6。Haliburton 2025-26 沒有出賽紀錄。
- 結果（第二階段，role-model 產出，lead 抽查 `sim/m2.json` 相符）：
  - (m0) 通過：3 個 seed 逐位元相同。
  - (m1) 通過：57 passed。
  - (m2) 不過：tov36 MAE 0.167 → 0.320，差 +0.152，90% CI [+0.128, +0.178]，n 378。全聯盟 TOV 誤差 −1.2% → +4.2%（other 類用常數，少 3.9%）。
  - creationDependence 三分組的平均誤差：
    - 低：−0.130 → +0.182，從低估翻成高估；
    - 中：−0.003 → +0.018；
    - 高：+0.058 → +0.002。
  - 校準：kCtl 0.004377（每持球秒），kPass 0.08706（每次傳球）。
  - (m3) 不過（VPN 斷線後遠端 nohup 續跑完成，379 人，E-065 同 seed，lead 自算 `bias-check-e069.json`）：
    - 主版：仍偏袒長人，S AB 81.8→106.1、BA 95.2→118.1，ρ 平均 0.382→0.333（b1、b2、b3 都不過）；
    - 位置版：翻成偏袒後衛，S AB 37.5→−50.8、BA 50.1→−38.2，ρ 0.304→0.278（b1、b2 過，b3 −0.026 不過）；
    - 2K27 ρ：主版 0.484→0.451，位置版 0.297→0.389；
    - G5 名次（主版）：Brunson 61→24、Caruso 163→359、White 29→90。
  - 報告：`reports/handle-E069/sim/report.md`、`results.json`。
  - 附帶發現（不算證據）：
    - v41 驗證路徑本來就繞過 `src` 的失誤公式，拆分寫在 `reports/handle-E069/sim/engine.mjs`；
    - E069 開關會讓 v53 死球壓迫乘數對失誤失效。
  - `src/` 的改動存成 `sim/src-e069.patch`，src 已還原。
- 狀態：完成（第二階段 m2 不過 → 依 §4.2 記錄結果，模擬不變；handle、passSec 卡片端數字保留在 handle.csv，尚未接入正式卡）
- 相關：R-032、E-067、E-055、E-066、L-026、L-036
- 來源：使用者 2026-10-29「handle要想辦法測量，例如看持球佔有 + 控球失誤」→ 定義討論 →「GO」

### E-072
- 編號：原記為 E-069，與 handle 實驗撞號，2026-10-29 改號；報告目錄與預註冊內文仍寫 E069（預註冊凍結不改）。
- 日期：2026-10-29
- 內容：R-033 修法（使用者選「改替補水準」）。替補水準 r_repl 從「MIN≥500 池 pred 的 PR10」改成邊緣池 F（可上場 ≥20 場、出賽率 <0.5）的未收縮 pred 依分鐘加權平均 r_new；MPG 改用可上場場次（扣掉傷病等不可上場場次，教練決定、下放 G League、雙向未啟用都算可上場）；小樣本 pred 往 r_new 收縮（K=500 分鐘）。需要先抓 2025-26 每場 DNP 原因。
- 設定：`reports/card-0.2.0+E069-fringe-repl/preregistration.md`（凍結，sha256 a6c028db4101489af98650267bc18057aa5e51b97be6caecbd97b525c8527c78）。判定：(c0) 重現 card 0.2.0、(c1) npm test、(c2) E-064 RAPM 分半每場 ρ 差 90% 下界 > −0.02、(c3) evaluate 閘數不減、(R1) Sandfort < min(Drummond, Reed Sheppard)、(R2) F 的 OVR 中位數 < MIN≥1000 的 PR10。
- 結果：不通過（`reports/card-0.2.0+E069-fringe-repl/report.md`；尚未經 role-audit）。(c0) 重現 card 0.2.0 sha256 相同、(c1) npm test 57/57、(c2) ρ 差 +0.0037 [−0.0048, +0.0122] 過；(c3) evaluate 18/19→16/19（big14of16 降為 13/16、Mobley 進前十）不過；(R1) Sandfort 59.6 對 min(Drummond 50.2, Reed Sheppard 39.6) 不過；(R2) F 的 OVR 中位數 59.4 對 MIN≥1000 的 PR10 53.0 不過。
  - 關鍵數字：r_new = −1.03（MIN≥500 池 pred 的 PR≈27），比舊 r_repl −2.01 高。F 共 110 人、16,846 分鐘；F 裡已收縮的 pred 加權平均為 −0.97，和未收縮的 r_new 只差 0.06。
  - 解讀（lead）：小樣本的 pred 往聯盟平均拉，不是主因。即使不收縮，box score 推出來的能力值仍把健康卻 DNP 的人估在 MIN≥500 池約第 27 百分位，看不到教練不用他們的原因。替補水準往上移後，pred 低的常上場球員 g_r 更負（MIN≥1000 且 g_r<0 的人從 22 增到 58，Reed Sheppard 46.7→39.6），與 R-033 方向相反。K=250、1000 結論相同。
  - 資料：1230 場 box score 全到（`data/season-source/dnp-2025-26.json`）。沒列在分類表的原因碼 432 人次歸「不可上場」，其中無原因碼的 `INACTIVE|(none)` 354 人次；這部分若其實是雙向合約或 G League，A_p 會被低估。
- 狀態：完成（不通過，2026-10-29；交使用者裁定）
- 相關：R-033、R-028、E-064、E-066、L-026、L-037
- 來源：使用者 2026-10-29「改替補水準」

### E-070
- 日期：2026-10-29
- 內容：R-034 製造犯規改成以量為主（預註冊）。foulDraw＝池內百分位（0.75·z(vol)＋0.25·z(rate)），vol＝FTA/36 用 E-055 方法 (c) 收縮（k、λ、kh 只在擬合季重擬合，MIN_D2 300 分鐘），rate 沿用現行收縮後 FTA/FGA。卡片其他部分照 card 0.2.0 鏈路重算。
- 設定：`reports/card-0.2.0+E070-foul-volume/preregistration.md`（凍結，sha256 c3fe3cd7a049a6a33fb9cb892e1ccf77e77eb6bafb1033e7e539e6f5cc04c817，git HEAD c920fdf）。判定 (c0) w_vol=0 重現 card 0.2.0、(c1) npm test、(c2) E-064 RAPM 分半每場 ρ 差 90% 下界 > −0.02、(c3) evaluate 閘數不減；G5 名單 SGA、Luka、Embiid、Gobert 等 13 人只列表。
- 結果（`reports/card-0.2.0+E070-foul-volume/`，role-card 子代理；lead 抽驗 c0 逐位元、verdict.json、G5 名次；role-audit 2026-10-29 獨立重算成立，`audit/audit.md`：vol 擬合格點 argmin 相同、端對端重跑三組卡逐位元相同、c0–c3 全部重現、無事後調參；FD 名次差異只來自 99 分同分的排序）：(c0) 過，w_vol=0 的卡與 card 0.2.0 逐位元相同（per36 與 fitA 中間卡也與 E-064 相同）；(c1) 57 passed；(c2) 過，repl 每場 Δρ +0.0007 [−0.0009, +0.0022]；(c3) 18/19＝基準。vol 收縮後下半季 MAE 0.751（k=0 0.829）。foulDraw 係數／10 點 0.108→0.115（SE 0.046→0.050）；2K27 ρ 每場 0.6953→0.6987。OVR 平均變動 0.18、最大 1.2，前 20 只換第 20 名（Anunoby→Curry）。FD 名次 SGA 21→5、Luka 30→4、Embiid 13→2、Gobert 3→40、Adams 8→62。偏離預註冊 7 點已揭露於 report.md（z ddof=0、c0 保留原字串等，無參數調整）。
- 狀態：完成、通過（2026-10-29）；使用者「現在發 0.2.1」，但發布時 `reports/card-0.2.1/` 已被 E-071 P1 覆蓋（L-040），站上 0.2.1 不含 E-070；改由 card 0.2.2（0.2.0＋E-070＋E-071 P1）併入
- 相關：R-034、E-068、E-055、E-064、E-066、R-016、L-026
- 來源：使用者 2026-10-29「0.75 開始」

### E-071
- 日期：2026-10-29
- 內容：壓迫（pressure）改用個人逼失誤事件（預註冊）。現行 pressure＝four-factors RAPM 的 `tovNonSteal_defense`，雜訊大、含 RAPM 評估半的洩漏，網站又誤標「壓命中率」；模擬不讀它，只在 OVR 迴歸當特徵。新 force＝(z(STL/36)＋z(DEFL/36)＋z(對位失誤調整後/100poss)＋0.5·z(造進攻犯規/36))/3.5，各分量用 2024-25 動差法定 k 收縮；P1 只換 pressure 來源，P2 再加 foulDisc（−PF/36）。顯示用 PRES＝force − 0.25·z(PF)（顯示層，不進 OVR）。
- 設定：`reports/card-0.2.0+E071-pressure/preregistration.md`（凍結，sha256 ce64cd8ad67265aec20ef1653b05e588bf279c0f1f732c3c33235773ff604dde，git HEAD c920fdf）。判定 (c0) 重現 card 0.2.0、(c1) npm test、(c2) E-064 RAPM 分半每場 ρ 差 90% 下界 > −0.02、(c3) evaluate 閘數不減、(p1) force 相鄰季 Spearman ≥ 0.70；P2 要比 P1 的 ρ 差下界 > 0 才採。P0（拿掉 pressure）只報告，用來看洩漏優勢。
- 探索（lead 自算，事後，不算證據）：Diabaté PRES 99，但造進攻犯規 0、deflection 276 人第 223、對位失誤調整後 279 人第 112，Hornets 逼失誤率 30 隊第 25。逼失誤分量和犯規正相關（合成 r +0.19／+0.22，同位置內 +0.21～+0.42），兩者相鄰季都穩定（0.72～0.83），所以分成兩個屬性、只在顯示層合併。對位失誤欄 `MATCHUP_TOV` 存在（`leagueseasonmatchups`、`matchupsrollup`），調整後相鄰季 0.66、訊號佔變異約 0.77。
- 結果：P1（事件式 force 取代 tovNonSteal_defense）過 (c0) 逐位元重現、(c1) npm test、(c2) ρ 差 +0.0038 [−0.0055, +0.0135]、(c3) 18/19、(p1) 0.727；P2−P1 −0.0003 [−0.0018, +0.0013] 不採 P2。只是不變差，不是變準；P0（拿掉 pressure）−0.0122，屬性本身有用。2K27 每場 ρ 0.695→0.679（只報告）。stl 與 defl 相關 0.88。G5：Diabaté PRES 99→61.4、OVR 84.2→79.2（42→74 名）；Lowry 99→62.5；Dru Smith、Ausar Thompson 升到 99。audit（`audit/audit.md`）獨立重算全部逐位元相同；字面 k 敏感度 c2 +0.0016 [−0.0070, +0.0103]、p1 0.726，結論不變。
- 狀態：通過 G1–G4（2026-10-29，含勘誤 1）；使用者「採用 P1」，與 E-070 合併發為 card 0.2.2（R-039；合併關卡 c0a/c0b/c1/c2/c3 全過，見 `reports/card-0.2.2/gates.json`）
- 相關：R-022、R-031、E-067、E-070、L-026
- 來源：使用者 2026-10-29「去確認對位失誤。寫預註冊」
- 實作完成 2026-10-29：`reports/card-0.2.0+E071-pressure/report.md`（依採用規則 P1 過 c0–c3、p1；P2 − P1 CI 下界 −0.0018 不採 P2；結論由 lead 填）
- 勘誤 1（使用者 2026-10-29 核可）：§2.3 k 字面公式少乘 d 單位，改 k=σ₁²/τ²，見 `reports/card-0.2.0+E071-pressure/errata.md`（sha256 05dcd741…）。role-audit 重算中。

### E-073
- 日期：2026-10-29
- 內容：R-033／R-035／R-036 修法第二版。E-072 顯示 box score 看不到教練看到的東西，改成把用人當能力的直接證據：RAPM_另一半 ~ pred + ln(1+MPG_avail) + 出賽率 + 年輕(≤23)／老將(≥31) 與其和分鐘的交互項 + 年輕×練兵隊(勝率<0.35)×分鐘，交叉擬合（A 半特徵的係數只用 B 半答案估）。每場分五類：有出賽、輪休（REST 碼）、傷病／不可上場、疑似輪休（該隊有出賽 ≥10 場且平均 ≥24 分鐘、非連續 ≥3 場的教練決定）、教練不用；只有有出賽與教練不用算 A_p。
- 設定：`reports/card-0.2.0+E073-usage-evidence/preregistration.md`（凍結，sha256 db42fc16b50631a41189ca41756ad5a881e569ab60737208acd9d672c360f4de；第一版 eaca2e72… 派工前加 (R4) 後重凍，2026-10-29）。判定 (c0) 重現 card 0.2.0、(c1) npm test、(c2) RAPM 分半每場 ρ 差下界 > −0.02、(c3) evaluate ≥18/19、(c4) 用人特徵讓另一半 RAPM 預測變準（下界 > 0）、(R1) Sandfort < min(Drummond, Sheppard)、(R2) F 中位數 < MIN≥1000 PR10、(R3) 隊內 ρ(MIN, 每場 OVR) 中位數 ≥ 0.675、(R4) MIN<100 組 OVR PR90 < MIN≥1000 且 MPG 12–22 組中位數（card 0.2.0 現況 Oduro 72.8 vs 62.5，會不過）。(c4) 單獨沒過記「語意版」交使用者。
- 補充 1（`supplement-1.md`，sha256 f7b87296…f15a，派工後、看任何候選數字前）：R-035 基準 0.675 是 lead 原腳本不處理同分、中位數取 v[15] 的結果；(R3) 改用標準 Spearman 與標準中位數，門檻改成「≥ card 0.2.0 同算法值」（0.6608）。
- 結果：不通過，只有 (R1) 沒過（`reports/card-0.2.0+E073-usage-evidence/report.md`，ranking.csv sha256 9eeae54a…；role-card 子代理產出，lead 抽查 ranking.csv、results.json、c0 sha 相符；尚未經 role-audit）。
  - 過：(c0) sha 相同；(c1) 57/57；(c2) Δρ +0.0025 [−0.0144, +0.0182]；(c3) 18/19；**(c4) 用人特徵讓另一半 RAPM 預測變準 Δρ +0.0202 [+0.0022, +0.0373]**；(R2) F 中位數 52.5 < 53.9；(R3) 0.733 ≥ 0.661；(R4) MIN<100 的 PR90 57.8 < 63.25。
  - 不過：(R1) Sandfort 54.4，Drummond 57.3，Reed Sheppard 52.2。Sandfort 從 61.0 降到 54.4，但 Sheppard 只從 46.7 升到 52.2。
  - 卡片係數：p 0.88，L 1.11，出賽率 −2.00，年輕 +0.24，老將 +0.11，年輕×L −0.15，老將×L +0.17，年輕×練兵隊×L −0.38。最後三項的方向和 R-035 一致；但年齡項在 A→B 與 B→A 兩個方向正負相反，個別不穩。拿掉年齡項（s3）後 (c2)、(c4) 都不過。
  - 個案：Kennedy Chandler 78.3→69.8、Cody Williams 35.8→32.5、McCain 57.9→57.7、Drummond 48.7→57.3。敏感度 s1–s3 的 (R1) 都不過。疑似輪休 43 組、84 人次。
  - 唯讀檢查：只有 `data/*2026-27*` 的 5 個檔在 04:01 被改，是現季資料更新，不是 e073.py 寫的。
- 狀態：完成（不通過，只差 (R1)，2026-10-29）；使用者接受為 card 0.3.0 候選（R-038）；role-audit 重算成立（2026-10-29，`audit/audit.md`：582 列 OVR 最大差 0、c2/c4/R1–R4 全部重現；18 條未寫到之處無事後挑選；10 個替代變體 (R1) 都不過，c4 下界只有 s3 變負；間接相依：fitA/fitB 卡用 RAPM 半季校準，p_B 含 RAPM_B 資訊，屬預註冊字面結果）；待以當時正式卡重跑 c0–c3、R1–R4
- 相關：R-033、R-035、R-036、E-072、E-064、L-026、L-036、L-037
- 來源：使用者 2026-10-29「寫預註冊」「然後要分清楚DNP和輪休」；同日「高分鐘替補球員比低分鐘淘汰球員OVR低」→ (R4)

### E-074
- 日期：2026-10-29
- 內容：賽中 OVR（2026-27）改用 card 0.2.2 當先驗：x0 屬性、凍結迴歸係數、每場錨點與 r_repl 全換 0.2.2；pressure（= 逼失誤）維持凍結；foulDraw 賽中更新改 E-070 量為主公式（z／百分位母體凍結為 card 0.2.2 的 2025-26 母體）；頁面 PRES 標籤改「壓迫」加 tooltip。換版不擬合，版號 inseason 0.2.1（R-019 PATCH）。
- 設定：`reports/ovr-inseason-2026-27/e074-card022/spec.md`（sha256 658cefed…7776）。判定 (c0) 開關關掉逐位元重現 inseason 0.2.0c、(c1) npm test、(c2) N=0 先驗 OVR 對 card 0.2.2 每場 OVR Spearman ≥ 0.99、(c3) 版號與頁面標籤。
- 結果（2026-10-29，role-card；`reports/ovr-inseason-2026-27/e074-card022/report.md`）：c0 `CARD_MODE=020` ranking.csv／no-prior.csv 與已發佈 0.2.0c 逐位元相同（ranking sha256 7e6f1a53…）；c1 npm test 57/57；c2 N=0 先驗 OVR 對 card 0.2.2 每場 OVR Spearman 0.99999（362 人），r_repl −1.7593，兩份 summary 鍵與 card 0.1.2 版相同；c3 `probe_base_version()`＝inseason 0.2.1，頁面 PRES「壓迫」＋tooltip。前 20 名進 Maxey、Tatum，出 Markkanen、Davis；|ΔOVR| 中位數 1.20、最大 8.5，最大 10 人全由 pressure 換定義造成（Sheppard +8.5、Banchero −8.1、Nembhard −8.0、Mobley −6.3）。foulDraw 新公式使高出手量球員的視窗 y 大幅上升（Edwards 55→85、SGA 57→79）。新檔：`live/build_prior_022.py`、`live/prior-2025-26-card022.json`（sha256 0518184f…）、`CARD_MODE` 開關（預設 022）。
- 狀態：完成（2026-10-29 lead 審過：c0 兩檔 sha256 自行核對相符、diff 已讀、npm test 由 dispatcher 重跑 57/57）；待使用者核可 commit 與發佈（R-031）
- 相關：R-039、R-031、R-019、R-018、E-070、E-071、E-064、L-026
- 來源：使用者 2026-10-29「賽中改跟 card 0.2.2：寫 spec 派工，含 c0 重現與新版號」

### E-075
- 日期：2026-10-29
- 內容：E-073（用人當能力證據）移到正式卡 card 0.2.2 重跑；只換輸入（p 全季／半季、基準卡、(R4) MPG），方法照 E-073 凍結檔。(R1) 依 R-038 只報告。
- 設定：`reports/card-0.2.2+E073-usage-evidence/preregistration.md`（sha256 faec88da…bcd5）
- 結果（2026-10-29，role-card 子代理；lead 抽驗：預註冊 sha、c0 sha 9f5700c2… 逐位元、npm exit 0、results.json 判定值、e073→e075 diff 只改路徑／標籤與 R1 改只報告）：**語意版**。c0 逐位元重現 card 0.2.2；c1 57/57；c2 Δρ −0.0005 [−0.0186, +0.0159] 過；c3 18/19＝基準；**c4 Δρ +0.0160 [−0.0002, +0.0321] 不過（差 0.0002；E-073 時下界 +0.0022）**；R1（只報告）Sandfort 53.6 < Drummond 57.7、Sheppard 60.4，現在成立；R2 51.7 < 52.1；R3 0.747 ≥ 0.641；R4 57.8 < 63.5。敏感度：s1、s2 c4 也不過；s3 c2、c4、R1 不過。MIN 分組 OVR 中位數 <100／100–300／300–1000／≥1000 = 51.6／52.7／55.6／73.4（card 0.2.2：55.7／57.6／58.9／72.6）。對 E-073 card 逐人 OVR 最大差 8.2（Sheppard 52.2→60.4），|差|≥2 有 90 人。ranking.csv sha256 01aab81a…2215。
- 狀態：完成（語意版，2026-10-29）；使用者依機會成本接受為 card 0.2.3 候選（R-040，版號使用者定）；role-audit 重算成立（2026-10-29，`audit/audit.md`：582 列 OVR 最大差 0、係數差 2.7e-15、diff 無邏輯改動；c4 下界對蒙地卡羅敏感：seed 1–20 有 12 個為正、10000 次 +0.0004，係數隨 bootstrap 重擬合則 −0.021；樣本內 rhoRapm 0.829→0.775、rho2k 0.681→0.740、rhoDef 0.567→0.490 只報告）；G5 使用者通過（「不錯」，2026-10-29），已發布 card 0.2.3（gh-pages b053b26）
- 相關：E-073、R-038、R-039、R-033、R-035、R-036、L-026
- 來源：使用者 2026-10-29「等 0.2.2 再重跑」

### E-077
- 日期：2026-10-29
- 內容：PHYS 只用身高＋體重/10（`scripts/build_season_league.js:120`、`scripts/build_benchmark_league.js:49`；README.md:165 寫「0.45/0.55 標準化加權」已過時）。檢定選秀體測 ape（臂展−赤腳身高）在 bio 身高、體重之外，能不能多解釋 OREB%、DREB%、BLK/36。依 PLAYER_ID 奇偶分半做 held-out ΔR²，以球員為單位 bootstrap 2000 次（seed 20261029）。
- 設定：`reports/E077-wingspan/preregistration.md`（看結果前寫，原 sha256 b04822d2…9089；編號由 E-076 改 E-077 後為 5ec87bbc…7515）；體測 `combine-anthro.json` 2000–2025 屆 1736 列（nba.com 網頁表格；stats API 不通）；偏離：2014-15 沒有 bio.json 被跳過，實際用 11 季。
- 結果（2026-10-29，App 自跑，未經 audit）：2591 個球員季、674 人，有體測的 450 人（68%）；ape 標準差 2.2 吋。ΔR²：OREB% +0.007 [−0.011, +0.021]、DREB% +0.009 [−0.006, +0.021]、**BLK/36 +0.050 [+0.022, +0.082] 過**。只有 1/3 過，所以照預註冊**不加進 PHYS**。每吋效果：OREB% +0.15 個百分點、DREB% +0.30 個百分點、BLK/36 +0.076（第 10 到第 90 百分位約差 0.46）。只報告：摸高的結果和 ape 相同（只有 BLK 過）；只看 2025-26 三者都不過；2025-26 護框對手命中率每吋 −0.84 個百分點，但 ΔR² 區間含 0。詳見 `results.md`。
- 狀態：完成（2026-10-29）；結論是 ape 不進 PHYS；若要用，候選是蓋帽屬性（需另立預註冊，且要處理沒體測的人：狀元與國際球員缺得多）
- 相關：E-076、L-026、R-007
- 來源：使用者 2026-10-29「測看看」（問：臂展能不能補進身材）

### E-078
- 日期：2026-10-29
- 內容：接 E-077，檢定 ape 在身高、體重之外，和抄截（假設 S：STL/36，11 季球員季）、整體防守嚇阻力（假設 D：四因素 RAPM 2022-26 的 pooledD、rimShare_defense、efg_defense，防守回合 ≥ 2000）有沒有關係。方法同 E-077（ID 奇偶分半 held-out ΔR²、bootstrap 2000 次、seed 20261029）。2025-26 護框命中差已在 E-077 看過，不列入判定。
- 設定：`reports/E078-wingspan-defense/preregistration.md`（看結果前寫，sha256 0ca99ad5…63bc）；沒有偏離。
- 結果（2026-10-29，App 自跑，未經 audit）：**S 不過、D 不過（0/3）**。ΔR²：STL/36 +0.010 [−0.039, +0.041]、pooledD +0.026 [−0.007, +0.055]、rimShare +0.022 [−0.004, +0.047]、efg +0.022 [−0.024, +0.058]。全樣本（樣本內）係數方向都一致為正，區間都不含 0：每吋 STL/36 +0.029、pooledD +0.145（差 6 吋約每百回合 +0.87 分）、rimShare +0.150、efg +0.061；只報告的 threeShare 每吋 −0.143（對手從籃下改投外線）。結論：效果存在但弱，樣本外預測不出來；RAPM 部分檢定力有限（n 609，基準 R² 0.01）。詳見 `results.md`。
- 狀態：完成（2026-10-29）；臂展唯一明確的訊號仍是 E-077 的蓋帽
- 相關：E-077、R-007、L-026
- 來源：使用者 2026-10-29「抄截大概也和臂展有關 或是整體防守嚇阻力」

### E-079
- 日期：2026-10-29
- 內容：RAPM 改用近期加權（季權重 d^(距最近一季季數)，λ 固定 3000）取代四季等權合併。第一階段只用舊季選 d（窗口前三季 → 目標 2017-18..2020-21，格點 d ∈ {1, 0.75, 0.5, 0.25, 0}），再在 2022-25 → 2025-26 檢驗一次 stint 回合加權 MSE（截距用目標季自身平均，比賽 bootstrap 2000、seed 20261029）。P 過才做第二階段：卡片管線所有讀 RAPM 的步驟改讀 d* 版（pooledPoss 保留不加權，人群不變）。
- 設定：`reports/card-0.2.3+E079-recency-rapm/preregistration.md`（凍結，sha256 bbdb9618dfdf27c304f7affd4daa282b1d4581607fc9556ac4cd00ebe3cb8ca8）。判定 (P) Δ 90% 上界 < 0；卡片層 (r0) d=1 重現三份 RAPM、(c0) 重現 card 0.2.3、(c1) npm test、(c2Q) E-064 舊量尺下界 > −0.02、(c2N) 新增現況量尺（另一半 2025-26 單季 RAPM × MPG）下界 > −0.02、(c3) ≥18/19、(R2)–(R4) 同 E-075。d* = 1 → 結束，記「等權合併已是最佳」。
- 已揭露：lead 看過 Banchero／Jalen Williams／Jalen Johnson 的卡片與 RAPM 值、年齡分組「卡片名次 − 2K 名次」事後探索（≤24 歲 +64、≥31 歲 −7.5）；沒看過任何前瞻數字。
- 不含：Jalen Williams 被標 PF（位置標籤）另案。
- 狀態：完成、不採用（2026-10-29）。P 未過，依預註冊停止，沒做第二階段，card 0.2.3 不變。d* = 0.25（選擇季平均 MSE 4158.614 vs d=1 4161.938）；主檢驗 2025-26 Δ +0.229，90% [−1.344, +1.799]。d=0（只看上一季）在 2025-26（Δ +2.734 [+0.540, +4.944]）和 2024-25 都顯著較差。λ 敏感度：CV 全選 3000，結果相同。事後觀察、不作判準：d=0.75 在 2025-26 的區間 [−1.259, −0.347] 會過，2024-25 上界 +0.010；要用必須另寫預註冊，用沒看過的季。報告 `reports/card-0.2.3+E079-recency-rapm/report.md`（results.json）。
- 相關：R-040、E-075、E-064、R-007、R-019、L-026、L-037
- 來源：使用者 2026-10-29「PF 好怪。paolo, jalen will, jalen johnson的排名都比預想中低很多」→「寫預註冊」

### E-081
- 日期：2026-10-29
- 內容：card 0.2.3 的樣本外年齡偏差診斷（不改卡）。以 E-075 半季卡片 g_c 為卡片；答案 N（主）= 另一半只用 2025-26 比賽的 RAPM net（λ 3000）× 另一半 MPG，答案 Q（只報告）= E-064 舊量尺。殘差 u = pct(答案) − pct(卡片)，主統計量 S = Spearman(年齡, u)，兩方向平均，球員 bootstrap 2000、seed 1。
- 設定：`reports/card-0.2.3+E081-age-residual/preregistration.md`（凍結，sha256 9e1402e0681580de27e9a344cd3ea0c01f8b7ad40b6a5b5fc570c4566829296e）。判定：S 的 90% 上界 < 0 → 年輕被低估；下界 > 0 → 老將被低估；兩者皆非 → C 線結案。自檢 (k0) 重現 E-075 c2、(k1) 重現 rapm.csv lastSeason*。
- 已揭露：2K 年齡分組的事後探索、E-075 與 E-079 的全部數字；沒看過殘差 × 年齡。
- 狀態：完成，判定「年輕被低估」（2026-10-29）。lead 抽驗：results.json 與報告一致，預註冊 sha256 不變，(k0)(k1) 最大差 0。
  - 答案 N：S = −0.202，90% [−0.262, −0.141]（AB −0.225、BA −0.179）。分組 u 平均：≤23 +0.101 [+0.070, +0.134]、24–27 +0.003、28–30 −0.030、≥31 −0.094 [−0.149, −0.044]。
  - 答案 Q（只報告）：S = −0.021 [−0.078, +0.034]，沒有偏差；N − Q = −0.181 [−0.229, −0.133]。
  - 解讀：卡片對齊四季合併 RAPM（校準 r 與 E-075 訓練目標 pooledNet 都是），合併 RAPM 對成長中的年輕球員落後、對衰退中的老將偏高。人群 AB 389、BA 388、聯集 395，0 人因缺年齡排除。具名球員的 u 在兩方向正負相反，不解讀個人。
  - 下一步：修正預註冊 E-084。
- 相關：E-075、E-064、E-079、E-082、E-084、R-007、L-026
- 來源：使用者 2026-10-29「設置一個goal 。讓我們把這個任務（位置錯誤，跨季RAPM，新秀vs老將）完成」

### E-082
- 日期：2026-10-29
- 內容：位置從單一硬標籤改成 2025-26 先發秒數比例（投票邏輯同 protocol.mjs；先發 < 5 次維持 one-hot），用在 calibrate-wing 的三處：位置交互項、r 的位置置中、防守加成置中。模擬目標 y 不重跑。之後接 E-075 與 build_card_023。
- 設定：`reports/card-0.2.3+E082-position-shares/preregistration.md`（凍結，sha256 fc1462b8fd887cb5de05a160b5b9cededb0bb416273474773b062db81c98d10a）。判定：(s0) 比例最大位置 = 原標籤（不符 ≤ 3 人）、(c0) one-hot 重現 card 0.2.3、(c1) npm test、(c2Q) 下界 > −0.02、(c2N) 用 E-081 的 rapm1 單季分半答案、下界 > −0.02、(c3) ≥ 18/19、(R2)–(R4) 同 E-075。全過 → G5；(c2N) 下界 > 0 → MINOR，否則 PATCH。
- 已揭露：F-033 的單人反事實與邊界人數。
- 狀態：完成、不採用（2026-10-29）。只有 (R3) 沒過：隊內 MIN–OVR Spearman 30 隊中位數 0.7248 < card 0.2.3 的 0.7469。lead 抽驗：results.json 與回報一致，基準 0.7469 就是 card 0.2.3 summary.json 的值，預註冊 sha256 不變。
  - 其餘全過：(s0) 334 人不符 0；(c0) 逐位元重現；(c1) 57/57；(c2Q) Δρ −0.0008 [−0.0041, +0.0025]；(c2N) +0.0010 [−0.0028, +0.0048]；(c3) 18/19；(R2) 52.6 < 52.8；(R4) 58.2 < 62.6。
  - 三人：Banchero 69.9／205 → 69.6／208；Jalen Williams 79.6／80 → 80.4／75；Jalen Johnson 81.9／63 → 81.8／63。前 30 名各位置人數不變；全體平均 |ΔOVR| 0.62。
  - 解讀：比例混合對樣本外量尺幾乎沒有影響，對三人也幾乎沒影響（F-033 的單人改標是極端反事實，比例混合只移一部分）。位置不是三人偏低的主因。
- 相關：F-033、E-075、E-081、R-019、L-026、L-037
- 來源：同 E-081

### E-083
- 日期：2026-10-29
- 內容：RAPM 近期加權，d 寫死 0.75，以完全沒看過的 2026-27 檢驗一次（窗口 2023-24..2025-26 → 2026-27）。方法照 E-079 §2.2–§2.3。P 過才做卡片層（照 E-079 §3）。
- 設定：`reports/card-0.2.3+E083-recency-2026-27/preregistration.md`（凍結，sha256 abb3e2a61d436f1181cced223a5b6e9abe6c94eea6a98789c39b1a9796262001）。(P) Δ = MSE(0.75) − MSE(1) 的 90% 上界 < 0，比賽 bootstrap 2000、seed 20271029。
- 開工條件：2026-27 例行賽打完，stint 建好且比賽數 ≥ 1200；不做期中檢驗。
- 已揭露：d = 0.75 是看過 E-079 的 2025-26 結果後才挑的，所以這次只能用新季檢驗。
- 狀態：預註冊凍結，等 2026-27 季末
- 相關：E-079、L-026
- 來源：同 E-081

### E-084
- 日期：2026-10-29
- 內容：修正 E-081 的「年輕被低估」。E-075 用人回歸的訓練目標從 fit 半季 pooledNet（四季合併）改成 fit 半季只用 2025-26 的 RAPM net（E-081 的 rapm1），權重改 rapm1 poss；特徵、年齡項、人群、卡片組裝都不動，沒有可調參數。
- 設定：`reports/card-0.2.3+E084-current-target/preregistration.md`（凍結，sha256 a7a034b50b39b48471f8f65e85b23c5875eee02bd064cbf39f87a066e03bb6ca）。判定：(c0) pooled 重現 E-075／card 0.2.3、(c1) npm test、(b) ΔS_N 下界 > 0、(c2N) 下界 > −0.02、(c2Q) 下界 > −0.05、(c3) ≥ 18/19、(c4) 用單季 net 下界 > 0、(R2)–(R4)。全過 → G5；(c2N) 下界 > 0 → MINOR，否則 PATCH。和 E-082 都過時跑合併版（§5）。
- 已揭露：E-081 全部數字；修正方向是看過 N／Q 差異後才選的，評估是同季另一半（交叉擬合），不是沒看過的季。
- 狀態：**採用，發成 card 0.2.4**（2026-10-29，R-042、R-044）。原記錄：完成、不通過（2026-10-29）。只有 (c3) 沒過：evaluate 16/19 < 18/19，多掉 carusoGate（Caruso 名次 78 → 103，參考 94）與 big14of16（13/16：Wembanyama 6 對參考 5、Embiid 18 對 17.5、Anthony Davis 45 對 32）。兩閘的參考名次取自 2K 與四季合併 RAPM。lead 抽驗：results.json、evaluation.json 與回報一致，預註冊 sha256 不變。
  - 其餘全過：(c0) 逐位元重現；(c1) 57/57；(b) ΔS_N +0.127 [+0.107, +0.147]（S_N −0.202 → −0.075）；(c2N) +0.025 [+0.009, +0.039]；(c2Q) −0.017 [−0.030, −0.004]；(c4) +0.046 [+0.028, +0.065]；(R2)(R3)(R4) 過（R3 0.7645 ≥ 0.7469）。
  - 副作用：S_Q −0.021 → +0.137（用合併量尺看變成老將被低估）；pred_new 標準差 1.65 → 1.01，卡片更偏向分鐘。MIN≥1000 OVR 中位數：≤23 歲 62.2 → 67.3，≥31 歲 80.8 → 76.0。
  - 三人：Banchero 69.9／205 → 76.1／133；Jalen Williams 79.6／80 → 82.0／76；Jalen Johnson 81.9／63 → 84.3／62。
  - 機械判定是不通過；使用者依機會成本裁定為**通過（R-042）**，role-audit（Opus）重算成立（2026-10-29，`audit/audit.md`）：點估計、係數與 OVR 差 0；seed 2–5 區間最多移動 0.0013；rapm1 從 stints 獨立重擬合，差 6e-14；沒有洩漏。results.json、report.md 的 verdict 已改為「通過（R-042）」，原判定保留在 verdict_mechanical。G5 使用者通過，2026-10-29 發成 card 0.2.4（PATCH，R-044）。
  - 退步六人的原因（稽核）：LeBron、Davis、Curry、Gobert、Embiid 是當季 RAPM 本來就低（例：LeBron 當季第 173、四季第 44）；只有 Caruso 是分鐘權重變重（能力名次 10 → 11，MPG 17.9）。
  - 稽核列出的下一輪目標：(i) pred 分散度壓縮讓低分鐘高效率的人吃虧（Caruso 型）；(ii) 沿用 E-075 的設計，coef_AB 訓練特徵含 p_B，p_B 用評估半 rapm-B 擬合，是間接路徑，影響沒量；(iii) card 0.2.2 的 p 被上限截住，9 人同為 1.894；(iv) mpg-A／B 出賽數與 player-games 依奇偶重算的結果有 35 人不同。E-082 不通過，所以 §5 的合併版不跑。退步項列為下一輪目標，見 R-042。
- 相關：E-081、E-075、E-082、R-019、R-042、R-043、R-044、L-026、L-037
- 來源：同 E-081

### E-087
- 日期：2026-10-29
- 假設：E-069 失敗是因為把失誤綁到持球秒數。只把實測 handle 用在「誰拿球」（`handlingScore` 的 handle 從 70 換成 `handle.csv`），失誤公式、create、assistBoost 都不動、不重新校準，個人失誤不會變差，長人偏袒會減輕。
- 做法：`reports/sim-0.1.0+E087-handle-share/preregistration.md`（sha256 f0814db3…f4d5）。閘：m0 開關關閉逐位元、m1 npm test、m2 tov36 MAE 非劣性（90% 上界 < +0.02）、m3 E-067 b1–b3 主版與位置版。前置 p0：確認 WinImp 與 v41 路徑真的呼叫 handlingWeights。
- 狀態：2026-10-29 停在 p0、未跑（L-046）。WinImp 與 v41 路徑 `shotSelection` 都是 `volume`，第一觸球走 `opportunityPlan` 實測率，`handlingWeights` 呼叫 0 次；換 handlingScore 對結果沒有任何作用。證據 `p0.json`。
- 附帶診斷（同季，不算證據）：`diag-allocation/report.md`。模擬分球對真實前場觸球 ρ 0.60，後衛 1.14、中鋒 0.77；持球後衛給太多（SGA 1.96、Dončić 1.73），長人給太少（Gobert 0.66），Hauser 0.75。分球沒有「把不持球的人當持球者」。lead 追查：每人 usage、助攻各組誤差 ±2%，觸球差距是定義不同（模擬只算有結果的觸球），不是分球偏差；列 loop.md H8，排除。失誤「分工」新預註冊沒寫：活鏈失誤已是兩段實測率（傳球段 passStolen、終結段 terminalRisk），前提不成立（L-046 重犯）。
- 相關：E-069、E-067、E-065、R-032、L-046

### E-089
- 日期：2026-10-29
- 假設：卡片每場值 g 的分鐘權重從 mpg/36 改成飽和 W(m) = (1 − e^(−m/15)) / (1 − e^(−36/15))（R-047）後，在同一價值定義的樣本外答案（另一半 rapm1 net × W(另一半 MPG)）上不變差，線性量尺沒有大幅退步。
- 做法：`reports/card-0.2.4+E089-minutes-saturation/preregistration.md`（凍結 2026-10-29，sha256 0fa1b15c0ce11096993b224851456abdb77eb17417ecaa55dd74257207a12fbe）。`e089.py` = `e084.py`（season 目標）加 `--minutes {linear,sat15}`，只改 g 的兩處；用人回歸特徵 L = log(1 + mpg) 不動。判定：(c0) linear 重現 card 0.2.4 sha256、(c1) npm test、(u) W 單元檢查、(m1) Δρ_{N_W} 下界 > −0.02、(m2) Δρ_{N_lin} 下界 > −0.05、(m3) Δρ_{Q_W} 下界 > −0.05；evaluate 19 閘只報告。
- 已揭露：lead 看過 card 0.2.4 全部欄位與 mpg 分布，只算過曲線在固定分鐘的值，沒算過任何候選數字。
- 狀態：**採用，發成 card 0.2.5（PATCH，R-048，2026-10-29）**。先前：完成、通過；role-audit 重算通過；G5 通過；待使用者定版號（2026-10-29）。audit（派工 20261029-193348-a83b00，`audit/audit.md`、`audit/audit_recalc.py`）自寫 W／g／四答案／bootstrap，Δρ 四值與 582 人卡片 OVR 逐位重現；用人回歸輸入仍取自 e089 管線（c0 與線性 g 差 4.4e−16 框住）。唯讀合併 sha 現在重算為 2ee6b8a1…，不等於 867054e7…，因為 data/ 有 13 檔在 19:19、19:42 被別的工作改過（晚於 E-089 19:05 跑完與 ro_after），reports 唯讀目錄 0 檔比預註冊新；下次唯讀 sha 要逐檔記錄而非只記合併值。G5：使用者看過 Caruso 103 → 39、Holmgren 11 → 6、Amen Thompson 4 → 10、Maxey 12 → 26，回「還行 可以接受」。先前狀態：完成、通過，待 role-audit 與 G5（2026-10-29，App 原地執行，使用者「你自己原地做」）。原記錄：預註冊草稿，待使用者核可。(c0) linear 重現 af37ce25…7203、(c1) npm test 57/57、(u) 過；(m1) Δρ_{N_W} +0.0096 [+0.0020, +0.0176]；(m2) Δρ_{N_lin} +0.0087 [+0.0011, +0.0168]；(m3) Δρ_{Q_W} +0.0066 [−0.0005, +0.0141]。只報告：Δρ_{Q_lin} +0.0051 [−0.0022, +0.0130]；evaluate 16/19 → 18/19（carusoGate、big14of16 轉過，剩 allFourStayTop10），ρ 2K27 0.748 → 0.738、四季 RAPM 0.746 → 0.779；Caruso 103 → 39 名，Dyson Daniels 17 → 18；MIN ≥ 1000 的 ρ(mpg, OVR) 0.749 → 0.657。卡片 `ranking.csv` sha256 73b1d6353142dd86327a022a19e939833c42a0aa0c69f3377201ffe411c0050a；報告 `report.md`。唯讀目錄雜湊跑前跑後相同。
- 相關：R-043、R-047、R-042、E-084、L-026
- 來源：使用者 2026-10-29

### E-091
- 日期：2026-10-29
- 假設：賽中 OVR（2026-27）改用 card 0.2.4 當先驗（inseason 0.2.1e → 0.2.2）：predNew（用人回歸）取代 p 進 g，MPG0 改 card 0.2.4 的 mpg 欄，r_repl／錨點改 E-084 results.json；用人特徵凍結在 2025-26，不擬合任何新參數。（spec 原編號 E-089，因 E-089／E-090 已被占用，改記 E-091。）
- 做法：`reports/ovr-inseason-2026-27/e089-card024/spec.md`；`live/run_c4_live.py` 新增 CARD_MODE=024（預設）；`live/build_usage_024.py` 呼叫 e084.py 重算凍結特徵 → `live/usage-2025-26-card024.json`。資料 cutoff 2026-10-28（sha256 606333d0…80be，67 PBP）。
- 結果：(c0) CARD_MODE=022 ranking.csv 188c8bed…、no-prior.csv e061bff3… 與 live/2026-10-28 逐位元相同；(c1) npm test 57/57；(c2) 368 人有限、t1 0.0444、lastOVR 對 card 0.2.4 ovr Spearman 0.999994、最大差 0.1；(c3) probe_base_version = inseason 0.2.2，但 HTML 不含字面「card 0.2.4」（season_nav.py 重寫來源文字，頁面顯示「先驗 正式卡 0.2.4」，禁改檔，待 lead 決定）；(c4) 582 人 ovr／mpg／gRepl 逐格重現、r_repl 與錨點差 0.0。0.2.1e→0.2.2：|ΔOVR| 中位數 2.80、最大 15.8、>10 分 15 人，最大 10 人幾乎全是用人項（Banchero +15.8、Keyonte George −15.6、Wells −15.0）；年輕 ≤23 中位數 +1.10、老將 ≥31 −0.60；前 20 進 Harper、出 Markkanen。MPG0 口徑差 >3 者 81 人（卡內 205）。r_repl −1.7593→−1.2724；錨點 PR1/50/99 −0.756/1.050/4.744 → −0.542/0.885/3.178。
- 狀態：完成，已採用並發布（2026-10-29 lead 審過：c0 兩檔 sha256、c2 lastOVR 對 card 0.2.4 最大差 0.1 自行重算，diff 已讀，npm test 自跑 57/57；(c3) 字面字串不過屬驗收寫法問題，頁面版本欄正確，接受）。完整發布 inseason 0.2.2a（gh-pages b39f4a3）；更新說明加「新賽季 0.2.2」一格後 --shell 重發（a9681d6）。注意：重抓後同截止日 2026-10-28 的資料 sha256 變成 31170cdc…（原 606333d0…），同 handoff 已記的「同截止日 sha 不同」問題，未查。
- 相關：R-044、E-074、E-084、R-019、R-031、L-026、L-050
- 來源：使用者 2026-10-29「將新賽季也跟上0.2.4」

### E-095
- 日期：2026-10-29
- 假設：新賽季 OVR（inseason 0.2.4a，原名 0.2.2a）改用 card 0.2.5 的分鐘權重 W(m) = (1−e^(−m/15))/(1−e^(−36/15))（取代 m/36），並換成 card 0.2.5 的 ranking 和錨點之後，追蹤整季答案的能力不會變差。不主張變準：W 和線性的答案卡不是同一個目標，最多 PATCH。
- 做法：`reports/ovr-inseason-2026-27/e095-card025-minutes/preregistration.md`（原編號 E-094，和防守天花板重號，2026-10-29 改號）。`run_c4_live.py` 加 CARD_MODE=025（預設仍 024）；新回測 `backtest_e095.py` import `backtest_e064.py`，副版 RG1 加 `--minutes {linear,sat15}`，錨點與答案卡同式重算。前置：(c0) linear 重現 E-064 RG1、(c0L) 線上 024 不變、(c1) npm test、(u) W 單元值、(L1) 025 的 ref 轉換重現 card 0.2.5 ovr（每人差 ≤ 0.1）。判定：(1) RG1-sat15 對 W 答案卡過 v5 V1∧V2；(2) Y5、Y6 × N=3/5/10/20 每格 MAE 差 ≤ +0.05。(1) 過 (2) 不過時交使用者選。
- 已揭露：lead 看過 E-089 卡片端全部結果、線上 0.2.2a、E-064 和 E-091 結果，以及 `backtest_e064.py` 的結構；沒看過任何用 W 算的新賽季數字。
- 狀態：預註冊已凍結（2026-10-29，使用者「核可」），sha256 66000292…db71（`preregistration.sha256`）；凍結前只把採用後版號改成 inseason 0.2.5（R-050），判定沒動。2026-10-29 跑完：前置 (c0)(c0L)(c1)(u)(L1) 全過；(1) 過（RA 與字面 A 兩種基準都過）；(2) **不過**，8 格 MAE 差 +0.19～+0.29（門檻 ≤ +0.05），合併 +0.24 [+0.16, +0.32]，低分鐘三分位增幅最大（約 +0.4）。線上頁 024→025：|ΔOVR| 中位數 1.4、最大 6.8，Caruso 85→33 名。role-audit 獨立重算 8 格差 ≤ 1.4e-5，結論成立（`audit/audit.md`）。依預註冊不自動採用，交使用者選；**使用者選 A 採用（R-052）**，2026-10-29 發布 inseason 0.2.5a（gh-pages 0e9836d）。(1) 基準沒寫明見 L-053。
- 相關：R-047、R-048、R-019、R-023、R-031、E-064、E-089、E-091、L-026、L-034、L-048、L-050、L-053
- 來源：使用者 2026-10-29「曲線的部分都完成了嗎」→「寫預註冊」

### E-096
- 日期：2026-10-29
- 假設：屬性 99 以上改用 99 + 51·(1 − e^(−Δ/(1.96·SD)))，理論上限 150（命中率型在 100% 時剛好 150）；中／近距離另加量價屬性 midValue、shortValue（出手量 × 超出替補的命中率，照 E-057 三分），只顯示不進 OVR。取代 E-090 的 125 上限與曲線外延。
- 做法：`reports/card-0.2.5+E096-tail150/preregistration.md`，基準 card 0.2.5，判定 c0–c3 同 E-090＠0.2.5；量價屬性先過 h1v 才開尾巴。
- 已揭露：見預註冊 §0（lead 看過 E-090 全部結果、手算過 Giannis／Toppin／Hayes 的近距離、看過少數人中距離出手數）。
- 狀態：進行中（預註冊凍結 2026-10-29，使用者「你就先照那个方法做」，sha256 8deade79…09e1）
- 相關：E-090、E-057、R-020、R-024、L-026、R-007
- 來源：使用者 2026-10-29「用标准差是对的…封顶就设置在150」「中距离跟近距离…既要看产量，也要看命中率」

### E-097
- 日期：2026-10-29
- 假設：E-096 之上兩處改動：(1) mid、short 收縮先驗從位置平均改成聯盟平均（命中率與量價屬性都改，使用者「每個位置都應該一樣」）；(2) 所有屬性頂端的尺從全池 SD 改成池內前 10% 的 SD（量價分布右偏，全池 SD 把頂端距離放大，Giannis shortValue 137）。
- 做法：`reports/card-0.2.5+E097-topscale/preregistration.md`，基準 card 0.2.5，判定 c0–c3 同 E-096；mid／short 的 h1、h1v 用聯盟先驗重跑；e097s／e097p 拆解、e097v 只報告。
- 已揭露：見預註冊 §0（lead 看過 E-090、E-096 全部結果與 shortValue 分布）。
- 狀態：不採用（2026-10-29，使用者「我们先不采用」；預註冊凍結 sha256 f395ebc3…093d25df）。判定 c0–c3 全過（c2N −0.0047 [−0.0087, −0.0007]、c2Q −0.0043 [−0.0078, −0.0010]、evaluate 19/19），但兩個主目標都是反效果：Giannis shortValue 137.2→140.1；Kessler（整季 0 次中距離）mid 99→142.7，全聯盟第一，Gafford 129、Poeltl 120。原因：改動二的尺必然比全池 SD 小（L-057）；中鋒中距離偏高來自 PBP 把補籃標成 Mid-Range（F-042），不是位置先驗（L-058）。中距離 99 並列 13→0。報告 `reports/card-0.2.5+E097-topscale/report.md`，診斷 `diag/`。
- 相關：E-096、E-090、E-057、L-026、R-007
- 來源：使用者 2026-10-29「命中率应该不需要依照位置做加权」「137…有点太高了吧」「A」「中间点不能用中位数」「由你这边本地开始做」

### E-101
- 日期：2026-10-30
- 假設：E-096 之上三處改動：(1) PBP 分區修正，Mid-Range 但 shotDistance < 8 呎的出手（F-042 的補籃、補扣）改歸近距離，mid、short 收縮改向聯盟平均（R-055）；(2) 百分位、r99、r01 改對 2022-23 到 2025-26 四季合併池計算（R-056）；(3) 頂端的尺 S = max((r99 − r90)/1.044, SD_pool)，只壓縮不放大（合成分布方向自查見預註冊 §0，L-057）。
- 做法：`reports/card-0.2.5+E101-crossera/preregistration.md`，基準 card 0.2.5；判定 c-pre（分區一致性）、c0–c3 同 E-096，加 c4（> 140 的值 ≤ 2 個）；e101z（只修分區）、e101g（純差距尺）、e101w（長窗）只報告。
- 已揭露：見預註冊 §0（lead 看過 E-090、E-096、E-097 全部結果與四季 PBP 依距離的聯盟合計；沒算過任何跨季 PR90／PR99／差距，也沒算過修正分區後的球員值）。
- 狀態：通過，role-audit 重算成立（2026-10-30，`audit/audit.md`，抓到報告基準混用與 fitA／primary 兩處，已更正，L-060）；使用者 2026-10-30 選「A 進 G5」，G5 名單（`g5/g5-list.json`）使用者 2026-10-30「A」通過，**採用為正式卡 card 0.2.6（PATCH，R-060）**，`reports/card-0.2.6/`，2026-10-30 commit、push 並部署名單頁。原判定 2026-10-30；預註冊凍結 sha256 44d1eb0a…40f3e5，使用者「你執行」）。c-pre mid +0.0002／short +0.0001；c2N −0.0027 [−0.0069, +0.0015]、c2Q −0.0032 [−0.0067, +0.0004]；evaluate 19/19；> 140 的值 0 個。中距離準度 = 99 的人 13→1（Kessler 99→60.9，0 投），Giannis shortValue 137.2→129.0（唯一 > 120）。副作用：OVR 重擬後 mid 每 10 分價值 .206→.137、long .436→.382、short .389→.531（primary），Curry 第 23→32、Brunson 第 51→58、Duren 第 53→37（對 card 0.2.5）；對 card 0.2.5 有 303 人移動 ≥ 5 名。mid h1 頂底都不開（n=5）。foulDraw／drive／onBall 是每季標準化值，跨季池對它們無意義（F-046）。報告 `reports/card-0.2.5+E101-crossera/report.md`。
- 相關：E-096、E-097、F-042、R-055、R-056、R-060、L-057、L-026
- 來源：使用者 2026-10-30「我们可以用很多个年份的 PR 90到99来看」「先把它合并到近距离会比较好」「你執行」

### E-105
- 日期：2026-10-30
- 內容：名單卡片「近 5 場」加單場貢獻值（使用者選 A：自己擬合 box → RAPM）。每 36 分鐘 PTS、FGA、FTA、FG3M、OREB、DREB、AST、STL、BLK、TOV、PF 對 rapm1-A net 做加權最小平方（權重 poss，A 半上場 ≥ 300 分鐘，356 人；A／B＝int(GAME_ID)%2，同 E-081）。沒有可調參數。只顯示，不進 OVR。
- 做法：`scripts/fit_game_contribution.py` → `reports/game-contribution/{weights.json, baseline-2025-26.json, report.md}`；`scripts/enrich_roster_viewer.py` 每場算貢獻值、近 5 場用合計換算、和 2025-26 整季比（±1 上色），換算 OVR 傾向：把差值當 pred 變動，照 card 0.2.5 錨點（E-089 report_only.card.new）與 W(MPG) 換算，正文只寫升／降／持平與「明顯」（≥ 2.4），換算 OVR 放 tooltip（照 5 場直接換算會到 150，太誇張）。
- 結果：B 半樣本外，貢獻值對 rapm1-B 加權 r 0.444、Spearman 0.394；Game Score／36 只有 0.361／0.291；A 半 RAPM 本身預測 B 半 0.462／0.405（穩定度上限）。正負值／36 對 B 半 RAPM 0.868 不算數：是同一批比賽算的。樣本內 0.529 只供參考（R-007）。權重：STL +1.00、TOV −0.95、FG3M +0.30、AST +0.29、BLK +0.27、PTS +0.26、FGA −0.23、截距 −3.15。2025-26 近 5 場差值 SD 1.21（場均 ≥ 20 分鐘 291 人），2026-27 開季全聯盟分鐘加權平均差 −0.35。
- 狀態：已上線（2026-10-30）
- 相關：E-081、E-089、R-007、R-028、L-026
- 來源：使用者 2026-10-30「把它每一场比赛的贡献值把它列出来。这个准不准是一回事」→「先用 A」

### E-110
- 日期：2026-10-30
- 假設：單場評分（E-105／R-062）漏掉防守；加入 NBA 單場 hustle（撥球、干擾出手、製造進攻犯規、地板球、掩護助攻）與防守對位（比進攻者平常少讓幾分、逼出失誤）後，樣本外對 RAPM 的相關比只用 box 高（H1），防守型球員評分名次往上（H2）。
- 做法：`reports/E110-defensive-rating/preregistration.md`（草稿）。2025-26 全部 1230 場抓 `boxscorematchupsv3`、`boxscorehustlev2`（存 `data/matchup-source/2025-26/`）；M0 box 11 項／M1 ＋hustle 5 項／M2 ＋對位 2 項，擬合同 E-105（加權最小平方，A→B 與 B→A）。判定 s1：M2（或 M1）對 M0 的 A→B Δr bootstrap 下界 > 0 且 B→A Δr > 0；s2（半盲）5 個防守者 ≥ 4 人名次往上。只顯示，不進 OVR；過了才另做第二階段（每日發布順便抓）。
- 已揭露：見預註冊 §1（E-105 全部結果、2026-10-30 評分對 OVR 名次差最大 12 人、單場穩定度 0.213／0.428；只看過 0022600003 一場的原始對位與 hustle）。
- 狀態：草稿，等使用者核可凍結（2026-10-30）
- 相關：E-105、R-062、R-007、L-026
- 來源：使用者 2026-10-30「只看 box score 准吗？」→「第三项做得到吗？」→「A」（先寫預註冊）

### E-107
- 日期：2026-10-30
- 假設：把 E-106 的 UL（防守加成不封頂 bonus = max(0, centeredD)，D 用 E-104 逐場線性、回合門檻 × 1/2）搬到正式卡 card 0.2.6（E-101 能力值）上，整體一致性（m1–m3）不明顯變差；Wembanyama 上升且 Wagner 仍在他後面（R-061）。lead 事前預期 Wemby #1–2、Wagner #3–5、Cade 大致不動、前 20 名換超過 3 人。
- 做法：`reports/card-0.2.6+E107-defense-UL/preregistration.md`（草稿）。組別 B6（card 0.2.6 原樣重建）、UL6 × primary／fitA／fitB；c0a／c0b 要重現 E-101 P1 卡與 card 0.2.6 ranking（a0a81ecb…6c91），c0c 要重現 E-106 UL。採用時一律 PATCH → card 0.2.7（L-026，非盲測）。
- 已揭露：見預註冊 §1（E-106 全部結果、card 0.2.6 名次；沒算過 0.2.6＋UL 的任何結果）。
- 結果：硬條件全過（c0a／c0b 重現 E-101 P1 卡與 card 0.2.6 ranking、c0c 重現 E-106 UL、npm test 57/57、u1、f2）。對 B6：m1 +0.0059 [+0.0009, +0.0111]、m2 +0.0016 [−0.0026, +0.0059]、m3 +0.0063 [+0.0011, +0.0116] 都過；r1' 過（Wagner #7、Wemby #3 → #2）。evaluate 19/19 → 18/19：big14of16 只剩 13/16（Embiid #17 → #24、Koloko #354 → #442 加成 1.47 → 0、Davis #40）。Luka #4 → #9、Durant #21 → #27、Derrick White #8 → #4；前 20 名只換 2 人；頂端 OVR 壓縮（SGA 107.3 → 104.0，PR99 錨點 3.51 → 4.12）。lead 事前預期 Wagner #3–5、前 20 換 > 3 人都錯（F-051）。總評 2/5，`reports/card-0.2.6+E107-defense-UL/report.md`。
- 狀態：草稿（2026-10-30），等使用者核可凍結
- 狀態更新：凍結（2026-10-30，使用者「凍結開跑」，sha256 344f860a…263c）並跑完；等使用者 G5：採用發 card 0.2.7（PATCH）、不採用、或先查 Embiid／Koloko。未 commit。
- 狀態更新：驗收通過、排隊待併版（2026-10-30，R-063）：照 PATCH 批次發版，維持 `card 0.2.6+E107`，不單獨發 0.2.7，等下一批改動一起出；名單頁仍是 0.2.6。
- 狀態更新：已採用（2026-10-30，R-065）：發 card 0.2.7（PATCH），`reports/card-0.2.7/`，名單頁 2025-26 改指 0.2.7；未做 role-audit。
- 編號：另一個 session 同日也用了 E-107（新賽季對齊 0.2.6，下一條）。本條較先寫、預註冊已用此號凍結，不改號；引用時寫「E-107 防守 UL」。
- 相關：E-106、E-104、E-101、R-061、R-060、R-019、F-049、F-051、L-026
- 來源：使用者 2026-10-30「b UL」→「先寫預註冊」

### E-114
- 日期：2026-10-30
- 假設：對位分數把被守者的助攻算進去（M4＝E-113 的 M3c），在沒看過的 2024-25 仍比 M2 準：季內 A／B 樣本外，以及 E-113 凍結的 2025-26 權重跨季套用，兩者都要更好。lead 事前預期 Δr +0.005～+0.02，s1 過的機率約五成。
- 做法：`reports/E114-assist-matchup/preregistration.md`（草稿）。先從現有 boxscore 組 2024-25 box，抓 1104 場對位與 hustle，算單季分半 RAPM；凍結前先做欄位檢查（L-068），結果填進 §1 給使用者看。
- 已揭露：E-110、E-113 全部結果（2025-26）；2024-25 只看過檔案清單。
- 狀態：草稿（2026-10-30），等使用者核可後才抓資料
- 相關：E-113、E-110、F-057、L-068、L-026
- 來源：使用者 2026-10-30「2」（E-113 報告的選項 2）

### E-116
- 日期：2026-10-30
- 假設：用順位分層的新秀平均當先驗卡（P2），新秀前 5～10 場的賽中 OVR 比替補級先驗（P0）或只看自己（P∅）更能預測剩下場次。
- 做法：`reports/E116-rookie-prior/preregistration.md`（草稿）。用 2025 選秀新秀在 2025-26 做留一法回測，比較 P0／P1／P2／P∅，判定後依結果選一組上線，讓 2026-27 頁的 42 個 2026 新秀都有 OVR。
- 已揭露：card 0.2.7 裡 55 個 2025 新秀的名次；2026-27 的 no-prior 名單。
- 狀態：草稿（2026-10-30），等使用者核可
- 狀態更新：草稿第二版（2026-10-30，使用者「按順位但是起點也不是很重要 趕快讓現有數據說話」）：只留順位分層一組；新秀 k＝σ²/τ²（新秀間變異，經驗貝氏），因為 n_prior=0 時現行 k_eff 取上界＝凍結在起點；回測只報告
- 狀態更新：凍結第三版（2026-10-30，使用者「A」＋「新秀每一順位都不同起點分吧 起點多少可以看前五季」）：起點＝2017–2021 五屆新秀（282 人，027 卡；2022–24 屆沒有 027 尺度的卡）各項能力對 ln(順位)＋位置的迴歸，落選當 61；τ²＝殘差變異；2025 屆變成真正樣本外回測。sha256 af3911d2…f85038。進行中
- 狀態更新：完成（2026-10-30），3/5：42 新秀都有 OVR、老將 368 列不變、npm test 過；2025 新秀樣本外 MAE N=10 新秀版 10.61／凍結 11.05／只看自己 9.99；頂順位被低估（Knueppel 85.5→65.0），起點尺度和 card 0.2.7 不合（creation +24.7、pass +13.9），見 F-060。等使用者決定上線。`reports/E116-rookie-prior/report.md`
- 狀態更新：上線（2026-10-30，使用者「1」，R-071）：daily 改跑 `live/run_c4_live_rookie.py`，名單頁 2027 頁新秀名字旁標「新秀先驗」（tooltip 寫已打場數）；gh-pages 7494587。尺度修正另開 E-121
- 相關：R-067、E-081、E-064
- 來源：使用者 2026-10-30「新秀要留 未來也要趕緊加入27的新秀」→ 選「B」

### E-117
- 日期：2026-10-30
- 假設：（描述性，不是候選）模擬關掉體力（`fatigue:false`，其他同 `budget` 模式正式 options）後，WinImp 名次、E-067 S、對答案 ρ，以及 30 隊互打的球隊淨分差／勝率 MAE、RMSE 會怎麼變。
- 做法：`reports/sim-0.1.0+E117-fatigue-off/spec.md`（sha256 6fcff6d0…9d99）；WinImp 同 E-065／E-076（379 人、baseSeed 20261028、30×16×2）；球隊同 E-076 t1（8 seed 20261028–35），差值 team＋seed 重抽 400 次 rngSeed 117；p0 驗證選項有接上（L-059）；在 5090 跑。
- 已揭露：見 spec §1（lead 沒跑過關體力；從公式推過預期主力略降、替補略升）。
- 結果：球隊淨分差 MAE 3.20→3.32（差 +0.12，90% [−0.24, +0.59]），勝率 MAE 0.087→0.093（差 +0.006，90% [−0.008, +0.021]），聯盟場均得分 117.5→119.1（真實 115.5）。主版 WinImp 名次 Spearman 0.91、平均名次差 36（獨立重跑雜訊下限 0.66／69），S（AB）81.8→79.7 仍偏長人，ρ 0.382→0.384。位置版 Spearman 0.77、平均名次差 56，S（AB）+37.5→−37.0（90% 區間不重疊），從偏長人翻成偏後衛；最高體力四分之一位置版升約 18 名，和「主力降」的推測相反。報告 `reports/sim-0.1.0+E117-fatigue-off/report.md`。
- 狀態：完成（2026-10-30，描述性；正式流程維持開體力）
- 相關：R-068、E-065、E-067、E-076、L-059、L-026
- 來源：使用者 2026-10-30「量 然後如果關體力 模擬的球隊賽季mae 會不會變動」

### E-121
- 日期：2026-10-30
- 假設：新秀起點換成 card 0.2.7 的尺度後，2025 新秀回測 N=10 MAE ≤ E-116 v3 的 10.61，頂順位不再被壓低。
- 做法：`reports/E121-rookie-scale/preregistration.md`（草稿）。三路線擇一：A 用 0.2.7 流程重建五屆新秀季卡、B 只用 2025 屆 0.2.7 擬合、C 五屆形狀＋2025 屆水準位移（lead 建議）；B／C 用留一法；2026-12-31 前瞻檢查只報告。
- 已揭露：E-116 全部結果與逐人表。
- 狀態：草稿（2026-10-30），等使用者選路線
- 狀態更新：上線（2026-10-30，R-073 路線 D 簡化版）：起點＝2K 順位曲線換本站尺度−5，x0 齊頭平移（`reports/E121-rookie-scale/report.md`）；老將 0 列變動、npm test 57/0。2025 屆回看 N=10 MAE 11.33（E-116 10.61），看過答案只報告；準確度等 2026-12-31 前瞻
- 相關：E-116、F-060、R-071、R-073、F-063
- 來源：使用者 2026-10-30 選 E-116 報告的選項 1

### E-125
- 日期：2026-10-30
- 假設：pass 從只看 AST%（AST/astCh）改成 0.5·zs(AST/36，E-055 (c) 收縮)＋0.5·zs(AST%)（R-074，寫法照 foulDraw w075），四季池與 S 錨點照 E-101 重算，樣本外 m1–m3 不明顯變差（門檻同 E-107）。
- 做法：`reports/card-0.2.7+E125-pass-volume/preregistration.md`（草稿）。基準 card 0.2.7（aebcadf1…c6b6）；P0（w_vol=0）要逐位元重現 attributes-e101.csv 與 card 0.2.7；凍結前只准跑 P0 與 vol 擬合。
- 已揭露：card 0.2.7 全部欄位；2025-26 常規池官方 AST_PCT 前 15 名與 AST/36（Giannis AST% 第 9、AST/36 6.8）。沒看過任何 comp、新 pass、OVR 或 Δρ。
- 結果（`reports/card-0.2.7+E125-pass-volume/`，role-card Sonnet 子代理；lead 從 attributes／results.json 重算 c0a、c0、改動欄、具名 pass 值與 m1–m3、p1、npm test 成立）：c0a 逐位元（395e86a0…）、c0 逐位元（aebcadf1…）、c1 57/57、u1 只有 pass 欄變（575/582 列）。m1 +0.0004 [−0.0004, +0.0013]、m2 +0.0007 [−0.0002, +0.0017]、m3 +0.0004 [−0.0005, +0.0013]，三項全過；p1 相鄰季 0.927／0.931／0.896（P0 0.922／0.929／0.889）。evaluate 18/19＝基準；2K27 ρ 0.7359→0.7369。astvol k=5.66、λ=0.5、kh=8。pass 名次（582 人）：Giannis 10→25（值 97.7→96.2，頂端壓縮所以分數只降 1.4）、SGA 14→26、Embiid 96→121、Trae 3→2、Draymond 45→38、Kawhi 121→157。OVR 前 20 只換第 19 名（Knueppel 進、Ausar Thompson 出），動 ≥10 名只有 4 人。simulatedPer36 P0／P50 逐人相同：這條鏈的 cards 沿用既有模擬 per36，新 pass 只進 OVR 迴歸，沒進模擬（R-074 說也進模擬，要另走模擬重跑）。偏離：2025-26 pass 實際入口是 E-090 `a0.py`／`a0-raw.json`（預註冊寫 a0_e101.py），w=0 已逐位元重現。
- 狀態：完成、判定全過；已發 card 0.2.7a（2026-10-30，使用者「0,2,7a」，R-077；`reports/card-0.2.7a/`）
- 相關：R-074、R-034、E-070、E-101、E-107、L-026、L-063
- 來源：使用者 2026-10-30「giannis only has 5 assist, why he is leading in pass」→「same as 3pt, we need to mix ast and ast%」

### E-123
- 日期：2026-10-30
- 假設：3PT（threeValue）、RIM（help）、PRES（pressure／presDisplay）照 E-101 框架（四季合併池、差距尺＋只壓縮保險、h1 過的那端才開）開 99 以上與 40 以下尾巴後，剛好 99 的並列（4／4／7／6 人）散開，卡片層不變差（m1–m3、c3 ≥ 18/19、c4 > 140 ≤ 2 個）。
- 做法：`reports/card-0.2.7+E123-tail-3pt-rim-pres/preregistration.md`（草稿）。基準 card 0.2.7。T（threeValue，只顯示）補抓 2022-23 追蹤投籃，抓不齊改三季池；H（help）沿用現行收縮、不用 E-080 位置收縮，f-eng 查引擎讀不讀 > 99；P（pressure）用 defense-tenth 現成的 2022-23、2023-24 hustle／matchups 重建 force，a0P 要逐人重現 E-071 force。變體 e123（主）、e123h、e123p（只報告）。
- 已揭露：三欄 2025-26 頂端名單與 99 並列人數、E-080／F-030（Stewart 原值 123、z 4.82）、E-071、E-057 全部結果；lead 手算 Stewart 可能 125–136。
- 狀態：已凍結（2026-10-30，使用者「Freeze and run」；sha256 bbaace39…2374，見 `reports/card-0.2.7+E123-tail-3pt-rim-pres/preregistration.sha256`）；2026-10-30 跑完，判定全過，總評 4/5；使用者採用（R-078），疊到 card 0.2.7a 重建（`rebase-027a/`：c0 只放 E-125 = 0.2.7a 逐位元，m1–m3 過，c3 18/19，c4 0，三欄和 e123 逐人相同；R-064 影響小：前 20 換 1 人、前 300 移動 ≥ 10 名 2 人），發為 **card 0.2.7b**（2026-10-30）
- 結果（`reports/card-0.2.7+E123-tail-3pt-rim-pres/report.md`，lead 已重算核對三欄 99 並列與 > 140）：剛好 99 的人 3PT 4→0（Curry 105.0）、RIM 4→0（Stewart 113.5、Wembanyama 108.7）、PRES 7→0（Thybulle 127.0）、presDisplay 6→0；> 140 為 0；c0 逐位元、m1–m3 ±0.001、c3 18/19。h1：T、P 底端沒過（維持 40），H 兩端過。副作用：Mobley 從第 22 名到第 29 名，Knueppel 進前 20、Anunoby 出。偏差 D1–D8；a0T 第一次 0.31 沒過，修重現 bug（3PA＝0 取聯盟先驗，D8）後才過，照字面違反 §3「不改規則重試」，交使用者裁定。
- 相關：E-090、E-096、E-101、E-080、E-071、E-057、R-024、R-055、R-056、R-072、F-046、L-072
- 來源：使用者 2026-10-30「為何 rim pres 3PT 的錨點沒修，最強的很多人都在 99 整」→「寫預註冊」

### E-131
- 日期：2026-10-30
- 假設：卡片 OVR 迴歸拿掉 physique（身高＋體重/10 百分位），heightInches 與其他屬性留著、form／ridge 照原 CV 程序重選，樣本外 m1–m3 不明顯變差（門檻同 E-107／E-125）。
- 做法：`reports/card-0.2.7b+E131-no-physique/preregistration.md`。基準 card 0.2.7b（361bcac6…1105）；calibrate-wing.py 加 `--dropAttr`，K0 要逐位元重現 0.2.7b、K1 拿掉 physique；凍結後先跑 K0 的 c0。模擬引擎不動。
- 已揭露：card 0.2.7a／0.2.7b 全部欄位、0.2.7a 的 16 項係數（physique +0.231／10 分 SE 0.102，heightInches −0.752／10 吋 SE 0.518）；2025-26 bio × pooled RAPM 相關（體重 r +0.18、同身高下體重 r +0.11，448 人）。沒看過拿掉後的任何結果。方向由使用者選，不是盲測。
- 狀態：凍結（2026-10-30，使用者「凍結開跑」；sha256 bd56dc35…1263））。
- 結果（`reports/card-0.2.7b+E131-no-physique/report.md`，role-card Sonnet 子代理；lead 重算 c0 sha、屬性欄不變、具名名次、前 20、m1–m3 成立）：c0 逐位元、c1 57/57、u1 過；m1 +0.0015 [−0.0014, +0.0044]、m2 −0.0014、m3 +0.0013 全過；evaluate 18/19＝基準；2K27 ρ 0.738→0.733。heightInches 係數 −0.77→+0.10、rebound 0.03→0.10。前十不動，前 20 只換 1 人（Ausar 出、Anunoby 進）；Zion 43→65（81.8→79.8）、Randle 154→163、Herb Jones 16→19、Mobley 28→23；後衛沒升（SGA 105.0→104.6）。MIN≥1000 名次移動 ≥10 名 42 人，多在 200 名後。偏離 8 項見報告（ranking 仍輸出 physique 欄、預註冊寫的 −0.752 是 0.2.7a 值等），都不影響判定。
- 狀態：完成、判定全過（2026-10-30）；採用，發 card 0.2.7c（2026-10-30，R-084；R-064 前 300 名 36 人移動 ≥ 10 名本該 PATCH，使用者裁定 0.2.7c）
- 相關：E-125、E-123、E-076、E-085、F-034、F-039、R-002、R-042、R-064、L-026
- 來源：使用者 2026-10-30「phys 有什麼效果」→「所以說體格和影響力沒有正相關。不需要放在網站」→ 選項 2（連 OVR 也拿掉）

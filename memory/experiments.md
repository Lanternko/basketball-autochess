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
- 結果：（待填）
- 狀態：進行中
- 相關：R-025、R-026、F-029、E-033、E-060、E-062、L-026、L-031
- 來源：使用者 2026-10-28「每場，含上場時間」

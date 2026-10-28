# inseason 0.1.0 即時版（2026-27）

賽中 C4（E-033，c=1 凍結）用 2026-27 已打場次逐球員更新能力值與 OVR。先驗＝v5 先驗卡 2025-26（card 0.1.0）。

**現行（inseason 0.2.1，E-074）**：先驗＝card 0.2.2（`prior-2025-26-card022.json`，`build_prior_022.py` 由 `reports/card-0.2.2/ranking.csv` 轉成）；凍結迴歸係數／每場錨點取 `reports/card-0.2.2/cards/P1/primary/{summary,pergame-summary}.json`；pressure＝逼失誤（賽中凍結）；foulDraw 賽中更新用 E-070 公式（常數凍結在先驗 JSON 的 `foulDrawFreeze`）。環境變數 `CARD_MODE=022`（預設）；`CARD_MODE=020` 逐位元重現 inseason 0.2.0c（先驗 `prior-2025-26-card012.json`）。輸出資料夾名要給絕對路徑才不會落在 live/ 底下。

## 怎麼跑
1. `node scripts/fetch_season_games.js 2026-27`（使用者已跑）→ `data/season-source-2026-27/`。
2. `node scripts/fetch_inseason_2026_27.js`：複製 player-games／team-games、重抓 bio、抓每場 PBP → `data/defense-seventh/2026-27/`。
3. `python -I reports/ovr-inseason-2026-27/live/run_c4_live.py [資料夾名]` → `live/<資料截止日>/{ranking.csv,no-prior.csv,meta.json,README.md}`。
4. `python -I scripts/build_inseason_viewer.py [日期]` → `live/<日期>/roster-viewer.html`。

規則：S* 的 δ²、rel 只用嚴格早於 S* 的起點（Y1..Y6、D1..D3；short／creation 不含 Y 起點，同 v5）；每人 f = min(自己的 GP/82, 1)；沒有先驗卡的人不給 OVR；2026-27 結果不回頭調任何參數（L-026）。

## 降級的資料層（C4 讀不到或讀到不完整的）
| 項目 | 狀況 | 影響 |
|---|---|---|
| four-factors、v3-league、dependence、shot-origin（2026-27） | 抓取腳本不抓 | pressure 凍結；onBall／help／physique／heightInches 本來就凍結，C4 不更新防守端屬性 |
| PBP 0022600101 | 來源檔只到第一節（比分 33,34 對 108,111），重抓一樣 | 該場不進 shots／PBP 衍生的樣本；box 仍計入。`fetch_inseason_2026_27.js` 因此 exit 1，預期內 |
| 2025-26 先驗卡 midA = shortA = defensePossessions = 0 | 先驗樣本為 0 | mid／short／pressure 的 k 一律取上界（保守，等於幾乎不動：w≈0.05） |
| 2025-26 凍結映射 | 既有檔沒涵蓋 2025-26 | 用 box 公式重建（同 build_season_cards 流程）；long／ft／drive／tovSkill／stamina 與上季卡差 ≤0.05（tovSkill 個別 1.45），pass 中位差 0.58、最大 5.9，rebound 中位 0.48、最大 4.3，creation 中位 3.4、最大 24（它依賴 ff／v3 層），mid 不可重現（先驗樣本 0，不影響） |
| δ² | D3 的 mid／short 配對因 2025-26 目標先驗樣本 0 而掉出 | 這兩項 δ² 用較少配對估 |
| 無先驗卡球員 | 55 人（新秀、沒進先驗卡者） | 只列 `no-prior.csv`，不給 OVR |
| N=0 的有先驗卡球員 | 220 人 | 不列入 ranking.csv |
| 逐點管線 pr／T | 固定為開季先驗卡 | ΔOVR 為「同一把尺」下的差 |

資料覆蓋：2026-10-20..2026-10-27、56 場、417 名球員、每人 1–4 場；樣本極小，OVR 變動多半是少數低 k 屬性（pass／creation／rebound／tovSkill／ft）的收縮結果，只看趨勢。

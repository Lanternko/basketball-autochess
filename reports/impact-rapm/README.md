# 真實影響力驗收：在場與不在場、RAPM

**目的：用真實比賽，判斷模擬和兩種 OVR 原型低估或高估了哪些球員。** box score 量不到的價值（拆解困境、沒戰術時硬解、吸引包夾替隊友製造空檔、卡位），都會反映在「這名球員在場時，球隊每回合多得或少失多少分」。

## 執行（需要本機資料）

```
python3 reports/impact-rapm/rapm.py --self-test   # 假資料測試，約 6 秒
python3 reports/impact-rapm/rapm.py               # 2022-23 到 2025-26 四季
python3 reports/impact-rapm/rapm.py --prior reports/ovr-rapm-calibrated-2025-26/priors.csv
                                                  # 以 box score 預測值為先驗的 RAPM
```

四因素 RAPM（哪些防守是可重現的個人能力）：

```
python3 reports/impact-rapm/four-factors.py --self-test   # 約 20 秒
python3 reports/impact-rapm/four-factors.py               # 四季，預估 10 分鐘左右
```

輸出 `four-factors.csv` 與 `four-factors-summary.json`。對手的抄截以外失誤、抄截、每回合出手數、eFG%、籃下出手比例、三分出手比例、罰球率、進攻籃板率，各自解出每位球員的攻守係數。另外把比賽切成兩半各估一次，算出每個因素的個人可靠度。

`--prior` 版會另外輸出 `rapm-prior.csv` 與 `rapm-prior-summary.json`，不覆蓋一般版。說明見 `reports/ovr-rapm-calibrated-2025-26/report.md`。

輸入是 `scripts/prepare_defense_b1.js` 產生的 stint 檔，這份 GitHub 快照沒有收錄：

- 2025-26：`reports/defense-b1/stints.jsonl`
- 其他三季：`reports/defense-seventh/<季>/stints/stints.jsonl`

每段 stint 記錄兩隊的五人名單；`teams[i].opponent.points` 是第 i 隊防守時對手的得分，`teams[i].defensivePossessions` 是對應的回合數。

## 輸出

| 檔案 | 內容 |
|---|---|
| `onoff.csv` | 每位球員每季：在場與不在場時的進攻效率、防守效率、淨效率（每 100 回合） |
| `rapm.csv` | 每位球員：控制隊友與對手後的進攻、防守、淨影響（每 100 回合）。分成四季合併版，以及只用 2025-26 的單季版 |
| `rapm-summary.json` | 選定的正則化強度、交叉驗證誤差，以及與四種榜單的排名相關和個別球員排名對照 |

## 方法

- **資料單位**：每段 stint 的每一邊算一筆，目標是每 100 回合得分，權重是回合數。
- **模型**：得分 = 聯盟平均 ＋ 進攻五人的 O 值總和 − 防守五人的 D 值總和。淨影響 = O ＋ D；D 為正代表少失分。
- **正則化強度**：只用「依比賽分組的 5 折交叉驗證」選擇，同一場比賽不會同時出現在訓練與測試中。
- **四季合併版**：每位球員只有一個係數，樣本大、比較穩定，但會混入能力隨年份的變化。單季版比較貼近 2025-26，但雜訊大。

## 對照與判讀

`rapm-summary.json` 的 `comparison2025_26` 只比較 2025-26 球員中，四季合併版累積至少 2,000 回合的人。對照的四種榜單：

- 模擬貢獻（位置校正）
- 模擬貢獻（位置校正＋收縮）
- 模擬校準 OVR
- 期望產出 OVR

判讀方式：

- **排名相關**：哪一種榜單和真實影響力最一致。
- **個別球員**：Brunson、Cade 等人的 RAPM 如果明顯高於模擬，代表**模擬本身**低估了這類球員，要先改模擬；如果模擬不低、只有公式低，代表**公式**缺了欄位。

## 已做的檢查

- `--self-test`：建立已知真實效果的假聯盟（150 人、1,200 場），RAPM 還原的相關為：進攻 0.88、防守 0.79、淨值 0.86。加入有參考價值的先驗後，淨值相關提高到 0.91，預測沒看過的比賽時誤差也下降。
- 在場與不在場統計，以及對照函式，都用小型假資料跑過。
- 真實資料尚未執行，因為 stint 檔只在本機。

## 限制

- RAPM 不是純因果：教練的上場安排、垃圾時間、球員搭配習慣都會混入。
- 單季 RAPM 的標準誤大約是每 100 回合 2～3 分，排名相鄰的球員無法區分。
- 罰球得分已計入 `points`。一回合以時間重疊拆分，可能不是整數。

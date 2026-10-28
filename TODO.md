# TODO

## 3PT 第二階段：難度調整（壓迫下的命中）
- 背景（2026-10-28）：卡片 3PT 只等於往聯盟平均拉回的三分%（`scripts/.seventh-base-2025-26-25.js:30-31`），不分持球自投或接球投，也不看防守距離，所以出手少、多為空檔的射手（如 Portis）排名偏高。第一階段 v59（依出手頻率改拉回目標）改善在雜訊內，又讓 Giannis 掉出前十，不採用，見 `reports/ovr-v59-3pt-prior-2025-26/`。
- 進行中：v62 卡片端的難度調整與出手量研究，見 `reports/ovr-v62-3pt-difficulty-2025-26/`。直覺驗收：Curry、Edwards、Knueppel、LaMelo 要在 3PT 前 15。
- 待做：模擬每次出手要帶入難度（出手類型與防守壓迫），避免和能力值重複計算。改完 C4 要重新驗收。
- 驗收：沿用直覺式指標（中位誤差／誤差 >10 分人數／80% 命中＋球員抽查表）。

## 切入 B 階段：模擬也拆 drive／foulDraw
- 背景（2026-10-28）：`drive` 原本是 FTA/FGA 百分位，模擬卻把它當突破／創造能力用（`src/probability_model.js` 第 86、194、246、364–368 行），導致 Gobert 被當成持球威脅。A 階段只改卡片，見 `reports/ovr-v60-drive-split-2025-26/`。
- 待做：
  1. 跟 3PT 第二階段併成同一個資料調查任務：NBA tracking 的 Drives（突破次數、突破後出手／得分／罰球／傳球／失誤）、Possessions（每次觸球運球數、持球秒數）、Play type（Isolation、PnR Ball Handler），確認 2025-26 前 41 場的切點拿不拿得到。
  2. 模擬改成犯規語意用 `foulDraw`，創造／包夾／出手位置語意用新 `drive`。
  3. 跟 3PT 第二階段一起重跑 C4 驗收，只驗一次。

## 不急：OVR 裡新 drive 係數 ≈ 0 的原因
- 背景（2026-10-28，v60）：對 RAPM 回歸時，價值全給了 `foulDraw`（+0.074/10 點），新 `drive` 係數 −0.013（SE 0.072）。
- 待查：新 `drive` 是不是和 `pass`、`creation`、出手量高度共線，價值被那些屬性吸走了。看相關矩陣與 VIF，拿掉 `foulDraw` 後 `drive` 的係數會不會回來。
- 目前不打算人為壓低 `foulDraw`：資料支持它有價值，籃球上製造犯規也確實是價值。

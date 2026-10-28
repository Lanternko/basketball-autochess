# 外部參考（references）

論文、外部 repo、資料來源與方法出處。讀寫規則見 [README.md](README.md)。條目寫「我們借了什麼、用在哪」，不轉貼原文。

**不在開工必讀**，要查出處時才 grep。外部研究不直接當規則用：要實踐時，先蒸餾成我們自己的流程（`README.md` 的關卡／寫入規則、`R-`／`L-` 條目），再把「用在」欄指向那些地方。每次開工讀的是蒸餾後的流程，不是這份。

欄位（固定）：
- **ID**：`S-001` 起，只追加。
- **日期**：收錄日期。
- **標題**：原文標題。
- **作者**：作者與單位。
- **連結**：arXiv ID（用 API 核對過才寫）、repo、網址。
- **借用**：我們拿了哪個部分（章節、資料、方法）。
- **用在**：本 repo 對應的檔案、條目 ID。
- **狀態**：`採用`｜`參考`｜`待讀`｜`棄用`。改狀態時在括號註明日期與原因。
- **相關**：其他 ID。
- **來源**（選填）：誰在什麼對話或 commit 引入。

範例：

```
### S-999
- 日期：2026-10-28
- 標題：某篇論文
- 作者：某人（某大學）
- 連結：arXiv 0000.00000；https://github.com/org/repo
- 借用：§3 的分半驗證流程
- 用在：memory/README.md 五道門 G4
- 狀態：參考
- 相關：R-007
```

---

### S-001
- 日期：2026-10-28
- 標題：Build, Don't Play: Self-Improving LLM Research Agents Develop a Hearthstone Battlegrounds AI That Rivals Top Players
- 作者：Changlian Ma、Limin Wang（南京大學、上海人工智慧實驗室）
- 連結：arXiv 2610.33845（2026-10-24 發表，2026-10-28 用 arXiv API 核對標題與作者）；https://github.com/MCG-NJU/AutoTavern（TavernGym 模擬器＋TavernBench 960 題；不含 TavernAgent 權重與訓練碼）
- 借用：§4、附錄 A 的 typed research memory（多個研究 agent 共用固定欄位的記憶）與「每個主張過驗證關卡」的做法。經 jev-hearthstone 的 `memory/` 轉用。
- 用在：`memory/` 整套結構（README、handoff、L/R/F/E 條目）；五道門 G1–G5。
- 狀態：採用
- 相關：無
- 來源：2026-10-28 建立 memory/ 時引入；本條於 2026-10-28 對話補記。

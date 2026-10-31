# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫，不往下追加日期段。歷史在 findings／experiments／rulings／lessons；舊版全文在 `archive/`。
**多個 session 同時改本檔與工作樹**：覆寫前先重讀一次，只改自己負責的條目。

- **更新**：2026-10-30 中午，Claude Code App（lead；分支 claude/project-thread-63h2fz；工作區整理＋memory 瘦身）

## 目前基準
- **正式卡 card 0.2.7c**（E-131、R-084：卡片 OVR 迴歸拿掉 physique）：`reports/card-0.2.7c/`、`build_card_027c.py`，ranking sha 99466f36…1655。**未 commit、未部署**。名單頁 2025-26 拿掉 PHYS、重分組 投籃／進攻（DRV FD PASS CRT）／球權（REB TO PRES）／防守（PER D RIM DIQ）（`build_card_viewer.py` apply_common 之後改 GROUPS）；status_snapshot、enrich 錨點 GC_ANC、patch note 都指 0.2.7c。版本鏈：0.2.3（E-075）→0.2.4（E-084）→0.2.5（E-089）→0.2.6（E-101）→0.2.7（E-107 UL）→0.2.7a（E-125）→0.2.7b（E-123）→0.2.7c；每版細節查 experiments／rulings 對應 ID。
- **新賽季頁 inseason 0.2.7b**（E-128，R-085 使用者破例採用；commit 3d07cbe、gh-pages df19175，數據至 2026-10-29）：`run_c4_live.py` CARD_MODE 預設 027b（027 逐位元重現 0.2.7）。新秀先驗 E-121（2K 起點，`live/rookie-prior-2026.json`；重跑 `build_rookie_prior.py` 後要接 `build_2k_start.py`；前瞻檢查 2026-12-31）。新秀／老將 onBall、help 賽中逐場更新（R-076，`live/rookie_defense.py`）；defenseBonus 每天重擬合 E-104 D（`live/defense_bonus.py`）。3PT 頂端改走即時池尾巴、不封 99（R-087，未 commit、未部署）；INS 開季被觀測值拉到 99 以下是雙重收縮，另議。
- **網站**：GitHub Pages 首頁 2026-27、`2025-26.html`（`build_card_viewer.py`、共用 `season_nav.py`）。已上線：DIQ 欄含負分（R-080）、能力值整數顯示、近 5 場＋單場貢獻值（E-105）、影響力四格、賽季切換。體力欄已拿掉。只改 UI 用 `python -I scripts/daily_inseason_update.py --shell` 立刻發布；每日排程 14:30／16:30（registry `basketball-inseason-daily`）。
- **新賽季頁收現役名單上還沒出賽的人**（2026-10-31，使用者「Kon 只是受傷」）：`fetch_inseason_2026_27.js` 多抓 commonallplayers → `data/defense-seventh/2026-27/roster.json`；`run_c4_live.py` 把有卡、在名單上、N=0 的人列入（OVR＝開季先驗，球隊以名單為準，3PT 池只用已出賽者）。10-31 實測多 68 人（Kon 第 15、Butler 第 14），已出賽 374 人逐欄不變；roster.json 缺檔時退回舊行為。已發布 gh-pages 1f530f6；同日補頭像、沒出賽的人顯示「本季尚未出賽」並排「—」格子，卡片和別人等高。
- 模擬 sim 0.1.1（R-088，2026-10-30 刪體力，和 0.1.0 `fatigue:false` 逐位元相同；已合回主 checkout 並 commit）；防守 `nba-defense-v3`（R-010）；賽中 OVR C4（E-033）；長人偏袒量尺照 E-099／E-102。

## 進行中／等使用者
- **rulings／lessons 整併**（2026-10-30，使用者要求）：`memory/rulings.md` 88 條併成 20 條、`memory/lessons.md` 83 條併成 15 條（預註冊、看實際執行路徑、共用 checkout commit 等各併成一條）；舊 ID 查各檔檔尾「舊 ID 對照」表，pre-commit 把表裡的 ID 算保留（README 寫入規則例外）。新條目若同主題，改寫該條並在「合併」欄記新 ID；下一個 ID R-090、L-083。findings／experiments 不整併（開工不讀，是帳本）。
- **薪水相關分析**（F-072，`reports/salary-corr/`）：已 commit，探索分析不進版本。2K 最貼近薪水（0.71–0.87），card OVR 0.58–0.67，RAPM 單季 0.2–0.3；以前賽季用替代 OVR（bref 進階數據學 0.2.7c，樣本外 ρ 0.80–0.86）。真 OVR 重建以前賽季要約 8 層實驗檔逐季重跑，使用者未要求。
- **E-132 卡片改讀自製先驗 RAPM（L2）**：完成；階段 A 取消、階段 B 待 **2027-02** 回來算。等使用者：errata、要不要另立「連 defenseBonus 一起換」。
- **E-134 舊季滾動回測先驗 RAPM 卡**：預註冊草稿 `reports/card-0.2.7c+E134-rolling-prior/`，等使用者選範圍並凍結；defenseBonus 這次一起換（補 L-079）。
- **E-133 分項目遺忘率**（2026-10-30）：完成 1/5「沒有改善」，使用者不採用（R-090，F-071、L-080）。
- **E-129 賽中權重曲線**：完成 2/5「沒有改善」，使用者不採用（R-090，F-070）。賽中更新速度這條線先停，等 2026-27 季後再說。
- **E-122 回合時長 D1**：凍結、A1 修正（L-077）後執行中。
- **E-117 模擬關體力描述量測**：完成（2026-10-30）。球隊賽季誤差略差但在雜訊內，主版 WinImp 幾乎不動（Spearman 0.91），位置版長人偏袒 S 從 +37 翻成 −37。正式流程維持開體力。報告 `reports/sim-0.1.0+E117-fatigue-off/report.md`。
- **sim 0.1.1 刪體力**（R-088，2026-10-30）：使用者「合」，已從 worktree `.claude/worktrees/agent-ab18991181a92d44a` 合回主 checkout 並 commit（19 檔；E-122 在 defense_fourth_game.js 的未 commit 改動沒進 commit、仍在工作樹）。主 checkout 重驗：npm test 52 過、c0 120 場 sha 604439d5…412a 和舊引擎相同。傳 `fatigue:true` 會報錯；v14–v41 memoized 舊鏈會壞（舊研究腳本）。2026-10-30 依 R-089 再拿掉 doubleThreat 體格項（主 checkout 3 檔，已 commit；和改動前＋E-086 ch1 hook 逐位元相同，timed_game 鎖定雜湊改 edec4342…，npm test 52 過，`dblthreat-phys.diff`）。待修：得分偏高 119.1 vs 115.5（TODO）。報告 `reports/sim-0.1.1-no-fatigue/report.md`。
- **E-130 DIQ 拿掉 2500 回合門檻**：1/5 不採用（R-083），程式在 worktree `D:/Projects/CODING/ba-e130`（未 commit）。等使用者：結案，或另議新秀 DIQ 只顯示不進 OVR。
- **新賽季頁影響力四格改自製 EPM 式**（R-086）：已 commit、上線；只顯示不進 OVR。待觀察：開季 Kawhi（116 回合）排第 4 這類小樣本靠生涯值撐的名次；生涯噪音 c 偏保守。
- **E-135 包夾威脅拿掉體格項**（loop H10）：完成 1/5「失敗」（2026-10-30）。樣本外 S 61.1→60.8，區間含 0；頂端長人名次不動。原因：真實球員 doubleThreat 被量測錨點抵銷（F-073、L-081）。報告 `reports/sim-0.1.0+E135-dblthreat-phys/report.txt`。使用者依奧坎剃刀裁定刪掉體格項（R-089），已改進 sim 0.1.1 並 commit。等使用者：下一步方向（查量測錨點 m.self／籃板二次進攻／停長人線）。
- **E-114 助攻算進對位**：草稿，等核可。
- **E-100 防守 D 傷停降權**：第一階段 3/5；等使用者要不要第二階段、2019-20 原因碼補法。
- E-090 屬性尾巴：experiments 仍登記「派工中」，實際已被 E-096→E-101（card 0.2.6）取代，狀態欄待收掉。
- 新賽季頁跟上 card 0.2.7c（OVR 拿掉 physique）：另走 inseason 實驗（R-050），列在 TODO.md。顯示分組 2026-10-31 已先和 2025-26 頁一致（PHYS 不顯示，R-012；commit f21b3d9、gh-pages d1db3c0）；ΔOVR 欄改名「較開季」。
- 待裁定小項：TO（tovSkill）刪或改持球分母（R-032）；INS 拆近框＋終結（先查和 DRV 重疊）；Curry 下滑可否接受；foulDraw／drive／onBall 改原始值（F-046）；補籃另開能力值（R-056）；網站防守四項的權重與第三項名字（R-053）；stamina 要不要顯示；Hauser「護球」欄改名。
- 等季末：E-083 跨季 RAPM d=0.75（2026-27 季末）；「換隊隔年變好」子組（E-127，季後）。

## 未 commit 的改動
- card 0.2.7c 整組（reports、`build_card_027c.py`、名單頁分組、status_snapshot）；E-096／E-097／E-104／E-106／E-107／E-130／E-132 報告；`src/defense_fourth_game.js`、`reports/ovr-rapm-calibrated-2025-26/fit.py`（別的 session）；memory 多檔。
- 工作區整理（2026-10-30 本回合）：刪根目錄 `trace-*.log`；`graphify-out/` 移出 git＋加 `.gitignore`；`DESIGN.md`／`PRODUCT.md` 搬進 `docs/`；`AGENTS.md` 改指向 `CLAUDE.md`；本檔日誌段移到 `archive/handoff-log-2026-10.md`，瘦身前整份存 `archive/handoff-2026-10-30-full.md`；新增 `memory/build_digest.py` → `digest.md`（lessons／rulings 一行一條摘要；不進 git，開工先跑它重產再讀），CLAUDE.md／README／四個 skill 已改指摘要表。
- 工作區整理第二批（2026-10-30，同回合）：`reports/` 內 464 個超過 128KB 的結果 JSON（league、cards、card-values、coefficients 等，約 300 MB）`git rm --cached` 移出 git，檔案仍在本機，用旁邊 .sha256／.md 核對；`scripts/github_snapshot.py` 的納入規則同步改成只收證據類 JSON。66 個點字首產生腳本搬到 `scripts/archive/generated/`、21 個只剩舊報告提到的腳本搬到 `scripts/archive/retired/`（名單與理由見該目錄 README），`.gitignore` 加 `/scripts/.*`。`.git` 本身 152 MB 要縮得重寫歷史，沒做。
- 共用 checkout：`scripts/season_nav.py`、memory 條目檔常混有別的 session 的改動，只挑自己的段落 commit；`reports/` 被 gitignore，要 `git add -f`。

## 下一步
- 等使用者裁 E-132 errata、E-130 結案；之後新賽季頁跟上 0.2.7c。
- DeepSeek 餘額不足（402），auto_review 失效，等使用者儲值。

## 開放問題
- 長人偏袒量尺（E-102）：(a) E-076 G5 升不升版（原稱 sim 0.1.1 候選；0.1.1 已給刪體力，若採用改叫 0.1.2）（使用者 2026-10-30 選下一步「2」、沒表態升版，照 lead 建議暫不升）；(b) 量尺定為 X 計分＋聯合區間＋60 樣本、b1 停止條件怎麼改寫；H1 基準陣容定義未裁定。
- 體力與換人線擱置（R-068，TODO.md）；「聰明教練團」構想要等疲勞曲線。
- 卡片 OVR 要不要、怎麼接進對局（F-010）。
- Stewart help 99（E-080 未過；TODO「護框／協防拆分」）。臂展 F-031 以後再深入；README PHYS 公式說明過時（F-032）。

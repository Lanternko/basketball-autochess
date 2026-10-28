# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫。歷史在 findings／experiments／rulings／lessons。

- **更新**：2026-10-29，Claude Code App（lead；分支 claude/project-thread-63h2fz，已 push）

## 進行中的工作
- 版本號改制（R-018）：正式卡片 = `card 0.1.0`；下列實驗都掛在它上面。
- v62 3PT 難度與出手量（E-056，`card 0.1.0+E056`）：完成（被 max_turns 截斷但報告齊全）。直覺驗收未過，等使用者決定 3PT 定義。
- E-057 三分價值（量為主、同量比準，R-020）：完成，`reports/card-0.1.1+E057-three-value/`。取代版 2K27 ρ 0.4956、Mobley 進前十，主驗收未過，不採用進 OVR；並列版 0.5175 但屬事後挑選（L-026）。待使用者選：threeValue 只當顯示用（PATCH），或另行預註冊並列版樣本外檢驗。2K27 三分參考（R-021，`reports/ref-2k27-3pt/`）：2K 前 100 名中對上 82 人，與 2K 三分的 Spearman 在現行 long 是 0.17，在 threeValue 是 0.49。2K 比 threeValue 更看重少量但很準的射手（Kennard、Durant、Cam Johnson），也比較看好高難度的持球射手（Brunson、Tatum、Markkanen）。
- E-058 onBall／help 縮水：完成、不採用（`reports/card-0.1.1+E058-defense-shrink/`）。對手三分命中差在測試季沒有任何方法贏過「人人聯盟平均」，onBall 現行算法基本是雜訊。下一步提案 E-059：onBall 改用干擾三分／36＋對位負擔＋被針對程度（defense-tenth step4-t2 的建議），已 GO 並完成（E-059）：預註冊驗收全過，2K27 ρ 0.5124（+0.0032，bootstrap 90% 區間含 0），Luka onBall 9→269；但 Wembanyama onBall 14→373（T 的位置組錯置：Wembanyama 列 F 卻守中鋒）。待使用者裁定：是否採用、算 PATCH 還是 MINOR、T 對長人要不要另行預註冊修正。使用者選「先修長人」→ E-060 已預註冊並派工（T 改成對手在他面前比平常多出手多少）。 E-060 完成、不採用：2K27 ρ 0.5181（區間下界 +0.0003），Luka 9→276，但長人仍掉到 340 名後（Wembanyama 344、Gobert 356、Embiid 368），原因是長人守長人時對手籃下出手本來就多。待使用者選：E-061 只在外線用 T（例如 T 只算 MATCHUP_FG3A，或長人改用護框指標），需重新預註冊。 使用者選 E-061（T 只算三分出手），已完成、不採用：2K27 ρ 0.5143（區間含 0，且比 E-060 差），長人仍在 326–369 名。三版 T 都讓長人掉，結論是外線單防指標不適用守禁區的人。待使用者裁定：(a) 長人的 onBall 改由護框／協防分量處理、onBall 只評外線（需新預註冊）；(b) 接受 E-060（OVR 前 20 長人名次幾乎不變，只是 onBall 屬性欄難看）；(c) 停止改 onBall。 → 使用者裁定採用 E-060（R-022：onBall＝外線單防，長人看 help）。card 0.1.2 候選 = 0.1.1 + E-060（PATCH），卡片 `reports/card-0.1.1+E060-onball-targeting/primary/ranking.csv`。尚未做：寫進 `scripts/build_season_league.js` 讓模擬吃新 onBall、status_snapshot 的 OFFICIAL_CARD 仍指 v58，等使用者說發版再切。
- v61（E-055）完成：19/19，低分鐘膨脹多數壓下，但 2K27 ρ 降 0.028、長人 15/16；等使用者抽查。
- lead 已抽驗：v61 ranking 雜湊與 long 欄一致；v62 雜湊未重跑。
- 下一版：`card 0.1.1` = 0.1.0 + E-054 + E-055（E-056 不含）。依 R-019 是 PATCH（2K27 ρ 沒變準），G1–G3 已在 v61 報告通過、前 20 名只換 1 人，不必重跑 G4；卡片就是 `reports/ovr-v61-shrink-history-2025-26/ranking.csv`。等使用者說發版再寫 R 條目定版。
- 正式卡片仍是 v58 H1-m0（R-012）。v60 切入拆欄（E-054）完成、19/19 過，未升正式卡，待使用者決定。
- 2026-27 賽中名單頁已部署 GitHub Pages（https://lanternko.github.io/basketball-autochess/，gh-pages 分支 80b948e，只含 index.html）：C4 S* 起點、數據截至 2026-10-27、N=1–4。產物在 `reports/ovr-inseason-2026-27/live/`（未 commit）。2026-10-28 修正（L-032）：2025-26 先驗卡缺 midA／shortA 讓近框、中距離被凍結，`run_c4_live.py` setup 改用同季出手分區補上（582/582），k、w、c 都沒動。修後 ΔOVR：≤−1 有 47 人、≥+1 有 14 人（修前 30／4）；Kessler −5.76→−2.45、Maxey −2.34→−1.39、Jerome −2.06→−0.92。中距離 4 場多半未達最低樣本門檻，仍是 x0。其餘已知問題：creation 映射重建中位差 3.4／最大 24、pass 最大 5.9；OVR 不含得分量與正負值（設計限制，C4R 已停，E-034）；罰球觀測值偏低已查明（2026-10-28）：視窗卡 `shooting()`（tools/ovr_common.py:84）先加 100 次「聯盟平均」虛擬出手再查曲線，C4 又再往 x0 收縮一次，等於雙重收縮且第一次拉向聯盟平均。Maxey 24/28 FT → 71.5（不加虛擬出手是 87.0）；全名單按 x0 分三組，高組 y−x0：ft −12.8、long −11.1、short −11.6，低組反而 +4～+10 → 好射手小樣本必降、差射手必升，是 ΔOVR 偏負的主因之一。回測（Y1..D3）也用同一函式，所以 C4 預註冊成績已含此偏差；已預註冊回測 E-062（以 x0 為中心 C4s／拿掉虛擬出手 C4r）：兩者都不採用，Y6 MAE 變差 0.3、C4s 合併差顯著為正；高組偏低大半是真實回歸平均。上線維持 C4，頁面不動。
- E-064 → 每場 OVR 已上線（R-028，2026-10-29，gh-pages 2870ddb）：卡片 card 0.2.0（`reports/card-0.2.0/`，替補水準基準 r_repl −2.015、錨點 −0.661／1.237／4.769），賽中 inseason 0.2.0a（`run_c4_live.py` E064_MODE 預設 G1，新增「預測MPG」欄；`off` 可逐位元重現 2026-10-27）。狀態板已改記 card 0.2.0（樣本內 ρ 0.814、2K27 0.695，和每 36 版不可直接比）。已 commit 47dcad0 並 push（分支 claude/project-thread-63h2fz，尚未合併 main）。待查：同截止日 2026-10-27 的賽中數據 sha256 與前次發布不同（子代理未查原因）；Dashboard artifact（Qk3xTJiB5iXHXgKXStEVCP）本帳號讀不到，沒更新。接戰場分鐘見 TODO.md（R-027）。
- 其餘基準不變：防守 `nba-defense-v3`（R-010）；賽中 OVR 上線 C4（E-033），v5 之後沒有 v6（R-009）。

## 誰在做
- 沒有在跑的派工。App（lead）等使用者決定 3PT 定義（拆「準度／投射威脅」兩欄或只留準度）與 card 0.1.1 何時發版。

## 未 commit 的改動
- memory/：README 版本號兩節、R-018、L-028、E-055／E-056 結果、本檔（77c4b0f 之後）。
- scripts/enrich_roster_viewer.py（移除球隊色點，來源不明）。
- TODO.md 未追蹤（3PT 第二階段模擬端、切入 B 階段、drive 共線調查）。

## 下一步
- 審 v61、v62；決定 v60／v61／v62 合併成一張候選卡再跑一次 evaluate 與審查板（L-021）。
- 之後（都等使用者）：切入 B＋3PT 模擬端併一次資料調查（tracking Drives／Possessions／Play type），C4 只重驗一次；C4 接進賽中卡片（F-010）。
- DeepSeek 餘額不足（402），auto_review 失效，等使用者儲值。

## 開放問題
- 3PT 屬性定義：命中能力（可預測）vs 投射威脅／承擔（直覺）；要不要像 drive 一樣拆兩欄（E-056）。
- `scripts/enrich_roster_viewer.py` 有未 commit 的改動（移除球隊色點），來源不明，待使用者確認。
- 卡片 OVR 要不要、怎麼接進對局（F-010）。
- v60 是否升正式卡。

## 2026-10-28 晚間更新
- 狀態板已切 card 0.1.2（0.1.1 + E-060 onBall）。E-063（模擬吃 E-060 onBall，原誤登 E-062）驗收不過，模擬維持 v53 onBall。
- R-024：E-057 threeValue 上線為 3PT 顯示欄（正式卡＋賽中），原 long 顯示為「3P準」，OVR 不變。賽中 inseason 0.1.1。
- 每日自動更新：`scripts/daily_inseason_update.py`（測試 `python -I test/daily_inseason_update.py`），排程 "Basketball Inseason Daily" 每天 14:30（主）＋16:30（補跑）pythonw；最後一場美東約 0:45–1:00 結束＝台北 EDT 12:45／EST 13:45，registry `basketball-inseason-daily`。狀態 `reports/ovr-inseason-2026-27/live/publish_state.json`，log `live/logs/daily.log`。首次發布 inseason 0.1.1a（gh-pages 1e53a79）已在線上確認。
- 注意：排程跑的是工作樹裡尚未 commit 的腳本（fetch_inseason_2026_27.js、build_inseason_viewer.py、daily_inseason_update.py 等），R-023 的「同 git HEAD 可重現」要等使用者同意 commit 後才成立。
- 2026-10-28 23:30：賽中先驗換成 card 0.1.2（inseason 0.1.2a，gh-pages 302b4a6），3P準 欄拿掉、新增 FD 製造犯規欄。drive 改 PBP 版、算不出本季值 → 凍結；foulDraw 用 FTA/FGA 百分位照 C4 更新（SGA ΔOVR −7.7 主要來自 foulDraw 96→82，未事後凍結）。f=0 檢查最大差 0.059；但 lastOVR 與 0.1.2 卡 ovr 有 2 人差 0.6–0.7（D.White、Caruso，pressure 高的防守者，原因未查），其餘 ≤0.4。見 L-034。
- 2026-10-29：網站加賽季切換（gh-pages a247ab8）：首頁＝2026-27 賽中，`2025-26.html`＝card 0.1.2 正式卡（`scripts/build_card_viewer.py`，共用 `scripts/season_nav.py`）；數值模式套等第色、3PT 副標「三分」、3P%/3PA 欄拿掉。每日發布一次提交兩檔。
- 未修：賽中 ΔOVR 對的是 lastOVR（White 98.3）不是正式卡 99.0，White 顯示 +0.55 實為 −0.1；要查 lastOVR 與正式卡差異原因，修好後 ΔOVR 改對 formalOVR。
- E-065 完成（2026-10-29）：WinImp（R-025 字面）V1 不過，ρ 0.41／0.35 輸卡片；事後用 fitA/fitB 卡仍輸。V2 字面過但無對照（L-036）。White 樣本外不高估；Kenrich 高估。輸出與 verdict_e065.py 未 commit。

## 2026-10-29 使用者抽查 McCain／收縮目標
- R-029：使用者把 McCain 排在 2026 雷霆第 8（Wallace 之後、Joe 之前）；card 0.2.0 是 57.9（#359），費城 37 場的 TS .506 對雷霆 30 場 .593，整季等權平均把他拉低。lead 用 box score 粗估雷霆段每 36 約 66，非正式卡。
- R-030：小樣本往聯盟平均收縮是高估，目標要依人而定（Topić 往 40、受傷 Giannis 往 80）。MIN<100 那組每 36 中位 65.8，高於 MIN 100–1000 各組（約 62.5）。
- TODO.md 新增兩題：「整季能力值依近期／交易後加權」「小樣本收縮目標依人而定」。已合併寫成 E-066 預註冊並凍結（`reports/card-0.2.0+E066-recency-target/preregistration.md`）：A 同季日期衰減 H＝∞／60／30 天；B 收縮目標改 MPG 分組平均（B1 本組、B2 一律 MPG<12 組）。尚未派工，等使用者看過預註冊；實作交 role-card。

## 2026-10-29 名單卡片影響力
- 使用者要求：卡片「前三強項＋弱項」改成影響力。`scripts/enrich_roster_viewer.py` 新增 `impactChips`：進攻／防守／淨影響＝2025-26 單季 box-prior RAPM（`reports/impact-rapm/rapm-prior.csv` lastSeasonO/D，每 100 回合），團隊在場＝`onoff.csv` 2025-26 在場淨效率（交易球員依 onPoss 加權，tooltip 附在場減不在場）。賽中頁也用 2025-26 值（2026-27 無 RAPM）。已發布（gh-pages 30942278）。
- 新增 deploy-shell：`python -I scripts/daily_inseason_update.py --shell`，只改頁面（UI／顯示）時用，沿用最後發布那天的 live 資料重建兩頁並發布，不抓資料、不跑 C4、版號與 dataSha256 不動。改公式會動到數字，仍走完整流程並改版號（G2）。網站顯示改動 push 後就跑它，不等每日排程。

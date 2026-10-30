# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫。歷史在 findings／experiments／rulings／lessons。

- **更新**：2026-10-29 18:40，Claude Code App（lead；分支 claude/project-thread-63h2fz，已 push 到 41cf2bd）

## 進行中的工作
- **名單頁 DIQ 欄已上線**（2026-10-30，R-080，220a8a6，gh-pages 5a29983 已在線上確認）：防守意識改成表格防守組 PRES 右邊一欄。未處理的使用者提問：TO（tovSkill，OVR 係數 +0.34／SD，偏袒低持球射手）要不要刪或照 R-032 改持球時間分母；INS 要不要拆近框（自己打到籃下）＋終結（命中率），要先查和 DRV 重疊。兩者都動 OVR，要另立實驗。
- **card 0.2.7a 已發**（2026-10-30，R-074、R-077）：card 0.2.7 + E-125 pass 量率各半，`reports/card-0.2.7a/`（= E-125 work/P50，sha256 04a9c266…165f）。名單頁 2025-26、OVR 傾向錨點、狀態板已改指 0.2.7a。Giannis pass 名次 10→25（值 97.7→96.2），OVR 前 20 只換 1 人（Knueppel 進、Ausar 出）。待辦：新 pass 只進 OVR，模擬沒重跑，要進模擬另立實驗；新賽季頁仍用 0.2.7 公式，要跟上另走 inseason（R-050）。
- 版本號改制（R-018）：正式卡片 = `card 0.1.0`；下列實驗都掛在它上面。
- v62 3PT 難度與出手量（E-056，`card 0.1.0+E056`）：完成（被 max_turns 截斷但報告齊全）。直覺驗收未過，等使用者決定 3PT 定義。
- E-057 三分價值（量為主、同量比準，R-020）：完成，`reports/card-0.1.1+E057-three-value/`。取代版 2K27 ρ 0.4956、Mobley 進前十，主驗收未過，不採用進 OVR；並列版 0.5175 但屬事後挑選（L-026）。待使用者選：threeValue 只當顯示用（PATCH），或另行預註冊並列版樣本外檢驗。2K27 三分參考（R-021，`reports/ref-2k27-3pt/`）：2K 前 100 名中對上 82 人，與 2K 三分的 Spearman 在現行 long 是 0.17，在 threeValue 是 0.49。2K 比 threeValue 更看重少量但很準的射手（Kennard、Durant、Cam Johnson），也比較看好高難度的持球射手（Brunson、Tatum、Markkanen）。
- E-058 onBall／help 縮水：完成、不採用（`reports/card-0.1.1+E058-defense-shrink/`）。對手三分命中差在測試季沒有任何方法贏過「人人聯盟平均」，onBall 現行算法基本是雜訊。下一步提案 E-059：onBall 改用干擾三分／36＋對位負擔＋被針對程度（defense-tenth step4-t2 的建議），已 GO 並完成（E-059）：預註冊驗收全過，2K27 ρ 0.5124（+0.0032，bootstrap 90% 區間含 0），Luka onBall 9→269；但 Wembanyama onBall 14→373（T 的位置組錯置：Wembanyama 列 F 卻守中鋒）。待使用者裁定：是否採用、算 PATCH 還是 MINOR、T 對長人要不要另行預註冊修正。使用者選「先修長人」→ E-060 已預註冊並派工（T 改成對手在他面前比平常多出手多少）。 E-060 完成、不採用：2K27 ρ 0.5181（區間下界 +0.0003），Luka 9→276，但長人仍掉到 340 名後（Wembanyama 344、Gobert 356、Embiid 368），原因是長人守長人時對手籃下出手本來就多。待使用者選：E-061 只在外線用 T（例如 T 只算 MATCHUP_FG3A，或長人改用護框指標），需重新預註冊。 使用者選 E-061（T 只算三分出手），已完成、不採用：2K27 ρ 0.5143（區間含 0，且比 E-060 差），長人仍在 326–369 名。三版 T 都讓長人掉，結論是外線單防指標不適用守禁區的人。待使用者裁定：(a) 長人的 onBall 改由護框／協防分量處理、onBall 只評外線（需新預註冊）；(b) 接受 E-060（OVR 前 20 長人名次幾乎不變，只是 onBall 屬性欄難看）；(c) 停止改 onBall。 → 使用者裁定採用 E-060（R-022：onBall＝外線單防，長人看 help）。card 0.1.2 候選 = 0.1.1 + E-060（PATCH），卡片 `reports/card-0.1.1+E060-onball-targeting/primary/ranking.csv`。尚未做：寫進 `scripts/build_season_league.js` 讓模擬吃新 onBall、status_snapshot 的 OFFICIAL_CARD 仍指 v58，等使用者說發版再切。
- v61（E-055）完成：19/19，低分鐘膨脹多數壓下，但 2K27 ρ 降 0.028、長人 15/16；等使用者抽查。
- lead 已抽驗：v61 ranking 雜湊與 long 欄一致；v62 雜湊未重跑。
- 下一版：`card 0.1.1` = 0.1.0 + E-054 + E-055（E-056 不含）。依 R-019 是 PATCH（2K27 ρ 沒變準），G1–G3 已在 v61 報告通過、前 20 名只換 1 人，不必重跑 G4；卡片就是 `reports/ovr-v61-shrink-history-2025-26/ranking.csv`。等使用者說發版再寫 R 條目定版。
- 正式卡片仍是 v58 H1-m0（R-012）。v60 切入拆欄（E-054）完成、19/19 過，未升正式卡，待使用者決定。
- 2026-27 賽中名單頁已部署 GitHub Pages（https://lanternko.github.io/basketball-autochess/，gh-pages 分支 80b948e，只含 index.html）：C4 S* 起點、數據截至 2026-10-27、N=1–4。產物在 `reports/ovr-inseason-2026-27/live/`（未 commit）。2026-10-28 修正（L-032）：2025-26 先驗卡缺 midA／shortA 讓近框、中距離被凍結，`run_c4_live.py` setup 改用同季出手分區補上（582/582），k、w、c 都沒動。修後 ΔOVR：≤−1 有 47 人、≥+1 有 14 人（修前 30／4）；Kessler −5.76→−2.45、Maxey −2.34→−1.39、Jerome −2.06→−0.92。中距離 4 場多半未達最低樣本門檻，仍是 x0。其餘已知問題：creation 映射重建中位差 3.4／最大 24、pass 最大 5.9；OVR 不含得分量與正負值（設計限制，C4R 已停，E-034）；罰球觀測值偏低已查明（2026-10-28）：視窗卡 `shooting()`（tools/ovr_common.py:84）先加 100 次「聯盟平均」虛擬出手再查曲線，C4 又再往 x0 收縮一次，等於雙重收縮且第一次拉向聯盟平均。Maxey 24/28 FT → 71.5（不加虛擬出手是 87.0）；全名單按 x0 分三組，高組 y−x0：ft −12.8、long −11.1、short −11.6，低組反而 +4～+10 → 好射手小樣本必降、差射手必升，是 ΔOVR 偏負的主因之一。回測（Y1..D3）也用同一函式，所以 C4 預註冊成績已含此偏差；已預註冊回測 E-062（以 x0 為中心 C4s／拿掉虛擬出手 C4r）：兩者都不採用，Y6 MAE 變差 0.3、C4s 合併差顯著為正；高組偏低大半是真實回歸平均。上線維持 C4，頁面不動。
- E-064 → 每場 OVR 已上線（R-028，2026-10-29，gh-pages 2870ddb）：卡片 card 0.2.0（`reports/card-0.2.0/`，替補水準基準 r_repl −2.015、錨點 −0.661／1.237／4.769），賽中 inseason 0.2.0a（`run_c4_live.py` E064_MODE 預設 G1，新增「預測MPG」欄，2026-10-29 名單頁已拿掉該欄（看不出作用）、ΔOVR 改五色分段（±1 灰、±1～4 淺綠／橘、≥±4 深綠／紅）；`off` 可逐位元重現 2026-10-27）。狀態板已改記 card 0.2.0（樣本內 ρ 0.814、2K27 0.695，和每 36 版不可直接比）。已 commit 47dcad0 並 push（分支 claude/project-thread-63h2fz，尚未合併 main）。待查：同截止日 2026-10-27 的賽中數據 sha256 與前次發布不同（子代理未查原因）；Dashboard artifact（Qk3xTJiB5iXHXgKXStEVCP）本帳號讀不到，沒更新。接戰場分鐘見 TODO.md（R-027）。
- **正式卡 card 0.2.3**（2026-10-29，R-040）= card 0.2.2 + E-075（用人當能力證據：分鐘、出賽率、年齡、練兵隊；DNP 與輪休分開，R-036）。`reports/card-0.2.3/`，已發布（網站 2025-26 頁、狀態板）。樣本內 rhoRapm 0.829→0.775、2K27 0.681→0.740。賽中先驗仍是 card 0.2.2（inseason 0.2.1b）。
- **賽中已跟上 card 0.2.4**（2026-10-29，E-091，inseason 0.2.2a，gh-pages b39f4a3／更新說明 a9681d6）：`run_c4_live.py` CARD_MODE 預設 024（022 逐位元重現 0.2.1e）；用人特徵凍結 2025-26（`live/usage-2025-26-card024.json`），MPG0＝mpgAvail，r_repl／錨點取 E-084。報告 `reports/ovr-inseason-2026-27/e089-card024/report.md`。程式改動已 commit（使用者 2026-10-29「Commit 並 push」）。同截止日 2026-10-28 重抓後資料 sha 變 31170cdc…（未查）。
- **新賽季已跟上 card 0.2.5**（2026-10-29，E-095 → R-052，**inseason 0.2.5a**，gh-pages 0e9836d，線上版本欄已確認 0.2.5a）：`run_c4_live.py` CARD_MODE 預設 025（飽和分鐘權重 W、card 0.2.5 先驗、E-089 錨點）；024 逐位元重現 0.2.4a（原名 0.2.2a）。E-095 的 (2) 沒過（回測 MAE 多 0.19–0.29，低分鐘組最多），使用者選 A，以和名單頁一致為優先。報告在 `reports/ovr-inseason-2026-27/e095-card025-minutes/`（report.md、audit/audit.md）。版號規則 R-050：新賽季＝先驗卡版號。L-053：沿用舊閘門時，預註冊要寫明基準是哪張卡。**程式與 memory 還沒 commit**（`run_c4_live.py`、`season_nav.py` 的 0.2.5 條目）。使用者以為正式卡已改 99 以上錨點：那是 E-090／E-080，還沒進正式卡。
- 前正式卡 card 0.2.2（2026-10-29，R-039）= card 0.2.0 + E-070 foulDraw 以量為主 + E-071 P1 pressure 改逼失誤。已發布（網站 2025-26 頁、狀態板）。PRES 欄改稱「壓迫」並加 tooltip。先前發布的 card 0.2.1 其實只含 E-071 P1（L-040，R-037 勘誤）。賽中已跟上：inseason 0.2.1（E-074，2026-10-29）先驗改用 card 0.2.2，`run_c4_live.py` CARD_MODE 預設 022、`020` 逐位元重現 0.2.0c；pressure 凍結、foulDraw 賽中改 E-070 公式（常數凍結在 prior JSON 的 foulDrawFreeze）。
- 其餘基準不變：防守 `nba-defense-v3`（R-010）；賽中 OVR 上線 C4（E-033），v5 之後沒有 v6（R-009）。

## 誰在做
- **目標「年輕球員偏低」**（2026-10-29 設，使用者「設置一個goal 。讓我們把這個任務（位置錯誤，跨季RAPM，新秀vs老將）完成」；lead 在 App 做）。三條都有結論才算完成：
  - A 位置標籤：查明來源、量化重標對 OVR 的影響（反事實診斷，不是採用）；影響大才寫修正預註冊。
  - B 跨季 RAPM：E-079 不採用；d=0.75 另寫凍結預註冊，等 2026-27 有足夠比賽才跑（之前不准看）。
  - C 新秀 vs 老將：card 0.2.3 用樣本外量尺（E-064 另一半）看殘差和年齡有沒有關係；有顯著偏差才寫修正預註冊，沒有就結案。
  - 進度（2026-10-29）：
    - A：F-033 查明標籤照官方先發秒數最多的位置，沒標錯。E-082 先發比例混合不採用：只 R3 沒過，0.7248 < 0.7469。對樣本外與三人幾乎沒影響，**A 結案：位置不是主因**。
    - B：E-083 凍結（d=0.75，等 2026-27 季末），目前無事可做。
    - C：E-081 判定年輕被低估（當季量尺 S −0.202）。E-084（用人回歸目標改成單季 RAPM）的機械判定只差 (c3)；使用者依機會成本裁定**通過（R-042）**。role-audit（Opus）重算成立（`reports/card-0.2.3+E084-current-target/audit/`）。G5 通過，**已發成 card 0.2.4（PATCH，R-044）**，狀態板與 2025-26 名單頁改指 0.2.4。退步項列為下一輪目標：四季量尺降、分鐘權重改成遞減（R-043；Caruso 型低分鐘高效率吃虧、Dyson 型上場時間撐起名次；曲線待使用者定）、老將（五位是當季 RAPM 真的低）、p_B 間接路徑、p 上限截斷、mpg-A／B 出賽數不一致。
    - 達成條件勘誤：lead 原本寫的「有顯著偏差才修、修正要全閘過」違反 R-040；改成「偏差修到、沒弄壞、利大於弊」即可（R-042、L-045）。
    - **收工狀態（2026-10-29 18:40）**：A、C 完成；B 只能等 2026-27 季末。這個目標的 App 對話已收工。2026-10-29 使用者選定飽和 1−e^(−m/15)、尺度 15（R-047）。E-089（`reports/card-0.2.4+E089-minutes-saturation/`，預註冊凍結 sha 0fa1b15c…2fbe）2026-10-29 在 App 原地跑完，**預註冊六條全過**：主量尺 Δρ_{N_W} +0.0096 [+0.0020, +0.0176]，線性量尺也小升；evaluate 16/19 → 18/19，Caruso 103 → 39 名。role-audit 重算成立，G5 通過（「還行 可以接受」），**使用者定為 card 0.2.5（PATCH，R-048，2026-10-29 20:00）**：`reports/card-0.2.5/`（ranking.csv 與 E-089 逐位元相同 73b1d635…050a，npm test 57/57），狀態板 OFFICIAL_CARD 與 2025-26 名單頁改指 0.2.5（本機已重產），season_nav 更新說明加 0.2.5。**已 commit d5d2afc 並 push（2026-10-29）**；gh-pages 2025-26 頁已是 0.2.5（版本 0.2.5、更新紀錄 0.2.5 標「目前」），20:03 正式 shell 部署回「內容未變」，因為別的 session 部署名單頁 UI 時已一併帶上。之後發版注意：`reports/` 被 gitignore 要 `git add -f`；共用工作目錄裡 `scripts/season_nav.py` 常混有別的 session 的改動，只挑自己的段落 commit。賽中先驗仍是 card 0.2.4（inseason 0.2.2a），跟上 W 另走 inseason 實驗。
- **E-107 防守 UL 搬到 card 0.2.6**（2026-10-30，接 E-106／R-061；與新賽季的 E-107 撞號）：預註冊凍結 sha256 344f860a…263c，已跑完，總評 2/5，`reports/card-0.2.6+E107-defense-UL/report.md`，未 commit。硬條件全過、m1–m3 小幅正向、r1' 過：Wemby #3 → #2、Wagner 維持 #7、Derrick White #8 → #4。副作用：evaluate 18/19（big14of16：Embiid #24、Koloko 加成歸 0）、Luka #4 → #9、頂端 OVR 壓縮（SGA 107.3 → 104.0）。**已發 card 0.2.7**（R-065，2026-10-30）：`reports/card-0.2.7/`，2025-26 名單頁、OVR 傾向錨點、狀態板都改指 0.2.7；沒做 role-audit。新賽季頁仍用 0.2.5，新賽季 E-107 要改對齊 0.2.7（R-050）。可再查：Embiid／Koloko 為何掉。另 R-063／R-064：每日賽中更新不再加字母；字母改給小版本（修 bug 或影響小的改動，影響大才升 PATCH，UL 屬影響大）。
- **E-096／E-097／E-101 卡片尾巴**（2026-10-29～30，lead 在 App 本機跑）：
  - E-096（99 以上改 150 上限、midValue／shortValue）判定全過、總評 3/5；已被 E-101 取代，不再抽查（R-060）。
  - E-097（聯盟先驗＋頂尖群 SD）判定全過但**不採用**（R-055）：尺做反了（L-057），中鋒中距離是 PBP 補籃標錯（F-042）。
  - **E-101**（2026-10-30，修 PBP 分區＋四季合併錨點＋差距尺）判定全過、總評 4/5，**已發成正式卡 card 0.2.6**（2026-10-30，R-060，PATCH）：`reports/card-0.2.6/`（ranking.csv 與 E-101 逐位元相同 a0a81ecb…6c91，npm test 57/57），2025-26 名單頁、狀態板、名單頁貢獻值 OVR 傾向錨點改指 0.2.6，已 commit、push、部署 gh-pages。新賽季先驗仍是 card 0.2.5（inseason 0.2.5a），跟上 0.2.6 要另走 inseason 實驗。中距離 99 並列 13→1、> 140 為 0、Giannis shortValue 129。副作用：射手 OVR 下滑（Curry 24→32），因 OVR 重擬後 mid／long 權重降、short 升。報告 `reports/card-0.2.5+E101-crossera/report.md`。
  - role-audit 重算成立（`audit/audit.md`），報告兩處基準錯誤已更正。使用者 2026-10-30 選「A 進 G5」，G5 名單 `g5/g5-list.json` 使用者「A」通過；前 20 名換 3 人，不必重跑 G4。
  - **待使用者**：新賽季要不要跟上 0.2.6；Curry 下滑可否接受；foulDraw／drive／onBall 改原始值（F-046）；補籃另開能力值（R-056）。
  - 檔案在 `reports/card-0.2.5+E096-tail150/`、`reports/card-0.2.5+E097-topscale/`、`reports/card-0.2.5+E101-crossera/`，E-096、E-097 沒 commit；E-101 主要檔案隨 card 0.2.6 commit（pool／history／變體能力值檔沒 commit）。
- E-079（2026-10-29）：RAPM 近期加權取代四季等權合併，**完成、不採用**：P 未過（d* 0.25，2025-26 Δ +0.229 [−1.344, +1.799]），沒做卡片層，card 0.2.3 不變；d=0.75 事後看會過，不作判準，要用需新預註冊＋沒看過的季（`reports/card-0.2.3+E079-recency-rapm/report.md`）。起因：使用者覺得 Banchero（#205）、Jalen Williams、Jalen Johnson 偏低；lead 診斷是模擬與合併 RAPM 都不看好、2K 看好，另疑合併 RAPM 偏袒老將。Jalen Williams 被標 PF（聯盟名單是 SG）另案未查。
- E-073：使用者接受為 card 0.3.0 候選（R-038）；role-audit 重算成立（2026-10-29，`reports/card-0.2.0+E073-usage-evidence/audit/`）。使用者選「等 0.2.2 再重跑」；0.2.2 已發布，E-075（`reports/card-0.2.2+E073-usage-evidence/`，預註冊 sha256 faec88da…bcd5）結果「語意版」：只有 c4 沒過（下界 −0.0002），R1 現在也成立（Sandfort 53.6 < Drummond 57.7）。使用者依機會成本接受（R-040）；role-audit 已派（App 內 sonnet 子代理），版號使用者定為 card 0.2.3；role-audit 重算成立（2026-10-29）；G5 通過（使用者「不錯」）；**card 0.2.3 已發布**（2026-10-29，gh-pages b053b26，`reports/card-0.2.3/` ranking.csv sha256 933797d8…；狀態板改 0.2.3）。賽中先驗仍是 card 0.2.2（inseason 0.2.1），要不要換另案。App（lead）等使用者決定 3PT 定義（拆「準度／投射威脅」兩欄或只留準度）與 card 0.1.1 何時發版。
- **E-116 新秀先驗卡（3/5，已上線 R-071）→ E-121 起點換 2K（已上線 R-073）**（2026-10-30）：daily 跑包裝程式 `live/run_c4_live_rookie.py`，2027 頁新秀標「新秀先驗」。E-116 起點頂順位被低估（F-060），使用者選 E-121 路線 D 簡化版：起點＝2K 近三屆同順位曲線換本站尺度再齊頭扣 5（第 1 順位 68、第 10 約 52、第 30 約 47），`reports/E121-rookie-scale/build_2k_start.py` 改寫 `live/rookie-prior-2026.json`（E-116 版備份 `rookie-prior-2026-e116.json`；之後若重跑 `build_rookie_prior.py` 要接著重跑 build_2k_start）。2025 屆回看 N=10 MAE 11.33 對 E-116 10.61（看過答案只報告）；準確度等 **2026-12-31 前瞻檢查**（prereg §3.4）。成長曲線 `reports/rookie-growth/`（F-063）。新秀防守 10-30 起賽中更新（使用者：一有數據就更新）：onBall／help 出賽後直接用當季追蹤值（w=1，`live/rookie_defense.py`，daily 加抓 `scripts/fetch_defense_tracking.mjs`）；老將 onBall／help 10-30 解凍（R-076：四季窗口逐場線性遞減、每人照實際季數正規化，`rookie_defense.veteran`），npm 57/0，已發布（commit 8f04fc1、gh-pages 2217dda）。defenseBonus 10-30 改成每天重擬合 E-104 D（窗口 [c, 328+c]，`live/defense_bonus.py`；daily 加跑 `scripts/build_inseason_stints.js`），c=0 和 def-L-primary 完全一致，npm 57/0，已發布；新秀沒有先驗卡，加成仍是 0。2027 頁新秀身高 0 已修（build_inseason_viewer 改讀 ranking.csv heightInches）。

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
- 臂展（F-031，E-077／E-078，使用者 2026-10-29 說「以後再深入」）：只有蓋帽在樣本外有額外資訊，不進 PHYS；抄截、防守嚇阻方向一致但太弱。深入時的候選做法（deflections、加檢定力、缺值補法）寫在 F-031。README.md:165 的 PHYS 公式說明過時（F-032）。

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
- E-066（近期加權＋小樣本收縮目標，R-029、R-030）已跑完並經 role-audit 重算：兩題都不過，卡片維持 card 0.2.0（`reports/card-0.2.0+E066-recency-target/report.md`、`audit/audit.md`）。McCain／Topić 的問題仍未解；B 方向（往同 MPG 組拉）在屬性回測上變差，下一步要從卡片層或別的機制處理。教訓見 L-037。

## 2026-10-29 名單卡片影響力
- 使用者要求：卡片「前三強項＋弱項」改成影響力。`scripts/enrich_roster_viewer.py` 新增 `impactChips`：進攻／防守／淨影響＝2025-26 單季 box-prior RAPM（`reports/impact-rapm/rapm-prior.csv` lastSeasonO/D，每 100 回合），團隊在場＝`onoff.csv` 2025-26 在場淨效率（交易球員依 onPoss 加權，tooltip 附在場減不在場）。賽中頁也用 2025-26 值（2026-27 無 RAPM）。已發布（gh-pages 30942278）。
- 新增 deploy-shell：`python -I scripts/daily_inseason_update.py --shell`，只改頁面（UI／顯示）時用，沿用最後發布那天的 live 資料重建兩頁並發布，不抓資料、不跑 C4、版號與 dataSha256 不動。改公式會動到數字，仍走完整流程並改版號（G2）。網站顯示改動 push 後就跑它，不等每日排程。
- 2026-10-29 每日完整發布曾停擺：E-080 未 commit 的 `CURVE_DEF_RIM = RIMD_SCURVE ? [...] : [...]` 讓 `ovr_common.py` 解析失敗（L-048）。41cf2bd 讓解析器照 JS 規則讀旗標（關閉取後一組，與 HEAD 及 node 載入值逐位元相同），已發 inseason 0.2.1e（數據至 2026-10-28，gh-pages 52bd2eb），排程恢復正常。另：共用 checkout 時 commit 一律帶路徑（L-047；a8440d1 混入 card 0.2.4 的 memory 改動）。
- 2026-10-29 新增收工提醒 Stop hook（腳本已 commit；設定檔 `.claude/settings.local.json` 只在本機）：`.claude/hooks/handoff_reminder.py`，註冊在本機 `.claude/settings.local.json`（pythonw 絕對路徑，只在這台機器生效）。session 改了 memory/ 以外的 repo 檔、跑了 scripts／reports 腳本或派工，之後沒更新 handoff.md 時，在工作告一段落的回合（App 是有 wrap_up 的回合）提醒一次；同一份工作不重複提醒，派工子 session 不檢查。
- E-067 長人偏袒量尺凍結並跑基準線（2026-10-29）：卡片（fit 卡）沒有偏袒；模擬 WinImp 主版、位置版都偏袒長人（S +82～95／+38～50），位置版還低估 PG。下一步轉回模擬引擎，驗收照 E-067 §3（b1–b3）。
- Hauser HDL 99：HDL 是 tovSkill（TOV/(FGA+.44FTA+AST+TOV)），在模擬裡是每次觸球的失誤率；v41 驗證中他的模擬 TOV/36 是 0.89，實際 0.65，模擬已經高估他的失誤，所以數值不用改。問題在顯示名稱「護球」，建議改名，待使用者決定。

- E-071 壓迫（2026-10-29，`reports/card-0.2.0+E071-pressure/`）：P1 過 G1–G4、audit 獨立重算逐位元相同（含勘誤 1：k=σ₁²/τ²，使用者核可，L-039）。只是不變差、不是變準；Diabaté PRES 99→61.4、OVR 84.2→79.2。已採用並併入 card 0.2.2（R-039）。（E-069 撞號已處理：fringe-repl 改為 E-072。）
- 2026-10-29 E-069 第一階段完成：handle（R-032）h1、h2、h3 都過，對 2K27 Ball Handle ρ 0.74。passSec 對 2K Pass Accuracy ρ −0.47（Luka 40、Hauser 99），只當模擬的傳球風險用。下一步：使用者看過名單後，派第二階段（模擬失誤拆分，m3 在 5090 跑）。
- 2026-10-29 E-072（原 E-069 fringe-repl，`reports/card-0.2.0+E069-fringe-repl/`）不通過：(c3) 18→16/19、(R1) Sandfort 59.6 > Sheppard 39.6、(R2) 邊緣池中位數 59.4 > 53.0。r_new −1.03 比舊 r_repl −2.01 高；模型本身把健康 DNP 的人估在池內約 PR27，收縮不是主因。下一步等使用者裁定：分鐘／DNP 當直接證據（含 R-035 年齡例外）需新預註冊。DeepSeek 餘額不足（auto-review 402）。
- 2026-10-29 E-073 預註冊凍結（`reports/card-0.2.0+E073-usage-evidence/`，sha256 db42fc16…，派工前加 (R4) 低分鐘組 PR90 < 高分鐘替補中位數後重凍）：用人（分鐘、出賽率、年齡、練兵隊）當能力證據的交叉擬合回歸；DNP 與輪休分開（R-036）。已派（App 內 sonnet 子代理，dispatch 路由 self：main 帳號 7 天 98%、worker 已 2 任務、DeepSeek 402）。lead 已核對：McCain 低分是 pred PR26＋MPG 17.3，RAPM 整季 +0.08、半季 −0.23／+0.14，雷霆段在場 +4.2 但在場減不在場 −7.7，E-073 預期只部分改善；季後賽分鐘沒進資料，要另開題。R-034 撞號已處理：分鐘正相關改為 R-035（L-038）。
- 2026-10-29 E-073 結果：不通過，只有 (R1) 沒過（Sandfort 54.4 > Sheppard 52.2；Drummond 57.3）。(c4) 過，代表用人資訊在樣本外確實有預測力。(R2)(R3)(R4) 都過。等使用者裁定；尚未經 role-audit。
- 2026-10-29 E-069 第二階段：m2 不過（tov36 MAE 0.167→0.320，低創造依賴組從低估翻成高估），模擬不變，src 已還原（patch 在 sim/）。m3 因 5090 VPN 斷線未完成，只當資訊。下一步若再試：失誤 hazard 不要直接乘持球秒數（例如改成每次觸球的基準機率加上 handle 調整），要寫新預註冊。
- 2026-10-29 E-069 m3 補完：主版更偏袒長人（S +106／+118），位置版翻成偏袒後衛（S −51／−38），兩版 ρ 都降。失誤拆分整體不採用。報告在 reports/handle-E069/sim/report.md。
- handle 線收尾（2026-10-29，R-046）：E-087 停在 p0（活鏈不呼叫 handlingWeights，L-046）；分球診斷 H8 排除；失誤已是實測兩段，handle 模擬端擱置，只留卡片屬性。未 commit。

## 2026-10-30 名單卡片近 5 場與貢獻值
- 手機版近 5 場：正負值格切 60° 缺角放正三角形 ▼，展開變金色不翻轉；表格只從數值格啟動內部捲動；平均列的投籃／三分／罰球顯示合計命中率。都已發布。
- E-105 單場貢獻值已上線：近 5 場表多「貢獻」欄（box score 換算每 36 分鐘淨影響，權重擬合 2025-26 RAPM A 半，B 半樣本外 r 0.44），數字寫絕對值，顏色和自己 2025-26 平均比、五色五等分（使用者 2026-10-30 裁定：同樣 +3 替補是進步、SGA 是退步）。切點＝2025-26 全部比賽差值絕對值的 20／60 百分位：單場 ±0.7／±2.4、近 5 場 ±0.3／±1.1（分布圖 `reports/game-contribution/gc-delta-dist.png`）；**顯示名稱改「評分」、0 起跳（R-062）**：評分＝0.75×(貢獻值＋7.5)，低於 0 記 0（單場約 1% 到 0、約 4% 超過 10，聯盟平均 ≈5.6；整季平均擠在 5.2–6.6，最高 SGA／Jokić 8.3）。表下只寫「N 場平均評分 X　上季 Y」，切點與換算 OVR 放 tooltip；2026 頁下拉改「整季細項」（場均／每 36、進球-出手、前後場籃板、犯規、整季評分），2027 頁仍是近 5 場；貢獻欄放勝負後面、分鐘移到最右。A+／99 存在 localStorage `bbac.mode`（兩個賽季頁共用）；手機寬度 A+／99 由 `season_nav.py` 搬到更新說明旁靠右。顏色是排名不是顯著。只顯示，不進 OVR。要重擬權重跑 `python -I scripts/fit_game_contribution.py`（`reports/game-contribution/`，要 `git add -f`）。 **E-110（草稿，等使用者核可凍結）**：評分加 hustle＋防守對位，預註冊 `reports/E110-defensive-rating/preregistration.md`；已實測 stats.nba.com `boxscorematchupsv3`／`boxscorehustlev2` 一場 1 秒可抓。凍結後派 role-card 補抓 2025-26（約 2460 次請求、本機）再擬合。

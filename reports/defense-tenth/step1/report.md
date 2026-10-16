# 第十批第一步：向性稽核

第一步完成，停止於量測。沒有修改既有程式、凍結版本或保存的能力卡，沒有下載資料。第二步誤差拆解、第三步跨季設計尚未執行。

**結論：引擎能對陣容組合與若干向性缺口作出反應，但凍結 v3 的主要護框與防守籃板能力路徑被區段防守訊號取代；它不符合這一批的新「純球員卡」定義。四個向性欄位全部為 70，也讓有機制的部分無法區分真實球員。** 以下測試驗證程式反應，不驗證 NBA 預測準確度。

## 1. 訊號來源與機制

區段估計同時放進攻、防守五人，對區段結果作正則化估計；[scripts/estimate_defense_third.py:25](D:/Projects/CODING/basketball-autochess/scripts/estimate_defense_third.py:25)、[scripts/estimate_defense_third.py:109](D:/Projects/CODING/basketball-autochess/scripts/estimate_defense_third.py:109)。資料 bundle 把 engine-signals 轉成 defenseSignals，[scripts/build_defense_seventh_bundle.js:21](D:/Projects/CODING/basketball-autochess/scripts/build_defense_seventh_bundle.js:21)；實際執行傳入這個 side channel，[src/defense_seventh_jobs.js:7](D:/Projects/CODING/basketball-autochess/src/defense_seventh_jobs.js:7)。它不是直接球隊 ID 補丁，卻使用了使用者此次排除的球員在場時球隊結果。

| 向性 | 判定（凍結 v3） | 陣容機制與弱點 | 程式位置 |
|---|---|---|---|
| 護框不足 | 有機制，但主要球員卡路徑被覆蓋 | 原本協防取前兩名 .6/.4，再加體格、空間稅；v3 主禁區命中率由中性防守加區段 shortFG 訊號取代。中距離、補籃仍可能受 help 影響。阻攻只是把既有投失分類，不再降低命中率。 | [src/probability_model.js:201](D:/Projects/CODING/basketball-autochess/src/probability_model.js:201)；[src/probability_model.js:276](D:/Projects/CODING/basketball-autochess/src/probability_model.js:276)；[src/defense_fourth_effects.js:14](D:/Projects/CODING/basketball-autochess/src/defense_fourth_effects.js:14)；[src/rebound_block_model.js:86](D:/Projects/CODING/basketball-autochess/src/rebound_block_model.js:86) |
| 外線防守不足 | 有機制 | 同槽位對位者 onBall 改三分／中距離命中率；原出手封鎖受到 zoneSignal 中性化與區段出手訊號取代。沒有先過掉外防、再迫使輪轉補位的空間事件鏈，也沒有按對手弱點動態換對位。 | [src/defense_fourth_game.js:266](D:/Projects/CODING/basketball-autochess/src/defense_fourth_game.js:266)；[src/probability_model.js:280](D:/Projects/CODING/basketball-autochess/src/probability_model.js:280)；[src/defense_fourth_effects.js:17](D:/Projects/CODING/basketball-autochess/src/defense_fourth_effects.js:17) |
| 空間／三分威脅 | 有機制，部分很弱 | 其他四人的射程平均、最高 gravity、前兩名創造力與傳球共同影響空間與禁區機會；v3 contextLongScale=0，三分直接隊友情境加成關閉，contextShortScale=.5。出手傾向來自個人 threeRate，但二分的禁區／中距離先驗比例全聯盟共用。 | [src/probability_model.js:53](D:/Projects/CODING/basketball-autochess/src/probability_model.js:53)；[src/probability_model.js:123](D:/Projects/CODING/basketball-autochess/src/probability_model.js:123)；[src/probability_model.js:354](D:/Projects/CODING/basketball-autochess/src/probability_model.js:354)；[src/probability_model.js:369](D:/Projects/CODING/basketball-autochess/src/probability_model.js:369)；[src/defense_probability.js:27](D:/Projects/CODING/basketball-autochess/src/defense_probability.js:27) |
| 控球與傳導 | 傳導有機制；控球配置很弱 | pass 前兩名 .8/.2、creation 前兩名 .75/.25，影響傳球成功與出手機會；tovSkill 改持球失誤。v3 按過去每分鐘球權量選控球者、按 FGA/min 選接球者，繞過 handlingWeights 與 receiverWeights。handle 仍小幅影響自主出手命中，但無獨立的 handle→持球失誤機制。 | [src/probability_model.js:53](D:/Projects/CODING/basketball-autochess/src/probability_model.js:53)；[src/probability_model.js:297](D:/Projects/CODING/basketball-autochess/src/probability_model.js:297)；[src/probability_model.js:450](D:/Projects/CODING/basketball-autochess/src/probability_model.js:450)；[src/defense_fourth_game.js:243](D:/Projects/CODING/basketball-autochess/src/defense_fourth_game.js:243)；[src/defense_fourth_game.js:288](D:/Projects/CODING/basketball-autochess/src/defense_fourth_game.js:288)；[src/defense_probability.js:46](D:/Projects/CODING/basketball-autochess/src/defense_probability.js:46) |
| 籃板 | 有機制；防守能力路徑被覆蓋 | 位置、投籃區域落點、衝搶率、籃板與體格共同形成非線性競爭；v3 中性化防守方 rebound/physique，再用區段 DREB 訊號取代。進攻籃板與個人歸屬仍有反應。 | [src/rebound_block_model.js:5](D:/Projects/CODING/basketball-autochess/src/rebound_block_model.js:5)；[src/rebound_block_model.js:41](D:/Projects/CODING/basketball-autochess/src/rebound_block_model.js:41)；[src/rebound_block_model.js:59](D:/Projects/CODING/basketball-autochess/src/rebound_block_model.js:59)；[src/defense_fourth_game.js:187](D:/Projects/CODING/basketball-autochess/src/defense_fourth_game.js:187) |

這五類不能全部簡化成「有／無」：原始機制存在、卡的觀測缺失、以及 v3 訊號覆蓋是三種不同問題。

## 2. 方法與登記

- 用 2025–26、日曆 K41 的有效 v3 卡，截止日 2026-01-16；582 名去重球員。真實卡極端選擇池為截止前至少 300 分鐘的 322 人。
- 聯盟平均隊為截止前分鐘加權的五名平均卡，PG/SG/SF/PF/C 各一名；不強迫其模擬效率等於真實聯盟平均。
- 14 組陣容 × 2 種訊號模式 × 每格 2,000 場 = 56,000 場。種子 202610120–202612119，共用種子、交替隊伍順序，4 worker，完成耗時 376.84 秒。
- 為隔離向性，固定五人，關閉疲勞與換人、犯滿門檻 99、不打延長；保留終場策略。因此「v3 訊號開啟」指原訊號路徑，不是正常輪替完整賽季回測。
- 合成卡只是記憶體中的平均卡複本。除明列 threeRate=0 的組別，過去球權量、抄截率、罰球傾向等保持相同；故屬性與觀測量刻意不一致，是壓力測試，不能當真實新球員建卡方式。
- 合成 ID 的區段訊號設為聯盟中心，效應恰為 0，避免缺 ID 被當 0 再減中心的假效應；真實卡保留各自訊號。
- 主效率為實際引擎球權：100×總得分／總球權；失誤率為 TOV／球權。出手分布是有記錄 FGA 的比例，「禁區」含限制區與其他 paint 二分，不只籃框 6 呎。歷史 FGA−OREB+TOV+.44FTA 代理另存 summary.json，不混用。
- 區間為 2,000 個共同 seed 的成對 Monte Carlo delta-method 95%；它不包含真實球隊抽樣，不能拿來宣稱跨季改善。全體已看過答案的 2025–26 資料僅供這次機制診斷。

登記時間：2026-10-13T02:23:07.540Z；SHA-256：

`61c9d7c275d4a96bd547162309ea87f66245c25cc5a51660d6dcb46b5267cda3`

## 3. 合成測試

### v3 原訊號開啟（固定輪替量測）

| 陣容 | ORtg | DRtg↓ | TOV% | 自己禁區／三分% | 對手禁區／三分% | 淨效率差 vs 互補（95%） |
|---|---:|---:|---:|---|---|---|
| 五名平均卡 | 110.35 | 110.68 | 14.16 | 47.87／38.59 | 47.92／38.47 | -7.35 [-8.33, -6.36] |
| 向性互補，同各屬性總和 | 117.92 | 110.90 | 14.13 | 57.10／32.32 | 47.63／39.29 | 0.00 [0.00, 0.00] |
| 能力集中，同各屬性值的多重集合 | 115.20 | 110.59 | 13.45 | 58.23／31.49 | 47.76／39.09 | -2.41 [-3.31, -1.50] |
| 五人外防P95，護框help=0 | 110.48 | 109.01 | 14.12 | 47.89／38.55 | 49.53／35.58 | -5.55 [-6.49, -4.60] |
| 五人護框P95，外防onBall=0 | 111.08 | 124.74 | 14.25 | 47.80／38.63 | 41.59／45.54 | -20.68 [-21.68, -19.68] |
| 五人三分long=0，保留出手傾向 | 98.09 | 109.97 | 15.85 | 54.20／23.82 | 47.90／38.47 | -18.90 [-19.86, -17.93] |
| 五人long=0且threeRate=0 | 103.42 | 110.29 | 15.00 | 70.19／0.47 | 48.02／38.32 | -13.88 [-14.83, -12.93] |
| 五人handle/pass/tovSkill=0 | 90.11 | 110.20 | 27.17 | 31.80／48.28 | 48.16／38.34 | -27.11 [-28.08, -26.14] |
| 只將五人handle設0 | 109.55 | 110.76 | 14.24 | 47.88／38.54 | 47.94／38.42 | -8.22 [-9.20, -7.25] |
| 只將五人rebound設0 | 103.22 | 110.29 | 13.56 | 46.64／39.49 | 47.96／38.44 | -14.08 [-15.06, -13.09] |

### 同卡、關閉五組區段訊號

| 陣容 | ORtg | DRtg↓ | TOV% | 自己禁區／三分% | 對手禁區／三分% | 淨效率差 vs 互補（95%） |
|---|---:|---:|---:|---|---|---|
| 五名平均卡 | 110.21 | 110.20 | 14.16 | 47.89／38.36 | 47.85／38.32 | -11.31 [-12.28, -10.33] |
| 向性互補，同各屬性總和 | 117.85 | 106.53 | 14.20 | 57.01／32.37 | 36.47／48.27 | 0.00 [0.00, 0.00] |
| 能力集中，同各屬性值的多重集合 | 115.01 | 107.12 | 13.44 | 58.31／31.34 | 36.67／48.03 | -3.42 [-4.32, -2.53] |
| 五人外防P95，護框help=0 | 110.01 | 134.23 | 14.28 | 47.71／38.53 | 86.07／8.89 | -35.54 [-36.54, -34.53] |
| 五人護框P95，外防onBall=0 | 110.55 | 134.03 | 14.22 | 47.73／38.50 | 13.90／79.91 | -34.80 [-35.84, -33.76] |
| 五人三分long=0，保留出手傾向 | 97.96 | 109.45 | 15.89 | 54.02／23.71 | 47.96／38.27 | -22.81 [-23.80, -21.82] |
| 五人long=0且threeRate=0 | 103.00 | 109.71 | 14.99 | 69.78／0.50 | 48.11／38.05 | -18.03 [-18.99, -17.06] |
| 五人handle/pass/tovSkill=0 | 89.69 | 109.80 | 27.09 | 31.86／47.95 | 48.13／38.14 | -31.43 [-32.45, -30.41] |
| 只將五人handle設0 | 108.97 | 110.82 | 14.32 | 47.82／38.38 | 47.89／38.35 | -13.17 [-14.15, -12.19] |
| 只將五人rebound設0 | 103.03 | 123.89 | 13.47 | 46.48／39.41 | 50.18／36.63 | -32.18 [-33.18, -31.17] |

這是既有 rim/rebound/live/zone/foul 五個開關全部關閉的診斷，不是另立新基準。

## 4. 有反應與被覆蓋的地方

**護框缺口被覆蓋。** 外防 P95、help=0 的 DRtg：訊號開啟 109.01，關閉 134.23。各自對平均卡的 DRtg 差為 −1.67 [−2.25,−1.09]、+24.03 [23.39,24.67]。這個組別同時增強外防與削弱護框，所以不將整體效率差歸因於單一參數；固定機率探針與原始碼才證明主護框路徑覆蓋：訊號開啟時平均、help=0、護框 P95 三組的對手禁區自主投籃命中機率完全相同，都是 .5215886208。關閉後分別 .5199679920／.6884845884／.4652949186。

**外線弱點有反應。** 護框 P95、onBall=0 在訊號關閉時，對手 79.91% 的出手是三分，禁區僅 13.90%；無護框組對手則 86.07% 禁區、8.89% 三分。引擎確實會依防守缺口改出手分布，但幅度是否合理尚未驗證。

**無三分有代價，但不是完全禁投。** long=0 保留原三分傾向，ORtg 97.96；再把 threeRate=0，ORtg 103.00、三分比 0.50%。前者仍投 23.71% 三分。零能力仍有最低命中機率，[src/constants.js:463](D:/Projects/CODING/basketball-autochess/src/constants.js:463)；後者仍有約 0.5% 三分，是終場落後強制選三分，[src/defense_fourth_game.js:340](D:/Projects/CODING/basketball-autochess/src/defense_fourth_game.js:340)。完全不投三分改善約 5 分是避免低效率出手，不能據此宣稱空間價值不合理。

**傳球／保護球很重要，handle 本身很弱。** 三項歸零使純卡模式 ORtg 110.21→89.69，TOV% 14.16→27.09；對平均卡的失誤率差 +12.93pp [12.70,13.16]。僅 handle=0：ORtg 降 1.24 [−1.81,−0.67]，失誤率 +0.16pp [−0.01,+0.33]。因此不能說控球完全無反應，但其控球者配置與持球失誤機制未使用 handle 來表達。

**防守籃板卡的數值被覆蓋，但進攻籃板仍響應。** 五人的 rebound=0 時，v3 個人籃板口徑 DRB% 74.21→74.34，差 +0.13pp [−0.19,+0.45]；關訊號後 74.58→50.49，差 −24.09pp [−24.46,−23.72]。開訊號仍有 ORtg 下降 7.13，不能說整個籃板向性無反應。團隊籃板不計入此個人 DRB% 分母，另存計數。

**相同總和仍有組合效應。** 互補與集中陣容每一屬性的多重集合完全相同；對平均卡也各欄位總和相同（最大誤差 0）。關訊號後，集中相對互補 ORtg −2.84 [−3.44,−2.24]，DRtg +0.59 [−0.05,+1.22]，淨效率 −3.42。這驗證非加總模型存在，不代表已驗證真實化學效應：個人屬性聯合配置、位置配對、top-2／max 與非線性曲線同時改變，不能把全部差值歸為單一戰術互補。也未聲稱相同非線性 OVR。

## 5. 不改真實球員屬性的五人組

下列是卡內的相對排名，不是實際 NBA 防守頂尖或真的不會控球的判定。

- 真實卡：低護框池內外防前五：Jericho Sims、Ben Sheppard、Brandon Williams、Aaron Holiday、Naji Marshall。
- 真實卡：低外防池內護框前五：Alex Sarr、Neemias Queta、Nic Claxton、Robert Williams III、Donovan Clingan。
- 真實卡：三分能力最低五名：Ja Morant、Brandon Williams、Dyson Daniels、Amen Thompson、Tristan Vukcevic。
- 真實卡：傳球/保護球/突破平均最低五名：Baylor Scheierman、Nicolas Batum、Gary Harris、Deandre Ayton、Nique Clifford。

| 陣容 | ORtg | DRtg↓ | TOV% | 自己禁區／三分% | 對手禁區／三分% | 淨效率差 vs 互補（95%） |
|---|---:|---:|---:|---|---|---|
| 真實卡：低護框池內外防前五 | 111.31 | 116.70 | 14.15 | 52.18／36.24 | 52.82／33.77 | -12.41 [-13.38, -11.44] |
| 真實卡：低外防池內護框前五 | 136.94 | 93.37 | 12.60 | 79.32／8.29 | 25.32／54.05 | 36.55 [35.59, 37.52] |
| 真實卡：三分能力最低五名 | 106.77 | 112.21 | 17.77 | 70.21／13.72 | 53.38／33.49 | -12.45 [-13.39, -11.51] |
| 真實卡：傳球/保護球/突破平均最低五名 | 105.61 | 110.28 | 19.69 | 36.28／50.62 | 46.28／39.31 | -11.68 [-12.66, -10.70] |

| 陣容 | ORtg | DRtg↓ | TOV% | 自己禁區／三分% | 對手禁區／三分% | 淨效率差 vs 互補（95%） |
|---|---:|---:|---:|---|---|---|
| 真實卡：低護框池內外防前五 | 111.33 | 113.46 | 14.20 | 52.20／36.14 | 59.18／27.84 | -13.44 [-14.44, -12.44] |
| 真實卡：低外防池內護框前五 | 136.38 | 101.35 | 12.71 | 79.16／8.38 | 24.11／59.01 | 23.72 [22.75, 24.68] |
| 真實卡：三分能力最低五名 | 106.93 | 109.83 | 17.62 | 70.27／13.58 | 49.16／37.36 | -14.21 [-15.18, -13.24] |
| 真實卡：傳球/保護球/突破平均最低五名 | 105.44 | 107.86 | 19.73 | 36.24／50.34 | 39.26／46.17 | -13.74 [-14.73, -12.74] |

真實卡最低三分組五人的 long 都為 30.373（有效卡的下界附近），不是 0；低控球組仍全員 handle=70，是按 pass/tovSkill/drive 選的代理組。真實護框組 ORtg 高至 136.38，與其他卡屬性、極端位置與觀測量一起作用；此壓力測試不能用來證明這五人能在 NBA 達到該效率，也不能將其與合成組的差距當作防守訊號品質驗收。

## 6. 完全沒反應、沒有機制、資料未提供的區別

已驗證的**主路徑無反應**：v3 的 help 對主要禁區 make；rebound/physique 對防守籃板成功的舊技能路徑。程式以中性值取代它們。其他路徑仍可反應，所以不是整場完全不變。

**沒有明確機制**：實際突破過人→護框者補位→外圍輪轉的事件鏈；動態防守對位；獨立 handle 對失誤 hazard 的映射。當前是聚合機率與同槽位對位。

**有機制但資料不提供差異**：582 人的 handle/offBall/screen/breakDbl 全為 70，來源 [scripts/build_season_league.js:72](D:/Projects/CODING/basketball-autochess/scripts/build_season_league.js:72)。沒有辦法用這些卡區分自主控球、無球切入、掩護與抗包夾。

**較弱／繞過的路徑**：v3 使用觀測球權量配置控球與接球；三分直接隊友情境加成關閉；五人防守訊號只取算術平均，[src/defense_fourth_effects.js:7](D:/Projects/CODING/basketball-autochess/src/defense_fourth_effects.js:7)，本身沒有 top-2 或角色互補，且來自區段結果。

推測（尚未驗證準確度）：如果改用純球員卡預測重組名單，固定歷史球權量、缺失的四項向性與兩分區域個人傾向，可能使模型無法合理重新分配角色。這次不能判定哪個是四季預測誤差的主要來源，也不提出已量化的準確度增益。

## 7. 執行稽核、限制與重跑

- 完整 28 格，每格 2,000 場；56,000 場數值全部有限。
- protocol 雜湊與結果一致；所有登記的既有 src/scripts/test 程式、package.json、凍結檔與輸入卡指紋無變動。工作區原有修改不屬於本次修改；沒有回退它們。
- 首次 worker 啟動因 parent 的 --input-type=module 使 CommonJS eval 的 require 不可用而失敗，未產生比賽結果；僅修正記憶體量測 harness 的 execArgv:[] 後完成。沒有更改引擎或重新選擇測試規則。
- 完整重跑指令見 [execution-command.md](D:/Projects/CODING/basketball-autochess/reports/defense-tenth/step1/execution-command.md)。命令只寫報告；既有 results.json 會拒絕覆寫，重跑使用新的輸出目錄並保留原結果。
- [protocol.json](D:/Projects/CODING/basketball-autochess/reports/defense-tenth/step1/protocol.json) 保存全套卡、控制、來源 SHA；[summary.json](D:/Projects/CODING/basketball-autochess/reports/defense-tenth/step1/summary.json) 保存全部指標、標準誤與成對區間；[probability-probes.json](D:/Projects/CODING/basketball-autochess/reports/defense-tenth/step1/probability-probes.json) 保存確定性探針。

本步只回答「引擎有沒有反應向性」。沒有修正、沒有跨季準確度結論；後續誤差拆解與跨季方案留待下一步。

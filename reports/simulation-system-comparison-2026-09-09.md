# Hoop Land、Basketball GM 與本專案模擬系統比較

日期：2026-09-09。這是實作與資料結構比較，不是三者 NBA 預測準確度排名。沒有執行新的完整球季，沒有修改 Hoop Land 存檔。

## 本機 Hoop Land 證據

- 已安裝於 `D:/SteamLibrary/steamapps/common/Hoop Land`；Steam manifest buildid 為 24356323。
- Save Slot 01 的 `PRO_LEAGUE_SAVE_FILE` 可直接以 JSON 解析；meta.buildVersion 為 1.09.76。
- 存檔是 Hoop League (default)，30 隊虛構球員，season.totalGames=29、currentDay=4；不是 2025–26 NBA 82 場資料。
- 本次讀取時有 60 個 Pro box scores，皆 inProgress=false，皆有非空 playByPlay。不能僅憑檔案判斷每場是快模、觀看或手動遊玩。
- 球員分開保存 attributes、skills、tendencies、minutes、usage、gameStatus、gameStats、stats。傾向含 pass、lob、cross、spin、step、runPlay、offReb、defReb、stealOnBall、stealOffBall、block 等。
- attributes 包含 LAY/DNK/INS/MID/TPT/FTS/DRB/PAS/ORE/DRE/STL/BLK/STR/SPD/STM。數值是陣列，未確認內部編碼，不能直接當 UI 的 0–10 分。
- 保存 sliders 與 simulationSliders 兩組；本次 simulationSliders 各欄皆 50，simulationPace=0。
- coachSettings 包含 substitutions、timeouts、lateGameFouling、offensivePlayCalling、defensivePlayCalling。欄位存在不代表已驗證其演算法品質。
- playByPlay 保存 time、period、score、球隊與球員索引、play enum、shotData。抽樣事件部分 score=[0,0]，故不能直接把每列 score 都當有效比分。shotData 有位置欄位也不等於完整十人軌跡。
- gameLength、totalPeriods 等設定值存在編碼，未解碼前不直接翻譯成分鐘或節數。

## 比較

| 面向 | Hoop Land | Basketball GM | 本專案目前 |
|---|---|---|---|
| 核心形態 | 官方確認場上與快模雙引擎；公式未公開 | 事件與機率推進比賽時鐘 | 固定回合或搶分制的傳球／投籃機率循環 |
| 傳球決策 | 有傳球、空接、戰術執行等傾向，詳細權重未知 | 依 usage 選出手者，再抽是否助攻及傳球者 | 持球者比較出手品質，再抽出手、傳球窗口、攔截與接球者；可連傳 |
| 空間 | 場上有角色與球運動；快模是否使用幾何尚未知 | 所讀核心沒有十人連續座標模擬 | 無球／掩護／協防是能力修正；呈現層事後產生位置 |
| 時間 | 有比賽時間與事件時間戳；快模另有 pace | 節末、耗時、進攻時間與末段節奏 | 依回合數停止；UI 剩餘時間是動畫播放時間 |
| 球員輸入 | 能力＋技能＋獨立動作傾向 | 基礎能力合成 usage、傳球、防守、籃板等 | NBA 統計映射的 16 欄，部分手填；另有可選同季出手傾向 |
| 防守 | 有 matchup、pressure、doubleTeam 狀態及防守傾向，公式未知 | 團隊合成防守與個人事件權重 | 主要同索引對位＋團隊協防；不是即時換防／補位 |
| 疲勞輪替 | 有體力狀態、先發替補與自動換人設定 | 能量、休息、犯規麻煩、傷病及垃圾時間輪替 | 按累積回合削弱近中遠投與切入；固定五人、無替補休息 |
| 犯規 | 有規則設定、PF、罰球事件 | 非投籃犯規、bonus、and-one、三罰、罰球籃板等 | 目前犯規為固定兩罰，無犯滿離場、bonus、and-one、罰球籃板 |
| 籃板與阻攻 | ORE/DRE 分開、有傾向和數據 | 抽樣籃板、阻攻事件 | 有進攻籃板續攻與補籃；阻攻是未進球細分，不額外降低命中率 |
| 助攻數據 | 球員 AST 已存在 | 命中後記助攻 | 有傳球鏈，但沒有正式球員 AST；assistedRate 是診斷指標 |
| 季賽 | 有賽程、完整名單、逐場與球季數據 | 完整聯盟／賽季系統 | 現有 Monte Carlo 與回合／per36 測試，非 30 隊輪替球季 |
| 可檢驗性 | 存檔可讀、公式未知，適合黑箱對照 | 原始碼可讀，可追溯公式 | 原始碼、seed、事件與診斷皆可控 |

## 三個關鍵判斷

1. 我們已經有明確傳球鏈，不能簡化成「只抽誰得分」。但它用抽象空檔與 EV，不是依實際距離決策，切入也還不是獨立空間過程。
2. `courtside.js` 先呼叫 `simulateGame(...,{possessions:50,replay:true})`，再生成場景和動畫長度；因此畫面不是籃球結果的原因。若要 Hoop Land 式全自動場上比賽，需讓位置、路徑、球移動時間與防守距離進入決策核心。
3. Basketball GM 最值得借鏡的是賽制與時間管理；Hoop Land 值得借鏡動作傾向與場上演出。完整程度不能代替統計準確度驗證。

## 準確度現況

本專案已有 `four-team-calibration.md` 的 20 人固定五人、per36 實驗。得分 MAE 由 2.212 到 2.411，FTA 由 1.676 到 0.791、失誤由 0.624 到 0.276；因得分退步沒有升為預設。不能拿這些結果與完整 NBA 球季直接比較。

Hoop Land 的 60 場本機資料是虛構聯盟早期樣本，且執行模式未知；Basketball GM 本輪僅查原始碼。三者目前沒有相同名單、賽程、出勤、參數的共同實驗，不能宣稱誰勝率或排行榜最準。

## 建議順序

1. 補真實時鐘、24 秒、四節／延長賽、完整犯規、替補輪替與球員分鐘。
2. 補球員 AST、罰球籃板等完整記帳，將能力與動作傾向分開。
3. 建立同一 2025–26 名單與同條件 1,230 場 benchmark；報 30 隊戰績、全員排行榜、比分分布及重複球季區間。
4. 場上空間決策獨立分階段加入，但事件核心與快轉／觀戰共用，避免觀看方式改變結果。

## 來源

- [Hoop Land 開發者：雙引擎](https://steamcommunity.com/app/2453660/discussions/0/614304582405017911/)
- [Hoop Land 官方傾向預告](https://www.reddit.com/r/HoopLand/comments/16vp871/)
- [Basketball GM 比賽核心](https://github.com/zengm-games/zengm/blob/master/src/worker/core/GameSim.basketball/index.ts)：本日讀取 master，未鎖 commit，未來可能變動。
- [Basketball GM 能力合成](https://github.com/zengm-games/zengm/blob/master/src/common/constants.basketball.ts)
- 本專案：src/simulation_engine.js、src/probability_model.js、src/constants.js、src/teams.js、src/courtside.js、src/per36_report.js、src/season_style.js、reports/four-team-calibration.md。
- Hoop Land 本機存檔只讀，未將完整使用者存檔或遊戲程式複製進 repo。

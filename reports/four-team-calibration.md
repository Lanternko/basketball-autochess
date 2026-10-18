# 四隊校準實驗結果

採用判斷：失誤與FTA改善，但得分誤差未通過不退步條件；不升為正式預設。此為實驗設定，未套用正式卡表。固定全70對手，不是球隊PR50；疲勞關閉。

以CLE/LAL各120場比較9組共用係數；以新seed各1000場重跑四隊。OKC/NYK未參與係數選擇，但所有球員出手／罰球傾向均來自同季資料，不能稱為獨立賽季預測。

最佳參數：情境加成倍率 0.5；持球失誤倍率 1.8。罰球命中率曲線不變，FTA/FGA作兩罰事件先驗；尚無and-one、三罰、罰球籃板。

| 全20人MAE | 舊版 | 實驗 |
|---|---:|---:|
| pts | 2.212 | 2.411 |
| oreb | 0.514 | 0.403 |
| dreb | 0.691 | 0.699 |
| reb | 0.871 | 0.774 |
| tov | 0.624 | 0.276 |
| fta | 1.676 | 0.791 |
| stl | 0.676 | 0.565 |
| blk | 0.328 | 0.331 |
| twoPct | 0.121 | 0.094 |
| threePct | 0.069 | 0.052 |
| ftPct | 0.020 | 0.020 |
| usage代理(pp) | 1.220 | 1.885 |

三分命中率僅納入真實per36至少1次三分出手者；率類誤差以0–1表示。舊版與新驗證seed不同，差異包含抽樣誤差。

訓練隊 CLE/LAL：綜合誤差 4.276
未參與選參 OKC/NYK：綜合誤差 3.507

# 36 分鐘等效驗證報表

疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。

**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。

USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。診斷另列正規化五人 USG 代理誤差，不作正式驗收。

抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。

信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。

## 騎士 2015-16

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

同季傾向輸入：三分、罰球出手；情境倍率 0.5；失誤倍率 1.8。這些輸入不是獨立預測。

n=1000 · seed=20260909 · pace=93.82 · 每方 70 回合（35.813 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 86.8–69.2；對基準隊勝率 88.9%；每百回合攻／防 123.3／98.4。

真實整隊每百回合攻／防 110.2／103.9（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 19.5 / 22.5 | 3.9 / 3.4 | 2.6 / 2.7 | 0.6 / 1.2 | 0.2 / 0.4 | 50.5% / 44.8% | 24.3 / 28.5 |
| JR Smith | 17.6 / 14.6 | 4.1 / 3.3 | 1.3 / 0.9 | 0.6 / 1.2 | 0.3 / 0.3 | 48.1% / 41.5% | 19.0 / 17.7 |
| LeBron James | 25.8 / 25.5 | 6.6 / 7.5 | 3.7 / 3.3 | 0.7 / 1.4 | 0.5 / 0.7 | 65.0% / 52.0% | 28.9 / 30.5 |
| Kevin Love | 15.5 / 18.3 | 9.7 / 11.3 | 2.0 / 2.1 | 0.6 / 0.9 | 0.7 / 0.6 | 50.6% / 41.9% | 18.3 / 23.3 |
| Tristan Thompson | 8.4 / 10.2 | 10.1 / 11.7 | 1.0 / 1.0 | 0.7 / 0.6 | 1.0 / 0.8 | 65.9% / 58.8% | 9.4 / 11.4 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 19.2–19.9 | 0.7 / 0.9 | 3.3 / 2.4 | 56.3% / 50.2% | 36.8% / 32.1% | 89.0% / 88.5% | 31.5 |
| JR Smith | 17.2–18.0 | 0.7 / 0.7 | 3.4 / 2.7 | 56.4% / 43.8% | 45.3% / 40.0% | 61.7% / 63.4% | 30.7 |
| LeBron James | 25.4–26.2 | 1.3 / 1.5 | 5.3 / 6.0 | 68.0% / 57.3% | 37.6% / 30.9% | 70.6% / 73.1% | 35.6 |
| Kevin Love | 15.1–15.8 | 2.7 / 2.2 | 7.1 / 9.1 | 56.6% / 46.7% | 41.2% / 36.0% | 84.9% / 82.2% | 31.5 |
| Tristan Thompson | 8.2–8.6 | 3.1 / 4.3 | 7.0 / 7.5 | 65.9% / 58.8% | — / — | 59.2% / 61.6% | 27.7 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 36.9% | 20.0% | 1.061 | 6.0% | 2.3% | -1.2 |
| JR Smith | 8.9% | 26.6% | 1.210 | 3.9% | 2.5% | 3.1 |
| LeBron James | 36.7% | 18.5% | 1.155 | 18.9% | 2.6% | 1.6 |
| Kevin Love | 9.0% | 28.3% | 1.103 | 6.2% | 2.6% | -2.6 |
| Tristan Thompson | 8.5% | 6.5% | 1.130 | 10.4% | 3.0% | -0.8 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.702Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:27.246Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.678Z

## 湖人 2001-02

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

同季傾向輸入：三分、罰球出手；情境倍率 0.5；失誤倍率 1.8。這些輸入不是獨立預測。

n=1000 · seed=20260909 · pace=93.32 · 每方 70 回合（36.005 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 90.6–75.5；對基準隊勝率 85.7%；每百回合攻／防 129.4／107.9。

真實整隊每百回合攻／防 108.0／100.4（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 24.2 / 27.1 | 11.5 / 10.6 | 2.4 / 2.5 | 0.5 / 0.6 | 1.0 / 2.0 | 68.2% / 57.9% | 26.2 / 31.4 |
| Kobe Bryant | 28.0 / 23.7 | 4.6 / 5.2 | 2.7 / 2.6 | 0.6 / 1.4 | 0.2 / 0.4 | 63.1% / 46.9% | 29.8 / 29.9 |
| Derek Fisher | 19.2 / 14.3 | 3.6 / 2.7 | 1.4 / 1.1 | 0.5 / 1.2 | 0.2 / 0.2 | 47.6% / 41.1% | 20.5 / 17.3 |
| Rick Fox | 9.4 / 10.1 | 5.7 / 6.1 | 2.1 / 2.1 | 0.6 / 1.1 | 0.3 / 0.3 | 56.8% / 42.1% | 11.9 / 15.0 |
| Robert Horry | 9.7 / 9.2 | 7.9 / 8.0 | 1.3 / 1.5 | 0.5 / 1.3 | 0.7 / 1.5 | 51.3% / 39.8% | 11.6 / 12.7 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 23.8–24.6 | 3.8 / 3.5 | 7.7 / 7.1 | 68.2% / 58.0% | 0.0% / 0.0% | 56.5% / 55.5% | 36.1 |
| Kobe Bryant | 27.6–28.4 | 0.8 / 1.3 | 3.8 / 3.9 | 64.6% / 48.9% | 36.3% / 25.0% | 86.6% / 82.9% | 38.3 |
| Derek Fisher | 18.8–19.6 | 0.7 / 0.3 | 2.9 / 2.4 | 52.7% / 41.0% | 45.5% / 41.3% | 85.8% / 84.7% | 28.2 |
| Rick Fox | 9.1–9.7 | 1.1 / 1.4 | 4.6 / 4.7 | 67.0% / 47.9% | 40.0% / 31.3% | 83.5% / 82.4% | 27.9 |
| Robert Horry | 9.5–10.0 | 2.4 / 2.2 | 5.5 / 5.9 | 57.7% / 41.6% | 42.1% / 37.4% | 79.9% / 78.3% | 26.5 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 37.0% | 6.2% | 1.170 | 24.4% | 2.4% | -3.4 |
| Kobe Bryant | 36.6% | 18.8% | 1.214 | 14.8% | 2.3% | 1.7 |
| Derek Fisher | 9.0% | 35.5% | 1.211 | 2.9% | 2.0% | 4.2 |
| Rick Fox | 8.7% | 22.3% | 1.048 | 5.5% | 3.3% | -2.2 |
| Robert Horry | 8.7% | 17.2% | 1.085 | 5.1% | 2.6% | -0.4 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.164Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.512Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.137Z

## 雷霆 2025-26

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

同季傾向輸入：三分、罰球出手；情境倍率 0.5；失誤倍率 1.8。這些輸入不是獨立預測。

n=1000 · seed=20260909 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 96.5–74.4；對基準隊勝率 93.9%；每百回合攻／防 128.2／98.8。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 37.3 / 33.7 | 4.7 / 4.7 | 2.9 / 2.4 | 0.7 / 1.5 | 0.3 / 0.8 | 60.6% / 55.3% | 35.4 / 32.3 |
| Jalen Williams | 21.8 / 21.7 | 5.7 / 5.9 | 2.6 / 2.4 | 0.7 / 1.5 | 0.5 / 0.3 | 57.3% / 48.4% | 23.8 / 25.2 |
| Chet Holmgren | 18.3 / 21.3 | 10.8 / 11.1 | 2.2 / 1.9 | 0.7 / 0.8 | 1.0 / 2.4 | 65.0% / 55.7% | 18.0 / 21.4 |
| Luguentz Dort | 9.9 / 11.2 | 4.9 / 4.8 | 1.2 / 1.1 | 0.7 / 1.2 | 0.3 / 0.5 | 42.0% / 38.5% | 11.7 / 13.9 |
| Isaiah Hartenstein | 9.3 / 13.7 | 12.1 / 14.0 | 2.4 / 2.6 | 0.6 / 1.5 | 1.1 / 1.1 | 68.2% / 62.2% | 11.1 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.9–37.8 | 0.8 / 0.6 | 3.9 / 4.0 | 63.6% / 60.2% | 40.1% / 38.6% | 89.6% / 87.9% | 33.2 |
| Jalen Williams | 21.4–22.1 | 1.1 / 1.0 | 4.7 / 4.8 | 59.7% / 52.3% | 33.5% / 29.9% | 84.2% / 83.7% | 28.4 |
| Chet Holmgren | 17.9–18.6 | 3.3 / 2.3 | 7.5 / 8.7 | 68.5% / 64.6% | 43.1% / 36.2% | 80.6% / 79.2% | 28.9 |
| Luguentz Dort | 9.6–10.2 | 0.8 / 1.1 | 4.1 / 3.7 | 55.1% / 48.7% | 38.0% / 34.4% | 72.6% / 75.9% | 26.8 |
| Isaiah Hartenstein | 9.0–9.5 | 3.8 / 4.7 | 8.3 / 9.3 | 68.4% / 63.7% | 17.4% / 0.0% | 56.3% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.8% | 27.0% | 1.256 | 17.5% | 2.2% | 5.5 |
| Jalen Williams | 33.9% | 19.7% | 1.097 | 9.8% | 2.3% | 0.5 |
| Chet Holmgren | 9.9% | 21.6% | 1.210 | 22.4% | 3.4% | -1.8 |
| Luguentz Dort | 9.7% | 18.7% | 1.045 | 3.2% | 2.5% | -1.1 |
| Isaiah Hartenstein | 9.7% | 12.9% | 1.031 | 11.8% | 3.4% | -3.1 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

## 尼克 2025-26

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

同季傾向輸入：三分、罰球出手；情境倍率 0.5；失誤倍率 1.8。這些輸入不是獨立預測。

n=1000 · seed=20260909 · pace=97.71 · 每方 73 回合（35.861 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 88.8–77.0；對基準隊勝率 79.0%；每百回合攻／防 121.2／105.1。

真實整隊每百回合攻／防 118.7／112.3（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 25.0 / 26.8 | 3.6 / 3.4 | 2.6 / 2.4 | 0.6 / 0.8 | 0.2 / 0.1 | 51.7% / 46.7% | 28.1 / 29.6 |
| Mikal Bridges | 16.8 / 15.8 | 4.2 / 4.2 | 1.2 / 1.1 | 0.7 / 1.4 | 0.4 / 0.8 | 58.6% / 49.0% | 17.2 / 17.0 |
| OG Anunoby | 16.4 / 18.1 | 5.8 / 5.7 | 2.5 / 2.0 | 0.7 / 1.7 | 0.5 / 0.8 | 58.5% / 48.4% | 17.7 / 19.4 |
| Karl-Anthony Towns | 18.2 / 23.3 | 12.3 / 13.8 | 3.9 / 2.9 | 0.5 / 1.0 | 1.4 / 0.6 | 60.4% / 50.1% | 21.4 / 25.1 |
| Josh Hart | 12.5 / 14.3 | 6.0 / 8.8 | 3.0 / 2.3 | 0.6 / 1.4 | 0.4 / 0.3 | 55.7% / 50.8% | 15.6 / 16.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 24.5–25.4 | 0.6 / 0.4 | 3.0 / 3.0 | 57.6% / 52.2% | 41.1% / 36.9% | 85.6% / 84.1% | 35.0 |
| Mikal Bridges | 16.4–17.2 | 0.7 / 1.1 | 3.5 / 3.1 | 69.0% / 58.2% | 41.4% / 37.1% | 81.5% / 82.7% | 32.8 |
| OG Anunoby | 16.0–16.7 | 1.1 / 1.4 | 4.7 / 4.3 | 68.6% / 58.4% | 44.6% / 38.6% | 82.9% / 82.8% | 33.2 |
| Karl-Anthony Towns | 17.9–18.6 | 3.8 / 3.6 | 8.4 / 10.2 | 64.6% / 55.7% | 40.9% / 36.8% | 87.7% / 85.8% | 31.0 |
| Josh Hart | 12.1–12.8 | 0.9 / 1.7 | 5.1 / 7.1 | 64.1% / 57.4% | 44.5% / 41.3% | 66.6% / 72.0% | 30.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 38.4% | 21.4% | 1.131 | 8.3% | 2.1% | 0.5 |
| Mikal Bridges | 14.2% | 16.6% | 1.233 | 9.4% | 2.3% | 1.4 |
| OG Anunoby | 14.4% | 18.0% | 1.163 | 18.2% | 3.2% | -0.3 |
| Karl-Anthony Towns | 18.5% | 21.2% | 1.091 | 26.9% | 3.8% | -2.0 |
| Josh Hart | 14.5% | 22.8% | 1.042 | 13.4% | 3.4% | 0.4 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.584Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:30.017Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.660Z

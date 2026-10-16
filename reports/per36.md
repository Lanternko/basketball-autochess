# 36 分鐘等效驗證報表

疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。

**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。

USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。診斷另列正規化五人 USG 代理誤差，不作正式驗收。

抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。

信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。

## 勇士 2016-17

對手：全屬性 70 壓力測試隊（單項 PR50；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 113.1–80.6；對基準隊勝率 98.9%；每百回合攻／防 150.2／107.0。

真實整隊每百回合攻／防 114.8／103.4（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Stephen Curry | 35.8 / 27.3 | 5.3 / 4.8 | 2.5 / 3.3 | 0.5 / 1.9 | 0.3 / 0.2 | 59.0% / 46.8% | 32.1 / 28.6 |
| Klay Thompson | 22.3 / 23.7 | 5.2 / 3.9 | 0.9 / 1.7 | 0.6 / 0.9 | 0.5 / 0.5 | 59.9% / 46.8% | 19.1 / 25.8 |
| Kevin Durant | 38.1 / 27.0 | 9.2 / 8.9 | 1.8 / 2.4 | 0.7 / 1.1 | 0.8 / 1.7 | 69.0% / 53.7% | 31.8 / 27.1 |
| Draymond Green | 6.5 / 11.3 | 11.1 / 8.7 | 0.9 / 2.7 | 0.7 / 2.2 | 1.3 / 1.5 | 57.0% / 41.8% | 7.3 / 15.9 |
| Andre Iguodala | 10.4 / 10.3 | 6.8 / 5.5 | 0.5 / 1.0 | 0.7 / 1.4 | 0.6 / 0.7 | 63.7% / 52.8% | 9.6 / 11.1 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Stephen Curry | 35.3–36.4 | 0.9 / 0.8 | 4.4 / 4.0 | 68.9% / 53.7% | 49.7% / 41.1% | 89.4% / 89.8% | 33.4 |
| Klay Thompson | 21.8–22.7 | 0.9 / 0.7 | 4.3 / 3.2 | 72.5% / 51.6% | 48.5% / 41.4% | 86.1% / 85.3% | 34.0 |
| Kevin Durant | 37.6–38.6 | 2.0 / 0.7 | 7.2 / 8.2 | 77.6% / 60.8% | 45.4% / 37.5% | 88.2% / 87.5% | 33.4 |
| Draymond Green | 6.3–6.7 | 3.4 / 1.4 | 7.7 / 7.3 | 63.6% / 49.4% | 34.9% / 30.8% | 67.1% / 70.9% | 32.5 |
| Andre Iguodala | 10.2–10.7 | 1.4 / 0.9 | 5.4 / 4.6 | 72.2% / 65.1% | 40.5% / 36.2% | 67.8% / 70.6% | 26.3 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Stephen Curry | 36.5% | 26.7% | 1.312 | 9.9% | 2.8% | 5.8 |
| Klay Thompson | 8.7% | 38.4% | 1.396 | 9.1% | 2.3% | -4.7 |
| Kevin Durant | 36.5% | 13.0% | 1.396 | 30.9% | 2.5% | 6.8 |
| Draymond Green | 8.7% | 11.6% | 1.038 | 3.2% | 3.3% | -7.3 |
| Andre Iguodala | 9.6% | 10.3% | 1.290 | 8.5% | 2.6% | -0.6 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2016-17&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612744&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:25.029Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2016-17&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612744&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:25.462Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2016-17&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612744&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:25.702Z

## 騎士 2015-16

對手：全屬性 70 壓力測試隊（單項 PR50；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.82 · 每方 70 回合（35.813 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 96.7–75.4；對基準隊勝率 92.0%；每百回合攻／防 137.4／107.2。

真實整隊每百回合攻／防 110.2／103.9（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 24.5 / 22.5 | 4.4 / 3.4 | 1.8 / 2.7 | 0.5 / 1.2 | 0.2 / 0.4 | 50.5% / 44.8% | 26.3 / 28.5 |
| JR Smith | 16.1 / 14.6 | 4.8 / 3.3 | 0.7 / 0.9 | 0.5 / 1.2 | 0.3 / 0.3 | 52.1% / 41.5% | 16.1 / 17.7 |
| LeBron James | 29.2 / 25.5 | 7.6 / 7.5 | 2.3 / 3.3 | 0.6 / 1.4 | 0.6 / 0.7 | 62.6% / 52.0% | 29.1 / 30.5 |
| Kevin Love | 18.6 / 18.3 | 11.3 / 11.3 | 1.3 / 2.1 | 0.5 / 0.9 | 0.7 / 0.6 | 54.3% / 41.9% | 19.4 / 23.3 |
| Tristan Thompson | 8.3 / 10.2 | 11.6 / 11.7 | 0.6 / 1.0 | 0.6 / 0.6 | 1.0 / 0.8 | 58.7% / 58.8% | 9.1 / 11.4 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 24.1–24.9 | 0.9 / 0.9 | 3.5 / 2.4 | 58.8% / 50.2% | 40.6% / 32.1% | 89.6% / 88.5% | 31.5 |
| JR Smith | 15.7–16.5 | 1.0 / 0.7 | 3.7 / 2.7 | 58.0% / 43.8% | 47.3% / 40.0% | 62.7% / 63.4% | 30.7 |
| LeBron James | 28.7–29.6 | 1.7 / 1.5 | 5.9 / 6.0 | 72.0% / 57.3% | 36.8% / 30.9% | 70.6% / 73.1% | 35.6 |
| Kevin Love | 18.2–19.0 | 3.6 / 2.2 | 7.7 / 9.1 | 60.7% / 46.7% | 42.9% / 36.0% | 84.5% / 82.2% | 31.5 |
| Tristan Thompson | 8.1–8.6 | 4.0 / 4.3 | 7.6 / 7.5 | 64.4% / 58.8% | 32.0% / — | 59.0% / 61.6% | 27.7 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 37.0% | 20.4% | 1.135 | 6.0% | 2.4% | 0.7 |
| JR Smith | 8.8% | 24.2% | 1.226 | 3.9% | 2.3% | 0.2 |
| LeBron James | 36.8% | 17.1% | 1.212 | 18.9% | 2.9% | 1.7 |
| Kevin Love | 8.7% | 31.9% | 1.173 | 6.2% | 2.5% | -1.5 |
| Tristan Thompson | 8.7% | 6.4% | 1.102 | 10.4% | 3.9% | -1.1 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.702Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:27.246Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.678Z

## 雷霆 2025-26

對手：全屬性 70 壓力測試隊（單項 PR50；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 106.1–79.4；對基準隊勝率 97.8%；每百回合攻／防 141.0／105.5。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 37.7 / 33.7 | 5.2 / 4.7 | 1.7 / 2.4 | 0.7 / 1.5 | 0.3 / 0.8 | 60.4% / 55.3% | 33.4 / 32.3 |
| Jalen Williams | 23.6 / 21.7 | 6.7 / 5.9 | 1.7 / 2.4 | 0.5 / 1.5 | 0.5 / 0.3 | 54.4% / 48.4% | 23.7 / 25.2 |
| Chet Holmgren | 21.9 / 21.3 | 12.5 / 11.1 | 1.3 / 1.9 | 0.6 / 0.8 | 1.0 / 2.4 | 65.3% / 55.7% | 19.2 / 21.4 |
| Luguentz Dort | 13.2 / 11.2 | 5.6 / 4.8 | 0.9 / 1.1 | 0.5 / 1.2 | 0.4 / 0.5 | 49.7% / 38.5% | 13.4 / 13.9 |
| Isaiah Hartenstein | 9.8 / 13.7 | 13.8 / 14.0 | 1.4 / 2.6 | 0.5 / 1.5 | 1.1 / 1.1 | 63.0% / 62.2% | 10.3 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 37.2–38.2 | 0.9 / 0.6 | 4.3 / 4.0 | 67.2% / 60.2% | 42.8% / 38.6% | 90.1% / 87.9% | 33.2 |
| Jalen Williams | 23.2–24.0 | 1.3 / 1.0 | 5.4 / 4.8 | 61.6% / 52.3% | 35.8% / 29.9% | 84.6% / 83.7% | 28.4 |
| Chet Holmgren | 21.5–22.3 | 4.1 / 2.3 | 8.4 / 8.7 | 72.6% / 64.6% | 40.9% / 36.2% | 80.5% / 79.2% | 28.9 |
| Luguentz Dort | 12.9–13.6 | 1.0 / 1.1 | 4.5 / 3.7 | 59.2% / 48.7% | 41.2% / 34.4% | 71.7% / 75.9% | 26.8 |
| Isaiah Hartenstein | 9.5–10.0 | 4.4 / 4.7 | 9.4 / 9.3 | 69.9% / 63.7% | 31.8% / 0.0% | 55.5% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.6% | 23.6% | 1.288 | 17.5% | 2.2% | 3.5 |
| Jalen Williams | 34.0% | 18.2% | 1.142 | 9.8% | 2.2% | 0.4 |
| Chet Holmgren | 9.9% | 24.3% | 1.288 | 22.4% | 3.4% | -0.6 |
| Luguentz Dort | 9.7% | 22.2% | 1.126 | 3.2% | 2.9% | 0.5 |
| Isaiah Hartenstein | 9.8% | 11.6% | 1.067 | 11.8% | 3.6% | -3.9 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

## 尼克 2025-26

對手：全屬性 70 壓力測試隊（單項 PR50；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=97.71 · 每方 73 回合（35.861 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 103.8–82.2；對基準隊勝率 94.0%；每百回合攻／防 141.6／112.1。

真實整隊每百回合攻／防 118.7／112.3（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 27.1 / 26.8 | 4.1 / 3.4 | 1.5 / 2.4 | 0.5 / 0.8 | 0.3 / 0.1 | 52.3% / 46.7% | 27.2 / 29.6 |
| Mikal Bridges | 18.1 / 15.8 | 4.9 / 4.2 | 0.7 / 1.1 | 0.5 / 1.4 | 0.4 / 0.8 | 62.1% / 49.0% | 16.2 / 17.0 |
| OG Anunoby | 20.4 / 18.1 | 6.9 / 5.7 | 1.6 / 2.0 | 0.5 / 1.7 | 0.6 / 0.8 | 65.0% / 48.4% | 18.5 / 19.4 |
| Karl-Anthony Towns | 22.8 / 23.3 | 14.8 / 13.8 | 2.5 / 2.9 | 0.4 / 1.0 | 1.6 / 0.6 | 63.3% / 50.1% | 22.3 / 25.1 |
| Josh Hart | 15.4 / 14.3 | 6.9 / 8.8 | 1.9 / 2.3 | 0.5 / 1.4 | 0.4 / 0.3 | 58.4% / 50.8% | 15.8 / 16.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 26.6–27.5 | 0.8 / 0.4 | 3.3 / 3.0 | 59.8% / 52.2% | 43.2% / 36.9% | 87.7% / 84.1% | 35.0 |
| Mikal Bridges | 17.7–18.5 | 0.9 / 1.1 | 4.0 / 3.1 | 72.6% / 58.2% | 44.2% / 37.1% | 82.9% / 82.7% | 32.8 |
| OG Anunoby | 20.0–20.8 | 1.6 / 1.4 | 5.3 / 4.3 | 74.9% / 58.4% | 45.7% / 38.6% | 84.2% / 82.8% | 33.2 |
| Karl-Anthony Towns | 22.4–23.3 | 5.3 / 3.6 | 9.5 / 10.2 | 70.6% / 55.7% | 42.9% / 36.8% | 86.8% / 85.8% | 31.0 |
| Josh Hart | 15.0–15.7 | 1.2 / 1.7 | 5.7 / 7.1 | 67.6% / 57.4% | 46.5% / 41.3% | 68.6% / 72.0% | 30.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 38.7% | 16.7% | 1.202 | 8.3% | 2.1% | -0.4 |
| Mikal Bridges | 14.1% | 16.5% | 1.318 | 9.4% | 2.3% | 0.3 |
| OG Anunoby | 14.2% | 20.6% | 1.292 | 18.2% | 3.6% | 0.5 |
| Karl-Anthony Towns | 18.5% | 22.6% | 1.201 | 26.9% | 3.9% | -1.0 |
| Josh Hart | 14.5% | 23.7% | 1.147 | 13.4% | 3.5% | 0.6 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.584Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:30.017Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.660Z

## 湖人 2001-02

對手：全屬性 70 壓力測試隊（單項 PR50；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.32 · 每方 70 回合（36.005 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 96.5–79.8；對基準隊勝率 88.7%；每百回合攻／防 137.8／114.0。

真實整隊每百回合攻／防 108.0／100.4（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 25.0 / 27.1 | 13.0 / 10.6 | 1.5 / 2.5 | 0.3 / 0.6 | 1.1 / 2.0 | 61.9% / 57.9% | 25.9 / 31.4 |
| Kobe Bryant | 28.2 / 23.7 | 5.3 / 5.2 | 1.7 / 2.6 | 0.5 / 1.4 | 0.2 / 0.4 | 58.3% / 46.9% | 28.3 / 29.9 |
| Derek Fisher | 16.4 / 14.3 | 4.1 / 2.7 | 0.7 / 1.1 | 0.4 / 1.2 | 0.2 / 0.2 | 48.5% / 41.1% | 17.1 / 17.3 |
| Rick Fox | 14.6 / 10.1 | 6.5 / 6.1 | 1.7 / 2.1 | 0.4 / 1.1 | 0.4 / 0.3 | 56.8% / 42.1% | 15.6 / 15.0 |
| Robert Horry | 12.2 / 9.2 | 9.0 / 8.0 | 0.9 / 1.5 | 0.4 / 1.3 | 0.7 / 1.5 | 52.9% / 39.8% | 13.1 / 12.7 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 24.6–25.4 | 4.4 / 3.5 | 8.7 / 7.1 | 69.8% / 58.0% | 35.0% / 0.0% | 56.8% / 55.5% | 36.1 |
| Kobe Bryant | 27.7–28.6 | 1.1 / 1.3 | 4.3 / 3.9 | 67.3% / 48.9% | 39.2% / 25.0% | 86.9% / 82.9% | 38.3 |
| Derek Fisher | 16.1–16.8 | 0.8 / 0.3 | 3.3 / 2.4 | 51.8% / 41.0% | 46.0% / 41.3% | 84.9% / 84.7% | 28.2 |
| Rick Fox | 14.2–15.0 | 1.4 / 1.4 | 5.2 / 4.7 | 69.7% / 47.9% | 41.6% / 31.3% | 83.5% / 82.4% | 27.9 |
| Robert Horry | 11.9–12.6 | 2.8 / 2.2 | 6.2 / 5.9 | 59.1% / 41.6% | 43.8% / 37.4% | 79.4% / 78.3% | 26.5 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 36.7% | 5.3% | 1.190 | 24.4% | 2.7% | -3.7 |
| Kobe Bryant | 36.6% | 15.2% | 1.233 | 14.8% | 2.6% | 0.1 |
| Derek Fisher | 8.9% | 31.1% | 1.210 | 2.9% | 2.3% | 0.9 |
| Rick Fox | 8.9% | 28.9% | 1.153 | 5.5% | 3.2% | 1.5 |
| Robert Horry | 8.9% | 19.5% | 1.151 | 5.1% | 2.6% | 1.2 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.164Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.512Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.137Z

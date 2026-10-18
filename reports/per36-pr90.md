# 36 分鐘等效驗證報表

疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。

**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。

USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。診斷另列正規化五人 USG 代理誤差，不作正式驗收。

抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。

信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。

## 勇士 2016-17

對手：全屬性 94 壓力測試隊（單項 PR90；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 89.6–126.0；對基準隊勝率 0.4%；每百回合攻／防 119.1／167.4。

真實整隊每百回合攻／防 114.8／103.4（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Stephen Curry | 28.4 / 27.3 | 2.2 / 4.8 | 2.9 / 3.3 | 0.1 / 1.9 | 0.3 / 0.2 | 47.9% / 46.8% | 31.8 / 28.6 |
| Klay Thompson | 22.9 / 23.7 | 2.2 / 3.9 | 1.5 / 1.7 | 0.1 / 0.9 | 0.5 / 0.5 | 49.5% / 46.8% | 24.1 / 25.8 |
| Kevin Durant | 26.8 / 27.0 | 3.9 / 8.9 | 2.2 / 2.4 | 0.1 / 1.1 | 0.9 / 1.7 | 54.7% / 53.7% | 28.7 / 27.1 |
| Draymond Green | 4.2 / 11.3 | 4.9 / 8.7 | 1.1 / 2.7 | 0.1 / 2.2 | 1.5 / 1.5 | 42.8% / 41.8% | 6.5 / 15.9 |
| Andre Iguodala | 7.4 / 10.3 | 2.9 / 5.5 | 0.6 / 1.0 | 0.1 / 1.4 | 0.7 / 0.7 | 49.7% / 52.8% | 8.9 / 11.1 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Stephen Curry | 27.9–28.9 | 0.6 / 0.8 | 1.6 / 4.0 | 53.1% / 53.7% | 43.8% / 41.1% | 89.1% / 89.8% | 33.4 |
| Klay Thompson | 22.4–23.3 | 0.5 / 0.7 | 1.6 / 3.2 | 57.2% / 51.6% | 43.8% / 41.4% | 87.1% / 85.3% | 34.0 |
| Kevin Durant | 26.3–27.2 | 1.2 / 0.7 | 2.7 / 8.2 | 62.6% / 60.8% | 38.7% / 37.5% | 88.4% / 87.5% | 33.4 |
| Draymond Green | 4.0–4.4 | 2.1 / 1.4 | 2.8 / 7.3 | 48.5% / 49.4% | 32.1% / 30.8% | 67.9% / 70.9% | 32.5 |
| Andre Iguodala | 7.1–7.6 | 0.9 / 0.9 | 2.0 / 4.6 | 58.1% / 65.1% | 33.7% / 36.2% | 66.9% / 70.6% | 26.3 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Stephen Curry | 36.2% | 28.9% | 1.103 | 9.9% | 3.1% | 5.5 |
| Klay Thompson | 8.8% | 36.1% | 1.176 | 9.1% | 3.4% | 0.3 |
| Kevin Durant | 36.3% | 13.2% | 1.154 | 30.9% | 3.8% | 3.7 |
| Draymond Green | 8.9% | 11.8% | 0.814 | 3.2% | 3.8% | -8.1 |
| Andre Iguodala | 9.8% | 9.9% | 1.056 | 8.5% | 3.1% | -1.4 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2016-17&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612744&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:25.029Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2016-17&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612744&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:25.462Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2016-17&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612744&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:25.702Z

## 騎士 2015-16

對手：全屬性 94 壓力測試隊（單項 PR90；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.82 · 每方 70 回合（35.813 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 73.2–117.7；對基準隊勝率 0.1%；每百回合攻／防 104.0／167.3。

真實整隊每百回合攻／防 110.2／103.9（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 18.6 / 22.5 | 1.9 / 3.4 | 2.3 / 2.7 | 0.1 / 1.2 | 0.3 / 0.4 | 40.3% / 44.8% | 26.3 / 28.5 |
| JR Smith | 15.2 / 14.6 | 2.0 / 3.3 | 1.1 / 0.9 | 0.1 / 1.2 | 0.4 / 0.3 | 43.0% / 41.5% | 19.3 / 17.7 |
| LeBron James | 17.9 / 25.5 | 3.2 / 7.5 | 2.5 / 3.3 | 0.1 / 1.4 | 0.7 / 0.7 | 47.5% / 52.0% | 24.4 / 30.5 |
| Kevin Love | 16.1 / 18.3 | 5.1 / 11.3 | 2.0 / 2.1 | 0.1 / 0.9 | 1.0 / 0.6 | 42.1% / 41.9% | 22.0 / 23.3 |
| Tristan Thompson | 5.4 / 10.2 | 5.5 / 11.7 | 0.7 / 1.0 | 0.1 / 0.6 | 1.4 / 0.8 | 44.6% / 58.8% | 8.1 / 11.4 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 18.2–19.0 | 0.6 / 0.9 | 1.3 / 2.4 | 46.1% / 50.2% | 33.8% / 32.1% | 89.5% / 88.5% | 31.5 |
| JR Smith | 14.8–15.5 | 0.5 / 0.7 | 1.4 / 2.7 | 45.3% / 43.8% | 41.1% / 40.0% | 62.5% / 63.4% | 30.7 |
| LeBron James | 17.5–18.3 | 1.0 / 1.5 | 2.2 / 6.0 | 54.7% / 57.3% | 32.0% / 30.9% | 71.0% / 73.1% | 35.6 |
| Kevin Love | 15.8–16.5 | 2.2 / 2.2 | 2.9 / 9.1 | 46.1% / 46.7% | 37.6% / 36.0% | 83.7% / 82.2% | 31.5 |
| Tristan Thompson | 5.2–5.6 | 2.6 / 4.3 | 2.9 / 7.5 | 49.2% / 58.8% | 27.1% / — | 59.4% / 61.6% | 27.7 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 36.8% | 23.4% | 0.942 | 6.0% | 3.0% | 0.7 |
| JR Smith | 8.7% | 23.9% | 1.031 | 3.9% | 3.0% | 3.4 |
| LeBron James | 37.0% | 15.5% | 0.961 | 18.9% | 3.5% | -3.0 |
| Kevin Love | 8.8% | 30.7% | 0.967 | 6.2% | 3.8% | 1.1 |
| Tristan Thompson | 8.7% | 6.4% | 0.879 | 10.4% | 4.1% | -2.2 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.702Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:27.246Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.678Z

## 雷霆 2025-26

對手：全屬性 94 壓力測試隊（單項 PR90；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 80.4–124.7；對基準隊勝率 0.1%；每百回合攻／防 106.7／165.7。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 27.8 / 33.7 | 2.3 / 4.7 | 2.1 / 2.4 | 0.1 / 1.5 | 0.5 / 0.8 | 47.7% / 55.3% | 32.0 / 32.3 |
| Jalen Williams | 15.0 / 21.7 | 2.9 / 5.9 | 2.0 / 2.4 | 0.1 / 1.5 | 0.8 / 0.3 | 40.8% / 48.4% | 20.7 / 25.2 |
| Chet Holmgren | 18.1 / 21.3 | 6.0 / 11.1 | 2.0 / 1.9 | 0.1 / 0.8 | 1.7 / 2.4 | 52.4% / 55.7% | 20.8 / 21.4 |
| Luguentz Dort | 12.1 / 11.2 | 2.5 / 4.8 | 1.4 / 1.1 | 0.1 / 1.2 | 0.6 / 0.5 | 39.2% / 38.5% | 16.3 / 13.9 |
| Isaiah Hartenstein | 7.3 / 13.7 | 6.7 / 14.0 | 1.7 / 2.6 | 0.1 / 1.5 | 1.7 / 1.1 | 50.6% / 62.2% | 10.3 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 27.4–28.3 | 0.6 / 0.6 | 1.8 / 4.0 | 53.3% / 60.2% | 36.2% / 38.6% | 88.8% / 87.9% | 33.2 |
| Jalen Williams | 14.6–15.3 | 0.8 / 1.0 | 2.1 / 4.8 | 46.9% / 52.3% | 28.9% / 29.9% | 84.7% / 83.7% | 28.4 |
| Chet Holmgren | 17.8–18.5 | 2.4 / 2.3 | 3.5 / 8.7 | 59.0% / 64.6% | 35.4% / 36.2% | 78.9% / 79.2% | 28.9 |
| Luguentz Dort | 11.7–12.4 | 0.6 / 1.1 | 1.9 / 3.7 | 45.0% / 48.7% | 34.4% / 34.4% | 71.0% / 75.9% | 26.8 |
| Isaiah Hartenstein | 7.1–7.6 | 2.8 / 4.7 | 3.9 / 9.3 | 57.0% / 63.7% | 25.8% / 0.0% | 58.6% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.7% | 23.6% | 1.066 | 17.5% | 2.7% | 2.1 |
| Jalen Williams | 33.9% | 18.4% | 0.903 | 9.8% | 3.2% | -2.6 |
| Chet Holmgren | 9.9% | 22.5% | 1.052 | 22.4% | 4.9% | 1.0 |
| Luguentz Dort | 9.7% | 22.7% | 0.925 | 3.2% | 3.9% | 3.4 |
| Isaiah Hartenstein | 9.8% | 12.8% | 0.857 | 11.8% | 4.5% | -3.9 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

## 尼克 2025-26

對手：全屬性 94 壓力測試隊（單項 PR90；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=97.71 · 每方 73 回合（35.861 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 80.2–123.4；對基準隊勝率 0.0%；每百回合攻／防 109.4／168.4。

真實整隊每百回合攻／防 118.7／112.3（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 21.0 / 26.8 | 1.8 / 3.4 | 1.9 / 2.4 | 0.1 / 0.8 | 0.3 / 0.1 | 42.4% / 46.7% | 26.4 / 29.6 |
| Mikal Bridges | 13.2 / 15.8 | 2.2 / 4.2 | 0.9 / 1.1 | 0.1 / 1.4 | 0.5 / 0.8 | 47.8% / 49.0% | 15.4 / 17.0 |
| OG Anunoby | 15.5 / 18.1 | 3.1 / 5.7 | 2.0 / 2.0 | 0.1 / 1.7 | 0.7 / 0.8 | 49.5% / 48.4% | 18.3 / 19.4 |
| Karl-Anthony Towns | 17.4 / 23.3 | 6.7 / 13.8 | 3.0 / 2.9 | 0.1 / 1.0 | 1.8 / 0.6 | 49.0% / 50.1% | 22.1 / 25.1 |
| Josh Hart | 13.1 / 14.3 | 3.0 / 8.8 | 2.7 / 2.3 | 0.1 / 1.4 | 0.4 / 0.3 | 45.5% / 50.8% | 17.7 / 16.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 20.5–21.4 | 0.5 / 0.4 | 1.3 / 3.0 | 47.2% / 52.2% | 37.8% / 36.9% | 86.1% / 84.1% | 35.0 |
| Mikal Bridges | 12.9–13.5 | 0.6 / 1.1 | 1.6 / 3.1 | 56.6% / 58.2% | 37.8% / 37.1% | 82.1% / 82.7% | 32.8 |
| OG Anunoby | 15.1–15.8 | 1.0 / 1.4 | 2.1 / 4.3 | 56.9% / 58.4% | 40.9% / 38.6% | 85.6% / 82.8% | 33.2 |
| Karl-Anthony Towns | 17.0–17.8 | 3.2 / 3.6 | 3.5 / 10.2 | 55.4% / 55.7% | 38.0% / 36.8% | 87.7% / 85.8% | 31.0 |
| Josh Hart | 12.8–13.5 | 0.8 / 1.7 | 2.2 / 7.1 | 50.5% / 57.4% | 41.4% / 41.3% | 66.8% / 72.0% | 30.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 38.4% | 20.8% | 1.013 | 8.3% | 2.6% | -1.1 |
| Mikal Bridges | 14.3% | 14.5% | 1.081 | 9.4% | 2.7% | -0.4 |
| OG Anunoby | 14.2% | 18.0% | 1.045 | 18.2% | 4.5% | 0.3 |
| Karl-Anthony Towns | 18.4% | 22.0% | 0.973 | 26.9% | 4.9% | -1.3 |
| Josh Hart | 14.6% | 24.7% | 0.941 | 13.4% | 4.3% | 2.5 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.584Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:30.017Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.660Z

## 湖人 2001-02

對手：全屬性 94 壓力測試隊（單項 PR90；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.32 · 每方 70 回合（36.005 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 73.6–120.6；對基準隊勝率 0.0%；每百回合攻／防 105.1／172.4。

真實整隊每百回合攻／防 108.0／100.4（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 15.9 / 27.1 | 5.8 / 10.6 | 1.6 / 2.5 | 0.1 / 0.6 | 1.5 / 2.0 | 49.3% / 57.9% | 21.5 / 31.4 |
| Kobe Bryant | 17.8 / 23.7 | 2.1 / 5.2 | 1.9 / 2.6 | 0.1 / 1.4 | 0.3 / 0.4 | 43.8% / 46.9% | 24.2 / 29.9 |
| Derek Fisher | 17.9 / 14.3 | 1.6 / 2.7 | 1.3 / 1.1 | 0.0 / 1.2 | 0.3 / 0.2 | 41.8% / 41.1% | 23.0 / 17.3 |
| Rick Fox | 11.4 / 10.1 | 2.7 / 6.1 | 2.2 / 2.1 | 0.1 / 1.1 | 0.5 / 0.3 | 43.0% / 42.1% | 16.5 / 15.0 |
| Robert Horry | 10.6 / 9.2 | 3.8 / 8.0 | 1.4 / 1.5 | 0.1 / 1.3 | 1.0 / 1.5 | 41.0% / 39.8% | 14.8 / 12.7 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 15.5–16.2 | 2.7 / 3.5 | 3.1 / 7.1 | 56.1% / 58.0% | 28.5% / 0.0% | 58.5% / 55.5% | 36.1 |
| Kobe Bryant | 17.4–18.1 | 0.6 / 1.3 | 1.5 / 3.9 | 50.9% / 48.9% | 32.0% / 25.0% | 86.1% / 82.9% | 38.3 |
| Derek Fisher | 17.5–18.3 | 0.5 / 0.3 | 1.2 / 2.4 | 42.0% / 41.0% | 41.6% / 41.3% | 85.0% / 84.7% | 28.2 |
| Rick Fox | 11.1–11.8 | 0.8 / 1.4 | 1.8 / 4.7 | 51.4% / 47.9% | 36.3% / 31.3% | 82.0% / 82.4% | 27.9 |
| Robert Horry | 10.3–10.9 | 1.6 / 2.2 | 2.2 / 5.9 | 43.2% / 41.6% | 39.0% / 37.4% | 79.3% / 78.3% | 26.5 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 36.8% | 5.7% | 0.968 | 24.4% | 3.0% | -8.1 |
| Kobe Bryant | 36.8% | 14.8% | 0.987 | 14.8% | 3.0% | -3.9 |
| Derek Fisher | 8.8% | 33.2% | 1.027 | 2.9% | 2.7% | 6.7 |
| Rick Fox | 8.8% | 26.3% | 0.915 | 5.5% | 4.2% | 2.4 |
| Robert Horry | 8.8% | 20.1% | 0.948 | 5.1% | 3.7% | 2.8 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.164Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.512Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.137Z

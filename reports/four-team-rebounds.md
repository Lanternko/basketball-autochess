# 四隊籃板比例校準

固定全屬性70基準，不代表聯盟平均實力；每隊1000場、相同seed、疲勞關閉。舊報表保留不覆蓋。

球員籃板比例來自同季聯盟 OREB / (OREB + DREB)，包含罰球籃板，因此只作目前 live-FG 模型的近似基準。位置／落點／能力影響相對爭搶機率；尚未模擬衝搶後快攻的代價。

| 指標 MAE | 修改前 | 修改後 |
|---|---:|---:|
| pts | 2.212 | 2.150 |
| oreb | 0.514 | 0.458 |
| dreb | 0.691 | 0.640 |
| reb | 0.871 | 0.793 |
| tov | 0.624 | 0.649 |

騎士 2015-16：聯盟進攻籃板基準 23.80%。[NBA來源](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=0&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0)

雷霆 2025-26：聯盟進攻籃板基準 25.99%。[NBA來源](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=0&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0)

尼克 2025-26：聯盟進攻籃板基準 25.99%。[NBA來源](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=0&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0)

湖人 2001-02：聯盟進攻籃板基準 28.86%。[NBA來源](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=0&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0)

# 36 分鐘等效驗證報表

疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。

**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。

USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。診斷另列正規化五人 USG 代理誤差，不作正式驗收。

抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。

信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。

## 騎士 2015-16

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.82 · 每方 70 回合（35.813 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 94.2–75.3；對基準隊勝率 89.8%；每百回合攻／防 133.8／107.1。

真實整隊每百回合攻／防 110.2／103.9（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 24.0 / 22.5 | 4.2 / 3.4 | 1.7 / 2.7 | 0.5 / 1.2 | 0.2 / 0.4 | 50.3% / 44.8% | 26.5 / 28.5 |
| JR Smith | 15.9 / 14.6 | 4.5 / 3.3 | 0.7 / 0.9 | 0.5 / 1.2 | 0.3 / 0.3 | 52.1% / 41.5% | 16.2 / 17.7 |
| LeBron James | 28.6 / 25.5 | 7.3 / 7.5 | 2.2 / 3.3 | 0.6 / 1.4 | 0.6 / 0.7 | 62.3% / 52.0% | 29.3 / 30.5 |
| Kevin Love | 17.9 / 18.3 | 10.6 / 11.3 | 1.3 / 2.1 | 0.5 / 0.9 | 0.7 / 0.6 | 54.2% / 41.9% | 19.2 / 23.3 |
| Tristan Thompson | 7.8 / 10.2 | 11.0 / 11.7 | 0.6 / 1.0 | 0.6 / 0.6 | 1.0 / 0.8 | 58.1% / 58.8% | 8.8 / 11.4 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 23.6–24.4 | 0.7 / 0.9 | 3.5 / 2.4 | 58.8% / 50.2% | 40.3% / 32.1% | 89.8% / 88.5% | 31.5 |
| JR Smith | 15.5–16.2 | 0.8 / 0.7 | 3.7 / 2.7 | 57.5% / 43.8% | 47.7% / 40.0% | 63.4% / 63.4% | 30.7 |
| LeBron James | 28.2–29.1 | 1.3 / 1.5 | 6.0 / 6.0 | 71.8% / 57.3% | 36.6% / 30.9% | 70.7% / 73.1% | 35.6 |
| Kevin Love | 17.5–18.2 | 3.0 / 2.2 | 7.7 / 9.1 | 60.8% / 46.7% | 42.8% / 36.0% | 83.8% / 82.2% | 31.5 |
| Tristan Thompson | 7.6–8.0 | 3.4 / 4.3 | 7.7 / 7.5 | 63.9% / 58.8% | 32.0% / — | 59.1% / 61.6% | 27.7 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 37.0% | 20.4% | 1.135 | 6.0% | 2.3% | 0.9 |
| JR Smith | 8.8% | 24.2% | 1.228 | 3.9% | 2.3% | 0.3 |
| LeBron James | 36.8% | 17.2% | 1.211 | 18.9% | 2.9% | 2.0 |
| Kevin Love | 8.7% | 31.8% | 1.174 | 6.2% | 2.6% | -1.7 |
| Tristan Thompson | 8.7% | 6.4% | 1.100 | 10.4% | 3.7% | -1.4 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.702Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:27.246Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.678Z

## 雷霆 2025-26

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 105.2–80.4；對基準隊勝率 96.3%；每百回合攻／防 139.8／106.8。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 37.5 / 33.7 | 5.1 / 4.7 | 1.7 / 2.4 | 0.7 / 1.5 | 0.3 / 0.8 | 60.3% / 55.3% | 33.5 / 32.3 |
| Jalen Williams | 23.4 / 21.7 | 6.5 / 5.9 | 1.6 / 2.4 | 0.5 / 1.5 | 0.5 / 0.3 | 54.4% / 48.4% | 23.7 / 25.2 |
| Chet Holmgren | 21.7 / 21.3 | 12.1 / 11.1 | 1.3 / 1.9 | 0.6 / 0.8 | 1.0 / 2.4 | 65.1% / 55.7% | 19.3 / 21.4 |
| Luguentz Dort | 13.1 / 11.2 | 5.4 / 4.8 | 0.9 / 1.1 | 0.5 / 1.2 | 0.4 / 0.5 | 49.5% / 38.5% | 13.4 / 13.9 |
| Isaiah Hartenstein | 9.5 / 13.7 | 13.5 / 14.0 | 1.4 / 2.6 | 0.5 / 1.5 | 1.1 / 1.1 | 62.8% / 62.2% | 10.2 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 37.0–38.0 | 0.9 / 0.6 | 4.2 / 4.0 | 67.2% / 60.2% | 42.6% / 38.6% | 90.2% / 87.9% | 33.2 |
| Jalen Williams | 23.0–23.8 | 1.3 / 1.0 | 5.2 / 4.8 | 61.9% / 52.3% | 35.2% / 29.9% | 84.1% / 83.7% | 28.4 |
| Chet Holmgren | 21.3–22.1 | 3.9 / 2.3 | 8.2 / 8.7 | 72.5% / 64.6% | 40.6% / 36.2% | 80.3% / 79.2% | 28.9 |
| Luguentz Dort | 12.8–13.4 | 1.0 / 1.1 | 4.4 / 3.7 | 59.3% / 48.7% | 40.9% / 34.4% | 71.6% / 75.9% | 26.8 |
| Isaiah Hartenstein | 9.2–9.8 | 4.2 / 4.7 | 9.3 / 9.3 | 69.7% / 63.7% | 32.2% / 0.0% | 54.9% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.5% | 23.5% | 1.288 | 17.5% | 2.3% | 3.6 |
| Jalen Williams | 34.0% | 18.2% | 1.142 | 9.8% | 2.2% | 0.4 |
| Chet Holmgren | 9.9% | 24.5% | 1.288 | 22.4% | 3.3% | -0.5 |
| Luguentz Dort | 9.7% | 22.2% | 1.126 | 3.2% | 2.7% | 0.6 |
| Isaiah Hartenstein | 9.8% | 11.6% | 1.066 | 11.8% | 3.6% | -4.0 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

## 尼克 2025-26

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=97.71 · 每方 73 回合（35.861 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 100.5–83.2；對基準隊勝率 88.6%；每百回合攻／防 137.2／113.5。

真實整隊每百回合攻／防 118.7／112.3（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 26.5 / 26.8 | 3.9 / 3.4 | 1.5 / 2.4 | 0.5 / 0.8 | 0.3 / 0.1 | 52.1% / 46.7% | 27.4 / 29.6 |
| Mikal Bridges | 17.5 / 15.8 | 4.6 / 4.2 | 0.7 / 1.1 | 0.5 / 1.4 | 0.4 / 0.8 | 61.6% / 49.0% | 16.2 / 17.0 |
| OG Anunoby | 19.8 / 18.1 | 6.4 / 5.7 | 1.5 / 2.0 | 0.5 / 1.7 | 0.6 / 0.8 | 64.6% / 48.4% | 18.6 / 19.4 |
| Karl-Anthony Towns | 21.6 / 23.3 | 13.2 / 13.8 | 2.4 / 2.9 | 0.4 / 1.0 | 1.6 / 0.6 | 63.0% / 50.1% | 21.8 / 25.1 |
| Josh Hart | 15.0 / 14.3 | 6.5 / 8.8 | 1.8 / 2.3 | 0.5 / 1.4 | 0.4 / 0.3 | 58.0% / 50.8% | 15.9 / 16.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 26.1–27.0 | 0.6 / 0.4 | 3.3 / 3.0 | 59.4% / 52.2% | 43.5% / 36.9% | 87.7% / 84.1% | 35.0 |
| Mikal Bridges | 17.2–17.9 | 0.7 / 1.1 | 3.9 / 3.1 | 72.6% / 58.2% | 43.4% / 37.1% | 83.0% / 82.7% | 32.8 |
| OG Anunoby | 19.4–20.2 | 1.2 / 1.4 | 5.3 / 4.3 | 74.8% / 58.4% | 45.2% / 38.6% | 84.7% / 82.8% | 33.2 |
| Karl-Anthony Towns | 21.2–22.0 | 4.0 / 3.6 | 9.2 / 10.2 | 70.3% / 55.7% | 43.2% / 36.8% | 86.5% / 85.8% | 31.0 |
| Josh Hart | 14.7–15.4 | 0.9 / 1.7 | 5.6 / 7.1 | 67.0% / 57.4% | 46.7% / 41.3% | 69.6% / 72.0% | 30.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 38.9% | 16.7% | 1.202 | 8.3% | 2.1% | -0.1 |
| Mikal Bridges | 14.0% | 16.5% | 1.318 | 9.4% | 2.2% | 0.4 |
| OG Anunoby | 14.2% | 20.5% | 1.292 | 18.2% | 3.8% | 0.5 |
| Karl-Anthony Towns | 18.4% | 22.8% | 1.199 | 26.9% | 4.0% | -1.5 |
| Josh Hart | 14.6% | 23.6% | 1.148 | 13.4% | 3.5% | 0.7 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.584Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:30.017Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.660Z

## 湖人 2001-02

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.32 · 每方 70 回合（36.005 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 96.6–81.6；對基準隊勝率 86.3%；每百回合攻／防 138.0／116.6。

真實整隊每百回合攻／防 108.0／100.4（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 25.1 / 27.1 | 12.7 / 10.6 | 1.5 / 2.5 | 0.3 / 0.6 | 1.2 / 2.0 | 62.0% / 57.9% | 25.9 / 31.4 |
| Kobe Bryant | 28.2 / 23.7 | 5.2 / 5.2 | 1.7 / 2.6 | 0.5 / 1.4 | 0.2 / 0.4 | 58.4% / 46.9% | 28.3 / 29.9 |
| Derek Fisher | 16.4 / 14.3 | 4.0 / 2.7 | 0.7 / 1.1 | 0.4 / 1.2 | 0.2 / 0.2 | 48.4% / 41.1% | 17.1 / 17.3 |
| Rick Fox | 14.7 / 10.1 | 6.4 / 6.1 | 1.7 / 2.1 | 0.4 / 1.1 | 0.4 / 0.3 | 56.9% / 42.1% | 15.5 / 15.0 |
| Robert Horry | 12.3 / 9.2 | 8.9 / 8.0 | 0.9 / 1.5 | 0.4 / 1.3 | 0.7 / 1.5 | 52.9% / 39.8% | 13.2 / 12.7 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 24.7–25.5 | 4.4 / 3.5 | 8.4 / 7.1 | 70.1% / 58.0% | 34.5% / 0.0% | 56.6% / 55.5% | 36.1 |
| Kobe Bryant | 27.8–28.7 | 1.1 / 1.3 | 4.1 / 3.9 | 67.4% / 48.9% | 39.3% / 25.0% | 87.0% / 82.9% | 38.3 |
| Derek Fisher | 16.0–16.7 | 0.8 / 0.3 | 3.2 / 2.4 | 51.8% / 41.0% | 45.7% / 41.3% | 84.8% / 84.7% | 28.2 |
| Rick Fox | 14.3–15.0 | 1.4 / 1.4 | 5.0 / 4.7 | 69.8% / 47.9% | 41.8% / 31.3% | 83.6% / 82.4% | 27.9 |
| Robert Horry | 12.0–12.6 | 2.8 / 2.2 | 6.0 / 5.9 | 59.1% / 41.6% | 43.9% / 37.4% | 79.2% / 78.3% | 26.5 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 36.7% | 5.3% | 1.189 | 24.4% | 2.7% | -3.6 |
| Kobe Bryant | 36.6% | 15.3% | 1.233 | 14.8% | 2.6% | 0.2 |
| Derek Fisher | 8.9% | 31.1% | 1.211 | 2.9% | 2.4% | 0.9 |
| Rick Fox | 9.0% | 28.8% | 1.153 | 5.5% | 3.1% | 1.4 |
| Robert Horry | 8.8% | 19.6% | 1.151 | 5.1% | 2.5% | 1.2 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.164Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.512Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.137Z

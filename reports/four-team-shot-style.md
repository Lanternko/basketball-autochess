# 四隊個人出手傾向實驗

固定全屬性70基準，不代表聯盟平均實力；每隊1000場、相同seed、疲勞關閉。舊報表保留不覆蓋。

球員籃板比例來自同季聯盟 OREB / (OREB + DREB)，包含罰球籃板，因此只作目前 live-FG 模型的近似基準。位置／落點／能力影響相對爭搶機率；尚未模擬衝搶後快攻的代價。

| 指標 MAE | 修改前 | 修改後 |
|---|---:|---:|
| pts | 2.212 | 2.048 |
| oreb | 0.514 | 0.423 |
| dreb | 0.691 | 0.652 |
| reb | 0.871 | 0.756 |
| tov | 0.624 | 0.692 |

實驗使用同季 FG3A/FGA 作為三分出手先驗，不是獨立驗證；命中曲線、罰球、失誤及球權公式未改。只啟用於這份報表，未套用遊戲卡表。

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

模擬比分 96.2–75.5；對基準隊勝率 93.8%；每百回合攻／防 136.7／107.3。

真實整隊每百回合攻／防 110.2／103.9（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 21.6 / 22.5 | 4.1 / 3.4 | 1.6 / 2.7 | 0.5 / 1.2 | 0.2 / 0.4 | 52.7% / 44.8% | 24.4 / 28.5 |
| JR Smith | 16.6 / 14.6 | 4.4 / 3.3 | 0.7 / 0.9 | 0.4 / 1.2 | 0.3 / 0.3 | 50.0% / 41.5% | 16.6 / 17.7 |
| LeBron James | 33.7 / 25.5 | 7.2 / 7.5 | 2.4 / 3.3 | 0.6 / 1.4 | 0.6 / 0.7 | 70.1% / 52.0% | 32.9 / 30.5 |
| Kevin Love | 15.1 / 18.3 | 10.2 / 11.3 | 1.1 / 2.1 | 0.5 / 0.9 | 0.7 / 0.6 | 53.4% / 41.9% | 16.6 / 23.3 |
| Tristan Thompson | 9.1 / 10.2 | 10.7 / 11.7 | 0.6 / 1.0 | 0.6 / 0.6 | 1.0 / 0.8 | 67.0% / 58.8% | 9.5 / 11.4 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 21.2–22.0 | 0.6 / 0.9 | 3.5 / 2.4 | 58.9% / 50.2% | 39.8% / 32.1% | 89.1% / 88.5% | 31.5 |
| JR Smith | 16.2–17.0 | 0.7 / 0.7 | 3.7 / 2.7 | 58.6% / 43.8% | 47.1% / 40.0% | 62.7% / 63.4% | 30.7 |
| LeBron James | 33.3–34.2 | 1.2 / 1.5 | 5.9 / 6.0 | 73.4% / 57.3% | 37.2% / 30.9% | 71.4% / 73.1% | 35.6 |
| Kevin Love | 14.8–15.5 | 2.6 / 2.2 | 7.6 / 9.1 | 60.3% / 46.7% | 42.2% / 36.0% | 83.8% / 82.2% | 31.5 |
| Tristan Thompson | 8.9–9.4 | 3.0 / 4.3 | 7.7 / 7.5 | 67.0% / 58.8% | — / — | 58.7% / 61.6% | 27.7 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Kyrie Irving | 36.8% | 17.4% | 1.130 | 6.0% | 2.6% | -1.2 |
| JR Smith | 8.8% | 26.5% | 1.271 | 3.9% | 2.3% | 0.7 |
| LeBron James | 36.8% | 20.9% | 1.281 | 18.9% | 2.7% | 5.5 |
| Kevin Love | 8.9% | 28.7% | 1.168 | 6.2% | 2.7% | -4.4 |
| Tristan Thompson | 8.8% | 6.5% | 1.193 | 10.4% | 3.3% | -0.7 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.702Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:27.246Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2015-16&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612739&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:26.678Z

## 雷霆 2025-26

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 106.3–80.1；對基準隊勝率 97.2%；每百回合攻／防 141.2／106.4。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 35.4 / 33.7 | 5.0 / 4.7 | 1.6 / 2.4 | 0.7 / 1.5 | 0.3 / 0.8 | 64.0% / 55.3% | 31.9 / 32.3 |
| Jalen Williams | 24.3 / 21.7 | 6.2 / 5.9 | 1.6 / 2.4 | 0.5 / 1.5 | 0.5 / 0.3 | 59.6% / 48.4% | 24.3 / 25.2 |
| Chet Holmgren | 21.9 / 21.3 | 11.7 / 11.1 | 1.3 / 1.9 | 0.7 / 0.8 | 1.1 / 2.4 | 70.4% / 55.7% | 19.0 / 21.4 |
| Luguentz Dort | 10.8 / 11.2 | 5.3 / 4.8 | 0.7 / 1.1 | 0.5 / 1.2 | 0.4 / 0.5 | 44.1% / 38.5% | 11.4 / 13.9 |
| Isaiah Hartenstein | 14.0 / 13.7 | 12.9 / 14.0 | 1.7 / 2.6 | 0.5 / 1.5 | 1.1 / 1.1 | 73.9% / 62.2% | 13.5 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 34.9–35.8 | 0.8 / 0.6 | 4.2 / 4.0 | 67.1% / 60.2% | 43.5% / 38.6% | 89.6% / 87.9% | 33.2 |
| Jalen Williams | 23.8–24.7 | 1.1 / 1.0 | 5.1 / 4.8 | 62.0% / 52.3% | 35.8% / 29.9% | 84.4% / 83.7% | 28.4 |
| Chet Holmgren | 21.5–22.3 | 3.4 / 2.3 | 8.3 / 8.7 | 74.8% / 64.6% | 39.6% / 36.2% | 79.9% / 79.2% | 28.9 |
| Luguentz Dort | 10.5–11.1 | 0.8 / 1.1 | 4.5 / 3.7 | 56.7% / 48.7% | 40.3% / 34.4% | 70.7% / 75.9% | 26.8 |
| Isaiah Hartenstein | 13.7–14.3 | 3.6 / 4.7 | 9.3 / 9.3 | 74.1% / 63.7% | 33.3% / 0.0% | 55.9% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.8% | 20.5% | 1.299 | 17.5% | 2.3% | 2.0 |
| Jalen Williams | 33.9% | 17.2% | 1.178 | 9.8% | 2.3% | 0.9 |
| Chet Holmgren | 9.9% | 25.4% | 1.334 | 22.4% | 3.3% | -0.8 |
| Luguentz Dort | 9.8% | 19.0% | 1.121 | 3.2% | 2.7% | -1.4 |
| Isaiah Hartenstein | 9.5% | 17.9% | 1.183 | 11.8% | 3.6% | -0.7 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

## 尼克 2025-26

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=97.71 · 每方 73 回合（35.861 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 100.4–83.2；對基準隊勝率 89.1%；每百回合攻／防 137.0／113.6。

真實整隊每百回合攻／防 118.7／112.3（非同一對戰條件）；每場截斷 0.0010 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 25.7 / 26.8 | 3.9 / 3.4 | 1.5 / 2.4 | 0.5 / 0.8 | 0.3 / 0.1 | 53.2% / 46.7% | 26.9 / 29.6 |
| Mikal Bridges | 17.1 / 15.8 | 4.6 / 4.2 | 0.7 / 1.1 | 0.5 / 1.4 | 0.4 / 0.8 | 61.0% / 49.0% | 16.0 / 17.0 |
| OG Anunoby | 19.2 / 18.1 | 6.5 / 5.7 | 1.5 / 2.0 | 0.5 / 1.7 | 0.6 / 0.8 | 62.6% / 48.4% | 18.2 / 19.4 |
| Karl-Anthony Towns | 23.6 / 23.3 | 13.1 / 13.8 | 2.5 / 2.9 | 0.4 / 1.0 | 1.5 / 0.6 | 67.2% / 50.1% | 23.3 / 25.1 |
| Josh Hart | 14.8 / 14.3 | 6.5 / 8.8 | 1.8 / 2.3 | 0.5 / 1.4 | 0.4 / 0.3 | 58.5% / 50.8% | 15.7 / 16.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 25.3–26.1 | 0.6 / 0.4 | 3.3 / 3.0 | 59.2% / 52.2% | 43.5% / 36.9% | 87.8% / 84.1% | 35.0 |
| Mikal Bridges | 16.8–17.5 | 0.7 / 1.1 | 3.9 / 3.1 | 72.3% / 58.2% | 42.7% / 37.1% | 82.5% / 82.7% | 32.8 |
| OG Anunoby | 18.8–19.6 | 1.1 / 1.4 | 5.3 / 4.3 | 74.7% / 58.4% | 45.2% / 38.6% | 84.3% / 82.8% | 33.2 |
| Karl-Anthony Towns | 23.2–24.0 | 3.9 / 3.6 | 9.2 / 10.2 | 71.7% / 55.7% | 44.7% / 36.8% | 86.4% / 85.8% | 31.0 |
| Josh Hart | 14.4–15.1 | 0.9 / 1.7 | 5.6 / 7.1 | 67.0% / 57.4% | 46.8% / 41.3% | 69.1% / 72.0% | 30.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Jalen Brunson | 38.8% | 15.9% | 1.194 | 8.3% | 2.2% | -0.7 |
| Mikal Bridges | 14.0% | 16.3% | 1.316 | 9.4% | 2.2% | 0.2 |
| OG Anunoby | 14.2% | 19.8% | 1.286 | 18.2% | 3.9% | 0.1 |
| Karl-Anthony Towns | 18.6% | 24.6% | 1.228 | 26.9% | 3.8% | -0.1 |
| Josh Hart | 14.4% | 23.4% | 1.147 | 13.4% | 3.3% | 0.5 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.584Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:30.017Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612752&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:29.660Z

## 湖人 2001-02

對手：PR50 基準隊 · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

n=1000 · seed=20260908 · pace=93.32 · 每方 70 回合（36.005 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 100.1–81.4；對基準隊勝率 91.8%；每百回合攻／防 143.1／116.3。

真實整隊每百回合攻／防 108.0／100.4（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 32.1 / 27.1 | 12.3 / 10.6 | 1.6 / 2.5 | 0.3 / 0.6 | 1.2 / 2.0 | 73.4% / 57.9% | 30.3 / 31.4 |
| Kobe Bryant | 29.2 / 23.7 | 5.1 / 5.2 | 1.6 / 2.6 | 0.5 / 1.4 | 0.3 / 0.4 | 66.3% / 46.9% | 28.7 / 29.9 |
| Derek Fisher | 16.7 / 14.3 | 3.8 / 2.7 | 0.7 / 1.1 | 0.4 / 1.2 | 0.2 / 0.2 | 47.5% / 41.1% | 17.1 / 17.3 |
| Rick Fox | 12.1 / 10.1 | 6.1 / 6.1 | 1.3 / 2.1 | 0.4 / 1.1 | 0.4 / 0.3 | 59.2% / 42.1% | 12.9 / 15.0 |
| Robert Horry | 10.0 / 9.2 | 8.4 / 8.0 | 0.8 / 1.5 | 0.5 / 1.3 | 0.7 / 1.5 | 53.0% / 39.8% | 11.0 / 12.7 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 31.6–32.5 | 3.9 / 3.5 | 8.4 / 7.1 | 73.4% / 58.0% | 20.0% / 0.0% | 57.1% / 55.5% | 36.1 |
| Kobe Bryant | 28.8–29.6 | 0.9 / 1.3 | 4.2 / 3.9 | 67.9% / 48.9% | 39.6% / 25.0% | 86.6% / 82.9% | 38.3 |
| Derek Fisher | 16.3–17.1 | 0.7 / 0.3 | 3.2 / 2.4 | 51.8% / 41.0% | 45.8% / 41.3% | 85.8% / 84.7% | 28.2 |
| Rick Fox | 11.8–12.5 | 1.1 / 1.4 | 5.0 / 4.7 | 69.0% / 47.9% | 42.9% / 31.3% | 81.6% / 82.4% | 27.9 |
| Robert Horry | 9.7–10.3 | 2.3 / 2.2 | 6.0 / 5.9 | 60.0% / 41.6% | 43.1% / 37.4% | 80.1% / 78.3% | 26.5 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shaquille O'Neal | 36.7% | 7.3% | 1.314 | 24.4% | 2.7% | 0.8 |
| Kobe Bryant | 36.7% | 15.1% | 1.270 | 14.8% | 2.3% | 0.6 |
| Derek Fisher | 9.0% | 34.2% | 1.257 | 2.9% | 2.3% | 0.8 |
| Rick Fox | 8.8% | 26.2% | 1.153 | 5.5% | 2.9% | -1.2 |
| Robert Horry | 8.8% | 17.2% | 1.143 | 5.1% | 2.5% | -1.0 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.164Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.512Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2001-02&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612747&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:31.137Z

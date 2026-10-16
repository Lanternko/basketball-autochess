# 36 分鐘等效驗證報表

疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。

**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。

USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。正規化五人 USG 只作代理校準驗收，不代表真實五人陣容的驗收。

抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。

信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。

## 雷霆 2025-26

對手：全屬性 70 壓力測試隊（單項 PR50；非球隊 PR） · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

球權模型：stable；情境 1；失誤倍率 1；失誤底值 0.015；順下接球 0.75。

n=2000 · seed=20261219 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 101.2–77.8；對基準隊勝率 95.3%；每百回合攻／防 134.4／103.3。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 33.3 / 33.7 | 5.0 / 4.7 | 2.0 / 2.4 | 0.7 / 1.5 | 0.3 / 0.8 | 59.8% / 55.3% | 30.7 / 32.3 |
| Jalen Williams | 21.5 / 21.7 | 6.2 / 5.9 | 1.9 / 2.4 | 0.6 / 1.5 | 0.5 / 0.3 | 55.1% / 48.4% | 22.3 / 25.2 |
| Chet Holmgren | 22.5 / 21.3 | 11.5 / 11.1 | 2.3 / 1.9 | 0.7 / 0.8 | 1.0 / 2.4 | 65.1% / 55.7% | 21.2 / 21.4 |
| Luguentz Dort | 10.3 / 11.2 | 5.2 / 4.8 | 0.9 / 1.1 | 0.5 / 1.2 | 0.4 / 0.5 | 48.8% / 38.5% | 11.1 / 13.9 |
| Isaiah Hartenstein | 13.5 / 13.7 | 12.6 / 14.0 | 2.2 / 2.6 | 0.5 / 1.5 | 1.1 / 1.1 | 62.7% / 62.2% | 14.7 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 33.0–33.6 | 0.9 / 0.6 | 4.1 / 4.0 | 66.7% / 60.2% | 42.7% / 38.6% | 89.7% / 87.9% | 33.2 |
| Jalen Williams | 21.2–21.8 | 1.2 / 1.0 | 5.0 / 4.8 | 62.6% / 52.3% | 35.0% / 29.9% | 84.8% / 83.7% | 28.4 |
| Chet Holmgren | 22.2–22.8 | 3.5 / 2.3 | 8.0 / 8.7 | 72.9% / 64.6% | 40.7% / 36.2% | 80.4% / 79.2% | 28.9 |
| Luguentz Dort | 10.1–10.6 | 0.9 / 1.1 | 4.3 / 3.7 | 57.4% / 48.7% | 40.8% / 34.4% | 72.7% / 75.9% | 26.8 |
| Isaiah Hartenstein | 13.3–13.7 | 3.9 / 4.7 | 8.7 / 9.3 | 70.6% / 63.7% | 33.1% / 0.0% | 57.5% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 37.0% | 16.6% | 1.276 | 21.8% | 2.3% | 0.8 |
| Jalen Williams | 33.9% | 13.3% | 1.143 | 9.7% | 2.2% | -1.0 |
| Chet Holmgren | 9.7% | 29.9% | 1.259 | 27.0% | 3.3% | 1.4 |
| Luguentz Dort | 9.7% | 15.7% | 1.117 | 2.7% | 3.0% | -1.8 |
| Isaiah Hartenstein | 9.6% | 24.5% | 1.110 | 9.6% | 3.3% | 0.5 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

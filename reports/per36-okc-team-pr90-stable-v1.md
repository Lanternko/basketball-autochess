# 36 分鐘等效驗證報表

疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。

**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。

USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。正規化五人 USG 只作代理校準驗收，不代表真實五人陣容的驗收。

抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。

信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。

## 雷霆 2025-26

對手：Cleveland Cavaliers · 籃板模型：opportunity · 火鍋：miss-decomposition-v1

球權模型：stable；情境 1；失誤倍率 1；失誤底值 0.015；順下接球 0.75。

n=1000 · seed=20260908 · pace=100.37 · 每方 75 回合（35.867 分鐘等效，再按比例換算到 36 分鐘）

模擬比分 84.7–93.3；對基準隊勝率 26.1%；每百回合攻／防 112.5／124.0。

真實整隊每百回合攻／防 117.6／106.5（非同一對戰條件）；每場截斷 0.0000 次。

| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 26.9 / 33.7 | 4.2 / 4.7 | 2.5 / 2.4 | 0.8 / 1.5 | 0.4 / 0.8 | 51.4% / 55.3% | 29.0 / 32.3 |
| Jalen Williams | 15.6 / 21.7 | 5.3 / 5.9 | 2.2 / 2.4 | 0.2 / 1.5 | 0.5 / 0.3 | 45.6% / 48.4% | 19.7 / 25.2 |
| Chet Holmgren | 21.9 / 21.3 | 10.2 / 11.1 | 3.4 / 1.9 | 0.3 / 0.8 | 1.0 / 2.4 | 56.2% / 55.7% | 24.4 / 21.4 |
| Luguentz Dort | 8.2 / 11.2 | 4.4 / 4.8 | 1.1 / 1.1 | 0.3 / 1.2 | 0.5 / 0.5 | 40.0% / 38.5% | 10.9 / 13.9 |
| Isaiah Hartenstein | 12.2 / 13.7 | 11.2 / 14.0 | 3.1 / 2.6 | 0.4 / 1.5 | 1.3 / 1.1 | 54.8% / 62.2% | 16.0 / 15.3 |

| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 26.4–27.3 | 0.9 / 0.6 | 3.4 / 4.0 | 57.7% / 60.2% | 35.0% / 38.6% | 89.3% / 87.9% | 33.2 |
| Jalen Williams | 15.3–16.0 | 1.2 / 1.0 | 4.1 / 4.8 | 51.7% / 52.3% | 28.2% / 29.9% | 84.0% / 83.7% | 28.4 |
| Chet Holmgren | 21.4–22.3 | 3.6 / 2.3 | 6.7 / 8.7 | 62.7% / 64.6% | 33.8% / 36.2% | 81.2% / 79.2% | 28.9 |
| Luguentz Dort | 8.0–8.5 | 0.9 / 1.1 | 3.6 / 3.7 | 46.9% / 48.7% | 33.5% / 34.4% | 70.5% / 75.9% | 26.8 |
| Isaiah Hartenstein | 11.9–12.5 | 4.0 / 4.7 | 7.1 / 9.3 | 61.7% / 63.7% | 27.6% / 0.0% | 58.0% / 61.0% | 24.2 |

### 球權與包夾診斷

| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |
|---|---:|---:|---:|---:|---:|---:|
| Shai Gilgeous-Alexander | 36.7% | 17.4% | 1.106 | 21.8% | 2.9% | -0.8 |
| Jalen Williams | 33.9% | 13.6% | 0.960 | 9.6% | 3.0% | -3.6 |
| Chet Holmgren | 9.8% | 29.9% | 1.088 | 27.1% | 4.8% | 4.6 |
| Luguentz Dort | 9.8% | 14.2% | 0.922 | 2.6% | 3.7% | -1.9 |
| Isaiah Hartenstein | 9.8% | 25.0% | 0.936 | 9.7% | 4.4% | 1.8 |

- [NBA base](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Base&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.228Z
- [NBA advanced](https://stats.nba.com/stats/leaguedashplayerstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=Totals&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.566Z
- [NBA team](https://stats.nba.com/stats/leaguedashteamstats?LeagueID=00&Season=2025-26&SeasonType=Regular+Season&PerMode=PerGame&MeasureType=Advanced&TeamID=1610612760&LastNGames=0&Month=0&OpponentTeamID=0&PaceAdjust=N&PlusMinus=N&Rank=N&Period=0) · 擷取 2026-09-08T00:04:28.296Z

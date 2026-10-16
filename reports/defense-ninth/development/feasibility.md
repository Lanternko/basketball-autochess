# 三個候選盲測季：僅查端點與格式，不下載比賽資料

查詢時間、網址、HTTP標頭結果保留於 [endpoint-probes.json](endpoint-probes.json)。所有新球季 API 請求均使用 HEAD，沒有 GET box／PBP／tracking／賽程內容，也沒有建立新球季資料目錄。文件查閱僅用來核對端點與欄位。

## 已驗證

| 球季 | CDN box／PBP 標頭 | Stats log／tracking／box v3／PBP v3 標頭 | 本次能否確認直接進現有流程 |
|---|---|---|---|
| 2021–22 | 403／403 | 均15秒逾時 | 不能；尚未驗證歷史內容與格式 |
| 2018–19 | 403／403 | 均15秒逾時 | 不能；尚未驗證歷史內容與格式 |
| 2017–18 | 403／403 | 均15秒逾時 | 不能；尚未驗證歷史內容與格式 |

**不能據此說資料不存在。** 已在本機成功下載、參與第八批的 2023–24 box／PBP 控制網址，HEAD 同樣回403。這個探測對區分「檔案缺失」與「HEAD／網路受阻」沒有鑑別力；沒有把403改標成404，也沒有改成GET取得樣本。

公開的客戶端原始文件列有：

- [Stats PBP v3](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/playbyplayv3.md)：包括 actionNumber、period、clock、teamId、personId、scoreHome／Away、shotResult、actionType、subType。文件的驗證 URL 使用 `0021700807`，是支持2017–18歷史查詢的文件證據，非本次成功取得資料。
- [Stats box v3](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/boxscoretraditionalv3.md)：包括 personId、position、minutes、points、plusMinusPoints 及 box 計數；也列 `0021700807` 的驗證 URL。
- [防守 tracking](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashptdefend.md)：有 Season、DateFrom／DateTo、TeamID、DefenseCategory（3 Pointers／Less Than 6Ft）參數；能對照現有查詢契約。文件沒有證明這三季每個截止日、每隊都非空，亦未證明GP日期篩選正確。
- [客戶端版本紀錄](https://github.com/swar/nba_api/releases)：PBP v2 有停用／空JSON警告，不把它列為已確認可用的救援路徑。

## 格式對照與需要的工作

現有抓取／重建走 CDN `game.actions` 與 `game.homeTeam/awayTeam.players`。Stats v3 的列／封裝格式不同；PBP 文件沒有列 CDN 的全部 qualifiers、personIds、助攻／換人／犯規細項欄位。即使網址可取得，不能直接把檔案換進既有重建器。

若後續獲准進入盲測，先做固定、只轉格式的資料介面：Stats v3→現有事件契約；保留原欄位，缺資料明列，不能用比分或手改分鐘補回。然後用原分鐘、五人、得分與四要素計數稽核。轉換器不得依盲測準確度改引擎或能力流程。Box starter/position 推導也需要獨立核對。

新季基本 log／bio 的端點契約已有，但本次的網路探測尚未確認歷史回應。v3／v4仍需要其截止日前 tracking、完整訓練 box 與嚴格區段，不只是有終場比分即可。

## 推測與覆蓋風險

2021–22 比2017–18／2018–19接近已跑的資料年代，可能比較容易接入，但這是推測。三季目前均沒有可辯護的嚴格覆蓋率點估計。先前四季嚴格覆蓋86.42–96.59%是已看過答案的實測，只能作工作量參考，不能當作舊季保證。

較早兩季若只能用Stats格式，換人語義、同時事件順序、跳球／團隊留球與出手分區資訊不足，可能使嚴格失敗超過15%、觸發85%覆蓋門檻。2021–22亦有相同可能。未讀任何新季逐場內容，不能量化哪一種失敗佔多少，也不能宣稱三季都已可進完整流程。

因此本項結論是：**端點與部分歷史格式有文件依據，當前路由／內容／嚴格覆蓋尚未驗證，三季盲測可行性仍有條件。** 若增量診斷停止，則不為確認覆蓋而下載；若通過，盲測前先凍結方法與格式處理規則，再按使用者下一步授權進行資料稽核。

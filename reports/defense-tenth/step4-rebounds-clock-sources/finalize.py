from pathlib import Path
import json,hashlib,datetime,cv2
R=Path('reports/defense-tenth/step4-rebounds-clock-sources');load=lambda f:json.loads(Path(f).read_text(encoding='utf8'))
ann=[{'game':'0022300806','season':'2023-24','date':'2024-02-23','sourcePage':'https://official.nba.com/archive/24-second-shot-clock-reset-suns-rockets/','videoFile':'clips/rim-yes-2024.mp4','shotAction':671,'reboundAction':672,'player':'Amen Thompson','officialRimContact':True,'officialEvidence':'Replay Center explicitly determined ball hit rim','possessionObservation':'white jersey number 1 gains control in basket area around 3.5-4.1s of clip; coarse interval, not frame-exact','videoClockObservation':{'clipSeconds':3.8,'broadcastGameClock':'1:38','broadcastShotClock':2.8,'status':'displayed count continues; not the legally required fresh14 state'},'legalReset':'14 on offensive control under Rule7; not inferred from displayed clock','inPriorIndividualAnchorPopulation':True,'use':'independent validation only; not input feature or probability sample','uncertainty':'first contact frame and exact control time not adjudicated by a second annotator; displayed clock not ground truth'}, {'game':'0022200722','season':'2022-23','date':'2023-01-25','sourcePage':'https://official.nba.com/archive/24-second-shot-clock-reset-wizards-rockets/','videoFile':'clips/rim-no-2023.mp4','shotAction':659,'reboundAction':660,'turnoverAction':661,'officialRimContact':False,'officialEvidence':'Replay Center explicitly determined ball did not hit rim','possessionObservation':'no independently labeled new offensive control instant; retain unknown','videoClockObservation':{'clipSeconds':8.5,'broadcastGameClock':'1:28','broadcastShotClock':0.8,'status':'screen reading before clock violation; not a rebound-time clock measurement'},'legalReset':'none from this missed shot','inPriorIndividualAnchorPopulation':False,'exclusionReason':'TEAM offensive rebound, not individual FG OREB','use':'source/label demonstration only; cannot silently add to prior individual-anchor sample','uncertainty':'no new individual OREB control label; source shot and team placeholder must remain distinct'}]
for a in ann:
 cap=cv2.VideoCapture(str(R/a['videoFile']));a['decodedFrames']=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));a['fps']=cap.get(cv2.CAP_PROP_FPS);a['durationSeconds']=a['decodedFrames']/a['fps'];assert a['decodedFrames']>0
(R/'annotations.json').write_text(json.dumps(ann,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
protected=load('reports/defense-tenth/step4-rebounds-clock-state/protected-before.json');protected.update(load('reports/defense-tenth/step4-rebounds-turnover-time/protected-before.json'));protected.update(load('reports/defense-tenth/step4-rebounds-clock-state/deliverable-hashes.json'));bad=[f for f,h in protected.items() if not Path(f).exists() or hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h];assert not bad
sha=hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest();assert sha==(R/'protocol.sha256').read_text().strip()
audit={'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocolSHA':sha,'protectedFiles':len(protected),'changed':bad,'engineChanged':False,'simulationRun':False,'officialMetadataProbes':12,'nonNullVideoURL':11,'regularClipsDownloaded':7,'regularClipsAllIdenticalPlaceholder':True,'placeholderSHA':'afcfdc3190903e3fc13c56c054fa40c39d1775af4a53d40ce040d6a25ea3ad3e','actualReplayClipsDecoded':2,'currentSampleIndependentLabels':1,'representativeCalibrationSampleAvailable':False}
(R/'audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf8')
report='''# 碰框與進攻時鐘：公開來源實測

結論：找到可實際觀看的官方重播影片與明確碰框判決。已下載並逐格抽圖檢查兩個案例（一有碰框、一無碰框），但還沒有四季具代表性的稽核樣本；不能估違例機率，也沒有新模擬或 MAE 結果。

## 已驗證的可用來源

|來源|實測結果|用途與界線|
|---|---|---|
|NBA Replay Center：2024-02-23 太陽@火箭|真正比賽影片，13.45秒，60fps，9.14MB；官方判定碰框|能連接本機2023–24投籃671、個人OREB672；一個直接獨立標籤|
|NBA Replay Center：2023-01-25 巫師@火箭|真正比賽影片，53.2秒，60fps，25.92MB；官方判定未碰框|連接本機2022–23投籃659、團隊籃板660、違例661；團隊籃板不屬於前批個人OREB樣本|
|NBA官方YouTube完整比賽候選|獨行俠@老鷹2024-01-26，oEmbed確認為NBA頻道、標題Full Game|只驗證公開metadata，尚未驗證全片播放、是否有剪輯或各個OREB的可見性|

官方判決來源：
- [太陽@火箭：有碰框](https://official.nba.com/archive/24-second-shot-clock-reset-suns-rockets/)
- [巫師@火箭：未碰框](https://official.nba.com/archive/24-second-shot-clock-reset-wizards-rockets/)
- [NBA頻道完整比賽候選](https://www.youtube.com/watch?v=sN8v9Uus6xw)

原始影片保存在 clips/；來源HTTP回應、網址、SHA與事件對照均已保留。annotations.json記錄標籤的來源、限制與畫面時間；不把官方事後判決餵給模擬。

## 重要發現：畫面顯示的時鐘也會錯

太陽@火箭的影片約3.8秒，畫面比賽時間1:38、轉播進攻時鐘2.8，Amen Thompson在籃下已取得球。畫面時鐘仍在沿用舊倒數；官方事後確認前一球確實碰框。按Rule7此個人進攻籃板應取得新的14秒。

因此要分開記錄四個東西：碰框判定、重新控制球時點、實際顯示的倒數、規則上應有的倒數。不能用「時鐘沒跳14」反推沒碰框，不能把轉播overlay直接當成合法時鐘答案。此案例本來就是被挑出重播的疑難球，不代表一般比賽錯鐘頻率。

[Rule7](https://official.nba.com/rule-no-7-24-second-clock)規定碰框後進攻方先取得球權重設14秒；[Rule13](https://official.nba.com/rule-no-13-instant-replay/)列出的時鐘證據優先順序以籃板上方計時器優先，轉播疊圖在後。官方頁面沿用「24-Second Shot Clock Reset」分類標題，不代表此球應重設24秒。

## 不可用與未驗證來源

1. **一般事件影片端點有假成功。** 使用前批每季第一個早期違例案例，投籃／籃板／違例共12次metadata請求全為HTTP200，11次有非空影片URL。實際下載其中7支投籃／違例影片，全部為同一SHA、869898 bytes、15.015秒的「VIDEO NOT AVAILABLE」佔位片。0支可標註；不能把11/12當影片覆蓋率。本次只有這四個疑難案例，不能推論全季所有事件影片都不可用。保留frame-access.jpg作證據。
2. **PBPStats tracking：有相關人工資料，但需會員。** 首頁列出三分出手時鐘與籃板位置人工標註，顯示27002次投籃、7172次籃板。沒有證據證明具備這四季所有OREB的碰框、重新控制與完整時鐘軌跡；未登入、未付費、未下載會員資料。[來源](https://tracking.pbpstats.com/)
3. **一般PBPStats增強逐球不是獨立時鐘答案。** 其公開程式能辨認非真籃板的placeholder，包括同刻違例的團隊籃板；仍不能以同一原始PBP推算的量充當碰框實測。[來源程式](https://pbpstats.readthedocs.io/en/latest/_modules/pbpstats/resources/enhanced_pbp/rebound.html)
4. **公開完整比賽索引**：下載189筆metadata，其中13筆日期在2022-10-01後，均在2024或2025日曆年。它們是被挑選公開的比賽、並非四季隨機樣本；影片未隨資料集提供。另抽查雷霆@騎士2025-01-08，oEmbed可用但頻道為Time for Basketball，並非NBA官方，未視為可直接採用的影片。full-game-candidates.json保留13筆待驗證線索。[作者資料集](https://github.com/choucisan/nba_games)
5. **LiveStats有shotClock欄位的文件**，但文件明載為場館LAN的TV feed，沒有查到本專案四季NBA的公開歷史資料；不能把欄位文件當已取得資料。[文件](https://d5wkep07po6si.cloudfront.net/livestats/tvfeed/index_basketball.html)
6. 舊data.nba.net範例路徑連線失敗；不據此斷言所有舊服務失效。
7. 2018金塊@灰狼另有官方未碰框判決文字，但頁面沒有嵌入可取的影片，且不在本批四季；只作來源線索，沒有混入樣本。[來源](https://official.nba.com/archive/13189-24-second-shot-clock-reset-nuggets-at-timberwolves/)

## 推測與下一步建議（未執行）

官方Replay Center最適合提供高可信度的「有／無碰框」案例與錯鐘案例，但選樣集中最後兩分鐘的爭議球。建議分兩條用途：
- 用官方判決案例驗證狀態邏輯、placeholder排除與錯鐘處理；不校準發生率。
- 用可完整觀看的官方全場影片，先固定場次與抽樣方式，再抽取一般OREB，對碰框、取得控制、籃板上方時鐘及轉播時鐘分欄標記；遮擋仍為unknown。要估聯盟發生率還須跨隊跨季補足代表性，不能只挑這些精彩完整賽。

這次證實來源可取得，並未證實能大規模覆蓋四季。下一批最值得做的是建立小型人工稽核集並量可標註率，先不要改引擎機率。

## 重跑與完整性

```powershell
node reports/defense-tenth/step4-rebounds-clock-sources/probe.mjs
node reports/defense-tenth/step4-rebounds-clock-sources/download.mjs
node reports/defense-tenth/step4-rebounds-clock-sources/secondary.mjs
node reports/defense-tenth/step4-rebounds-clock-sources/replays.mjs
node reports/defense-tenth/step4-rebounds-clock-sources/more-replays.mjs
node reports/defense-tenth/step4-rebounds-clock-sources/full-game-access.mjs
python reports/defense-tenth/step4-rebounds-clock-sources/finalize.py
```

網路回應與影片可用性可能隨時間變化。下載腳本只表示HTTP取回，annotations/audit才區分可解碼影片與不可用佔位片。來源抽圖為本次人工檢視紀錄；不宣稱有第二位標註者。
'''
report+=f"\nprotocol SHA-256：`{sha}`。{len(protected)}個既有保護檔內容未變。未改引擎、卡、基準或前批報告。本批到此停止。\n"
(R/'report.md').write_text(report,encoding='utf8')
files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'};(R/'deliverable-hashes.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf8');print(json.dumps(audit,indent=2))

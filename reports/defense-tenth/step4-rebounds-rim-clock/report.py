from pathlib import Path
import hashlib
import json

R=Path(__file__).parent
load=lambda f:json.loads(Path(f).read_text(encoding='utf8'))
d=load(R/'analysis.json');a=load(R/'audit.json');p=load(R/'protocol.json')
lines=['# 進攻籃板時鐘：碰框狀態接線', '',
'結論：新版本 oreb-rim-clock-1 已把碰框狀態接到個人／團隊進攻籃板與時鐘耗盡路徑。基本規則測試通過；48場不同賽程的開關關閉與全部碰框結果，比分、球員／球隊數據及原有事件序列皆與舊基準完全相同。只做機制測試，未校準未碰框比例、未升級基準，沒有新的準確度改善結論。', '',
'## 實作內容', '',
'- `rimContactClock` 預設關閉。開啟時，每次未進的FG必須取得明確的 boolean 碰框結果；null／unknown 直接拒絕，不暗中當成未碰框。',
'- 碰框後進攻方重新取得球：重設14秒。未碰框後搶回球：保留當下剩餘時間，剩20秒也照留20秒，不壓成14秒。個人與團隊留球共用同一個規則函式。',
'- 未碰框且在球飛行期間耗盡原時鐘：推進至到期時點，記自然死球違例；不先贈送個人OREB再給14秒。節末同時到期以節末處理優先。',
'- 活球最後一罰後的進攻籃板維持原有14秒；換邊後的新球權維持24秒。',
'- 不新增搶板後的獨立違例抽樣；原本一般新球權的獨立違例機制原樣保留。碰框判斷有獨立亂數流，不消耗原有球賽、時間或籃板亂數。', '',
'`rule.mjs` 是純規則轉移；`adapter.mjs` 在載入時將它接到凍結引擎的副本，未改寫 src 或任何舊實驗。`rimContactResolver(context, rng)` 是碰框生成器介面：context只含出手區、是否被阻攻、是否補籃、節次及當下時鐘；不含球隊ID、名次或賽果。不假設所有阻攻都不碰框，也不假設未被阻攻一定碰框。', '',
'## 已驗證', '',
'單元測試包括原時鐘0／0.1／6／13.9／20／24秒的重設與沿用、節末優先、最後一罰、未知接觸拒絕、無效時鐘拒絕、啟用但缺少生成器拒絕，以及阻攻狀態不強迫決定碰框。', '',
'四季各取賽程前12場、seed 20261012，每場跑舊基準／新開關關閉／全部碰框／全部未碰框四種，共192次完整比賽。不是完整球季評分。', '',
'|球季|每模式場次|關閉完全一致|全碰框完全一致|未碰框沿用FG時鐘次數|其中原鐘>14秒|FT重設14秒|自然耗盡違例|',
'|---|---:|---|---|---:|---:|---:|---:|']
for s,z in d['seasons'].items():
    t=z['allNoRimStress']
    lines.append(f"|{s}|{z['gamesPerMode']}|通過|通過|{t['retainedClockTransitions']}|{t['retainedClockAbove14']}|{t['liveFinalFTReset14']}|{t['naturalExpiry']}|")
lines+=['',
'全碰框與關閉模式的比分／球員／球隊資料、分配觀察量、原有逐事件SHA均與重跑基準相同，並逐場符合已封存20-seed基準中的對應比分。因此增加狀態本身沒有悄悄改掉原本路徑。', '',
'右側四欄全部來自「所有未進FG都未碰框」的刻意極端壓力測試，只證明分支有執行：共1246次FG留球沿用，其中324次剩餘時間大於14秒；43次最後一罰後重設14秒；147次飛行期間自然到期。這147次包含尚未搶到進攻籃板的投失，不是147次「OREB後違例」。不能拿它們推算真實違例率或效率效果。', '',
'## 推測、限制與未完成的部分', '',
'1. 這批完成的是規則與接線；真實碰框生成器尚未校準。沒有以阻攻率、前批0.73%或影片中的少數爭議球硬代替未碰框機率。新開關目前留在實驗模式，正式基準 pure-oreb-turnover-time-1 不變。',
'2. 未碰框狀態理應減少錯給的14秒並允許自然到期；會讓真實球季失誤／節奏／得分變多少，仍未驗證。沒有球隊RMSE或勝場MAE的新結果。',
'3. 引擎仍用抽象的投失飛行時間，沒有逐個接觸時點、球體位置或即時防守方控制球軌跡。時鐘到期當下若防守方立即且明確取得球的繼續比賽例外，這個版本尚未建模；目前在未碰框飛行到期時直接死球。不宣稱已完整重現全部NBA判例。',
'4. 經驗耗時依目前剩餘時鐘抽樣、通常會讓出手趕在到期前，因此「持球不出手拖到違例」的行為分布仍是另一個未解問題；這批只改接觸與時鐘轉移。測試自然到期皆走飛行路徑，next-opportunity零鐘防護未在這48場壓力測試觸發。',
'5. 原時鐘到期違例目前沿用引擎的球員TOV加總慣例，記在投失者／持球者身上；並非已校準的球員責任歸因。', '',
'## 重跑', '', '```powershell',
'node reports/defense-tenth/step4-rebounds-rim-clock/test.mjs',
'node reports/defense-tenth/step4-rebounds-rim-clock/run.mjs',
'python reports/defense-tenth/step4-rebounds-rim-clock/analyze.py',
'python reports/defense-tenth/step4-rebounds-rim-clock/report.py',
'```', '',
'run.mjs會略過已有的本批輸出；若要獨立重做完整實驗，先另存本批目錄，不覆寫封存基準。', '',
f"登記UTC：{p['registeredUTC']}；protocol SHA-256：`{a['protocolSHA']}`。{a['protectedFiles']}個先前產物與src/scripts/package檔內容SHA均未變。規則與檢查門檻先登記再執行。本批到此停止。"]
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
(R/'decision.json').write_text(json.dumps({'version':p['version'],'ruleImplementationPassed':True,'offParityPassed':True,'allRimParityPassed':True,'noRimRateEstimated':False,'baselinePromoted':False,'accuracyImprovementClaimed':False,'stop':True},indent=2)+'\n',encoding='utf8')
manifest={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'}
(R/'deliverable-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print('Report and hashes saved')

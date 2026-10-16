import pathlib,json,hashlib
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');d=load(R/'timing-audit.json');s=load(R/'source-verification.json');a=load(R/'audit.json');assert not d['registered95pctGuardPassed'];assert not a['issues'];assert hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest()==(R/'protocol.sha256').read_text().strip()
decision={'candidateImplemented':False,'simulationRun':False,'baselineChanged':False,'reason':'registered necessary timing guard failed: only16.42% of eligible observed postOREB clock losses compatible with >=13sec elapsed; cannot use all0.73% as fresh14sec violation target','previousInterpretationCorrected':'engine lacks independent post-reset clock sampling, but prior overall clock loss incidence does not identify this missing fresh14 process','noNewConstants':True,'noCardOrEngineChanges':True,'nextProposal':'reconstruct rim-contact/reset/remaining-shot-clock states with explicit unknowns before calibrating a hazard; do not infer all blocks as no-rim or all rebounds as fresh14 resets','protocolSHA':a['protocolSHA']};(R/'decision.json').write_text(json.dumps(decision,indent=2)+'\n',encoding='utf8')
L=['# 進攻籃板後14秒違例：先驗證重設前提','',
'結論：推翻「把先前0.73%的搶板後違例全部補成新的14秒違例」這個修法。本輪依預登記門檻停在來源與時序診斷，沒有新增機率、沒有跑候選模擬、沒有改基準。上一批對0.73%的歸因過快：程式缺少重設後獨立抽樣是真，但觀察到的違例大多不符合新14秒已走完的時間條件。','',
f"版本 `{p['version']}`；登記 UTC `{p['registeredUTC']}`；SHA-256 `{a['protocolSHA']}`。四季皆已看過答案／當季in-sample。規則先登記再重新讀取逐球；不是盲測。",'',
'## 已驗證：大部分事件不是新的14秒用完','',
'起點沿用有效個人FG進攻籃板、相同得分核對與特殊FT排除。這次用所有起點稽核（不是只取每球權第一個），校準候選的暴露條件固定為當節剩餘>14秒；終點為首次己方FG／普通FT前的官方shot clock失誤。每列保留原始比賽、投失、籃板與失誤action編號。','',
'預先登記：容許一秒時間戳誤差，把搶板至違例>=13秒視為「可能與完整14秒相容」的必要條件；若不足95%的目標事件符合，就不實作強制14秒違例。相容不代表已證實碰框、無中途重設或資料正確。','',
'| 球季 | 可用比賽 | 剩>14秒的OREB起點 | 其後先時鐘違例 | <3秒 | 3～<13秒 | >=13秒 | 時間相容比例 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for season,x in d['perSeason'].items():
 q=x['counts'];L.append(f"| {season} | {x['games']} | {q['eligible']} | {q['eligibleClock']} | {q['under3']} | {q['from3to13']} | {q['compatible']} | {100*x['compatibleShare']:.2f}% |")
ci=d['equalSeasonCompatible95Franchise'];early=sum(x['counts']['under3']/x['counts']['eligibleClock'] for x in d['perSeason'].values())/4;lateRate=sum(x['counts']['compatible']/x['counts']['eligible'] for x in d['perSeason'].values())/4
L+=['',f"四季等權時間相容比例僅{100*d['equalSeasonCompatibleShare']:.2f}%，franchise重抽20,000次95%區間 [{100*ci[0]:.2f}%, {100*ci[1]:.2f}%]，遠低於預登記95%門檻。不到三秒即違例的比例為{100*early:.2f}%；約83.58%在13秒之前就違例。此處只有真實事件，沒有seed雜訊，所以區間是球隊抽樣，不虛構seed重抽。",'',
f">=13秒相容事件約占所有剩>14秒起點的{100*lateRate:.3f}%；這也不是可直接使用的14秒機率，因為仍未確認碰框及途中重設。先前0.73%使用每球權第一起點、剩>=3秒口徑，本表用所有起點、剩>14秒；分母不同，不把兩者的小差當成新發現。",'',
'## 規則與程式稽核','',
'NBA規則要求未成功FG碰到籃圈後、進攻方首先重新取得球權才重設14秒；FG未碰圈則不重設。見[NBA官方Rule7，SectionIV(b)(5)、IV(d)(1)](https://official.nba.com/rule-no-7-24-second-clock)。所以「記到進攻籃板」本身不能當成完整14秒已重設的證據。','',
'- src/defense_fourth_game.js:197 對個人進攻籃板一律shotClock=140；177行對團隊進攻留球亦重設，沒有碰框狀態。',
'- 同檔366～371行會產生blocker並記FGX，但rebound(shooter,zone)沒有接收blocker或rim-contact狀態。被封阻不必然未碰框，因此也不能直接把所有block當作不重設。',
'- 同檔393行只在新POSSESSION抽plannedViolation；241行消耗後清除；301行在independentClock啟用時阻止由耗時撞限產生違例。這確實缺少後續時鐘事件，但不能用混雜的0.73%直接補。','',
'## 原始資料核驗與個案','',
f"共核驗{s['allClockEventsVerified']}筆（含當節剩<=14秒）搶板後shot clock失誤：投失與籃板參照、球隊、節次、事件先後、原始時鐘差均一致；所有目標事件時間差非負。短於13秒事件中沒有介於籃板與違例之間的犯規；不能用這些犯規解釋短時距。",'',
'逐筆完整索引在clock-events.json；source-examples.json固定取每季賽程順序最早兩筆<13秒事件，沒有挑好看的例子。例：2023–24的0022300074，J. Grant投失被封阻→05:28進攻籃板→同為05:28球隊shot clock失誤。2025–26的0022500095，Zion於02:55進攻籃板→同為02:55球隊shot clock失誤。這些來源不能被排成搶板後再耗14秒的事件。','',
'來源的這些shot／rebound／turnover紀錄沒有明確rim-contact或實際shot-clock欄位。短時距違例之前的投失，被封阻比例四季約40～48%；全部可用OREB投失被封阻比例約10%。這是事後描述性關聯，不是無碰框分類器；未被封阻的短時距事件也很多。','',
'## 推測、失敗與不確定','',
'- 已驗證：新14秒的單一補抽前提不成立；引擎對FG進攻籃板無條件重設；來源多為短時距官方shot clock失誤。',
'- 推測：有一部分可能是未碰框／封阻後沿用原時鐘，或逐球記帳時點與實際控制球時點不同。僅憑事件時間與block欄位，不能判定每筆屬哪種。',
'- 未識別：真正無碰框率、每次OREB實際剩餘shot clock、是否應重設、取得球權的精確時點；不能用違例樣本中的83.58%去估全體未碰框率。',
'- 失敗／未完成：沒有得到可驗證的14秒抽樣機率，沒有產生候選或MAE進步證據；不是把基準不變當成一次成功驗收。',
'- 本批沒合併任何先前候選，沒有更動球員卡、籃板取得／歸屬、失誤、犯規、時鐘或聯盟常數。','',
'## 下一步提案（本輪不實作）','',
'先重建可稽核的進攻時鐘狀態，分開「確認應重設」「確認沿用」「資料不足」。沿時間順序保留出手前剩餘時鐘、投失飛行／封阻、接觸籃圈、重新控制球與犯規留球。只在資訊足夠的區段核對時間，未知不硬補；不得靠後來是否違例反推當下碰框再拿去當驗證。先量可識別覆蓋率與時鐘誤差，再決定新增哪一條風險及校準方式。不能以所有封阻都不碰框、或所有進攻籃板都有14秒替代。','',
'## 完整性與重跑','',
f"真實逐球可用1230／1230／1229／1227場；四場缺資料清單保留在real.json。新讀取與前次樣本逐筆核對通過（parity.json）。{a['protectedFiles']}份受保護檔案SHA未改，protocol SHA核對通過，基準和所有舊輸出不動。沒有新模擬，所以不重列net／wins分數當成新結果。",'',
'```powershell',
'node reports/defense-tenth/step4-rebounds-clock14/read.mjs',
'python reports/defense-tenth/step4-rebounds-clock14/audit-timing.py',
'python reports/defense-tenth/step4-rebounds-clock14/verify.py',
'python reports/defense-tenth/step4-rebounds-clock14/report.py','```','',
'本批在預登記guard失敗後停止；不另改門檻、不調出一個能過關的14秒率，也不自行開始下一批。']
(R/'report.md').write_text('\n'.join(L)+'\n',encoding='utf8');files={str(f.relative_to(R)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'};(R/'deliverable-hashes.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf8');print('Complete',len(files),'files, no candidate; compatibility',d['equalSeasonCompatibleShare'])

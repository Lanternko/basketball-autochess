import json,pathlib,hashlib
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));d=load(R/'analysis.json');old=load(R.parent/'step4-rebounds-paths/analysis.json');s=load(R/'summary.json');p=load(R/'protocol.json');a=load(R/'audit.json');parity=load(R/'parity.json')
assert hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest()==(R/'protocol.sha256').read_text().strip()
for k,x in d['pooledOverall'].items():
 for field in ['real','sim','delta']:assert abs(x[field]-old['pooledOverall'][k][field])<1e-12,(k,field)
impact={'zoneOnly':True,'allUnzonedPooledMetricsUnchanged':True,'routes':{k:{'oldReal':old['pooledRoutes'].get(k),'correctedRealAndFrozenSimulation':v} for k,v in d['pooledRoutes'].items()}}
(R/'reader-impact.json').write_text(json.dumps(impact,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# 獨立分區讀取修正版：進攻籃板後的出手分布','',
'結論：修正矛盾分區後，舊診斷的方向反轉。模擬搶板後籃下出手機會偏少、中距離偏多；不是籃下出手過多、中距離不足。這一批只修診斷讀取口徑，沒有修改卡、機率、時鐘、個人籃板分配或凍結版本，也沒有新準確度提升可宣稱。','',
f"版本 `{p['version']}`；登記UTC `{p['registeredUTC']}`；SHA-256 `{a['protocolSHA']}`。四季均已看過答案，當季重現診斷。模擬直接沿用既有12個season-seed，不重跑。聯合區間為3seed、20,000次franchise＋seed跨季配對重抽，四季等權；不作20seed版本採用檢定。",'',
'## 規則與來源稽核','',
'只修正 actionType=2pt、area=Mid-Range，且以下三項同時成立的事件：','',
'1. 動作文字含Layup／DUNK／tip／putback。','2. 原始shotDistance為0–4呎。','3. x、y座標有效，換算距最近籃框不超過4呎。','',
'三項都支持籃下才改判short；名義中距離存在近框衝突但證據不齊則列unknown。3pt以動作類型判long，已識別paint維持short，正常Mid-Range維持mid，未識別2pt區域列unknown。分類不使用命中／投失、球員ID、球隊或勝場；座標僅判投籃位置，並非搶板落點追蹤。完整規則見protocol.json、zone.mjs。','',
'| 球季 | 稽核全部FG事件 | Mid→籃下 | unresolved／unknown | 可用場數 |','|---|---:|---:|---:|---:|']
for season,x in s['seasons'].items():
 n=x['allFG'];g=next(z['games'] for z in parity if z['season']==season);lines.append(f"| {season} | {n['n']} | {n['repaired']} | {n['unknown']} | {g} |")
lines+=['','合計10,767筆FG事件修正為籃下；969筆列unknown。是新讀取器的輸出，不回寫原始PBP。所有改判與未解清單存於source-audit.json。','',
'## 搶板後第一個進攻事件：修正前後','',
'分母是含有效球員FG進攻籃板的球權，每個球權只取第一個有效OREB。以下是「先出手在該區」的機率，不是條件於FG的分區占比；其餘為先FT、先失去球權、節末。','',
'| 路徑 | 真實舊標籤 | 真實修正後 | 凍結模擬 | 模擬−修正真實（百分點），聯合95% |','|---|---:|---:|---:|---:|']
for k,label in [('fg_short','籃下／禁區'),('fg_mid','中距離'),('fg_long','三分'),('fg_unknown','未判定分區')]:
 x=d['pooledRoutes'][k];o=old['pooledRoutes'].get(k,{}).get('realProbability',0);ci=x['probabilityDeltaInterval'];interval='不作模型表現判定' if k=='fg_unknown' else f"{ci['delta']*100:+.3f} [{ci['joint95'][0]*100:+.3f}, {ci['joint95'][1]*100:+.3f}]";lines.append(f"| {label} | {o*100:.3f}% | {x['realProbability']*100:.3f}% | {x['simProbability']*100:.3f}% | {interval} |")
lines+=['','unknown約占所有搶板後第一次FG的0.108%；保留於FG與得分總數，不塞回mid。模擬沒有資料缺漏unknown類別，故不以unknown對模擬的差值評估機制好壞。','',
'| 先FG路徑的第一球命中率 | 真實修正後 | 凍結模擬 | 模擬−真實（百分點），聯合95% |','|---|---:|---:|---:|']
for k,label in [('fg_short','籃下／禁區'),('fg_mid','中距離'),('fg_long','三分')]:
 x=d['pooledRoutes'][k];ci=x['firstFgMakeDeltaInterval'];lines.append(f"| {label} | {x['realFirstFgMake']*100:.3f}% | {x['simFirstFgMake']*100:.3f}% | {ci['delta']*100:+.3f} [{ci['joint95'][0]*100:+.3f}, {ci['joint95'][1]*100:+.3f}] |")
lines+=['','中距離真實命中率由60.95%修正為40.71%，模擬42.86%；不支持提高中距離命中率。修正後籃下真實58.99%、模擬56.49%，才是值得進一步拆解的條件命中率差異。仍需控制補籃／重攻、出手者與防守情境，不能把2.50百分點直接全加到投籃卡。','',
'## 補籃proxy的參考答案也改變','']
q=s['pooled']['quickProxy'];lines += [f"相同首次OREB球權樣本，『同一搶板者、首個FG在3秒內、判為籃下』的真實proxy：舊讀取器{q['oldQuickProxy']*100:.3f}%，新讀取器{q['quickProxy']*100:.3f}%。符合時間／同人但分區unknown另有{q['quickUnknown']*100:.3f}%。這是來源修正造成的重分類，並非新模擬或真實比賽變化。",'',
'本次未重跑帶同一首次球權標記的模擬事件觀察器，因此不把歷史all-anchor／另一種特殊FT處理樣本的30–31%拿來直接比較，也不聲稱引擎補籃頻率現已對齊。舊報告保留，但依賴short標籤的proxy結論需重新驗證。','',
'## 不變項、限制與下一步','',
f"逐筆核對{sum(x['anchorRows'] for x in parity):,}個有效OREB記錄：只有route與firstFgZone可變，其餘舊欄位完全相同。完整得分仍是真實1.26733、模擬1.19124；差−0.07609，聯合95% [−0.08682,−0.06572]。出手前先失去球權8.02%對10.50%、第一次投失再搶到球員OREB28.51%對23.18%亦未變。所有非分區pooled指標與上一批相同，保留個人籃板分配改善。",'',
'已驗證：來源分區錯置、獨立讀取器修正、分區方向反轉、非分區不變。推測：立即補籃／拉出重攻未分開，可能同時造成出手、條件命中率與失誤偏差；尚未做因果消融。失敗／未完成：沒有新引擎改善、沒有跨季泛化測試、沒有證明既有建卡流程受同一問題影響、未取得搶板落點座標。','',
'下一步建議：以修正讀取器作驗證答案，讓同一事件觀察器分出立即補籃與拉出重攻，先比較兩者的持球失誤、非投籃犯規、第一球出手／命中與再搶板。只在條件事件支持時，測一個可獨立關閉的「搶板後持球風險」機制；不全局提高命中率、不提高中距離能力、不直接放大總OREB。需要改機率時另立protocol與20seed成對驗收，並保留個人賽後數據的獨立目標。','',
'本規則只修已發現的高可信矛盾；其他官方分區可能仍有誤差。bootstrap未包含分區標籤不確定性的誤差，unknown單列。原始PBP僅讀取；未下載新資料。','',
'## 重跑','',
'```powershell','node reports/defense-tenth/step4-rebounds-zone-reader/read.mjs','python reports/defense-tenth/step4-rebounds-zone-reader/analyze.py','python reports/defense-tenth/step4-rebounds-zone-reader/summarize.py','python reports/defense-tenth/step4-rebounds-zone-reader/report.py','```','',
f"稽核：{a['protectedFiles']}份既有檔案雜湊未變；逐筆不變項與全部pool指標斷言通過。單元案例包含左右籃框、缺座標、未知area、正常中距離、3pt優先，以及命中／投失不影響分區。原始缺場清單在real.json，沿用1230／1230／1229／1227場，不補值。",'']
(R/'report.md').write_text('\n'.join(lines),encoding='utf8');hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'};(R/'deliverable-hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('REPORT',len(hashes),'files')

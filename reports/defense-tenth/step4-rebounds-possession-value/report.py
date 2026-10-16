import pathlib,json,hashlib
R=pathlib.Path(__file__).parent;d=json.loads((R/'analysis.json').read_text(encoding='utf8'));p=json.loads((R/'protocol.json').read_text(encoding='utf8'));a=json.loads((R/'audit.json').read_text(encoding='utf8'))
lines=['# 進攻籃板完整球權得分與攻守誤差抵銷診斷','',
'結論：個人籃板歸屬改善保留，個人賽後數據是獨立驗收目標，不要求每项改善都降低勝場誤差。這一批只增加觀察紀錄，沒有修改引擎、卡、常數、輪替或凍結基準。完整搶板後得分仍低估；場均攻守誤差抵銷主要與回合數誤差相伴，不能據此宣稱各事件錯誤互相補償。','',
f"登記：`{p['version']}`，UTC `{p['registeredUTC']}`，SHA-256 `{a['registeredSHA']}`。四季均為**已看過答案、當季資料 in-sample**。條件事件診斷 3 seeds；攻守誤差拆解直接引用現有 20 seeds，不重新校準。",'',
'## 已驗證：進攻籃板後完整得分','',
'只以每次球權的第一個有效球員 FG 進攻籃板為起點，計算至原球權結束的己方投籃與普通罰球得分；再次進攻籃板不終止球權。排除含特殊罰球的球權，期末無得分保留為零。下表四季等權，20,000 次 franchise＋seed 跨季配對重抽。區間只供診斷，不作版本採用檢定。','',
'| 指標 | 真實 | 模擬 | 模擬−真實，聯合95%區間 |','|---|---:|---:|---:|']
for k,label in [('points','完整後續得分／含OREB球權'),('fgPoints','其中投籃得分'),('ftPoints','其中罰球得分'),('additionalOreb','後續有效球員FG進攻籃板數'),('zero','最終零分比例')]:
 x=d['pooledOreb']['first'][k];scale=100 if k=='zero' else 1;suffix='%' if k=='zero' else '';lines.append(f"| {label} | {x['real']*scale:.4f}{suffix} | {x['sim']*scale:.4f}{suffix} | {x['delta']*scale:+.4f} [{x['joint95'][0]*scale:+.4f}, {x['joint95'][1]*scale:+.4f}] |")
lines+=['','完整得分偏差 −0.0761 分／含OREB球權：投籃得分少 0.1111，罰球多 0.0350，兩者確有部分抵銷。這是条件事件的得分組成偏差，不能推論為球隊淨勝分誤差的全部原因。不得直接乘全聯盟OREB數作球隊可改善幅度：同球權重複搶板、排除樣本與聯盟校正會影響該換算。','',
'每個OREB皆作起點的重疊口徑：真實 1.2664、模擬 1.1920，差 −0.0745，聯合95% [−0.0860, −0.0629]。此口徑不可累加為球隊總得分貢獻。先前只看第一球FG得分而未含FT／再次搶板，因此不能當作完整PPP。','',
'| 球季 | 可用場數 | 首次OREB球權數 | 真實完整得分 | 模擬完整得分 |','|---|---:|---:|---:|---:|']
for s,x in d['oreb'].items():
 q=x['modes']['first'];lines.append(f"| {s} | {x['games']} | {q['real']['n']} | {q['real']['points']:.4f} | {q['sim']['points']:.4f} |")
lines+=['','## 已驗證：攻守誤差抵銷','',
'O = 去均值(預測得分−真實得分)，D = 去均值(真實失分−預測失分)。正D表示防守被高估。每季驗證 net MSE = O MSE + D MSE + 2 Cov(O,D)。抵銷比例定義 −2Cov／(O MSE＋D MSE)，負值表示放大，不表示抵銷。','',
'| 球季 | 場均得分RMSE | 場均失分RMSE | 場均net RMSE | 場均誤差抵銷比例 | 效率代理攻／守RMSE | 效率誤差抵銷比例 | 回合代理誤差對共同得失分誤差相關 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for s,x in d['errorComponents'].items():
 g=x['perGame'];e=x['efficiencyProxy'];c=x['paceAssociation'];lines.append(f"| {s} | {g['offenseRMSE']:.3f} | {g['defenseRMSE']:.3f} | {g['netRMSE']:.3f} | {g['cancellationFraction']*100:.1f}% | {e['offenseRMSE']:.3f}／{e['defenseRMSE']:.3f} | {e['cancellationFraction']*100:.1f}% | {c['correlationWithCommonScoringError']:.3f} |")
lines+=['','效率代理依既有 FGA−OREB＋TOV＋0.44FTA 口徑。由得分／進攻效率代理反推各隊回合代理，模擬逐seed計算後平均；共同得失分誤差 = (得分誤差＋失分誤差)／2。這是描述性相關，不是控制試驗，不能當成節奏的因果貢獻百分比。','',
'## 推測與下一步提案','',
'1. 各隊節奏尚未對齊，可能是場均得失分共同偏差的主要來源；聯盟平均回合數校準只能修平均，修不了各隊差異。尚未做節奏機制的因果消融，不能稱為已證實原因。','2. 搶板後完整得分不足，可能來自早期失誤、第一次出手選擇與命中率，以及後續再搶板機會；下一批應按事件路徑拆解再選一項修改，不直接加總體命中率。','3. 防守效率的球隊鑑別誤差仍大於進攻；這與「誰拿籃板」的個人統計驗收分開，不為了修防守而撤掉有效個人分配。','',
'## 失敗與限制','',
'沒有新準確度提升可宣稱，這一批只診斷；沒有證明已到噪音下限；没有測換隊泛化；沒用追蹤座標觀察搶板後落點。普通罰球含於完整得分；技術／特殊罰球排除整個球權。缺場未補值、未手改。','',
'缺場完整清單：']
for s,x in d['oreb'].items():
 for f in x['failures']:lines.append(f"- {s}：`{f['id']}`，{f['reason']}")
lines+=['','重跑：','```powershell','node reports/defense-tenth/step4-rebounds-possession-value/run.mjs','python reports/defense-tenth/step4-rebounds-possession-value/analyze.py','python reports/defense-tenth/step4-rebounds-possession-value/report.py','```','',f"稽核：12個season-seed，共14,760場的比分與完整球隊／球員統計逐項等於既有輸出；{a['protectedFiles']}份既有檔案雜湊未變。觀察器合成測試已驗證：兩次OREB後進球加罰，完整得分3分，首次球權只算一次。詳細各隊抵銷列表見 `analysis.json:largestCancellations`。",'',
'目前有圖譜chunk但無完整 graph.json；以既有節點定位籃板模組後，仍逐檔核對原碼。圖譜不作行號與事件定義的唯一依據。','']
(R/'report.md').write_text('\n'.join(lines),encoding='utf8')
hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'}
(R/'deliverable-hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('REPORT',R/'report.md','hashed',len(hashes),'files')

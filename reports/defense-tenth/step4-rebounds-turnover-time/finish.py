import json,pathlib,hashlib,datetime
r=pathlib.Path('reports/defense-tenth/step4-rebounds-turnover-time')
load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'))
p=load(r/'protocol.json');a=load(r/'analysis.json');j=load(r/'joint-intervals.json')['comparisons'];t=load(r/'timing-analysis.json');events=load(r/'event-analysis.json');oldEvents=load('reports/defense-tenth/step4-rebounds-clock/event-analysis.json');c=load(r/'cdf-audit.json')
pooled=j['four-seasons-equal'];pair=pooled['paired']['splitMinuscalibrated'];main=['netRMSE','winsMAE'];guard=['netRMSE','winsMAE','OREB_RMSE','DREB_RMSE']
harm=[k for k in guard if pair[k]['joint95'][0]>0];improved=[k for k in main if pair[k]['joint95'][1]<0]
candidate=[x for x in a['cells'] if x['version']=='split'];drift=[x['season'] for x in candidate if abs(x['metrics']['efficiencyBias'])>.5 or abs(x['metrics']['possessionsBias'])>.5]
timingPass=all(t['pooled'][s]['first']['absoluteErrorChange']<0 for s in ['liveTurnover','deadTurnover']);eligible=not harm and not drift and timingPass
decision={'eligibleMechanismCandidate':eligible,'baselinePromoted':eligible and bool(improved),'significantAccuracyImprovement':improved,'significantHarm':harm,'biasFailedSeasons':drift,'bothTurnoverTimingErrorsImproved':timingPass,'label':'已看過答案；同季重現'}
protected=load(r/'protected-before.json');issues=[f for f,h in protected.items() if not pathlib.Path(f).exists() or hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h];assert not issues
(r/'completion-audit.json').write_text(json.dumps({'protectedFiles':len(protected),'issues':issues,'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
(r/'decision.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ci=lambda v:'['+', '.join(f'{x:+.3f}' for x in v)+']'
conclusion=('耗時與準確度均通過，保留為新候選。' if decision['baselinePromoted'] else '耗時辨識改善，但準確度沒有顯著改善，不升為新基準。' if eligible else '未通過採用門檻，不升為新基準。')
lines=['# 活球／死球失誤耗時拆分', '',conclusion+' 本批只拆失誤後的耗時分布，聯盟 pace 只用官方球權代理校準；球員卡、投籃／犯規／失誤／抄截／籃板機率與補籃機制均沿用。四季全部已看過答案。', '',
'## 二十 seed 準確度','',
'季內去均值、四季等權合併；每版先平均二十 seed 再評分。差值是新候選減上一版 calibrated。95% 為 franchise＋seed 聯合配對重抽，20,000 次。','',
'| 指標 | 上一版 calibrated | 新 split | 差值與聯合 95% 區間 |','|---|---:|---:|---|']
for k in ['netRMSE','Pearson','Spearman','SDRatio','calibrationSlope','winsMAE','winsRMSE','winSlope','OREB_RMSE','DREB_RMSE']:
 d=pair[k];lines.append(f'| {k} | {pooled["versions"]["calibrated"][k]["point"]:.4f} | {pooled["versions"]["split"][k]["point"]:.4f} | {d["point"]:+.4f} {ci(d["joint95"])} |')
lines += ['', '次要比較（相對快速補籃之前 allocation）：', '', '| 指標 | 差值 | 聯合 95% |','|---|---:|---|']
for k in ['netRMSE','winsMAE','OREB_RMSE','DREB_RMSE']:
 d=pooled['paired']['splitMinusallocation'][k];lines.append(f'| {k} | {d["point"]:+.4f} | {ci(d["joint95"])} |')
lines += ['', '## 各季與聯盟漂移','', '| 球季 | net RMSE 舊→新 | wins MAE 舊→新 | 效率偏差 | 球權代理偏差 | TOV／場偏差 | STL／場偏差 | FG% 偏差 pp | 3P% 偏差 pp |','|---|---|---|---:|---:|---:|---:|---:|---:|']
for ss in p['seasons']:
 old=next(x['metrics'] for x in a['cells'] if x['season']==ss and x['version']=='calibrated');new=next(x['metrics'] for x in candidate if x['season']==ss)
 lines.append(f'| {ss} | {old["netRMSE"]:.3f}→{new["netRMSE"]:.3f} | {old["winsMAE"]:.3f}→{new["winsMAE"]:.3f} | {new["efficiencyBias"]:+.3f} | {new["possessionsBias"]:+.3f} | {new["TOVBias"]:+.3f} | {new["STLBias"]:+.3f} | {new["FGpctBias"]:+.3f} | {new["threePctBias"]:+.3f} |')
lines += ['', '每季各指標的成對區間、排名失敗隊及攻防誤差詳見 analysis.json 與 joint-intervals.json。不用球隊 net／勝場調任何常數。', '',
'## 時間機制是否修對','',
'單位秒；同上一批事件起點與終點定義。第一事件含出手、失誤、普通防守犯規、一般罰球或終止球權的防守籃板。完整球權尾段可跨多次進攻籃板。三 seed 診斷，不當二十 seed 準確度評測。','',
'| 起始狀態／終點 | 真實 | 上一版 | 新版 | 新版−上一版與聯合 95% | 絕對誤差變化與聯合 95% |','|---|---:|---:|---:|---|---|']
for s in ['liveTurnover','deadTurnover']:
 for k in ['first','full']:
  z=t['pooled'][s][k];lines.append(f'| {s} / {k} | {z["real"]:.3f} | {z["calibrated"]:.3f} | {z["split"]:.3f} | {z["change"]:+.3f} {ci(z["joint95"])} | {z["absoluteErrorChange"]:+.3f} {ci(z["absoluteErrorChangeJoint95"])} |')
lines += ['', '其他狀態：', '', '| 起點 | 真實第一事件 | 新版第一事件 | 新版−上一版 |','|---|---:|---:|---:|']
for s in ['made','dreb','playerOreb','teamOreb','ftOreb','foulRetained']:
 z=t['pooled'][s]['first'];lines.append(f'| {s} | {z["real"]:.3f} | {z["split"]:.3f} | {z["change"]:+.3f} |')
lines += ['', '## OREB 後事件副作用','', '| 指標 | 真實 | 上一版 | 新版 |','|---|---:|---:|---:|']
for k in ['immediateProxy','meanSeconds','earlyLoss','laterLoss','foul','fgPct','firstFgPointsPerOreb']:
 vals=[events['equalSeasonMeans']['real'][k],oldEvents['equalSeasonMeans']['simulation'][k],events['equalSeasonMeans']['simulation'][k]];lines.append('| '+k+' | '+' | '.join(f'{x:.4f}' for x in vals)+' |')
lines += ['', '事件比例的聯合區間見 event-joint-intervals.json；不採用 diagnose.py 的 game 正態近似作結論。這批沒有調整 OREB 後犯規、失球或出手分區。firstFgPointsPerOreb 只算第一個 FG 得分，不含罰球與後續再搶板；不是完整 PPP，不能直接視為進攻籃板價值。', '',
'## 校準、凍結與資料稽核','', '| 球季 | 原 pace | 新 pace | 校準輪數 | 最後校準球權偏差 | 收斂 | 活球 CDF 數／均值 | 死球 CDF 數／均值 |','|---|---:|---:|---:|---:|---|---|---|']
for ss in p['seasons']:
 z=load(r/ss/'calibration.json');base=load(pathlib.Path('reports/defense-tenth/step4-rebounds-clock')/ss/'calibration.json');cc=c[ss]['states']
 lines.append(f'| {ss} | {base["selected"]["pace"]:.6f} | {z["selected"]["pace"]:.6f} | {len(z["history"])} | {z["history"][-1]["bias"]:+.3f} | {z["converged"]} | {cc["liveTurnover"]["n"]} / {cc["liveTurnover"]["mean"]:.3f} | {cc["deadTurnover"]["n"]} / {cc["deadTurnover"]["mean"]:.3f} |')
at=load(r/'attribution-analysis.json')
lines += ['', '## 拆分與 pace 校準的歸因診斷', '', '僅相同三個診斷 seed 的點估計，不替代二十 seed 的聯合區間，不據此宣稱準確度改善。rawsplit 固定舊 pace；split 使用預先登記的聯盟球權校準。', '', '| 版本 | net RMSE | wins MAE | 球權代理偏差 |', '|---|---:|---:|---:|']
for v,z in at['pooled'].items():lines.append(f'| {v} | {z["netRMSE"]:.3f} | {z["winsMAE"]:.3f} | {z["possessionsBias"]:+.3f} |')
lines += ['', '拆分與校準都影響球權均值，所以不能把球權偏差縮小全部歸因於拆分。2023–24 新舊 pace 相同，三個 seed 的 rawsplit／split 比分、完整統計與耗時資料逐筆一致（3,690 場）。', '', '聯盟事件偏差仍存在：歷史季 TOV／STL 偏低、部分球季 3P% 偏高；本批沒有用這些誤差再調參，表中如實列示。這些是未解決項，不因本批球權對齊而視為通過整套引擎驗收。', '']
lines += ['', '已驗證：新兩個 CDF 合併後逐值等於各季 frozen turnover CDF。既有支援最小 .1 秒，因此零長區段仍排除；下載與規則未更換。當季全季資料適用本次重現，不能宣稱是資料外預測。', '',
'開關 OFF 四季共 4,920 場逐場比分、完整球員／球隊統計與 OREB 事件分類完全一致。正式評測 80 季、98,400 場；每季 82 場／隊。能力卡與事件機率保持不變；耗時仍可能改變場上分鐘、事件數、疲勞、迫近時限與後續 RNG 路徑，不能宣稱最終統計必然不變。', '',
f'protocol SHA-256：`{(r/"protocol.sha256").read_text().split()[0]}`；登記 UTC {p["registeredUTC"]}。CDF 支援補充登記與來源雜湊見 cdf-support-supplement.*、source-registration.json。',
f'保護 {len(protected)} 份既有檔案，變動 {len(issues)} 份；未修改 frozen v1–v5、T0 或任何先前報告。', '',
'執行紀錄：file job 只回傳完成摘要、完整結果仍寫檔，降低主程序記憶體；輔助事件分析原複用 putback 對照，已修正為預先登記的 calibrated 對照，主二十 seed 比較與候選對真實結果不變。詳見 execution-serialization.json、event-comparator-correction.json。','', '## 已驗證、推測、失敗分列','',
f'已驗證：OFF parity 通過；兩個耗時絕對誤差同時減少={timingPass}；符合本批機制候選門檻={eligible}。', '',
'推測：若耗時改善但 net／勝場不改善，原因可能是本批只修了反擊的時間，仍沒有修反擊的得分效率與陣容相性；這需要獨立資料與實驗，不能拿本批結果當因果證明。','',
f'失敗／未證實：漂移未通過季 {drift or "無"}；顯著退步項 {harm or "無"}；沒有顯著改善的主指標 {[k for k in main if k not in improved]}。', '',
'保留限制：犯規留球仍與籃板共用 retained；CDF 到球權結束與引擎抽到出手時刻的口徑落差仍在。沒有藉本批同時修掉，也未使用球隊 ID、net 或勝場補丁。', '',
'## 重跑指令','', '```powershell','node reports/defense-tenth/step4-rebounds-turnover-time/build-cdf.mjs','node reports/defense-tenth/step4-rebounds-turnover-time/calibrate.mjs','node reports/defense-tenth/step4-rebounds-turnover-time/run.mjs','node reports/defense-tenth/step4-rebounds-turnover-time/analyze.mjs','python reports/defense-tenth/step4-rebounds-turnover-time/bootstrap.py','python reports/defense-tenth/step4-rebounds-turnover-time/timing-analysis.py','python reports/defense-tenth/step4-rebounds-turnover-time/diagnose.py','python reports/defense-tenth/step4-rebounds-turnover-time/event-joint.py','node reports/defense-tenth/step4-rebounds-turnover-time/attribution.mjs','python reports/defense-tenth/step4-rebounds-turnover-time/attribution-analysis.py','python reports/defense-tenth/step4-rebounds-turnover-time/same-pace-check.py','python reports/defense-tenth/step4-rebounds-turnover-time/finish.py','```','',
'既有校準與模擬輸出會跳過；不得為了通過而改規則或重選參數。本批到此停止。']
(r/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
(r/'deliverable-hashes.json').write_text(json.dumps({str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in r.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'},indent=2)+'\n')
print(json.dumps(decision,ensure_ascii=True,indent=2))

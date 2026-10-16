import pathlib,json,hashlib,datetime
r=pathlib.Path('reports/defense-tenth/step4-rebounds-state-time')
load=lambda f:json.loads((r/f).read_text(encoding='utf8'))
a=load('analysis.json');p=load('protocol.json');audit=load('completion-audit.json')
names={'made':'對手得分後','dreb':'防守籃板後','liveTurnover':'活球失誤後','deadTurnover':'死球失誤後','playerOreb':'個人 FG 進攻籃板後','teamOreb':'團隊 FG 留球後','ftOreb':'罰球進攻籃板後','foulRetained':'非投籃犯規留球後'}
ci=lambda x:'['+', '.join(f'{v:+.3f}' for v in x)+']'
lines=['# 起始狀態耗時診斷','',
'結論：單一 pace 無法校正目前的時鐘。活球失誤後太慢，死球失誤與犯規留球後太快；兩者互相抵銷。個人進攻籃板到下一事件仍偏慢，但整波球權耗時已接近真實。這批只量測，未修改卡、機率、時鐘或聯盟常數；沒有新的 MAE 改善可宣稱。','',
'## 已驗證的耗時差異','',
'以下為四季等權；季內合併計數。單位秒。起點一律使用得分／籃板／失誤／犯規事件的比賽時鐘，不使用模擬 POSSESSION 的較晚時間。到下一事件包含出手、失誤、普通防守犯規、一般罰球或終止球權的防守籃板；不代表一定是下一次出手。','',
'| 起始狀態 | 真實到下一事件 | 模擬 | 差值與聯合 95% 區間 | 真實整波球權 | 模擬整波球權 |','|---|---:|---:|---|---:|---:|']
for s,z in a['pooled'].items():
 x=z['first'];f=z['full'];lines.append(f'| {names[s]} | {x["real"]:.3f} | {x["sim"]:.3f} | {x["difference"]:+.3f} {ci(x["joint95"])} | {f["real"]:.3f} | {f["sim"]:.3f} |')
lines += ['', '到下一留球節點／球權結束（segment）與完整球權（full）的區間：', '', '| 起始狀態 | segment 差值與 95% | full 差值與 95% |','|---|---|---|']
for s,z in a['pooled'].items():
 lines.append(f'| {names[s]} | {z["segment"]["difference"]:+.3f} {ci(z["segment"]["joint95"])} | {z["full"]["difference"]:+.3f} {ci(z["full"]["joint95"])} |')
lines += ['', '球權完整尾段可跨越多次進攻籃板；不同起點的尾段會重疊，不能加總成一場比賽的總時間。節末未完成案例不納入該項平均，另外計數。', '',
'## 引擎路徑與原因','',
'1. **活球與死球失誤共用同一分布。** `src/defense_fourth_game.js:80` 依 origin 選 CDF；傳球抄截、持球失誤及死球失誤都把 origin 設為 turnover。實測下一事件約 10.43／10.38 秒，真實卻是 6.46／13.25 秒。這是已確認的狀態辨識不足。','',
'2. **犯規留球套用籃板留球分布。** `src/defense_fourth_game.js:260` 非罰球的普通犯規後設 origin=retained；個人與團隊 OREB 也是 retained。實測非投籃犯規留球第一事件約 4.95 秒，真實約 9.46 秒。真實的判定是普通非投籃防守犯規、同鐘無一般罰球；少數特殊事件仍有歸屬歧義，屬事件分類代理。','',
'3. **CDF 標籤與抽樣用途不同。** `src/defense_pbp_analysis.js:67` 的真實 segment 到下一 OREB 或球權結束；`:93` 在 OREB 重開 segment，但非投籃犯規不重開。`scripts/prepare_defense_b1.js:18` 收這個 duration。引擎 `src/defense_fourth_game.js:242` 抽 opportunityDeadline，`:294` 在這個截止時間出手，投失後 `:170` 另加籃板飛行，投進後 `:376` 另加發球延遲。所以輸入不是精確的「到出手」分布。結構上的口徑落差已確認；它貢獻多少偏差尚未用關閉實驗確認，本批不修。','',
'4. **快速補籃修正保留，但不能據此把所有 OREB 後時間再縮短。** 個人 OREB 到下一事件偏慢 +0.52 秒，而到下一留球節點差 +0.04 秒、完整球權差 −0.11 秒。單純再加速可能把已接近真實的完整球權推得更短。團隊留球的完整尾段已短約 1.86 秒，罰球 OREB 短約 2.09 秒。','',
'同一條件平均的差異可能包含出手、犯規、失誤與再次搶板比例的差異，不能當成固定同一批回合的純時間因果效應。', '', '## 起始狀態占比與混合效應','',
'占比以八類中有有效下一事件者為分母，不含節初、跳球等其他起點。','',
'| 起始狀態 | 真實占比 | 模擬占比 | 狀態內耗時貢獻（秒） | 組成貢獻（秒） |','|---|---:|---:|---:|---:|']
for s,z in a['decomposition']['contributions'].items():lines.append(f'| {names[s]} | {100*z["realFrequency"]:.2f}% | {100*z["simFrequency"]:.2f}% | {z["withinState"]:+.3f} | {z["composition"]:+.3f} |')
d=a['decomposition'];lines += ['',f'八類起點到第一事件的混合平均：真實 {d["realFirstMean"]:.3f} 秒、模擬 {d["simFirstMean"]:.3f} 秒。差 {d["simFirstMean"]-d["realFirstMean"]:+.3f} 秒，可代數拆成狀態內 {d["withinState"]:+.3f} 秒與頻率組成 {d["composition"]:+.3f} 秒。這是描述性分解，不是球權總量的因果分解。', '', '## 樣本與稽核','',
'| 球季 | 真實場數 | 比分記帳不一致 | 時間逆序 | 尾段遇到異隊活動 | 第一事件未完成 | 完整尾段未完成 |','|---|---:|---:|---:|---:|---:|---:|']
for s,z in a['seasons'].items():
 x=z['real']['audit']
 lines.append(f'| {s} | {1230-len(z["missing"])-len(z["failures"])} | {len(z["scoreAudit"])} | {x["invalidTime"]} | {x["ownerMismatch"]} | {x["firstCensored"]} | {x["fullCensored"]} |')
lines += ['', '真實 4,916 場；每季三 seed，共 14,760 場模擬，與既有 calibrated 版逐場比分、完整球員與球隊統計一致。實際耗時對照只含有真實 PBP 的場次，合計 14,748 場模擬。缺場、參照異常、分類數量與每季每 seed 的中位數／P90 見 real.json、analysis.json；比分重建全部一致。遇到未知異隊活動即停止尾段搜尋，已取得的前段時間保留，未取得尾段視為截尾，不假設完成時間。','',
'缺 PBP：']
for s,z in a['seasons'].items():lines.append(f'- {s}：{z["missing"] or "無"}；讀取失敗 {z["failures"] or "無"}。')
lines += ['', '統計區間：20,000 次 franchise＋seed 聯合重抽，同一 franchise、seed 索引跨季配對，季內合併、季間等權；僅三個診斷 seed，不能代替二十 seed 的版本採用評測。四季均為已看過答案。', '',
f'protocol SHA-256：`{(r/"protocol.sha256").read_text().split()[0]}`；登記 UTC：{p["registeredUTC"]}。',
f'保護 {audit["protectedFiles"]} 份既有檔案，變動 {len(audit["changed"])} 份。觀測器不呼叫額外 RNG，補籃秒數與 pace 沿用上一版。', '',
'## 推測、失敗與下一步提案','',
'已驗證：狀態合併與 CDF 用途口徑有系統性落差，單一全聯盟 pace 無法同時修正相反方向的偏差。','',
'推測：先分開活球／死球失誤與犯規留球，再統一抽樣量到「下一個可觀測終止事件」的語意，比繼續調總 pace 更可能改善回合數與反擊時間。快速補籃的專用分布先保留。','',
'失敗／未證實：本批沒有實作修正，也沒有證明 net RMSE 或 wins MAE 改善。既有候選仍未通過上一批的球權偏差门檻，不升級。此資料不足以把剩餘 OREB 得分差全部歸因於耗時，犯規與丟球比例仍是不同機制。','',
'建議下一批先只拆活球／死球失誤耗時，共用現有機率與卡；這一組有最大、方向清楚的時間偏差。校準只用聯盟球權，不用 net／勝場，跑二十 seed 確認副作用。犯規留球與抽樣口徑各留獨立批次，以便歸因。預期改善時間辨識；是否帶動球隊準確度仍未知，不先承諾 MAE 降幅。', '',
'## 重跑指令','', '```powershell','node reports/defense-tenth/step4-rebounds-state-time/check.mjs','node reports/defense-tenth/step4-rebounds-state-time/real.mjs','node reports/defense-tenth/step4-rebounds-state-time/run.mjs','python reports/defense-tenth/step4-rebounds-state-time/analyze.py','python reports/defense-tenth/step4-rebounds-state-time/finish.py','```','',
'run 跳過已有診斷輸出；全部讀取本機既有資料，不抓新球季。本批到此停止。']
(r/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
(r/'deliverable-hashes.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in r.iterdir() if f.is_file() and f.name!='deliverable-hashes.json'},indent=2)+'\n')
print(json.dumps({'report':str(r/'report.md'),'parityGames':sum(z['games'] for z in a['parity']),'protectedChanges':audit['changed'],'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}))

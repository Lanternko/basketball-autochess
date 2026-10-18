import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
p=read(R/'protocol.json');a=read(R/'analysis.json')['cells'];ci=read(R/'joint-intervals.json')['comparisons'];coverage=read(R/'coverage.json')
fmt=lambda v:f'{v:.3f}'
def interval(q):return f"{q['point']:+.3f} [{q['joint95'][0]:+.3f}, {q['joint95'][1]:+.3f}]"
get=lambda s,v:next(c for c in a if c['season']==s and c['version']==v)
main=ci['four-seasons-equal']['paired']['drebMinuspooled'];f0=sum(get(s,'pooled')['metrics']['failures'] for s in p['seasons']);f1=sum(get(s,'dreb')['metrics']['failures'] for s in p['seasons']);n=main['netRMSE'];reb=main['DREB_RMSE']
support=n['joint95'][1]<0 and reb['point']<0 and f1<=f0
verdict='達到預登記的後續研究條件（不代表跨季或換隊驗證通過）' if support else '未達預登記的後續研究條件；維持 T0 純卡基準'
lines=['# 純卡防守籃板實驗：pure-dreb-rate-1','',f'結論：**{verdict}**。四季合併、相同聯盟校準對照下，淨勝分去均值 RMSE 差為 {interval(n)}；防守籃板率去均值 RMSE 差為 {interval(reb)} 個百分點。所有球季均為**已看過答案的同季重現**，不能解讀成盲測或換隊成績。','',f"規則於 {p['registeredAt']} 登記；SHA-256 `{hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest()}`。4季×2個新版本×20 seeds=160完整球季、196800場。T0引用既有80球季。另有校準與4個OFF一致性測試球季。",'',
'## 已驗證：主指標與配對差','', 'T0=凍結純卡；pooled=只修聯盟均值的純卡對照；dreb=同樣校準方法加獨立個人 DREB% 欄位。只可用 dreb−pooled 歸因於新機制。各版校準得到的常數不同，反映相同目標的均值匹配，不是固定同數值。所有區間均同時重抽30個 franchise與20個seed、跨季配對、20000次。每季去均值，四季等權合併。','',
'| 球季 | 版本 | net RMSE | Spearman | 勝場 MAE | 校準斜率 | net SD比 | DREB RMSE(pp) | DREB相關 | 防守proxy RMSE | 排名失敗隊數 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for s in p['seasons']:
 for v in ['T0','pooled','dreb']:
  m=get(s,v)['metrics'];lines.append('| '+' | '.join([s,v]+[fmt(m[k]) for k in ['netRMSE','Spearman','winsMAE','calibrationSlope','SDRatio','DREB_RMSE','DREB_Correlation','defenseProxyRMSE']]+[str(m['failures'])])+' |')
lines+=['','| 球季／合併 | 比較 | net RMSE 差 [聯合95%] | wins MAE 差 [聯合95%] | DREB RMSE 差(pp) [聯合95%] |','|---|---|---|---|---|']
for s in p['seasons']+['four-seasons-equal']:
 for pair in ['drebMinuspooled','drebMinusT0','pooledMinusT0']:
  z=ci[s]['paired'][pair];lines.append('| '+' | '.join([s,pair]+[interval(z[k]) for k in ['netRMSE','winsMAE','DREB_RMSE']])+' |')
lines+=['','其他指標的點估計與聯合區間完整列於 `joint-intervals.json`；所有120隊的攻防誤差與排名列於 `analysis.json`。','',
'## 已驗證：映射問題與本次改動','',
'舊路徑（`src/rebound_block_model.js`）讓攻、防共用總籃板屬性，防守競爭值再乘位置落點，以及 exp((0.7×籃板+0.3×身材−70)/45)。因而沒有獨立的防守籃板率欄位。這是程式事實；它是否造成主要賽季誤差，必須由上述對照判定。','',
'候選直接使用個人 DREB% 與個人 DREB／分鐘做Beta收縮，五人份額相加作為防守回收率，替代防守端總籃板／身材／位置倍率；進攻端競爭相對值、進攻籃板後補籃、團隊籃板與罰球回收機率保留。只修改記憶體載入的實驗版，沒有改寫 `src/`。`individualDrebCard=false` 且聯盟籃板常數為0時，四季各1230場比分及所有球隊／球員統計均與 T0 完全一致。','',
'| 球季 | 個人卡人數 | DREB%缺漏 | 分鐘覆蓋 | EB均值 | κ（機會數） | hustle分鐘覆蓋 | 幫隊友回收計數 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for c in coverage:lines.append(f"| {c['season']} | {c['players']} | {len(c['missing'])} | {100*c['minuteCoverage']:.5f}% | {c['mu']:.4f} | {c['kappa']:.2f} | {100*c['boxSummary']['minuteCoverage']:.5f}% | {c['boxSummary']['teammateRebounds']} |")
lines+=['','卡位暫未加分：hustle的 BOX_OUT_PLAYER_TEAM_REBS−BOX_OUT_PLAYER_REBS 可以辨識卡位者未自己取得的球，但混合攻防，而且籃板已計在隊友名下。直接加到五人DREB總和會重複計數。這次並未證明「卡位沒有作用」，而是現有彙總表不足以識別額外團隊回收的因果效果；不捏造係數。','',
'## 聯盟校準與個人統計漂移','',
'只調聯盟投籃logit偏移、pace與FG籃板logit截距，三個校準seed、最多六輪、最後評估點；失誤、犯規參數不改。下面為獨立20seed評估，效率／球權的偏差均為合併計數；FG與3P單位為百分點。校準未收斂與漂移均照列，不追加調參。','',
'| 球季 | 版本 | 校準收斂 | 效率偏差/100 | 球權偏差/場 | TOV偏差/場 | FG偏差(pp) | 3P偏差(pp) | OREB份額偏差(pp) | 分鐘MAE |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
for s in p['seasons']:
 for v in ['T0','pooled','dreb']:
  m=get(s,v)['metrics'];conv='—' if v=='T0' else str(read(R/s/f'calibration-{v}.json')['converged']);lines.append('| '+' | '.join([s,v,conv]+[fmt(m[k]) for k in ['efficiencyBias','possessionsBias','TOVBias','FGpctBias','threePctBias','orbShareBias','minuteMAE']])+' |')
lines+=['','## 重點球隊（正O／D代表高估進攻／防守強度）','','| 球季 | 球隊 | 版本 | 真實net | 預測net | O誤差 | D誤差 | 真實DREB% | 預測DREB% | 真實／預測名次 |','|---|---|---|---:|---:|---:|---:|---:|---:|---|']
for s in p['seasons']:
 for id in [1610612739,1610612752,1610612738,1610612760,1610612765]:
  for v in ['T0','pooled','dreb']:
   t=next(t for t in get(s,v)['teams'] if t['id']==id);lines.append('| '+' | '.join([s,t['name'],v]+[fmt(t[k]) for k in ['net','predictedNet','O','D','dreb','predictedDreb']]+[f"{t['actualNetRank']:.1f}/{t['netRank']:.1f}"])+' |')
lines+=['','## 排名失敗清單與歸因','','沿用T0及格線及歸因規則：真實前五掉出前十、真實倒五進前二十；勝場排名不計及格。關鍵時刻反事實若不能同時解掉該軸失敗並縮小一半誤差，一律列「無法解釋」。運氣標記不能解釋net誤差，真實分鐘已含DNP，不能再拿缺陣免除失敗。','']
for s in p['seasons']:
 for v in ['T0','pooled','dreb']:
  fs=get(s,v)['failures'];lines.append(f"- {s} {v}："+('無失敗隊。' if not fs else '；'.join(f"{t['name']} {t['actualNetRank']:.1f}→{t['netRank']:.1f}，O={t['O']:+.2f}、D={t['D']:+.2f}，{t['status']}" for t in fs)+'。'))
lines+=['','## 推測、失敗與限制','',
'- 個人DREB%也受同場隊友、對手投失及籃板分工影響；本次未驗證換隊可攜性。不能因為輸入是個人表就認定它是純能力。',
'- 五人DREB份額相加再截斷是本次預登記的近似；沒有位置落點與卡位事件模型。進攻籃板仍沿用舊身材／位置路徑；五中鋒常識問題這次沒有修。',
'- 真實名單與分鐘為軟目標，不是逐球換人重播；不能保證每個籃板機會的在場五人與真實相同。',
'- 四季所有結果均已看過答案；統計區間不會消除開發選擇偏誤。此次結果不構成外推準確度證明。',
'- 籃板統計與賽季淨勝分是兩個不同驗收項；籃板改善但net區間跨0，不可宣稱球隊強度有進步。','',
'## 重跑指令','',
'原protocol已登記，勿再執行register.mjs覆寫。依序執行：','', '```powershell','node reports/defense-tenth/step4-rebounds/prepare.mjs','node reports/defense-tenth/step4-rebounds/parity.mjs','node reports/defense-tenth/step4-rebounds/calibrate.mjs','node reports/defense-tenth/step4-rebounds/run.mjs','node reports/defense-tenth/step4-rebounds/analyze.mjs','python reports/defense-tenth/step4-rebounds/bootstrap.py','python reports/defense-tenth/step4-rebounds/report.py','node reports/defense-tenth/step4-rebounds/audit.mjs','```','',
'calibrate及run預設重用現有同版產物；要完整重算請先另存整個實驗目錄，避免覆寫已驗收輸出。完成本項即停止，未進行下一組改卡。']
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(R/'decision.json').write_text(json.dumps({'furtherResearchCriteriaMet':support,'verdict':verdict,'pooledRankFailures':f0,'candidateRankFailures':f1,'mainPaired':main},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(verdict.encode('ascii','backslashreplace').decode())

import json,pathlib,hashlib
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));d=load(R/'analysis.json');s=load(R/'source-audit.json');p=load(R/'protocol.json');a=load(R/'audit.json');m=d['pooledOverall'];q=d['pooledRoutes'];ad=d['attemptDecomposition']
lines=['# 搶板後失誤、第一次出手與再次搶板：路徑診斷','',
'結論：完整得分不足同時涉及「未走到出手／罰球」和「完成進攻後的條件得分」。不能靠一個總體命中率參數修正。再次搶板確實偏少，但第一次FG以外的得分反而略高，不應直接把所有後續搶板放大。另查到逐球分區標籤與補籃動作、距離有矛盾，分區結論需先修正資料讀取口徑；不修改任何凍結輸出。','',
f"規則 SHA-256：`{a['protocolSHA']}`；登記UTC `{p['registeredUTC']}`。四季均為已看過答案、同季in-sample。3 seeds（20261012–14），20,000次franchise＋seed跨季配對重抽，四季等權。只供診斷，不是20seed的版本採用檢定。",'',
'## 已驗證：完整得分的分解','',
'每次球權的第一個有效球員FG進攻籃板為起點，普通罰球及後續再搶板均包含。特殊FT球權排除；同一次球權不重複計入主表。','',
'| 指標 | 真實 | 模擬 | 差異及聯合95%區間 |','|---|---:|---:|---:|']
for k,label,scale in [('points','完整得分／含OREB球權',1),('firstFgReached','至少出現一次記帳FG的比例',100),('firstFgMakeRate','第一次記帳FG命中率',100),('recoveryPlayerGivenMiss','第一次FG投失後，下一個決定性事件是球員FG進攻籃板',100),('recoveryTeamGivenMiss','同上，團隊FG留球',100),('firstFgPoints','第一次FG直接得分／含OREB球權',1),('postFirstFgPoints','完整得分扣除第一次FG直接得分',1)]:
 x=m[k];lines.append(f"| {label} | {x['real']*scale:.4f} | {x['sim']*scale:.4f} | {x['delta']*scale:+.4f} [{x['joint95'][0]*scale:+.4f}, {x['joint95'][1]*scale:+.4f}] |")
lines+=['','「扣除第一次FG直接得分」包含整個球權的罰球，可能出現在第一次FG之前；不能把它解讀成純粹第一次出手後的得分。再次搶板指標亦不等同所有投失的官方OREB%：若投失後先發生FT或另一個FG，本診斷視為沒有直接FG搶回。','',
'| 出手／罰球前的流程 | 真實比例 | 模擬比例 | 差異（百分點）及聯合95% |','|---|---:|---:|---:|']
for k,label in [('ft_first','先罰球'),('loss_before_attempt','先失去球權'),('period_end','未完成進攻即節末')]:
 x=q[k];ci=x['probabilityDeltaInterval'];lines.append(f"| {label} | {x['realProbability']*100:.3f}% | {x['simProbability']*100:.3f}% | {ci['delta']*100:+.3f} [{ci['joint95'][0]*100:+.3f}, {ci['joint95'][1]*100:+.3f}] |")
lines+=['','先失去球權包含失誤、被抄截與沒有己方出手紀錄就由對手拿回球權，不能全部稱為官方TOV。','',
'把FG或普通FT都視為「有完成進攻嘗試」，其機率真實91.620%、模擬89.002%。有嘗試時完整得分真實1.3832、模擬1.3385。對稱分解 exact identity：','',
f"- 嘗試機會不足：{ad['frequencyContribution']:+.5f} 分，95% {ad['frequencyContributionJoint95']}。",
f"- 有嘗試時的條件得分不足：{ad['valueContribution']:+.5f} 分，95% {ad['valueContributionJoint95']}。",
'- 合計 −0.07609 分／含OREB球權；兩項約47%／53%。這是記帳分解，不是各機制的因果貢獻或修正收益。','',
'## 已驗證：不能拿Mid-Range標籤直接校準','',
'主要路徑表沿用舊分區規則，沒有因結果修改。它顯示名義中距離FG比例真實14.36%、模擬5.98%，且名義中距離命中率真實60.95%、模擬42.86%。來源稽核發現此比較受資料矛盾污染：area=Mid-Range、areaDetail=8-16 Left，卻同時是tip Layup／DUNK、shotDistance=0，座標也在籃框旁。','',
'| 球季 | 名義中距離第一出手數 | 距離0呎 | 比例 | 距離至少8呎的命中率（僅稽核） |','|---|---:|---:|---:|---:|']
for season,x in s.items():lines.append(f"| {season} | {x['midN']} | {x['midZeroDistance']} | {100*x['midZeroDistance']/x['midN']:.1f}% | {100*x['midAtLeastEightFeetMade']/x['midAtLeastEightFeet']:.1f}% |")
lines+=['','至少8呎的稽核值39–41%接近模擬43%；此篩選不是完整的新分區模型，不當作正式驗收。原先「中距離命中率不足」推測不成立為可直接採用的結論。沒有證明全體球員卡受同一缺陷污染，需追建卡資料來源；也不能宣稱修資料會必然改善勝場。','',
'來源補充稽核是在看到異常分區結果後登記的事後探索；規則及SHA另存 `source-audit-protocol.json`／`.sha256`。完整樣本與事件例子見 `source-audit.json`。總分、FG是否出現、FG總命中率、失去球權及再搶板比例不依賴area標籤，不受此分類問題影響。原有補籃proxy若要求short區，可能漏掉這些補籃；不重寫歷史報告。','',
'## 引擎稽核與推測','',
'- `src/defense_fourth_game.js:243`：非立即補籃時重新按進攻量選控球者。',
'- `src/defense_fourth_game.js:254`：每次opportunity均先抽非投籃犯規，補籃也會經過此分支。',
'- `src/defense_fourth_game.js:277`：立即補籃跳過傳球循環。',
'- `src/defense_fourth_game.js:311`：補籃仍抽pTovTouch，沒有獨立的搶板後持球失誤狀態。',
'- `src/defense_probability.js:49`：pressure模式依一般tovSkill與防守壓迫建立hazard，未按搶板後／一般控球分開。',
'- `src/probability_model.js:382`：putback確實強制short出手；名義short過多不能直接拿矛盾的真實分區反駁這條機制。','',
'推測：搶板者的一般持球失誤能力被套用到立即補籃，可能造成不必要的失去球權。但這一批未做因果消融，也未區分所有搶板後出界／抄截風險，不能認定刪除該抽樣就是正解。','',
'## 下一步提案與保留項','',
'先做一個獨立資料讀取版本：檢查補籃動作、shotDistance、座標與area矛盾，只對可明確辨識的矛盾補籃改判籃下；無法判定標unknown，不默認mid。新規則先登記，不覆寫原始資料或歷史输出。重算分區與補籃proxy，確認主表總分與無分區指標不變。預期效果是消除錯誤校準目標；它本身不是引擎準確度提升。','',
'之後優先測搶板後的持球失誤狀態，分立即補籃與拉出重攻，保留一般球權失誤機制；常數由實測的條件事件率決定，不按隊、不直接補得分。47%的分解是診斷上限參考，不是保證收益。不直接增加整體OREB率，因其他FG／FT得分已部分補償；球隊準確度需20seed成對比較，個人籃板分配亦為獨立驗收。','',
'保留已改善的籃板歸屬；本批未更換基準、未修改卡或機率。失敗項目：分區訊號尚不能作校準；未證明新機制有效；沒有新球季／換隊泛化結果。','',
'## 重跑與稽核','',
'```powershell','node reports/defense-tenth/step4-rebounds-paths/run.mjs','python reports/defense-tenth/step4-rebounds-paths/analyze.py','node reports/defense-tenth/step4-rebounds-paths/source-audit.mjs','python reports/defense-tenth/step4-rebounds-paths/report.py','```','',
f"12個season-seed，共14,760場比分、完整球隊／球員統計均與上一版完全一致；新增記錄投影回舊欄位後逐筆一致，真實資料同樣逐筆一致。{a['protectedFiles']}份既有檔案雜湊未變。可用真實場數1230／1230／1229／1227，缺場清單在real.json；不補值、不手改。合成測試已驗證FOUL→FT、先失誤、投失→再搶板→進球加罰的分類與得分。",'']
(R/'report.md').write_text('\n'.join(lines),encoding='utf8')
hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'};(R/'deliverable-hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('REPORT',len(hashes),'hashed files')

import pathlib,json,hashlib
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');b=load(R/'diagnosis.json');c=load(R/'candidate-diagnosis.json');d=load(R/'analysis.json');a=load(R/'accuracy-joint.json');audit=load(R/'audit.json');m=load(R/'multiplier.json')
assert hashlib.sha256((R/'multiplier.json').read_bytes()).hexdigest()==(R/'multiplier.sha256').read_text().strip();assert m['diagnosisSHA']==hashlib.sha256((R/'diagnosis.json').read_bytes()).hexdigest();assert not audit['issues'];assert len(load(R/'new-adapter-off-parity.json'))==12
x=b['pooled']['firstAnchors'];y=c['pooled']['firstAnchors'];cats=['passingLive','handlingLive','passingDead','handlingDead','offensiveFoul','otherViolation','clock'];sq=lambda z:sum((z['baseline'][k]-z['real'][k])**2 for k in cats)
guards={'matchedIncidenceCloser':abs(y['baseline']['matchedGeneric']-y['real']['matchedGeneric'])<abs(x['baseline']['matchedGeneric']-x['real']['matchedGeneric']),'categorySquaredErrorReduced':sq(y)<sq(x),'ftExcessNotSignificantlyIncreased':d['intervals']['candidate-baseline']['ftPoints']['joint95'][0]<=0}
decision={'promoted':False,'baselineChanged':False,'candidate':'postOrebTurnoverRisk','multiplier':m['multiplier'],'registeredGuardResults':guards,'failed':['FT point excess significantly increases','holding-live rate undershoots truth while offensive fouls remain high','postOREB total turnover undershoots truth and independent14sec clock remains absent','net RMSE and wins MAE joint95 include zero; three seeds only'],'retention':'sensitivity experiment only, not a calibrated production parameter','protocolSHA':(R/'protocol.sha256').read_text().strip()};(R/'decision.json').write_text(json.dumps(decision,indent=2)+'\n',encoding='utf8')
L=['# 搶板後失誤分類與非零風險試驗','',
'結論：拆出了可定位的錯配，但單一倍率修正失敗，不採用、不換基準。傳球被抄本來已接近真實；一般終結失誤門檻卻把持球被抄、傳球出界、進攻犯規等多類事件一起產生得過多。用非零倍率降低後，部分分類變準，但持球被抄與總失誤降過頭，進攻犯規仍多，罰球得分偏高加劇。完整得分更接近真實，不能據此認定機制已修好。','',
f"版本 `{p['version']}`，先登記 UTC `{p['registeredUTC']}`，SHA-256 `{decision['protocolSHA']}`。四季均已看過答案／當季in-sample；3seed（20261012–14），20,000次franchise＋seed跨季配對重抽，四季等權。沒有下載資料。沒有混入前批犯規候選。",'',
'## 定義與樣本','',
'真實與基準沿用相同有效個人FG進攻籃板、特殊FT排除及來源覆蓋。分類表以每球權第一個有效起點、當節至少剩三秒為分母，計算該起點到第一次己方FG／普通FT之前的官方失誤；不等同整個球權TOV率。早期為前三秒，晚期為其後。完整剩餘球權得分表保留所有第一起點，普通FT與後續重複OREB均計入。校準另用所有有效起點，避免將成功補籃者當分母。','',
'活球＝官方turnover有stealPersonId。bad pass／inbound及out-of-bounds descriptor bad pass歸傳球；lost ball及out-of-bounds descriptor lost ball歸持球。無法區分的出界、未映射官方subType另列，沒有硬配到持球。完整raw subtype／descriptor／是否抄截計數在diagnosis.json。',
'','模擬touchSteal對應持球活球只是觀察代理，不能證明每次真實lost ball都源自同一個動作。原泛稱touch門檻也產生傳球出界、進攻犯規和違例，不能直接解讀成單一控球能力。','',
'## 已驗證：誤差在哪類','',
'| 首次出手前事件／有效起點 | 真實 | 基準 | 非零倍率候選 | 候選−真實，聯合95%（百分點） |','|---|---:|---:|---:|---:|']
labels={'passingLive':'傳球被抄','handlingLive':'持球被抄（模擬touch代理）','passingDead':'傳球死球／出界','handlingDead':'持球死球／出界','offensiveFoul':'進攻犯規','otherViolation':'已映射其他違例','outUnclassified':'無法區分原因的出界','unmappedDead':'未映射死球類型','clock':'時鐘違例','totalTurnover':'合計官方失誤','earlyTurnover':'其中前三秒','lateTurnover':'其中三秒後'}
for k,label in labels.items():
 ci=y['baselineMinusReal'][k]['joint95'];L.append(f"| {label} | {100*x['real'][k]:.4f}% | {100*x['baseline'][k]:.4f}% | {100*y['baseline'][k]:.4f}% | [{100*ci[0]:+.4f}, {100*ci[1]:+.4f}] |")
L+=['','基準傳球被抄−真實的聯合95%為−0.138～+0.120百分點，這個機制不應一起降低。其他主要已映射終結類別均偏高。真實未分類占比的校準門檻，按預登記所有起點口徑計算，已通過5%；每球權第一起點另列約4.98%，包含out-of-bounds step（尚未分派為傳球或持球）及官方類型字串未映射者。這是分類限制，不宣稱全是未知籃球動作。','',
'## 單因素候選與失敗','',
f"依四季等權的所有起點『持球活球＋已映射一般死球』真實／模擬發生率比，固定倍率為 `{m['multiplier']:.16f}`。先存multiplier.json與SHA才跑候選，沒有依得分或勝場挑參數。其對應為事件發生率比對門檻倍率的近似，不是已識別的連續hazard或精確似然估計。",'',
'只在個人FG進攻籃板後、第一次FG／普通FT前縮放一般terminal touch門檻；普通非投籃犯規後保留狀態，出手、FT、球權結束及節末清除。開關postOrebTurnoverRisk，常數postOrebTouchMultiplier。保留原本RNG抽樣、活球／死球及類別分配。傳球攔截、時鐘、犯規、卡、籃板取得／歸屬、分鐘與pace皆不動。',
'','匹配類別的總偏差及平方誤差確實縮小，但同一倍率讓持球活球低於真實0.351百分點（95% −0.476～−0.232），進攻犯規仍高0.292（+0.219～+0.366）。合計失誤低0.957百分點（−1.296～−0.627）。一個倍率不足以重建不同原因的分布；本次沒有事後重估倍率或改分類。','',
'## 得分與快速出手','',
'| 指標 | 真實 | 基準 | 候選 | 候選−基準，聯合95% |','|---|---:|---:|---:|---:|']
for k,label,scale in [('points','完整剩餘球權得分',1),('ftPoints','普通罰球得分',1),('quickProxy','同搶板者三秒內short出手proxy',100),('earlyLoss','前三秒先失去球權',100),('lateLoss','三秒後先失去球權',100)]:
 z=d['intervals']['candidate-baseline'][k];v=[d['pooled'][side][k]*scale for side in ['real','baseline','candidate']];unit='%' if scale==100 else '';L.append(f'| {label} | {v[0]:.4f}{unit} | {v[1]:.4f}{unit} | {v[2]:.4f}{unit} | {z["delta"]*scale:+.4f} [{z["joint95"][0]*scale:+.4f}, {z["joint95"][1]*scale:+.4f}] |')
L+=['','完整得分缺口縮小，但普通罰球得分在原本偏高的基礎上再增加0.00960，95% +0.00713～+0.01223，未通過預登記護欄。這是多活下來的進攻會走進原有事件分支的結果，並非新增犯規公式；沒有用其他參數抵銷它。快速出手proxy仍少約9.30百分點。','',
'## 球隊誤差與聯盟副作用','',
'| 指標 | 基準 | 候選 | 候選−基準，聯合95% |','|---|---:|---:|---:|']
for k in ['netRMSE','winsMAE','winsRMSE']:
 z=a['candidateMinusBaseline'][k];L.append(f'| {k} | {a["versions"]["baseline"][k]:.4f} | {a["versions"]["candidate"][k]:.4f} | {z["delta"]:+.4f} [{z["joint95"][0]:+.4f}, {z["joint95"][1]:+.4f}] |')
L+=['','全部區間跨零，不能宣稱球隊準確度改善。基準2.816是同樣3seed子集，不能與先前20seed的2.555直接比較。三seed不是採用驗收，也沒有非劣性證明。','',
'| 球季 | 效率偏差：基準→候選 | 球權代理偏差：基準→候選 | TOV／場偏差：基準→候選 |','|---|---:|---:|---:|']
for s,q in d['leagueStats'].items():
 u=q['baseline'];v=q['candidate'];L.append(f"| {s} | {u['efficiencyBias']:+.3f}→{v['efficiencyBias']:+.3f} | {u['possessionBias']:+.3f}→{v['possessionBias']:+.3f} | {u['tovBias']:+.3f}→{v['tovBias']:+.3f} |")
L+=['','2023–24與2025–26的聯盟效率偏差超過+0.5；歷史三季原有總失誤不足加深。本次沒重校準聯盟常數。籃板機率和記在誰身上的公式未動；因事件鏈變化造成的籃板總數變化另見accuracy-joint.json，不算新的籃板改進。','',
'## 系統性缺口與推測','',
'已驗證：src/defense_fourth_game.js:393只在新POSSESSION抽plannedViolation；241行消耗一次後清除，301行在independentClock開啟時不由耗時撞限產生違例。個人OREB重設14秒後沒有新的獨立違例抽樣。因此本次搶板後樣本中模擬時鐘違例為零，真實約0.733%。本批只定位，沒有修這條路徑。',
'','推測：應先補齊14秒回合的事件風險，再分開估計活球與各死球原因；不能用通用持球失誤替缺少的時鐘違例補總數。全聯盟TOV不足與搶板後TOV過多同時存在，也顯示只看總平均會掩蓋起始狀態差異；這不證明歷史校準曾刻意用某個事件補另一個事件。其他起始狀態仍需同口徑驗證。',
'','失敗項目：單一倍率未能讓分類分布同時對齊；FT護欄失敗；總失誤及聯盟效率惡化；球隊誤差改善未成立。保留為敏感度實驗，倍率不升為正式參數，既有基準不變。本批到此停止。','',
'## 稽核與重跑','',
f"真實逐球1230／1230／1229／1227場，完整缺場清單在real.json及temporal-qa.json，負的第一事件時間為零。重用先前已逐場驗證的12份基準輸出（14,760場），本批只新增12份候選完整賽季（14,760場）。新adapter開關關閉另12組單場的比分及球員統計完全一致。{audit['protectedFiles']}份受保護檔案雜湊未改，protocol與multiplier雜湊驗證通過。第一次動態模組有括號語法錯誤、未產生模擬輸出，已記implementation-correction.json；只修語法，未改規則或倍率。",'',
'```powershell',
'node reports/defense-tenth/step4-rebounds-turnover-types/test.mjs',
'node reports/defense-tenth/step4-rebounds-turnover-types/read.mjs',
'python reports/defense-tenth/step4-rebounds-turnover-types/analyze.py',
'# multiplier.json 是已鎖定的測量值，核對 multiplier.sha256，不重新調參',
'node reports/defense-tenth/step4-rebounds-turnover-types/run.mjs',
'node reports/defense-tenth/step4-rebounds-turnover-types/smoke.mjs',
'python reports/defense-tenth/step4-rebounds-turnover-types/candidate-analysis.py',
'python reports/defense-tenth/step4-rebounds-turnover-types/outcomes.py',
'python reports/defense-tenth/step4-rebounds-turnover-types/accuracy.py',
'python reports/defense-tenth/step4-rebounds-turnover-types/report.py','```','',
'candidate-diagnosis.json為共用量測程式輸出，baseline欄位在該檔代表候選（檔內simulationVersion已註明）；其中再算出的eligibility／ratio不是第二個採用參數。唯一實際使用的倍率是先鎖定的multiplier.json，沒有反覆調整。']
(R/'report.md').write_text('\n'.join(L)+'\n',encoding='utf8');files={str(f.relative_to(R)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'};(R/'deliverable-hashes.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf8');print('Complete:',len(files),'deliverables; guard results',guards)

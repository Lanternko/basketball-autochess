import json,hashlib,datetime
from pathlib import Path
import numpy as np
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
save=lambda n,x:(r/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=read(r/'protocol.json');d=read(r/'diagnostics.json');timing=read(r/'timing-analysis.json');cal=read(r/'calibration.json');old=read('reports/defense-tenth/step4-rebounds-turnover-time/analysis.json')['cells']
assert hashlib.sha256((r/'protocol.json').read_bytes()).hexdigest()==(r/'protocol.sha256').read_text().strip()
assert hashlib.sha256((r/'timing-prereg.json').read_bytes()).hexdigest()==(r/'timing-prereg.sha256').read_text().strip()
full=read(r/'joint-intervals.json') if (r/'joint-intervals.json').exists() else None
league=[]
if full:
 for s in p['seasons']:
  source=next(x for x in d['league'] if x['season']==s);truth=source['truth'];row={'season':s,'truth':truth}
  for mode in ['baseline','combined']:
   allstats=[];games=0
   for seed in p['fullSeeds']:
    f=Path('reports/defense-tenth/step4-rebounds-turnover-time/runs')/f'{s}-split-{seed}.json' if mode=='baseline' else r/f'runs/{s}-combined-{seed}.json';x=read(f);games+=2*len(x['matches']);allstats.extend(t['stats'] for t in x['teams'])
   z={k:sum(t[k] for t in allstats) for k in allstats[0]};poss=z['fga']-z['oreb']+z['tov']+.44*z['fta']
   row[mode]={'eff':100*z['pts']/poss,'tov':z['tov']/games,'fg':100*z['fgm']/z['fga'],'three':100*z['fg3m']/z['fg3a'],'oreb':z['oreb']/games,'dreb':z['dreb']/games,'ppg':z['pts']/games,'poss':poss/games,'clock':z['clockTov']/games,'startedPoss':z['poss']/games}
  b=row['baseline'];c=row['combined'];row['gates']={'eff':abs(c['eff']-truth['eff'])<=.5}
  for k in ['tov','fg','three','oreb','dreb']:row['gates'][k]=abs(c[k]-truth[k])<=abs(b[k]-truth[k])+.1
  league.append(row)
else:league=d['league']
save('league-final.json',{'seeds':p['fullSeeds'] if full else p['diagnosticSeeds'],'rows':league})
# Adoption also requires the observed process to be credible. Timing is exploratory;
# do not call it a preregistered numerical pass/fail threshold.
paired=full['comparisons']['four-seasons-equal']['paired']['combinedMinusbaseline'] if full else None
predictionSafe=paired is not None and all(paired[k]['joint95'][0]<=0 for k in ['netRMSE','winsMAE'])
formal=bool(d['eventGatesPass'] and all(all(x['gates'].values()) for x in league) and predictionSafe)
save('decision.json',{'adopted':False,'preRegisteredGatesPass':formal,'eventDiagnosticPassed':d['eventGatesPass'],'leagueGatesPass':all(all(x['gates'].values()) for x in league),'predictionSafe':predictionSafe,'reason':'Counts improved but post-OREB timeout timing remains inconsistent; retain as experiment, no threshold retuning','timingIsExploratory':True,'baseline':'pure-oreb-turnover-time-1','physicalNoRimRateIdentified':False})
f=lambda x:f'{x:.3f}';pct=lambda x:f'{100*x:.3f}%'
lines=['# 進攻籃板時鐘：互斥違例路徑','',f"預登記的數量、聯盟偏差與球隊預測不退步門檻：{'通過' if formal else '未通過'}。額外耗時診斷不符，列為探索性失敗，不追認為預登記門檻，也沒有回頭修改參數。決策上先保留候選，正式基準不升級。",'',
'結論：違例數量的前後半驗證改善，但籃板後違例的時序仍不合理，保留實驗版，不取代正式基準。新球權、投失飛行到期、個人進攻籃板後逾時已分開記帳；不能把次數通過當成物理過程已校準。','',
f"版本 `{p['version']}`，登記UTC {p['registeredUTC']}，protocol SHA-256 `{(r/'protocol.sha256').read_text().strip()}`。四季都已看過答案，全部是開發季同季重現與事件驗證。",'',
'## 已驗證：實作與校準','',
'- 三個機制可獨立開關：`rimContactClock`、`competingFreshClock`、`postOrebDeadline`。原版、v1–v5及正式籃板基準均未修改。',
'- 投失飛行到期只在實際投失後發生；個人OREB後逾時先決定能否及時出手，失敗耗完剩餘進攻時限，直接返回，不記FG或另一次籃板。成功分支保留條件耗時CDF。這是事件結果與耗時的混合分布，不把所有CDF尾部直接轉成違例。',
'- 只有節內剩餘時間大於進攻時限才抽逾時；節末優先。個人FG OREB只抽一次，犯規或團隊留球後不重抽這個個人OREB分支。',
'- 10項deadline單元斷言與實際球賽100%逾時整合測試通過；所有模擬均通過原有球員／球隊、投籃、失誤等加總檢查。',
'- 正式基準模式四季×3 seed完整逐場比分及全部球員／球隊統計完全一致，共14760場；先導抽樣亦通過3072場比分一致檢查。',
'',
'只用各季前半合併估計；後半不重估。先導樣本為每季均勻取256場×3 seed，以前半的模擬可用機會當分母：',
'',f"- 其餘新球權違例機率 = {cal['freshClockProbability']:.9f}。分子是實際全場違例扣除近接投失違例與個人OREB後違例後的剩餘數量。",
f"- 個人FG OREB後逾時機率 = {cal['postOrebClockProbability']:.9f}。分子為真實個人FG OREB後、下一次顯著事件前的違例。",
f"- 有效未碰框參數固定沿用上一批訓練擬合 {p['pEffective']:.9f}，本批未重估。它仍不是實測物理機率。",'',
'## 開關對照：後半段','',
'下表是四季合併、完整賽程3 seed診斷。聯合事件區間對季內真實比賽、模擬比賽及跨季共用的seed索引重抽4000次；它是事件適配診斷，與下方球隊預測的franchise＋seed區間分開。','',
'|版本|投失後近接違例／投失|個人FG OREB後違例／OREB|全場違例／隊／場|','|---|---:|---:|---:|']
for x in d['eventResults']:
 if x['half']!='test':continue
 if x['mode']=='baseline':lines.append(f"|真實|{pct(x['immediateRate']['real'])}|{pct(x['postOrebRate']['real'])}|{f(x['clockPerTeamGame']['real'])}|")
 lines.append(f"|{x['mode']}|{pct(x['immediateRate']['sim'])}|{pct(x['postOrebRate']['sim'])}|{f(x['clockPerTeamGame']['sim'])}|")
h=next(x for x in d['eventResults'] if x['mode']=='combined' and x['half']=='test')
lines+=['','combined−真實的事件差異95%區間（百分點）：']
for key in ['immediateRate','postOrebRate']:
 x=h[key];lines.append(f"- {key}：{100*x['difference']:+.4f} [{100*x['difference95'][0]:+.4f}, {100*x['difference95'][1]:+.4f}]。")
lines+=['','全場違例分解，單位／隊／場：','', '|路徑|真實|combined|','|---|---:|---:|']
for k in ['immediate','postOreb','other']:lines.append(f"|{k}|{f(h['clockPathsPerTeamGame']['real'][k])}|{f(h['clockPathsPerTeamGame']['sim'][k])}|")
lines+=['',
'其他路徑仍是殘餘類別，並非每種實際進攻違例均已獨立重建；新球權抽樣也尚未完整描述犯規保留球後的逾時風險。前半估出的全聯盟共同機率不會自動追上後半的實際頻率變動。',
'',
'## 失敗項目：耗時','',
'在本批耗時產出前另登記 timing-prereg.json，未變更正式門檻或參數。真實資料完整逐球；模擬用各季均勻256場×3 seed，baseline／combined；對應比分與完整賽程結果一致。以下限個人OREB時節內剩餘時間>14秒，且下一個顯著事件就是違例。這是事後機制診斷，不是預登記的數值驗收門檻。','',
'|版本|樣本|平均秒數|≤3秒|≥13秒|','|---|---:|---:|---:|---:|']
t=timing['rows'][-1]
for k in ['real','baseline','combined']:
 x=t[k];lines.append('|'+k+'|'+str(x['n'])+'|'+('—' if x['meanSeconds'] is None else f(x['meanSeconds']))+'|'+('—' if x['atMost3Seconds'] is None else pct(x['atMost3Seconds']))+'|'+('—' if x['atLeast13Seconds'] is None else pct(x['atLeast13Seconds']))+'|')
lines+=['',
'原因已能從實作確認：post-OREB失敗機率目前對所有可用剩餘時鐘相同；大部分OREB被判為碰框後拿到14秒，因而大多數新逾時也等了14秒。它雖補上計數，仍錯置發生時機。這不能靠下修舊違例總量解決，也不應解讀為實測未碰框比例太低。有效接觸參數、剩餘時鐘分布與逾時條件風險仍糾纏。',
'',
'## 20 seed事件數量複核','']
if (r/'events-20seed.json').exists():
 xx=read(r/'events-20seed.json')[-1];a=xx['real'];b=xx['combinedMean'];lines += [f"後半合併：近接違例率 {pct(b['immediateRate'])}（真實 {pct(a['immediateRate'])}）；個人OREB後違例率 {pct(b['postOrebRate'])}（真實 {pct(a['postOrebRate'])}）；全場違例 {f(b['clockPerTeamGame'])}／隊／場（真實 {f(a['clockPerTeamGame'])}）。這是20 seed點估計，前面的事件差異區間仍屬獨立3 seed診斷，不挪作20 seed區間。",'']
lines += ['## 球隊準確度','']
if full:
 pooled=full['comparisons']['four-seasons-equal'];lines+=['20 seed（20261012–31），每季內去均值、四季等權；共同franchise與seed跨季成對重抽20000次。負差表示誤差下降。全季都已看過答案，沒有資料外提升的主張。','',
 '|指標|正式基準|combined|差 [聯合95%]|','|---|---:|---:|---:|']
 for k in ['netRMSE','winsMAE','winsRMSE','OREB_RMSE','DREB_RMSE','Pearson','SDRatio','calibrationSlope']:
  b=pooled['versions']['baseline'][k]['point'];c=pooled['versions']['combined'][k]['point'];z=pooled['paired']['combinedMinusbaseline'][k];lines.append(f"|{k}|{b:.4f}|{c:.4f}|{z['point']:+.4f} [{z['joint95'][0]:+.4f}, {z['joint95'][1]:+.4f}]|")
else:lines.append('事件門檻未通過，未擴跑20 seed；不宣稱MAE改善。')
lines+=['',
'## 聯盟副作用','',
f"下表使用 {len(p['fullSeeds']) if full else len(p['diagnosticSeeds'])} seed；合併計數口徑。數值為基準→候選（真實）。未調pace、一般失誤、FG或籃板參數。",'',
'|球季|效率／百回合|失誤／隊／場|OREB／隊／場|DREB／隊／場|球權代理／隊／場|','|---|---:|---:|---:|---:|---:|']
for x in league:
 b=x['baseline'];c=x['combined'];tr=x['truth'];cells=[f"{b[k]:.3f}→{c[k]:.3f} ({tr[k]:.3f})" for k in ['eff','tov','oreb','dreb']];lines.append('|'+x['season']+'|'+'|'.join(cells)+f"|{b['poss']:.3f}→{c['poss']:.3f}|")
lines+=['','各季聯盟門檻：']
for x in league:lines.append('- '+x['season']+'：'+json.dumps(x['gates'],ensure_ascii=False))
lines+=['',
'三個seed曾出現2024–25防守籃板／場退步超過0.1的訊號；20 seed未重現，不能以小樣本結果宣稱副作用成立。進攻與防守籃板的球隊間RMSE變化也都未達聯合區間顯著。','',
'同樣的違例總數放在不同時間，會改變全場可用時間與投籃／籃板機會。舊新球權違例常耗24秒，新自然到期與籃板後逾時的耗時不同；因此球權代理、得分與籃板／場可一起變動。這不是多計一個籃板本身，而是時序重分配的後果。是否符合真實節奏仍需獨立驗證，這輪沒有用重新調pace掩蓋。',
'',
'球權代理不是引擎逐次計數的實際新球權，不能把代理增加全部稱為多出來的進攻次數。尤其投失後直接違例會同時留下FGA與TOV，需分開看。','',
'## 時間預算的開關拆解（3 seed診斷）','',
'下列四季等權；rimPrior直接引用上一批同參數、同賽程、同seed的完整結果。各開關會互相影響，不作線性可加的因果分攤。','',
'|版本|球權代理／隊／場|實際新球權／隊／場|FGA／隊／場|顯式Violation等待秒／隊／場|','|---|---:|---:|---:|---:|']
attr=read(r/'attribution.json')['rows']
for mode in ['baseline','fresh','post','rimPrior','combined']:
 aa=[x for x in attr if x['mode']==mode];lines.append('|'+mode+'|'+'|'.join(f"{np.mean([x[k] for x in aa]):.3f}" for k in ['possProxy','startedPoss','fga','timeViolation'])+'|')
lines+=['',
'顯式Violation秒數只指原地耗完時限的等待；自然投失到期之前的時間記在Setup／Pass／Release／Flight等類別，不能把這欄當成所有違例球權的完整耗時。',
'',
'## 推測與下一步','',
'下一輪應讓籃板後逾時風險依「搶回當下的剩餘進攻時鐘」而變動，同時約束次數與耗時分布；只用訓練期資料，接觸狀態仍列為不可直接識別。先檢查模型是否有足夠的短鐘OREB機會，不應先把未碰框比例調高來硬湊早期違例。預期改善的是事件時序與時間預算，球隊MAE是否改善仍未知。',
'',
'限制：尚未建模到期當下防守方立即明確取得控制球的例外；抽象飛行時間不等於真實接觸時間；時計違例仍沿用舊引擎球員TOV加總慣例，暫記當下第一槽球員，未宣稱個人責任歸因正確。所有殘餘偏差與未通過門檻保留，不作球隊補丁。',
'',
'正式基準維持 pure-oreb-turnover-time-1。本批停止，不自動啟動下一輪。','',
'## 重跑','', '```powershell',
'node reports/defense-tenth/step4-rebounds-clock-competing/test.mjs',
'node reports/defense-tenth/step4-rebounds-clock-competing/integration.mjs',
'node reports/defense-tenth/step4-rebounds-clock-competing/run.mjs --pilot',
'python reports/defense-tenth/step4-rebounds-clock-competing/fit.py',
'node reports/defense-tenth/step4-rebounds-clock-competing/run.mjs',
'python reports/defense-tenth/step4-rebounds-clock-competing/analyze.py',
'node reports/defense-tenth/step4-rebounds-clock-competing/timing-real.mjs',
'node reports/defense-tenth/step4-rebounds-clock-competing/timing-run.mjs',
'python reports/defense-tenth/step4-rebounds-clock-competing/timing-analyze.py',
'node reports/defense-tenth/step4-rebounds-clock-competing/run.mjs --full # 僅事件門檻通過後',
'python reports/defense-tenth/step4-rebounds-clock-competing/prediction.py',
'python reports/defense-tenth/step4-rebounds-clock-competing/full-events.py',
'python reports/defense-tenth/step4-rebounds-clock-competing/attribution.py',
'python reports/defense-tenth/step4-rebounds-clock-competing/finish.py',
'```','',
'模擬會略過已有本批輸出；乾淨重做請另立目錄，不覆寫封存版本。']
(r/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
protected=read(r/'protected-before.json');changed=[f for f,h in protected.items() if not Path(f).exists() or hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h];assert not changed,changed
save('audit.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protectedFiles':len(protected),'changed':changed,'protocolUnchanged':True,'timingSupplementUnchanged':True})
save('deliverable-hashes.json',{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in r.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'})
print(json.dumps({'formalGatesPass':formal,'adopted':False,'paired':paired,'protected':len(protected)}))

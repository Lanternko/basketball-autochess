import json,hashlib,sys
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent;R=O.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def fmt(x,n=2):return '—' if x is None else f'{x:.{n}f}'
def interval(x):return '—' if not x else '['+', '.join(fmt(v) for v in x)+']'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(x) for x in row)+' |' for row in rows])+'\n'
def link(name,file):return f'[{name}]({(O/file).as_posix()})'
P=read(O/'protocol.json');cases=read(O/'cases.json');cover=read(O/'tracking-coverage.json');pbp=read(O/'pbp-coverage.json');port=read(O/'portability.json');changes=read(O/'portability-changes.json');onoff=read(O/'onoff-results.json');availability=read(O/'availability-results.json');dates=read(O/'tracking-date-audit.json');org=read(O/'organizers.json')
labels={'catchFG':'接球投 FG%','catch3FG':'接球三分 FG%','pullFG':'持球投 FG%','pull3FG':'持球三分 FG%','catchShare':'接球投占 FGA','pullShare':'持球投占 FGA','assistedMakeShare':'被助攻占 FGM'}
sha=(O/'protocol.sha256').read_text().split()[0]
lines=['# T2b：進攻卡換隊檢定與組織者依賴（四個已看過答案球季）','',
'結論：已量到組織者在場／出賽時的出手分工差異，但「角色球員投籃卡吸收主控功勞，且命中率落差主要集中接球投」沒有獲得兩個個案一致支持。溜馬不符合預登記的接球投集中條件；灰熊僅通過分類算術條件，Morant 在場的整體 FG 差仍跨零，不能認定主控造成投籃卡失準。此項完成量測與提案後停止，未建卡、未改引擎、未跑模擬。','',
'另有必須更正的 T2 問題：前次補充誤讀區段 DREB 的隊側，這是我的記帳判讀錯誤。舊產物保留，'+link('獨立勘誤','t2-rebound-erratum.md')+'列出所有受影響數字；全季 box／模擬籃板率不受影響。','',
'## 1. 登記、資料與口徑','',
f'版本 `{P["version"]}`；登記時間 `{P["registeredAt"]}`；SHA-256 `{sha}`。先登記再下載及產出。四季全部為已看過答案的描述性資料，使用全季個人數據選組織者與分組，不能解讀成截止日前預測成績。在場結果只當驗證用答案，沒有寫回任何卡。','',
'官方追蹤表為 `leaguedashplayerptshot` 的 GeneralRange：空白／Catch and Shoot／Pullups。864 筆請求全部成功：四季各全聯盟與30隊×3分類，另兩個個案各82日期×3分類。原始回覆、網址、參數與 SHA 見 '+link('抓取清單','fetch-manifest.json')+'。','',
'「球員有一筆追蹤資料」不代表每次出手都有追蹤：表中計數比可能超過100%，不把它當覆蓋率。計數不同仍保留原始值，未以 box 比例補齊；接球投、持球投與餘項的計數皆非負。','']
rows=[]
for c,b in zip(cover['inventory'],pbp):
 rows.append([c['season'],f"{c['trackingPlayers']}/{c['players']}",fmt(c['minuteCoverage']*100,4)+'%',f"{int(c['trackingFGA'])}/{int(c['officialFGA'])}",fmt(100*c['trackingFGA']/c['officialFGA'])+'%',f"{b['strictGames']}/1230",f"{b['matchedFGA']}/{b['strictFGA']}"])
lines+=[table(['球季','有追蹤列球員','分鐘可取得率','追蹤／box FGA','FGA 計數比','嚴格逐球場數','嚴格出手陣容接合'],rows),
'被助攻比例由逐球的 assistPersonId／FGM 計算。四季各有1230／1230／1229／1227場逐球；具助攻姓名卻缺 assistPersonId 的進球均為0。逐球與 box 少量 FGA 不一致的完整清單保留在 '+link('逐球稽核','pbp-coverage.json')+'，不手改。非嚴格比賽可用於全季被助攻進球計數，僅嚴格比賽用於場上五人比較。','',
'兩個個案的逐日追蹤加總都與相同球隊全季追蹤表完全一致；溜馬追蹤7303次出手、box7304，灰熊7648對7654。日期與球員層級差異見 '+link('逐日稽核','tracking-date-audit.json')+'。其餘球季全聯盟追蹤與 box 計數差異的來源未完全查明，不能宣稱逐球標籤完全覆蓋。','',
'## 2. 哪些比較做得到','',
'精確的接球投／持球投「組織者場上／場下」FG% 做不到：現有追蹤端點為日期聚合，沒有逐球追蹤標籤或 OnOff 篩選。[端點定義](https://raw.githubusercontent.com/swar/nba_api/master/src/nba_api/stats/endpoints/leaguedashplayerptshot.py)支持日期與出手篩選，未提供這項交叉條件。因此分成兩份，不混稱同一個效果：','',
'- 逐球場上／場下：同一球員、同一分區（禁區／中距離／三分），比較 FG、被助攻占進球比例、文字明確標示的 pull-up 占出手比例。最後一項只是代理，漏掉未標示的持球投，不等於官方完整分類。','- 官方整場出賽／缺陣：精確接球投、持球投，按同一球員與兩分／三分分層；這是整場可用性比較，仍混有對手、輪替及角色差異。','',
'組織者以球隊內 AST/min 最高者選出，至少500分鐘、場均20分鐘；另保留前季同規則選出的組織者。角色組為當季至少500分鐘或分鐘前十，且 AST%<20%、USG%<25%，排除當季與前季組織者。區段比較只納入該組織者實際為本隊出賽的嚴格比賽；不把他在對手隊出賽算作本隊出賽。','',
'ON/OFF 球員每邊至少50 FGA，分區每邊至少20 FGA，取兩邊較小分母加權。個案按整場重抽20000次；不把每次出手當獨立樣本。非模擬量測沒有 seed 不確定性。','']
lines+=[table(['球季','溜馬組織者','GP／分鐘','灰熊組織者','GP／分鐘'],[[s,org[s]['1610612754']['name'],f"{org[s]['1610612754']['GP']}／{int(org[s]['1610612754']['MIN'])}",org[s]['1610612763']['name'],f"{org[s]['1610612763']['GP']}／{int(org[s]['1610612763']['MIN'])}"] for s in P['seasons']]),
'Morant 2023–24僅9場，未達選取門檻，因此灰熊2024–25的「前季組織者」是 Pippen，當季組織者才是 Morant。Haliburton 2025–26零出賽，沒有可識別的 ON 樣本，沒有替他補值。','',
'## 3. 四季場上／場下與換隊檢定','',
'全聯盟下表為描述性點估計，單位百分點、方向為 ON−OFF；沒有對全聯盟點值宣稱因果或顯著。逐球記錄被助攻的是進球，分母必須是 FGM；它不是「被助攻出手命中率」。','']
lines+=[table(['球季','組別','合資格球員','FG 差','被助攻占 FGM 差','明示持球投占 FGA 差'],[[r['season'],r['subset'],r['players'],*[fmt(r['standardizedOnMinusOffPP'][m]) for m in ['FG','assistedMakeShare','explicitPullupShare']]] for r in onoff if r['team']=='league' and r['kind']=='current']),
'所有1488筆合資格球員／球隊／組織者對照（含前季錨點）見 '+link('逐球員 ON/OFF','onoff-players.json')+'；個案區間見下一節。','',
'相鄰季要求兩季各500分鐘、主要效力球隊占分鐘至少60%。FG 每類各100次，三分命中率各75次3PA；分布各200次總出手。季中前後各300分鐘，FG每類各50次、3FG各40次；分布各100次總出手。後者原登記未另訂分布門檻，實作採相鄰季的一半並在此明列；不是看到成績後選門檻。官方交易子樣本沿用 T2 交易稽核，不把所有短約換隊都叫交易。','',
'相關在各轉換期先去均值、等權合併；20000次球員＋franchise 配對重抽，兩端同抽，期別在重抽內等權。相關顯示穩定性，不是換隊因果證明。下列為 r [95%]；n 是球員對數，不是獨立球員數。','']
rows=[]
for m,label in labels.items():
 cells=[]
 for group in ['same','moved','officialTradeParticipant']:
  r=next(x for x in port if x['metric']==m and x['group']==group);cells.append(f"{fmt(r['pearson'])} {interval(r['ci95'])}; n={r['n']}")
 rows.append([label,*cells])
lines+=[table(['指標','留隊相鄰季','換隊相鄰季','官方交易季中前後'],rows),
'各球季／轉換期獨立結果見 '+link('分期結果','portability-by-period.json')+'。季中持球三分只有25對，部分重抽沒有足夠變異，相關有效重抽19165次；不把20000次當作20000份有效估計。','',
'換隊前後「差多少」不能只看相關。以下列平均變動及平均絕對變動，都是百分點；平均變動以後−前計，絕對變動仍包括抽樣誤差，不能當純環境效應。','']
rows=[]
for m,label in labels.items():
 rr=[next(x for x in changes if x['metric']==m and x['group']==g) for g in ['same','moved','officialTradeParticipant']]
 rows.append([label,fmt(rr[0]['meanAbsoluteChangePP']),f"{fmt(rr[1]['meanChangePP'])} {interval(rr[1]['changeCI95'])}",fmt(rr[1]['meanAbsoluteChangePP']),f"{fmt(rr[2]['meanChangePP'])} {interval(rr[2]['changeCI95'])}",fmt(rr[2]['meanAbsoluteChangePP'])])
lines+=[table(['指標','留隊平均絕對差','跨季換隊平均差 [95%]','跨季換隊絕對差','交易前後平均差 [95%]','交易前後絕對差'],rows),
'已驗證：出手占比跨季較穩，命中率的相關較低。跨季換隊 FG 的平均變化區間均跨零，沒有「一換隊就固定掉準」的方向；留隊／換隊相關區間重疊，也沒有正式證據宣稱兩者不同。完整均差與絕對差區間見 '+link('前後差值','portability-changes.json')+'。','',
'## 4. 溜馬與灰熊個案','',
'既有模擬誤差原樣引用，未重跑。以下進攻誤差是場均得分偏差扣掉30隊均值，單位分／隊／場，不能當分／百回合。L2與T0的建卡來源、先驗及全局投影不同，差額不是只切換投籃分類的一因子實驗。','']
a=read(R/'reports/defense-tenth/step3-a2/analysis.json');t0=read(R/'reports/defense-tenth/step4-t0/analysis.json');rows=[]
for c in cases:
 vv=next(x for x in a['cells'] if x['target']==c['season'])['versions']['L2']['teams'];q=next(x for x in vv if x['name']==c['team']);bias=sum(x['off']-x['actual']['off'] for x in vv)/30;cell=next(x for x in t0['cells'] if x['season']==c['season'] and x['version']=='pure');u=next(x for x in cell['teams'] if x['name']==c['team']);rows.append([c['season'],c['team'],fmt(q['off']-q['actual']['off']-bias,3),fmt(u['O'],3),fmt(u['D'],3)])
lines+=[table(['球季','隊伍','L2前季卡進攻誤差','T0當季純卡進攻誤差','T0防守對 net 貢獻誤差'],rows),
'溜馬5.383→1.297重現補充指令的約5.4→1.3。灰熊 L2進攻低估8.532，T0純卡仍低估5.825；T0凍結v3的進攻誤差為−6.091，不要把兩個版本混在同欄。','',
'分類算術：每球員以「當季該分類兩分／三分出手數 ×（前季該類命中率−當季命中率）×分值」加總，除82場。它固定當季出手量，正值代表前季率較高。前季該分區零出手則略過並列覆蓋；低樣本率未重新收縮，這不是新卡或模擬得分貢獻。三分構成差異已在分類內分開。','']
rows=[]
for c in cases:
 for group,key in [('全部輪替','allCategoryGap'),('角色球員','roleCategoryGap')]:rows.append([c['team'],group,*[fmt(c[key][cat],3) for cat in ['catch','pull','other']]])
lines+=[table(['隊伍','組別','接球投差','持球投差','其餘出手差'],rows),
'預登記條件是接球投的絕對差同時大於持球投與其餘，角色組也須一致。溜馬不通過；灰熊通過，但差距接近：全部1.685對1.434，角色組0.737對0.601。這只是分類集中條件，不足以證明組織者因果。其餘出手包含上籃與灌籃，很多仍可被助攻；絕不等同自主創造。','',
'兩個個案的組織者比較（百分點，ON−OFF或出賽−缺陣；95%按整場重抽）：','']
rows=[]
for c in cases:
 for subset in ['all','role']:
  r=next(x for x in onoff if x['season']==c['season'] and x['team']==c['team'] and x['kind']=='current' and x['subset']==subset);ci=r['ci95'] or {};rows.append([c['team'],subset,'逐球',f"{fmt(r['standardizedOnMinusOffPP']['FG'])} {interval(ci.get('FG'))}",f"{fmt(r['standardizedOnMinusOffPP']['assistedMakeShare'])} {interval(ci.get('assistedMakeShare'))}",f"{r.get('bootstrapGames',0)}場／{r['players']}人"])
lines+=[table(['隊伍','組別','比較','FG差 [95%]','被助攻進球占比差 [95%]','樣本'],rows)]
rows=[]
for c in cases:
 for subset in ['all','role']:
  r=next(x for x in availability if x['season']==c['season'] and x['kind']=='current' and x['subset']==subset);ci=r['ci95'] or {};rows.append([c['team'],subset,f"{r['playedGames']}／{r['dnpGames']}",*[f"{fmt(r['onMinusDnpPP'][m])} {interval(ci.get(m))}" for m in ['catchFG','pullFG','catchShare','pullShare']]])
lines+=[table(['隊伍','組別','出賽／缺陣場數','接球FG差 [95%]','持球FG差 [95%]','接球占比差 [95%]','持球占比差 [95%]'],rows),
'接球FG表中合資格分層皆是三分：兩分接球投未達每邊20次門檻，所以該比較的FG差與接球3FG差完全相同，不表示所有接球投都是三分。其他3FG區間、前季組織者的比較，以及逐日缺漏見 '+link('完整出賽／缺陣結果','availability-results.json')+'。Pippen的缺陣僅3場，無合資格官方分類比較；Haliburton整季不在，完全無法估本季ON/OFF。','',
'已驗證：Morant在場，被助攻進球占比+7.74pp [1.83,13.70]，但FG差−0.26pp [−5.22,4.50]；角色組區間更寬。Nembhard出賽時角色組接球投占比+6.88pp [1.33,12.34]，接球FG差−2.15pp [−7.63,3.81]。因此目前可辨識的主要是分工，無法辨識固定命中率增益。多項描述檢查未作多重比較驗收，不將個別過零區間升格為跨季確認。','',
'### 事後補充：被助攻「得分產量」與自主得分產量','',
'看完分類結果後，為避免把「其餘」誤當自主出手，另登記事後探索，見 '+link('探索規格','exploration-supplement.json')+'與SHA。以逐球每分區被助攻FGM／所有FGA、非被助攻FGM／所有FGA拆出產量，固定當季FGA後計算前−後。沒有把投失硬分成被助攻或非被助攻，故不是條件命中率，不能拿來通過前述預登記假說。','']
lines+=[table(['隊伍','被助攻產量差','非被助攻產量差','可比當季FGA／輪替FGA'],[[c['team'],fmt(c['posthocProductionGap']['assistedProduction'],3),fmt(c['posthocProductionGap']['unassistedProduction'],3),f"{c['posthocProductionGap']['coveredTargetFGA']}/{c['posthocProductionGap']['targetFGA']}"] for c in cases]),
'溜馬的被助攻產量下降與自主產量上升並存，與「失去組織者後轉成更多自主出手」相容；但也可能是角色、隊友、傷勢與樣本改變，不能從產量推回被助攻出手機率或把5.89分當成Haliburton的因果貢獻。灰熊的產量變化亦主要在被助攻進球。這是值得追查的推測，與前面的接球投集中測試不同。','',
'## 5. 逐人卡與替代解釋','',
'全部輪替（至少500分鐘或分鐘前十）的前季／當季長、中、近射、pass、drive、handle，官方接球投／持球投FGM/FGA與3FGM/3FGA、出手占比、被助攻進球占比、年齡、分鐘、出賽、分類差值與傷勢來源，都列在 '+link('逐人附表','players.md')+'與 '+link('完整個案JSON','cases.json')+'。','',
'目前卡只有 long／mid／short，沒有接球／持球兩套命中率欄位；不能把同一個long值冒稱兩張子卡。handle及offBall仍全為70；pass／drive則不同。附表把「卡屬性」與「觀測投籃分類」分表。','',
'卡差另含兩個來源：A2 L2取前季GP≥15的建卡流程、T0歷史卡取GP≥30流程；先驗與投籃區域來源／聯盟投影亦不同。歷史T0有效卡還須套其原本shotDelta，2025–26不另套。本次保留原始與有效屬性，沒有重新建卡消除這些差異。因此不把屬性差全稱為球員能力變化。','',
'新秀與前季無樣本者在L2已用目標季個人卡：灰熊Wells、Edey，溜馬Thompson、Kam Jones等，不把他們列成真正前季觀測。前季零分區出手不補率；Jay Huff等小樣本球員的原始率尤其不穩。','',
'官方事件僅作替代解釋：Haliburton跟腱缺陣；Nesmith、Nembhard、Mathurin當季有傷勢；Morant、Bane與Clarke的前季／當季傷勢也可能改變樣本。各事件與官方來源列於逐人附表；其他人標「本次未逐人核實」，不以GP推斷健康。年齡為官方AGE欄，無年齡曲線，不能從兩隊直接估年齡造成多少命中率差。','',
'## 6. 下一版提案（未實作）','',
'我建議先驗證出手方式分配，再決定是否拆投籃能力，沒有證據支持直接加一個「主控在場固定提高命中率」的係數。','',
'1. **個人傾向先拆開。** 在各出手區另存接球投／持球投／其他的attempt share；不把其他叫自主創造。理由是跨季換隊占比相關0.88／0.92，遠比FG穩定。預期改善持球者缺席後誰承接出手的分配；球隊RMSE收益目前不可量化。單獨開關，先驗收個人各類FGA與球權分配，再看純卡T0及T5，失敗即關。','2. **接球與持球命中率分欄候選。** 依各自FGA／3PA向聯盟同區先驗收縮；只用個人投籃數據，低樣本回退至分區混合卡。把現在固定70的handle拆解成可觀測的持球投與控球失誤資訊，不能只拿pull-up FG當控球。當季＋前季混合權重留T3依原規格驗證，本項不預先指定權重或開始建卡。預期提高出手情境可搬移性，沒有證據保證改善隊伍強度。','3. **組織相性只調機會、先不疊加FG。** 由場上球員個人助攻與失誤傾向決定接球機會供給，再和接球出手需求匹配；組織者不足時轉為持球或其他出手，並承擔其各自失誤與命中率。不能用隊伍net、ID、在場殘差反推。現有引擎已經有傳球／創造加成，必須另立開關對照其替換，避免在已含隊友環境的FG卡上再次加分。','',
'擬動位置（僅提案）：新獨立建卡腳本與版本輸出；'+f'[{"src/probability_model.js"}]({(R/"src/probability_model.js").as_posix()}:297)'+'目前assistBoost、passBoost與createBoost；'+f'[{"src/defense_game.js"}]({(R/"src/defense_game.js").as_posix()}:230)'+'目前傳球與出手選擇。凍結版本完全保留。進行前仍需另登記具體新規則、常數、開關與失敗門檻；本次不挑係數。','',
'## 7. 已驗證、推測、失敗','',
'**已驗證：**四季分類資料可取得；兩個案逐日與全季分類計數完全一致；嚴格逐球射手陣容接合100%；出手分布具跨季穩定性；兩個案都有可量到的分工改變。溜馬接球投集中假說不通過；灰熊僅通過算術條件。','',
'**推測：**組織供需和自主承接能力是現有卡未妥善表達的部分；失去主控可能使被助攻產量轉成自主產量。單靠目前觀測無法分離隊友、戰術、傷勢、選擇效應，也無法估計修改後的球隊RMSE收益。','',
'**失敗／限制：**無精確的C/S及完整pullup場上／場下標籤；無被助攻投失分母；Haliburton零ON，Pippen缺陣樣本不足；小樣本pullup三分不穩；tracking與box部分計數不一致、來源未全部定位；前季／當季凍結卡流程不同；季中分布的100次總出手門檻原登記未明訂，屬實作補充，該部分只列探索結果，不稱完整預登記檢定；傷勢未全員核實、未作傷勢因果校正；未執行任何新卡準確度或換隊模擬，所以不宣稱改卡成功。','',
'## 8. 重跑與保留檢查','',
'在專案根目錄，Python需numpy／scipy，Node使用現有環境。抓取有快取且先驗SHA；以下順序保留先後依賴：','',
'```powershell\nnode reports/defense-tenth/step4-t2b/fetch.mjs\npython reports/defense-tenth/step4-t2b/prepare.py\nnode reports/defense-tenth/step4-t2b/cards.mjs\npython reports/defense-tenth/step4-t2b/analyze.py\npython reports/defense-tenth/step4-t2b/availability.py\npython reports/defense-tenth/step4-t2b/changes.py\npython reports/defense-tenth/step4-t2b/enrich.py\npython reports/defense-tenth/step4-t2b/report.py\npython reports/defense-tenth/step4-t2b/audit.py\n```','',
'最終檢查見 '+link('稽核','audit.json')+'。未修改T0、A／A2、v1–v5、src或舊T2產物。T2b到此停止，未自動開始防守籃板實驗、T3或T4。']
(O/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')

detail=['# T2b逐球員附表','', '四季均已看過答案；此表為當季及前季描述。屬性為A2 L2有效卡→T0當季有效卡。新進無前季樣本者在L2使用目標季個人卡，不能當前季觀測。C/S與pull是觀測分類，不是現有卡欄位。raw/effective差異與來源見card-comparisons.json。','']
def ratepair(q,cat):
 if not q or not q.get('tracking'):return '—'
 t=q['tracking'][cat];return f"{int(t['FGM'])}/{int(t['FGA'])} ({fmt(100*t['FGM']/t['FGA'])+'%' if t['FGA'] else '—'})"
def threepair(q,cat):
 if not q or not q.get('tracking'):return '—'
 t=q['tracking'][cat];return f"{int(t['FG3M'])}/{int(t['FG3A'])} ({fmt(100*t['FG3M']/t['FG3A'])+'%' if t['FG3A'] else '—'})"
for c in cases:
 detail += [f"## {c['season']} {c['team']}",'','卡屬性：長射／中射／近射／傳球／切入（0–120）。handle、offBall全為70。AGE為官方該季AGE欄。', '']
 rows=[]
 for q in c['players']:
  card=q['cards'];a,b=card['prior'],card['currentEffective'];rows.append([q['name'],q['AGE'],f"{q['GP']}／{int(q['minutes'])}",int(q['previousMinutes']) if q['previousMinutes'] is not None else '—','前季卡' if card['priorKind']=='A-prior-card' else '當季新人卡',*[f"{fmt(a[k],1)}→{fmt(b[k],1)}" for k in ['long','mid','short','pass','drive']]])
 detail += [table(['球員','AGE','當季GP／分鐘','前季分鐘','L2來源','長射','中射','近射','pass','drive'],rows),'C/S觀測：前季全聯盟合計→當季本隊。分母為該分類FGA。未用組織者在場結果建卡。','']
 rows=[]
 for q in c['players']:
  a,b=q['priorTracking'],q['currentTracking'];rows.append([q['name'],ratepair(a,'catch')+' → '+ratepair(b,'catch'),threepair(a,'catch')+' → '+threepair(b,'catch'),fmt((a or {}).get('metrics',{}).get('catchShare'))+' → '+fmt((b or {}).get('metrics',{}).get('catchShare'))])
 detail += [table(['球員','接球 FGM/FGA (FG%)','接球 3FGM/3FGA (3FG%)','接球占FGA%'],rows),'持球投及被助攻進球觀測：','']
 rows=[]
 for q in c['players']:
  a,b=q['priorTracking'],q['currentTracking'];rows.append([q['name'],ratepair(a,'pull')+' → '+ratepair(b,'pull'),threepair(a,'pull')+' → '+threepair(b,'pull'),fmt((a or {}).get('metrics',{}).get('pullShare'))+' → '+fmt((b or {}).get('metrics',{}).get('pullShare')),fmt(q['assistedMakesPriorPct'])+' → '+fmt(q['assistedMakesCurrentPct'])])
 detail += [table(['球員','持球 FGM/FGA (FG%)','持球 3FGM/3FGA (3FG%)','持球占FGA%','被助攻占FGM%'],rows),'分類算術差（分／82場，前季率−當季率）。原始率不是收縮後能力；低樣本與缺失前季分區詳列JSON。','']
 rows=[]
 for q in c['players']:
  gap=q['categoryScoringGap'];prod=q['posthocProductionGap'];rows.append([q['name'],'是' if q['role'] else '否',*[fmt(gap.get(k,{}).get('oldMinusCurrentPointsPer82Games'),3) for k in ['catch','pull','other']],fmt(prod['assistedProduction'],3),fmt(prod['unassistedProduction'],3),f"{prod['coveredTargetFGA']}/{prod['targetFGA']}"])
 detail += [table(['球員','角色組','接球差','持球差','其餘差','事後被助攻產量差','事後自主產量差','事後可比FGA'],rows),'傷勢替代解釋（事件≠命中率因果；未核實≠健康）：','']
 for q in c['players']:
  notes='；'.join(f"{x['season']} {x['note']} [官方來源]({x['url']})" for x in q['injuryEvidence']) or '本次未逐人核實；GP與分鐘不等於傷勢。'
  detail.append(f"- {q['name']}：{notes}")
 detail.append('')
(O/'players.md').write_text('\n'.join(detail)+'\n',encoding='utf8')

e=read(O/'t2-rebound-erratum.json');rows=e['rows'];err=['# T2補充：區段防守籃板隊側勘誤','',
'前次T2補充誤把區段opponent.dreb換成另一隊的值，錯在我的欄位語義判讀。原產物不覆寫。本次改正只影響該補充的嚴格樣本及陣容分桶DREB%，不影響cached-factors.json的全季box、純卡／v3模擬籃板率，也未觸及T0。','',
'根據'+f'[prepare_defense_b1.js]({(R/"scripts/prepare_defense_b1.js").as_posix()}:32)'+'，一般進攻事件放對方防守側；防守籃板例外，放抓到籃板的同側。故防守側的opponent.dreb其實是自身DREB，opponent.oreb才是對手OREB。正確比率=DREB/(DREB+對手OREB)。本次逐隊加總嚴格場次DREB，與官方相同場次box完全一致，四季均通過。','',
'舊雜湊檢查只能證明檔案未變，無法檢查這個語義錯誤；本次加入事件側別與官方DREB對帳。','',table(['球季','隊伍','舊嚴格DREB%','正確DREB%','DREB／對手OREB'],[[r['season'],r['team'],fmt(r['oldDREBpct'],3),fmt(r['correctDREBpct'],3),f"{int(r['dreb'])}／{int(r['opponentOreb'])}"] for r in rows if r['type']=='teamStrict']),
'所有0／1／2+分桶逐項如下。桶內樣本小不作因果解讀；尤其騎士合資格護框者2+桶為空，不能稱為雙護框證據。','',table(['球季','隊伍','分類','數量桶','舊DREB%','正確DREB%','DREB／對手OREB'],[[r['season'],r['team'],r['type'],str(r['count'])+('+' if r['count']==2 else ''),fmt(r['oldDREBpct'],3),fmt(r['correctDREBpct'],3),f"{int(r['dreb'])}／{int(r['opponentOreb'])}"] for r in rows if r['type']!='teamStrict']),
'勘誤改變部分分桶差距與方向，因此舊的分桶DREB敘述應以本表取代；全季防守籃板被低估的觀察保留，但在做任何籃板機制修正前仍須使用改正後資料評估，不能說所有舊推論都不受影響。']
(O/'t2-rebound-erratum.md').write_text('\n'.join(err)+'\n',encoding='utf8')
print('REPORTS WRITTEN',flush=True)

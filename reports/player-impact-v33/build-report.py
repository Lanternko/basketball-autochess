"""Freeze completed conditional identification; no runtime adoption or new ranking."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path('reports/player-impact-v33');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fit=read(ROOT/'compensation-fit.json');audit=read(ROOT/'zero-self-audit.json')
verifiers=['data-verification.json','probability-verification.json','fit-verification.json','zero-self-audit.json']
for name in verifiers:
 d=read(ROOT/name);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
assert read('reports/player-impact-v32/status.json')['valid'] is False
counts=[]
for s in fit['seasons']:
 season=s['season'];d=read(ROOT/f'{season}-conditional-data.json');ix={c:i for i,c in enumerate(d['columns'])};players=Counter();examples={}
 for row in d['rows']:
  for j,pid in enumerate(row[ix['playerIds']]):
   if row[ix['selfMakeBase']][j]==0 and row[ix['selfMakeSlope']][j]==0 and row[ix['selfMakes']][j]>0:
    players[pid]+=row[ix['selfMakes']][j];examples[(row[ix['gameId']],row[ix['startIndex']],row[ix['endIndex']],row[ix['teamId']],pid)]=row[ix['selfMakes']][j]
 actual={p['playerId']:p['actualUnassistedMakesWithZeroModelSupport'] for p in audit['players'] if p['season']==season}
 assert dict(players)==actual
 a=next(x for x in audit['seasons'] if x['season']==season)
 assert a['nonSaturation']==0 and a['actualSelfMakes']==a['sourceFlowSaturated']==sum(players.values())
 for p in [p for p in audit['players'] if p['season']==season]:
  for e in p['examples']:
   key=(e['gameId'],e['startIndex'],e['endIndex'],e['teamId'],p['playerId'])
   assert examples[key]==e['actualSelfMakes'] and e['assignedSelfRate']==0 and e['sourceSelfRate']>0 and e['saturated']
 counts.append(a)
assert sum(x['actualSelfMakes'] for x in counts)==891

rows=list(csv.DictReader((ROOT/'2025-26-all-player-conditional-scores.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==582 and sum(int(r['freshFga'] or 0) for r in rows)==203079
names={int(r['playerId']):r['name'] for r in rows}
coverage='\n'.join(f"| {s['season']} | {s['coverage']['games']:,} | {s['coverage']['states']:,} | {s['coverage']['freshAttempts']:,} | {s['informativePlayerGames']:,} |" for s in fit['seasons'])
metric=[]
for s in fit['seasons']:
 old=next(x for x in s['measurements'] if x['label']=='fullCompensation');new=next(x for x in s['measurements'] if x['label']=='olderFit')
 metric.append(f"| {s['season']} | {old['primaryNll']:.6f} | {new['primaryNll']:.6f} | {old['primaryNll']-new['primaryNll']:+.6f} | {(old['primaryNll']-new['primaryNll'])/old['attempts']:.8f} | {old['shooterChoiceNll']-new['shooterChoiceNll']:+.6f} |")
zero='\n'.join(f"| {c['season']} | {c['actualSelfMakes']} | {c['players']} | {next(s for s in fit['seasons'] if s['season']==c['season'])['measurements'][0]['undefinedSelfAllocationMakes']} |" for c in counts)
selected=[]
for query in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Cade Cunningham','Victor Wembanyama','Mitchell Robinson','Stephen Curry','Neemias Queta']:
 matches=[p for p in fit['targetPlayers'] if query==names[p['playerId']]]
 assert len(matches)==1,query
 p=matches[0];selected.append(f"| {names[p['playerId']]} | {p['freshFga']} | {p['informativeGames']} | {p['sourcePrimaryOldNll']-p['sourcePrimaryFittedNll']:+.6f} |")
lo,hi=fit['conditionalWholeGameBootstrap95PerAttempt']
text=f'''# v33：從同一場的陣容變動檢查自主機會補償

**已完成四季4,421場原始PBP、270,090個陣容情境、754,914次一般出手的條件分配檢查，並輸出2025–26全582人。這不是新的完整比賽模擬、能力評分或OVR；正式模型沒有變更。**

資料支持減少「沒收到的機會全部轉成自主進攻」這項假設，但只選到已在v31測過的零補償端點。v31的一般比賽驗證已使多數個人誤差退步，三季勝場門檻未過，因此不能據此採用。另查明四季891次真實非助攻進球，在兩個端點都被指派零機率，需處理的是接球／自主機會的共同分配。

## 負荷與傷病原則保留

沿用已確認的[v29原型](../player-impact-v29/report.md)：主要看健康能打時的貢獻；單季傷缺不扣主要評分，反覆多季才小幅扣可靠度。缺賽不補零分鐘；高分鐘封頂；替補只使用來源可交付負荷，再由同位置平均70卡補足。0.10傷病權重仍是待校準政策，對手強弱及先發負荷下的效率外推仍未解決，不能將替補per36視為先發能力。

## 如何識別

對每位球員、每一隊、每一場，固定其實際一般FGA總量，比較該場不同實際五人陣容的出手分配。每個陣容的預期量＝該陣容實際全隊一般FGA × 模型出手者機率，再在同一球員隊伍場次內正規化。所有FGA包含投失，主指標不以進球數挑樣本；立即補籃沿用v17同人、3秒內等代理規則排除。

一個共同λ只混合「v31來源自主限制＝0」與「v30全部剩餘額度補為自主＝1」，不動傳球矩陣、來源屬性、勝負或名字。前三季等權估計，101點網格及局部細化；五折按整場分組，2025–26只檢查既定舊季係數。擴展[0,2]只作診斷。預先規定只有內點混合且舊季留出、目標季、目標季整場bootstrap下限皆改善，才考慮新候選；邊界值不構成已被一般試驗否決版本的採用理由。

| 球季 | 原始場次 | 攻方陣容情境（含零出手） | 一般FGA | 可區分兩端點的球員隊伍場次 |
|---|---:|---:|---:|---:|
{coverage}

來源暴露、疲勞、當下防守、犯規後可記FGA比例、接球與自主的EV選擇依現有引擎重建。獨立重讀全部原始逐球，逐陣容逐人核對FGA／非助攻FGM／助攻FGM；完整嚴格範圍的球員FG帳目相同。另4場實際引擎共3,132個機率呼叫逐項完全一致，漏傳壓迫值會被有限值檢查擋下。

**這仍是同季重現的條件關聯。** 雖按整場留出標籤，來源FG、角色、犯規、使用率描述仍使用完整同季資料，未逐折重建；2025–26也已在先前實驗看過。不能宣稱時間外盲測、獨立事件、自然實驗或因果持球能力。局部陣容結果標籤未直接送入機率函式，不代表所有來源輸入都不含進球結果。

## 結果

前三季、五個留出折與[0,2]擴展診斷都選λ＝0；沒有產生新的內點混合。NLL越低越好，正收益代表限制補償在此條件分配檢查較好。

| 球季 | 全補償主NLL | 舊季係數主NLL | NLL收益 | 每次FGA收益 | 五人出手者NLL收益 |
|---|---:|---:|---:|---:|---:|
{chr(10).join(metric)}

舊三季整場留出等季收益為{fit['olderHeldoutGainPerAttempt']:.8f} NLL／FGA。目標季總收益{fit['checkPrimaryGain']:.6f}，每次FGA {fit['checkGainPerAttempt']:.8f}；2,000次整場區塊bootstrap的95%區間[{lo:.8f}, {hi:.8f}]。幅度很小，不能當作命中率增加的百分點。區間固定來源描述與已估係數，不含重新擬合或來源／模型不確定性。

選定球員如下，只是同場陣容出手分配誤差，沒有轉成球員價值或名次。

| 球員 | 嚴格範圍一般FGA | 有差異場次 | 主NLL收益 |
|---|---:|---:|---:|
{chr(10).join(selected)}

非助攻進球分配、進球後助攻／非助攻標記及五人出手者次指標均在[完整結果](compensation-fit.json)保留。零支援事件不能用有限分數掩蓋：下段明列不可能事件；相關次指標的有限NLL只是1e-12評分下限診斷，未修改執行中的機率，不能稱為有限的精確似然。

## 確認另一個分配缺口

| 球季 | 實際非助攻FGM但兩端點機率皆零 | 涉及球員 | 其中整個球員隊伍場次的條件分配未定義進球數 |
|---|---:|---:|---:|
{zero}

四季891球均重算來源五人分配確認：接球量占滿該球員的終結額度，`incoming≈terminal`、`self=0`，即使來源自主角色大於零。λ只控制接球不足時增加的自主量，沒有接球不足的情況下，λ怎麼調都救不到。2025–26共217球，分布111人，並非某個位置或名字的專屬問題。這些是明確的模型支援缺口，不足以解釋全部排名差異，也未把非助攻進球等同一次單打。

[逐人及原始事件範例](zero-self-audit.json)保留來源自主量、實際接球分配與終結額度。下一個機制試驗應先驗證接球分配如何保留自主機會及傳球守恆，再檢查來源／一般比賽的助攻、出手與得分，不能只為消除零值加入不經驗證的任意加分或按名字修榜。

## 為何仍未採用

[v31一般試驗](../player-impact-v31/report.md)已完成28,023場四季驗證與10人9,600場負荷配對。相較v30，得分／36 MAE 0.775→0.815、助攻／36 0.206→0.267、3P 1.596→1.682百分點，14項個人指標中12項退步；2023–24、2024–25、2025–26勝場界線未過。條件來源分配小幅改善，與可轉移的一般比賽表現是不同檢驗，不能只挑有利的指標。

本輪沒有重新產生一般比賽、沒有新版全員OVR，最新完整實驗榜仍為v24。未知`offBall / screen / handle / breakDbl`仍為70，沒有把新量到的角色率冒稱為這些技能。正式模型仍為`pure-oreb-turnover-time-1`。後衛與中鋒、傷病與替補的整體評分目標未完成。

## 診斷錯誤與修復紀錄

v32準備腳本漏傳`pressureAttribute`，使預期得分比較產生NaN、接球選擇失效；[v32狀態](../player-impact-v32/status.json)已明確作廢全部估計。既有正式比賽引擎有傳該值，本錯誤不影響先前v30／v31一般試驗。v33補上參數、所有機率及EV的有限值檢查後，四季重新建資料，並以3,132次實際引擎呼叫核對一致。

v33初次擬合在主指標與五折完成後，因次指標假設每個自主進球皆有正機率而停止；沒有寫出結果。保留[該次協定](fit-protocol-before-secondary-support-check.json)，明列零支援及未定義群組後重新執行。主指標、訓練資料、搜尋範圍、驗證門檻與λ結果皆未改，沒有把不可能事件補進模型。

檔案：[全582人條件分數](2025-26-all-player-conditional-scores.csv)、[完整結果](compensation-fit.json)、[預先協定](fit-protocol.json)、[來源核對](data-verification.json)、[引擎呼叫核對](probability-verification.json)、[分數／網格／bootstrap獨立重算](fit-verification.json)。個人總量、per36與在場隊友／對手命中率的最新完整對照仍見[v31全582人176欄](../player-impact-v31/2025-26-player-validation.csv)。
'''
report=ROOT/'report.md';assert not report.exists();report.write_text(text,encoding='utf-8')
status={'stage':'completed-conditional-source-identification','valid':True,'adopted':False,'goalComplete':False,'fullOvr':False,'newOrdinarySimulatedGames':0,'rawGames':4421,'sourceStates':270090,'freshAttempts':754914,'allPlayers':582,'strictPbpPlayers':581,'lambda':fit['training']['lambdaValue'],'candidatePrimaryGatePassed':fit['candidatePrimaryGatePassed'],'unassistedMakesWithZeroModelSupport':891,'remaining':['joint self/receive opportunity allocation','source-opponent quality and workload portability','unknown skills still70','ordinary individual and team adoption gates','complete validated OVR']}
(ROOT/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
main=Path('reports/player-impact-validation/report.md');old=main.read_text(encoding='utf-8');heading=old.index('\n\n')
pointer='最新來源機制檢查為[v33同場陣容分配](../player-impact-v33/report.md)，附[全582人](../player-impact-v33/2025-26-all-player-conditional-scores.csv)與[核對](../player-impact-v33/verification.json)：四季4,421場原始PBP、754,914次一般出手，舊季估計及五折均選到已在v31測過的零補償端點，目標季條件NLL每次FGA僅改善0.000130。一般比賽仍以v31完整比較為準，不能憑這項小幅來源改善採用。另確認四季891次真實非助攻進球被接球分配占滿額度，兩端點均給零自主機會；下一步需修共同分配。v32診斷因漏傳防守壓迫參數已全數作廢；v33重建後3,132次實際引擎呼叫完全相符。來源仍為完整同季描述、未逐折重建，不能宣稱因果或盲測。正式模型及最新完整v24榜不變，任務未完成。'
assert '最新來源機制檢查為[v33' not in old;main.write_text(old[:heading]+'\n\n'+pointer+old[heading:],encoding='utf-8')
files=[p for p in ROOT.iterdir() if p.is_file() and p.name!='verification.json']+[main,Path('reports/player-impact-v32/status.json'),Path('reports/player-impact-v32/report.md')]
verification={'passed':True,'sourceAndProbabilityChecksPassed':True,'scoresGridFoldsBootstrapAnd582ExportPassed':True,'zeroSupportAuditIndependentlyRejoined':True,'officialModelUnchanged':True,'goalComplete':False,'hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
print(json.dumps(status,indent=2))

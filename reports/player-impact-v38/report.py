"""Separate the input bug fix, transport comparison and remaining rating work."""
import csv,json
from pathlib import Path
R=Path('reports/player-impact-v38');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(R/'summary.json');audit=read(R/'input-assembly-audit.json');v=read(R/'verification.json');assert v['passed'];stats37=read('reports/player-impact-v37/status.json');old={ver:{p['result']['playerId']:p['result'] for p in read(f'reports/player-impact-{ver}/ovr-probe-checkpoint.json')['rows']} for ver in ['v30','v37']}
lines=['# v38：修復OVR輸入重複校正，重新控制比較','',
'**已確認並修復實驗OVR輸入的傳球率重複校正錯誤。完成兩種分配共19,200場同來源角色健康負荷對照，所有40個場景及13項計數／配對區間獨立重算。這是輸入修復與機制比較，尚未完成新版全員OVR，也未採用v37。**','',
'## 根因與修復','',
'舊attachCreationReference把「目前卡片的傳球角色率」乘上來源成功率修正比；OVR的多層attachMeasurements又重複呼叫它，因此每多組裝一層就再乘一次。四季球隊重現走單次來源路徑，OVR另走多層路徑，這正是球隊數據看似良好、單人比較仍可能失真的具體原因之一。不是依球員名字或名次補分的問題。','',
'修復改成每次從不可變的v6原始角色卡與v17來源成功率稽核重建，保留原本60分鐘先驗與同一個數學校正，不增加擬合參數。完整一批驗證通過才寫入卡片；重複呼叫不再連乘，也不共用可被修改的來源物件。四季2,262個球員季、2,581張隊伍卡，與原本只校正一次的四季來源卡逐欄相同；連續套用五次仍相同。','',
'| 受查OVR組裝版本 | 人數 | 與單次來源不同的傳球率 | 被壓低 | 被提高 | 比單次多乘幾次 |','|---|---:|---:|---:|---:|---:|']
powers=read(R/'input-audit-verification.json')['repeatedCorrectionPowersAboveCanonical']
for a in audit['versions']:lines.append(f"| {a['version']} | {a['players']} | {a['changedPassRates']} | {a['archivedLower']} | {a['archivedHigher']} | {powers[a['version']]} |")
lines+=['','以原始來源值獨立重算連乘次數，可重建全部4,074列版本／球員傳球率，最大差約2.22e-16。其他角色欄位一致。v24來源角色不受此重複校正問題影響；不能據此宣稱v24所有評分都正確。v29、v30、v34至v37的舊負荷數值保留追溯，但不再視為來源角色相同的機制對照；傷病記錄與分鐘政策本身沒有因此失效。','',
'| 球員 | 原v30傳球率／分 | 原v37 | 正確單次來源 |','|---|---:|---:|---:|']
for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Cade Cunningham','Victor Wembanyama','Mitchell Robinson','Stephen Curry','Neemias Queta']:
 a=next(p for p in audit['rows'] if p['name']==name and p['version']=='v30');b=next(p for p in audit['rows'] if p['name']==name and p['version']=='v37');lines.append(f"| {name} | {a['archivedPassRate']:.6f} | {b['archivedPassRate']:.6f} | {a['canonicalPassRate']:.6f} |")
lines+=['','這些是助攻／接球來源推估的名目角色率，不是純傳球技能值或真實每分鐘傳球次數。每個球員的修正比不同，不能用一個排名乘數代替修復。','',
'## 重新控制的負荷對照','',
'兩組同用單次來源角色：全582名候選與150名對手先發，共732張實際卡均逐欄核對。兩組所有非投籃中心化資料完全相同，五張不同位置平均70隊友也完全一致；各自使用對應分配機制的來源投籃中心化。582個自然位置平均70陣容全走保留傳球分支。只選原本10人，沒有因結果改選球員。','',
'每人兩種負荷（出賽支援分鐘、共同封頂34.98分鐘），30對手、4seed、兩席次、兩輪替時序、四節48分鐘與既有疲勞；每場都配相同分鐘的平均70基準隊。合計2種機制×10人×960場＝19,200場。比較基準是各自同分鐘平均隊的整場分差，不是per36線性放大，也不是OVR分數。','',
'| 球員 | 出賽支援分鐘 | 單次來源＋v30分配 | 單次來源＋v37分配 | 分配改動差［95%］ |','|---|---:|---:|---:|---:|']
cross=0
for p in s['players']:
 a=next(a for a in p['arms'] if a['arm']=='supportedHealthy');d=a['transportChange'];cross+=d['ci95'][0]<=0<=d['ci95'][1];lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v30Canonical']['mean']:+.3f} | {a['v37Canonical']['mean']:+.3f} | {d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] |")
lines+=['',f'{cross}/10個健康支持分鐘的機制差區間跨零。SGA與Curry的點估計在v37較差，未校正多重比較的95%區間未跨零，不能說保留傳球就改善所有後衛。這些是固定模型配對模擬區間，不包含來源／模型／負荷外推不確定性，不能拿10人均值代替全員排名。','',
'## 助攻：輸入錯誤與分配差異分開','',
'下表為同一組出賽支援分鐘的模擬每場助攻，非真實NBA場均。原版本欄含重複校正，僅作錯誤追溯；右欄才是相同來源角色的機制差。','',
'| 球員 | 原v30錯誤輸入 | 修正輸入＋v30 | 原v37錯誤輸入 | 修正輸入＋v37 | 同來源機制差［95%］ |','|---|---:|---:|---:|---:|---:|']
for p in s['players']:
 a=next(a for a in p['arms'] if a['arm']=='supportedHealthy');t=a['stats']['ast'];before={}
 for ver in ['v30','v37']:
  arm=next(x for x in old[ver][p['playerId']]['arms'] if x['arm']=='supportedHealthy');before[ver]=sum(x['playerStats']['ast'] for g in arm['games'] for x in g['pair'])/240
 d=t['transportChange'];lines.append(f"| {p['name']} | {before['v30']:.3f} | {t['v30CanonicalPerWorkloadGame']:.3f} | {before['v37']:.3f} | {t['v37CanonicalPerWorkloadGame']:.3f} | {d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] |")
j=next(p for p in s['players'] if p['playerId']==203999);ja=next(a for a in j['arms'] if a['arm']=='supportedHealthy');fix=ja['stats']['ast']['inputCorrectionChanges']
lines+=['',f"Jokić輸入修復在v30分配內增加{fix['v30']['mean']:.3f}助攻／工作負荷場，點對點95%區間[{fix['v30']['ci95'][0]:.3f}, {fix['v30']['ci95'][1]:.3f}]；在v37分配內增加{fix['v37']['mean']:.3f}，區間[{fix['v37']['ci95'][0]:.3f}, {fix['v37']['ci95'][1]:.3f}]。控制相同來源後，兩種分配的Jokić助攻接近；全10人的助攻機制差95%區間都跨零。不能再把原先6.91→5.97的下降當成分配本身壓縮傳球的證據。",'',
'原始480場路徑重播也顯示傳出次數已下降，沒有因接球EV選擇自主而取消助攻；但那兩組輸入有混淆，故只用來定位檢查方向。[路徑診斷](../player-impact-diagnostics/pass-release-v37/report.md)。','',
'## 傷病與替補規則','',
'保留使用者指定政策：主要看能打時的貢獻，單季傷病不扣分，至少兩季有明確傷病／生病證據才小幅折減正向貢獻；不是把缺賽自動判成傷病。既有原型取充分覆蓋球季的第二高明確傷病比例，可靠度係數0／0.05／0.10作敏感度，0.10仍是待校準政策。','',
'替補先依實際逐場出賽分鐘封頂後的平均負荷測試，不直接把12分鐘的per36效率放大到35分鐘。超過封頂的分鐘不繼續加能力分；實際貢獻透過完整輪替比賽測量，沒有固定按分鐘線性乘分。第六人仍可因實際貢獻強而得到高分。','',
'「出賽支援分鐘」仍只是健康負荷代理，復出限時與部分場次受傷未完全分開；來源對手先發／替補品質與長負荷效率可持續性尚未校準。修復輸入不代表這些問題已解決。上表未套用多季傷病可靠度，沒有因缺賽得到更多每場休息。','',
'## 為何仍未採用','',
'v38只修正OVR輸入，不改兩種比賽引擎的四季來源路徑；一般比賽驗證沿用已完整核對的v30與v37，各自並未通過全部既有勝場門檻。v37四季28,023場驗證中，9／14個人誤差項目退步、四季勝場界線全未過。輸入bug與機制品質是兩件需要分別驗證的事，修復bug不能豁免勝場或個人檢查。','',
'阻攻仍有獨立問題：四季高阻攻族群82個球員季在v37全部低估。以實際陣容／出手拆查，Wemby同範圍真實BLK／36約3.76，原通用生成公式的期望上界約2.24；保留實際球隊阻攻總數再分配約3.55。優先檢查事件總量，但現有防守FG曲線已包含阻攻失投，不能再多扣一次對手FG。[四季785,193次來源出手獨立診斷](../player-impact-diagnostics/block-source-v37/report.md)。','',
'正式模型仍為pure-oreb-turnover-time-1，最新完整實驗OVR榜仍為v24。沒有發布v38前50，也沒有只靠10人排序。無球／掩護／控球／破包夾的70預設未直接量測補齊，個人數據與完整OVR目標尚未完成。','',
'檔案：[來源角色與原版本差異](input-assembly-audit.json)、[獨立連乘重建](input-audit-verification.json)、[同來源卡片核對](input-verification.json)、[40場景13項計數與區間](summary.json)、[實驗協定](protocol.json)、[配對數字核對](verification.json)、[整體核對](all-verification.json)、[v37四季與582人](../player-impact-v37/report.md)。']
f=R/'report.md';assert not f.exists();f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'canonicalRoleInputFixed':True,'sourcePlayerSeasonsTested':2262,'teamCardsTested':2581,'repeatedAssemblyTestCount':5,'actualPlayersAudited':582,'actualAndOpponentCardsControlled':732,'probePlayers':10,'probeGames':19200,'transports':2,'scenarios':40,'withinCanonicalTransportHealthyIntervalsOverlappingZero':cross,'candidateV37FailedWinGateSeasons':stats37['failedWinGateSeasons'],'historicalOvrAssembliesWithRepeatedCorrection':['v29','v30','v34','v35','v36','v37'],'historicalV24SourceRolesCanonical':True,'scope':'OVR input bug repaired in controlled constructor; comparable workload rerun complete. Neither transport adopted and no full OVR ranking.'}
(R/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(status,ensure_ascii=False,indent=2))

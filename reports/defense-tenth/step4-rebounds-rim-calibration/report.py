import json,hashlib,datetime
from pathlib import Path
r=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
a=read(r/'analysis.json');p=read(r/'protocol.json');selection=a['selection'];fmt=lambda v:f'{100*v:.3f}%'
lines=['# 投失碰框時鐘：間接校準與驗證','',
'結論：完成一個聯盟共同有效參數的擬合與後半季驗證，但未通過驗收，不升級正式基準。它不是可識別的物理未碰框率；單靠調碰框機率無法修好進攻籃板後的違例缺口。凍結來源與既有基準不修改。','',
'## 先登記的方法','',
f"版本 `{p['version']}`；UTC {p['registeredUTC']}；protocol SHA-256 `{(r/'protocol.sha256').read_text().strip()}`。四季都已看過答案，只作開發季事件校準。沒有下載新資料或搜尋更多影片。",
'',
'每季按既有賽程順序切成前後兩半。前半合併擬合一個 pEffective，後半只驗證，不重估。先用每季均勻取256場、3 seed 的固定網格 0／0.1／0.25／0.5／1，依相鄰兩點線性內插；再把選定值跑完四季各3 seed 全賽程。沒有以球隊 net、勝場、ID 或失誤總量擬合。',
'',
'實際可觀察標的：投失FG後2秒內，同一進攻方出現24秒違例，期間尚未出現個人籃板、任何防守籃板、另一次出手／罰球／犯規／其他失誤或節末。可以隔著同隊團隊進攻籃板記錄。這是「未有個人控制記錄前的近接違例」，不是影片證實的未碰框，團隊籃板也可能是記錄占位。兩邊使用同一狀態機。',
'',
'第二標的是個人FG進攻籃板後、下一個出手／罰球／犯規／籃板等終止事件之前的24秒違例。這個定義比以前包含中間犯規的全段0.733%更嚴格，不混用。',
'',
'## 擬合結果','',f"pEffective = **{selection['pEffective']:.9f}**。前三 seed 各自擬合為 "+'、'.join(f"{v:.6f}" for v in selection['seedwiseFits'])+'；這是亂數敏感度，不是物理參數信賴區間。',
'',
'|固定有效參數|訓練期近接違例／投失|進攻籃板後違例數|','|---:|---:|---:|']
for g in selection['grid']:lines.append(f"|{g['p']}|{fmt(g['rate'])}|{g['counts']['postOrebClock']}|")
lines+=['',f"真實訓練期標的 {fmt(selection['targetTrainRate'])}。p=0 共12個季×seed、3072場的比分逐場與封存正式基準一致。規則本身與採樣基準未偷偷漂移。",'',
'## 保留後半季驗證','',
'區間是對真實比賽整場重抽2000次的95%區間；用於事件適配門檻。這不是專案所用的球隊＋seed預測增益區間，也不據此宣稱球隊預測改善。模擬排除4場缺逐球資料的場次後比對。','',
'|球季|真實近接違例／投失 [95%]|模擬|真實OREB後違例／個人FG OREB [95%]|模擬|','|---|---:|---:|---:|---:|']
for x in a['eventResults']:
 if x['half']!='test':continue
 u=x['immediateRate'];v=x['postOrebRate']
 lines.append(f"|{x['season']}|{fmt(u['real'])} [{fmt(u['realGameBootstrap95'][0])}, {fmt(u['realGameBootstrap95'][1])}]|{fmt(u['sim'])}|{fmt(v['real'])} [{fmt(v['realGameBootstrap95'][0])}, {fmt(v['realGameBootstrap95'][1])}]|{fmt(v['sim'])}|")
h=next(x for x in a['eventResults'] if x['season']=='pooled' and x['half']=='test')
lines+=['',f"後半合併：全場24秒違例真實 {h['clockPerTeamGame']['real']:.4f}／隊／場，模擬 {h['clockPerTeamGame']['sim']:.4f}；±0.1門檻 {'通過' if a['pooledHoldoutClockPass'] else '未通過'}。",
'',
'近接率合併結果僅略低於真實區間下界約0.00044個百分點；這個判定未納入模擬seed的不確定性，不能把這個微小差距當作確定的統計失敗。拒絕採用的實質原因是OREB後違例為零，以及全場違例過多。','',
'## 全季聯盟副作用','',
'均為合併計數口徑再對同3 seed取平均。基準與候選使用相同seed；真實效率／FG等沿用先前計分板同口徑。數值為基準 → 候選（真實）。這不是20 seed準確度比較。','',
'|球季|效率／百回合|失誤／隊／場|FG%|3P%|進攻籃板／隊／場|','|---|---:|---:|---:|---:|---:|']
for x in a['league']:
 b=x['baselineSameSeeds'];c=x['candidate'];t=x['target']
 cells=[f"{b[k]:.3f} → {c[k]:.3f} ({t[k]:.3f})" for k in ['eff','tov','fg','three']]
 lines.append('|'+x['season']+'|'+'|'.join(cells)+f"|{b['oreb']:.3f} → {c['oreb']:.3f}|")
lines+=['','各季門檻結果：']
for x in a['league']:lines.append('- '+x['season']+'：'+json.dumps(x['gates'],ensure_ascii=False))
lines+=['',
'## 已驗證與失敗項目','',
'1. 參數確實能讓「投失後近接違例」從零上升；後半驗證是否通過見表與analysis.json。規則不是完全不敏感。',
'2. 所有固定網格與選定值都不能產生個人進攻籃板後的違例，明顯不符合真實資料。這是驗收失敗，不用總違例符合掩蓋。',
'3. 目前經驗耗時依剩餘進攻時間限制抽樣，出手機會被擠到時限前；獨立違例只在新球權抽一次。搶回球後沿用時鐘，並沒有補上「持球來不及出手」的分支。飛行到期的自然違例在記OREB之前發生，所以不能代替OREB後違例。',
'4. 舊基準的新球權獨立違例原先就用全場違例目標校過；再疊上自然到期會重複承擔一部分總量。沒有把原參數調低來湊過門檻。應按真實事件拆成互斥路徑再校準。',
'5. pEffective吸收了投籃時間、抽象飛行時間與未知接觸機率的共同誤差，無法聲稱它就是未碰框的21.1%。同一近接違例率可由不同碰框／耗時分布得到，物理參數仍未識別。',
'',
'## 真實違例的互斥分解（下一輪的觀測約束）','',
'以下分類只是可觀察事件路徑，不把它們當成實際碰框標記。','',
'|半季|投失後近接|個人OREB後|其餘|合計／隊／場|','|---|---:|---:|---:|---:|']
for half in ['train','test']:
 x=next(x for x in a['eventResults'] if x['season']=='pooled' and x['half']==half);z=x['real'];den=2*x['realGames'];v=[z['immediateClock'],z['postOrebClock'],z['clock']-z['immediateClock']-z['postOrebClock'],z['clock']]
 assert v[2]>=0
 lines.append('|'+half+'|'+'|'.join(f'{n/den:.4f}' for n in v)+'|')
lines+=['',
'## 推測與下一步','',
'優先修「事件結果與耗時共同決定」：先有及時出手／未及時出手的互斥分支，再在可出手分支抽取耗時，避免把每次出手都裁進時限內。將新球權與搶回球後的違例分開估計，再核對全場分項加總，不能額外疊加同一總量。這預期能修正零OREB後違例與總量重複；能否改善球隊或球員MAE尚未驗證。這批不偷偷加入另一組機制。',
'',
'保留限制：未建模防守方在到期當下立即明確取得球的繼續比賽例外；沒有逐個接觸時點／球體軌跡。不能用這輪近接率把這些缺口一起當成已解決。',
'',
'基準維持 pure-oreb-turnover-time-1。未通過事件與聯盟門檻，因此按預登記規則不擴跑20 seed、不產生新的勝場MAE改善結論；這不是判定參數對勝場完全沒影響。',
'',
'## 重跑','',
'```powershell',
'node reports/defense-tenth/step4-rebounds-rim-calibration/test.mjs',
'node reports/defense-tenth/step4-rebounds-rim-calibration/real.mjs',
'node reports/defense-tenth/step4-rebounds-rim-calibration/run.mjs',
'python reports/defense-tenth/step4-rebounds-rim-calibration/analyze.py --select',
'node reports/defense-tenth/step4-rebounds-rim-calibration/run.mjs --selected',
'python reports/defense-tenth/step4-rebounds-rim-calibration/analyze.py',
'python reports/defense-tenth/step4-rebounds-rim-calibration/report.py',
'```','',
'重跑模擬會略過已有本批結果；需乾淨重做時另建目錄，不覆寫封存產物。']
(r/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
protected=read(r/'protected-before.json');changed=[]
for f,hsh in protected.items():
 q=Path(f)
 if not q.exists() or hashlib.sha256(q.read_bytes()).hexdigest()!=hsh:changed.append(f)
assert not changed,changed
(r/'audit.json').write_text(json.dumps({'checkedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protected':len(protected),'changed':changed,'protocolUnchanged':hashlib.sha256((r/'protocol.json').read_bytes()).hexdigest()==(r/'protocol.sha256').read_text().strip()},indent=2)+'\n',encoding='utf8')
(r/'decision.json').write_text(json.dumps({'adopted':False,'reason':'post-OREB clock violations remain zero; parameter-only candidate failed preregistered gates','baseline':'pure-oreb-turnover-time-1','physicalNoRimIdentified':False},indent=2)+'\n',encoding='utf8')
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in r.rglob('*') if f.is_file() and f.name!='deliverable-hashes.json'}
(r/'deliverable-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(r/'report.md'),'protected':len(protected),'allGatesPass':a['allGatesPass']}))

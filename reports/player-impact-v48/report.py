import json
from pathlib import Path
from statistics import mean
R=Path('reports/player-impact-v48')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
p=read(R/'choice-protocol.json');scores=read(R/'scores.json');base=read(R/'baseline-offense-scores.json');new=read(R/'candidate-offense-scores.json');sel=read(R/'choice-selection.json')
cell=lambda s,v:next(c for c in scores['cells'] if c['season']==s and c['variant']==v)
oc=lambda s,v:next(c for c in (base if v=='v47' else new)['cells'] if c['season']==s)
metrics={}
for v in ['v47','v48']:
 metrics[v]={'teammateTwoFGmae':mean(oc(s,v)['summary']['two:teammates']['mae'] for s in p['seasons']),'teammateRAshareMAE':mean(oc(s,v)['summary']['ra:teammates:shareWithinTwo']['mae'] for s in p['seasons']),'teamPPGmae':mean(cell(s,v)['teamPPG']['mae'] for s in p['seasons']),'pts36mae':mean(cell(s,v)['individualSummary']['ALL']['pts36']['mae'] for s in p['seasons'])}
 for k in ['onshortFGpct','onlongFGpct']:metrics[v][k]=mean(cell(s,v)['defenseSummary']['ALL'][k]['mae'] for s in p['seasons'])
a,b=metrics['v47'],metrics['v48']
gates={'nonzeroOlderThreeSelection':sel['selectedSigma']>0,'teammateTwoFGmaeImproved':b['teammateTwoFGmae']<a['teammateTwoFGmae'],'teammateRAshareMAEimproved':b['teammateRAshareMAE']<a['teammateRAshareMAE'],'teamPPGmeanNonRegression':b['teamPPGmae']<=a['teamPPGmae'],'individualPTS36within002':b['pts36mae']<=a['pts36mae']+.02,'coarseDefenseWithin005pp':all(b[k]<=a[k]+.05 for k in ['onshortFGpct','onlongFGpct']),'fitVerified':read(R/'choice-fit-verification.json')['passed'],'runtimeVerified':read(R/'choice-verification.json')['passed']}
decision={'version':'v48','adopted':all(gates.values()),'gates':gates,'fourSeasonMean':metrics,'gameDefaultChanged':False,'ovrRecomputed':False,'namedPlayerExceptions':False,'scope':'Same-season reconstruction; older-three whole-game cross-validation selects shared regularization. Conditional lineup association is not causal gravity. Make-only prototype not included.','remainingWork':['Curry teammate shooting and off-court composition remain biased.','Observed game appearances and minute targets do not reproduce actual teammate co-occurrence.','Shooter allocation and rotation require separate measurement before attribution to spacing.']}
gates['olderThreeHeldoutNLLimproved']=next(x for x in sel['table'] if x['sigma']==sel['selectedSigma'])['meanNllPerTwoAttempt']<next(x for x in sel['table'] if x['sigma']==0)['meanNllPerTwoAttempt']
decision['adopted']=all(gates.values())
(R/'decision.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
lines=['# v48：隊友陣容與兩分出手區域','','狀態：'+('通過採用條件，可作量測模型開發基準。' if decision['adopted'] else '未通過全部採用條件，保留為候選；正式量測進攻基準仍為 v47。')+'遊戲預設及 OVR 未切換。','','## 變更與證據','','只修改新鮮兩分出手的籃下／其他油漆區／中距離分配。聯合估計投籃人與其他四位隊友的條件選擇係數，保留原本防守係數；三分選擇、所有命中率、罰球、補籃與角色設定不變。沒有姓名特例。','','較早三季、整場五折交叉驗證選出共用 sigma='+str(sel['selectedSigma'])+'；2025–26 不參與選擇。這是同季資料重建，不是預測未來賽季。最初測試的命中率係數僅保留來源資料原型，未混入本候選。','','## 全體誤差','','四季等權平均；百分比指標為百分點。隊友細區使用 strict PBP、新鮮出手共同樣本；個人與球隊使用完整賽季。','','| 指標 | v47 | v48 |','|---|---:|---:|']
for k in a:lines.append(f'| {k} | {a[k]:.4f} | {b[k]:.4f} |')
lines+=['','| 球季 | 隊友兩分 MAE v47→v48 | 隊友籃下占兩分 MAE | 球隊 PPG MAE |','|---|---|---|---|']
for s in p['seasons']:
 vals=[f"{oc(s,'v47')['summary'][k]['mae']:.4f} → {oc(s,'v48')['summary'][k]['mae']:.4f}" for k in ['two:teammates','ra:teammates:shareWithinTwo']];vals.append(f"{cell(s,'v47')['teamPPG']['mae']:.4f} → {cell(s,'v48')['teamPPG']['mae']:.4f}");lines.append('| '+s+' | '+' | '.join(vals)+' |')
lines+=['','## Curry 2025–26','','| 新鮮出手指標 | 實際 | v47 | v48 |','|---|---:|---:|---:|']
for k in ['two:on','two:off','two:teammates','ra:on:shareWithinTwo','ra:off:shareWithinTwo','ra:teammates:shareWithinTwo','ra:teammates:FGpct','paint:teammates:FGpct','mid:teammates:FGpct']:
 x,y=[oc('2025-26',v)['curry']['metrics'][k] for v in ['v47','v48']];lines.append(f"| {k} | {x['actual']:.3f} | {x['predicted']:.3f} | {y['predicted']:.3f} |")
lines+=['','出手組成有所改善，不代表隊友命中率已修好。原 v47 的隊友兩分誤差 −3.34pp，依投籃人×區域分解，組成項約 −3.26pp；固定真實出手與陣容時，預期隊友兩分為 60.34%，完整模擬卻為 58.53%。這指出完整流程的投籃人、區域及同場分配仍有問題。','','目前使用實際每場出賽、先發與分鐘目標，但啟發式換人不保證實際同場陣容。Payton II 等球員在 Curry 上下場時的出手分配有明顯落差；尚不能判定全部來自換人，也不能把條件陣容係數稱作已量測的因果空間能力。','','## 位置、細區與亂數','','個人 ALL/G/F/C、得分／助攻／失誤／三分／罰球及種子結果見 [scores.json](scores.json)；五區防守見 [fine-scores.json](fine-scores.json)。全體逐人新鮮進攻、Curry 投籃人×區域分解、三種子範圍見 [candidate-offense-scores.json](candidate-offense-scores.json)，比較基準見 [baseline-offense-scores.json](baseline-offense-scores.json)。三種子範圍描述模擬波動，不是真實資料信賴區間。','','## 事先列出的採用條件','','| 條件 | 結果 |','|---|---|']
for k,v in gates.items():lines.append(f"| {k} | {'通過' if v else '未通過'} |")
lines+=['','條件取自 [choice-protocol.json](choice-protocol.json)，未因 Curry 個案放寬。驗證見 [results-verification.json](results-verification.json)。']
pair=read(R/'pair-scores.json')
lines+=['','## 同場時間：獨立觀測','','另外重跑 v47 的 2025–26 strict 三種子，只在引擎每段真正計入球員秒數的位置觀測同場時間，未改換人。比賽與全部隊伍／個人統計與原 v47 完全相同。原始 stint 與模擬秒數都限定 Curry 有出賽的共同場次。','','| 球員 | Curry 狀態 | 實際同場分鐘 | 模擬分鐘 | 實際籃下次數/36 | 模擬籃下次數/36 |','|---|---|---:|---:|---:|---:|']
for pid in [1627780,202710]:
 row=next(x for x in pair['rows'] if x['playerId']==pid)
 for arm,m in row['arms'].items():lines.append(f"| {row['name']} | {arm} | {m['actualMinutes']:.2f} | {m['predictedMinutes']:.2f} | {m['actualRAper36']:.2f} | {m['predictedRAper36']:.2f} |")
lines+=['','Payton II 與 Curry 同場時間明顯不足，反而被大量排到 Curry 下場時；Butler 的方向相反。這已證實輪替分配有偏差，但每 36 分鐘的條件出手率也有落差，因此不能說輪替是唯一原因。下一個修正應先改善通用同場輪替，再評估空間與投籃人分配，避免能力係數補償錯誤陣容。完整結果見 [pair-scores.json](pair-scores.json)。']
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps(decision))

import json
from pathlib import Path
from statistics import mean
R=Path('reports/player-impact-v49');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));p=read(R/'protocol.json');rotation=read(R/'rotation-scores.json');scores=read(R/'scores.json');baseOff=read(R/'baseline-offense-scores.json');newOff=read(R/'candidate-offense-scores.json')
rc=lambda s,v:next(c for c in rotation['cells'] if c['season']==s and c['variant']==v)
bc=lambda s,v:next(c for c in scores['cells'] if c['season']==s and c['variant']==v)
keys=['fullActualMinutesMAE','fullRegulationTargetMinutesMAE','phaseAbsoluteMinutesPerAppearance','pairOverlapMinutesMAE','strictRegulationSourceMinutesMAE']
means={v:{k:mean(rc(s,v)[k] for s in p['seasons']) for k in keys} for v in ['v47','v49']};a,b=means['v47'],means['v49']
gates={k+'Improved':b[k]<a[k] for k in keys[:4]};gates['everySeasonActualMinutesNonRegression']=all(rc(s,'v49')['fullActualMinutesMAE']<=rc(s,'v47')['fullActualMinutesMAE'] for s in p['seasons']);gates['runtimeVerified']=read(R/'verification.json')['passed'];gates['fitVerified']=read(R/'fit-verification.json')['passed']
boxMean=lambda v,f:mean(f(bc(s,v)) for s in p['seasons'])
gameplay={v:{'teamPPGmae':boxMean(v,lambda c:c['teamPPG']['mae']),'pts36mae':boxMean(v,lambda c:c['individualSummary']['ALL']['pts36']['mae']),'paintDefenseFGmae':boxMean(v,lambda c:c['defenseSummary']['ALL']['onshortFGpct']['mae']),'threeDefenseFGmae':boxMean(v,lambda c:c['defenseSummary']['ALL']['onlongFGpct']['mae'])} for v in ['v47','v49']}
combinedGates={'teamPPGnonRegression':gameplay['v49']['teamPPGmae']<=gameplay['v47']['teamPPGmae'],'individualPTS36within002':gameplay['v49']['pts36mae']<=gameplay['v47']['pts36mae']+.02,'coarseDefenseWithin005pp':all(gameplay['v49'][k]<=gameplay['v47'][k]+.05 for k in ['paintDefenseFGmae','threeDefenseFGmae'])}
decision={'version':'v49','rotationAdopted':all(gates.values()),'combinedOffenseAdopted':all(gates.values()) and all(combinedGates.values()),'rotationGates':gates,'combinedOffenseGates':combinedGates,'fourSeasonRotationMean':means,'fourSeasonGameplayMean':gameplay,'gameDefaultChanged':False,'ovrRecomputed':False,'healthyAbilityUnchanged':True,'namedPlayerExceptions':False,'scope':'Measured same-season reconstruction. Known game appearances/starters/minute totals retained. Source phase/pair profiles exclude tested game fold. Timing is a statistical plan, not exact target-game substitution replay.','remainingWork':['Residual per-game source timing/overlap differences are expected and reported.','Emergency minimum-five foul-exhaustion retains the existing engine fallback; technical-foul penalties for that rare case are not newly implemented.','Overtime retains the existing heuristic; actual minute errors include differences in actual versus simulated overtime duration.','Player offense/defense calibration must be assessed on the corrected rotation; no automatic OVR or game preset promotion.']}
decision['remainingWork']+=['Payton/Curry overlap remains below source; source pair targets are not exactly realized by the online controller.','Short playing segments remain more frequent than source; the duration distribution is reported, not declared fully accurate.','Guard/big role coverage currently uses positions and a height fallback; flexible small-ball role recognition remains limited.']
(R/'decision.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
lines=['# v49：分鐘、上場時機與隊友搭配','','輪替狀態：'+('通過採用條件，作為後續量測修正的輪替開發基準。' if decision['rotationAdopted'] else '尚未通過全部採用條件，保留候選結果。')+'整體進攻基準：'+('通過回歸條件。' if decision['combinedOffenseAdopted'] else '未通過全部回歸條件，v47 進攻基準保留。')+'遊戲預設與 OVR 未切換。','','## 修正內容','','舊引擎把每位球員的預計分鐘隨比賽時間線性攤平，再由能力、體力、位置與分鐘缺口挑替補。這會讓應和主力同場的替補被排到主力休息時。新版本保留每場既有的實際出賽名單、先發及分鐘目標，改用各節歷史上場分布塑造累積分鐘目標，並追蹤隊友同場時間缺口。能力值完全不改；v48 的出手區域候選未合併。','','同場目標依歷史四種狀態估計：兩人都在場、僅 A、僅 B、都不在場；估計時限定兩人都有出賽的場次。以本場分鐘總額重新解出可行的共同分鐘，不直接照抄某一場的換人。每兩分鐘的機率經校準，對齊每階段五人與本場每位球員的分鐘總額，再在既有死球換人時點追趕累積目標。','','一般最短上場／休息時間取來源資料第 25 百分位；短暫出場已達目標時可提前換下。節間休息解除一般最短段落限制；最後三分鐘與剩餘分鐘已難完成時，也允許調整。罰球中的受保護投籃人不換下；有足夠人手時排除傷病與犯滿球員。','','## 資料與驗證邊界','','四季來源整場五折。每場使用其整折以外的輪替分布；先驗強度只由較早三季的留出機率誤差選擇。2025–26 不參與選擇。被測比賽的實際換人序列、投籃與得分都不作本場輪替輸入。已知的每場出賽／先發／分鐘總額仍是原本 v47 使用的重建條件，這不是未來出賽時間預測。','','加時保留舊啟發式換人。極少數來源僅列少量實際出賽球員、模擬又發生多名犯滿時，保留原引擎最低五人的處理並另外記錄，未把它當一般合法候選重排；額外技術犯規的事件處理不在本次修正內。NBA 最低五人例外與技術犯規規定見 [官方規則第 3 條](https://cdn.nba.com/manage/2026/01/Official-2025-26-NBA-Playing-Rules.pdf)。','','## 四季輪替誤差','','單位為分鐘。完整賽季實際分鐘誤差含真實與模擬加時長度不同的影響；regulation target 使用原有 48 分鐘正規化目標。時段誤差是每位球員每場、24 個區間上場分鐘絕對差之和，不是命中率。搭配誤差比較本場所有實際出賽球員配對，包括未同場的零值。','','| 指標 | v47 | v49 |','|---|---:|---:|']
for k in keys:lines.append(f'| {k} | {a[k]:.4f} | {b[k]:.4f} |')
lines+=['','| 球季 | 完整賽季實際分鐘 MAE v47→v49 | 正規時間目標 MAE | 時段誤差 | 同場時間 MAE |','|---|---|---|---|---|']
for s in p['seasons']:lines.append('| '+s+' | '+' | '.join(f"{rc(s,'v47')[k]:.4f} → {rc(s,'v49')[k]:.4f}" for k in keys[:4])+' |')
lines+=['','## Curry 與隊友：2025–26','','以下只計共同 PBP 場次的正規時間，不能直接與前一版包含加時的同場總數混用。','','| 球員 | Curry 狀態 | 實際分鐘 | v47 | v49 |','|---|---|---:|---:|---:|']
for pid in [1627780,202710]:
 x,y=[next(q for q in rc('2025-26',v)['curryTeammates'] if q['playerId']==pid) for v in ['v47','v49']]
 for arm in ['On','Off']:lines.append(f"| {x['name']} | {arm} | {x['actual'+arm]:.2f} | {x['predicted'+arm]:.2f} | {y['predicted'+arm]:.2f} |")
lines+=['','## 連續上場與種子差異','','三種子只衡量模擬亂數差異，不是實際資料信賴區間。完整各種子、時段／分鐘 P90 與連續上場分布見 [rotation-scores.json](rotation-scores.json)。','','| 球季 | 版本 | 上場段長中位數（秒） | P90（秒） | 超過 15 分鐘比例 |','|---|---|---:|---:|---:|']
for s in p['seasons']:
 for v in ['v47','v49']:
  d=rc(s,v)['stintDurationSeconds'];lines.append(f"| {s} | {v} | {d['median']:.1f} | {d['p90']:.1f} | {100*d['over900Share']:.2f}% |")
lines+=['','## 個人、球隊與防守回歸','','| 四季平均 MAE | v47 | v49 |','|---|---:|---:|']
for k in gameplay['v47']:lines.append(f"| {k} | {gameplay['v47'][k]:.4f} | {gameplay['v49'][k]:.4f} |")
lines+=['','投籃機率設定未改，但換人會改變出手人、對手與疲勞，所以統計仍可能變化。這些差異不能視為已提升 Curry 的三分或空間能力。個人全部位置與助攻、失誤、出手率等見 [scores.json](scores.json)，新鮮五區防守見 [fine-scores.json](fine-scores.json)，隊友兩分見 [candidate-offense-scores.json](candidate-offense-scores.json)。','','## 採用條件','','| 類別 | 條件 | 結果 |','|---|---|---|']
for label,gs in [('輪替',gates),('整體進攻',combinedGates)]:
 for k,v in gs.items():lines.append(f"| {label} | {k} | {'通過' if v else '未通過'} |")
lines+=['','所有原始觀測、來源、輸出雜湊與計分重建見 [results-verification.json](results-verification.json)。']
source=read(R/'source-stint-scores.json')
lines+=['','## 段落長度與未解偏差','','來源實際連續上場段只計正規比賽時間，模擬觀測另包含加時；若跨節始終沒換下，兩者都按連續比賽時鐘合併，因此不能把它解讀成沒有節間休息的實際體力負荷。','','| 球季 | 來源中位數秒 | v49 中位數秒 | 來源不足 60 秒比例 | v49 不足 60 秒比例 |','|---|---:|---:|---:|---:|']
for s in p['seasons']:
 real=next(c for c in source['cells'] if c['season']==s);sim=rc(s,'v49')['stintDurationSeconds'];lines.append(f"| {s} | {real['median']:.1f} | {sim['median']:.1f} | {100*real['under60Share']:.2f}% | {100*sim['under60Share']:.2f}% |")
lines+=['','新版本比舊版更接近來源的段落長度，但短段落仍偏多；Curry／Payton II 的共同時間也仍偏低。這次通過的是原訂整體分鐘、時段與同場誤差改善條件，不代表每場換人或每組搭配已完全正確。','','另有兩個較早三季的通用測試：在相同 60 場分散賽程上，比較搭配控制權重 0／0.25／1／4，未找到符合每季分鐘限制的更佳設定，保留 0.25，見 [tuning-selection.json](tuning-selection.json)。本候選亦檢查後衛／內線覆蓋，角色含位置與身高後備判斷；放寬該限制的測試在 2023–24 分鐘 MAE 惡化，故未合併，見 [role-selection.json](role-selection.json)。這是控制器假設而非球員能力加成，小球與多位置角色辨識仍有限制。','','整體進攻未升級的原因是個人得分／36 MAE 及外線防守 MAE 未達原本回歸門檻。後續應在已改善的 v49 輪替上重新檢查投籃人與出手分配，不能恢復錯誤輪替來維持舊的個人誤差。']
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps(decision))

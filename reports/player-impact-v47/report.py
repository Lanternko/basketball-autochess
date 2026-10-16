import json,hashlib
from pathlib import Path
import numpy as np
R=Path('reports/player-impact-v47');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));scores=read(R/'scores.json');fine=read(R/'fine-scores.json');oldfine=read('reports/player-impact-v46/fine-scores.json');fit=read(R/'ft-fit.json');fv=read(R/'fit-verification.json');p=read(R/'protocol.json');cells=scores['cells'];seasons=p['seasons'];variants=['v46','v47'];cell=lambda s,v:next(c for c in cells if c['season']==s and c['variant']==v)
mean=lambda v,f:float(np.mean([f(cell(s,v)) for s in seasons]))
ft={v:mean(v,lambda c:c['individualSummary']['ALL']['ftPct']['mae']) for v in variants};ppg={v:mean(v,lambda c:c['teamPPG']['mae']) for v in variants};defense={k:{v:mean(v,lambda c:c['defenseSummary']['ALL'][k]['mae']) for v in variants} for k in ['onshortFGpct','onlongFGpct','onshortShare','onlongShare','onFGA48']}
gates={'everySeasonFTmaeImproved':all(cell(s,'v47')['individualSummary']['ALL']['ftPct']['mae']<cell(s,'v46')['individualSummary']['ALL']['ftPct']['mae'] for s in seasons),'teamPPGmeanNonRegression':ppg['v47']<=ppg['v46'],'coarseDefenseMeanWithinPredeclared005pp':all(defense[k]['v47']<=defense[k]['v46']+.05 for k in ['onshortFGpct','onlongFGpct']),'fitVerified':fv['passed'],'runtimeVerified':read(R/'verification.json')['passed']}
adopted=all(gates.values());decision={'version':'v47','adopted':adopted,'adoptionScope':'Measured NBA offense FT-accuracy development baseline layered on frozen v46 defense; no product preset or OVR change.' if adopted else 'Candidate retained for diagnosis; v46 remains accepted development baseline.','gates':gates,'fourSeasonMean':{'individualFTmae_pp':ft,'teamPPGmae':ppg,'defenseMAE':defense},'gameDefaultChanged':False,'ovrRecomputed':False,'namedPlayerExceptions':False,'remainingWork':['Curry teammate two-point accuracy and overall spacing attribution remain unmodified.','Curry FTA and shot-volume residuals, AST and TOV remain separately tracked.','Measured gravity, pull-up/catch-and-shoot and rim-only teammate offense need independent source measurement.','v46 fine-zone defense limitations remain; game default and OVR have not been promoted.'],'scope':'Four already-seen seasons reconstructed using source appearances and minute targets; not future prediction. Source FT count prior chosen without2025-26; runtime adoption evaluated on all four reconstructed seasons.'}
(R/'decision.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# v47：量測罰球準度，接續 v46 防守基準','','狀態：'+('採用為後續量測模型的進攻開發基準。' if adopted else '未通過事先列出的採用條件，保留候選結果。')+'遊戲預設與 OVR 排名未切換。這是 Curry 進攻修正的第一步，尚未完成他的出手量或隊友空間修正。','','## 改了什麼、為什麼','','獨立重建確認：四季全部 2,581 個球員在隊條目，舊罰球機率都等於 `(FTM + 100 × 聯盟命中率) / (FTA + 100)`，再限制在 56%–90%。能力卡的 40–99 限制使高準度球員最多只到 90%，而固定 100 次先驗會再壓低高準度、較少出手的球員。這是通用轉換的誤差，沒有 Curry 姓名特例。','','新版本保留卡面 ft，以獨立的罰球機率進入投籃犯規、加罰、團隊犯規罰球與技術罰球；技術罰球手亦依同一機率挑選。若能力卡 ft 後續變化，仍透過舊曲線的 logit 差改變機率。普通投籃命中率、五區出手選擇、防守、犯規生成、籃板與進攻角色輸入不改。事件路徑可能因命中／落空和亂數分支改變，所以仍完整重跑。','','先驗由較早三季的整場五折交叉驗證選出：**'+str(fit['kappa'])+' 次罰球**。最小化等權三季的留出逐罰球 Bernoulli NLL；2025–26 不參與選擇。全季機率仍使用同季原始數據，這是重建測試。','','## 留出資料的罰球準度','','比較兩者都只用訓練場次的球員及聯盟計數；舊方案重現 100 次先驗與能力卡截斷，不使用完整球季能力來預測其留出場次。','','| 球季 | 舊方案 NLL/次 | 新方案 NLL/次 |','|---|---:|---:|']
for c in fv['crossfitComparison']:lines.append(f"| {c['season']} | {c['legacyNllPerAttempt']:.6f} | {c['newNllPerAttempt']:.6f} |")
lines+=['','## 完整模擬：個人與球隊','','個人 MAE 沿用至少 500 真實分鐘、罰球命中率另要求至少 50 次真實罰球的來源口徑，以真實分鐘加權；每球季三種子合併計數。球隊得分先平均三種子，再對 30 隊求 MAE。','','| 球季 | 個人 FT% MAE v46→v47（百分點） | 得分/36 MAE | 助攻/36 MAE | 球隊 PPG MAE |','|---|---|---|---|---|']
for s in seasons:
 a,b=cell(s,'v46'),cell(s,'v47');fmt=lambda f:f'{f(a):.4f} → {f(b):.4f}';lines.append('| '+s+' | '+' | '.join([fmt(lambda c:c['individualSummary']['ALL']['ftPct']['mae']),fmt(lambda c:c['individualSummary']['ALL']['pts36']['mae']),fmt(lambda c:c['individualSummary']['ALL']['ast36']['mae']),fmt(lambda c:c['teamPPG']['mae'])])+' |')
lines+=['',f"四季平均 FT% MAE：{ft['v46']:.4f} → {ft['v47']:.4f} 個百分點；球隊得分 MAE：{ppg['v46']:.4f} → {ppg['v47']:.4f} 分。",'','### 位置分組','','| 位置 | FT% MAE 四季平均 v46→v47 | 得分/36 MAE |','|---|---|---|']
for g in ['G','F','C']:
 vals=[]
 for k in ['ftPct','pts36']:vals.append(' → '.join(f"{mean(v,lambda c:c['individualSummary'][g][k]['mae']):.4f}" for v in variants))
 lines.append('| '+g+' | '+' | '.join(vals)+' |')
lines+=['','## Curry：沒有提高三分能力','','| 球季 | 指標 | 實際 | v46 | v47 |','|---|---|---:|---:|---:|']
for s in seasons:
 a,b=[next(p for p in cell(s,v)['individualPlayers'] if p['playerId']==201939) for v in variants]
 for k in ['pts36','fga36','fg3a36','threePct','fta36','ftPct','ast36','tov36']:
  x,y=a['metrics'][k],b['metrics'][k];lines.append(f"| {s} | {k} | {x['actual']:.3f} | {x['predicted']:.3f} | {y['predicted']:.3f} |")
oncourt=read(R/'offense-oncourt-scores.json')
lines+=['','### Curry 在場的隊友進攻','','strict PBP 場次，排除 Curry 自己；兩分合併禁區及中距離，不能解讀為純禁區或因果空間價值。','','| 球季 | 指標 | 實際 | v46 | v47 |','|---|---|---:|---:|---:|']
for c in oncourt['cells']:
 for k in ['teammatestwoPct','teammatesthreePct','teammatesthreeShare','deltaeFGpct']:
  m=c['curry']['metrics'][k];lines.append(f"| {c['season']} | {k} | {m['actual']:.3f} | {m['baseline']:.3f} | {m['predicted']:.3f} |")
lines+=['','這次沒有加入新的空間係數；上述變化來自罰球改變後的比賽路徑。全體相同樣本的在場誤差見 [offense-oncourt-scores.json](offense-oncourt-scores.json)。','','### 三種子的波動','','以下為 v47 完整球季的三種子最小至最大值，只描述模擬亂數差異，並非真實資料的信賴區間。','','| 球季 | Curry FT% 範圍 | Curry 得分/36 範圍 | 球隊得分 MAE 範圍 |','|---|---|---|---|']
for s in seasons:
 ds=cell(s,'v47')['seedDiagnostics'];vals=['–'.join(f'{f(d):.3f}' for d in [min(ds,key=f),max(ds,key=f)]) for f in [lambda d:d['curryFTpct'],lambda d:d['curryPTS36'],lambda d:d['teamPPGMAE']]];lines.append('| '+s+' | '+' | '.join(vals)+' |')
lines+=['','## 防守回歸追蹤','','下表為四季平均 MAE；命中率和出手占比為百分點，出手率為每 48 分鐘次數。0.05 個百分點的命中率平均波動容許值已在跑模擬前寫入 protocol，不是事後放寬。','','| 指標 | v46 | v47 |','|---|---:|---:|']
for k,vs in defense.items():lines.append(f"| {k} | {vs['v46']:.4f} | {vs['v47']:.4f} |")
lines+=['','### 細區防守','','新鮮出手口徑，對手在場命中率 MAE；v46 已明列的限制區／其他油漆區個人抵銷問題仍未修正。','','| 球季 | 區域 | v46 | v47 |','|---|---|---:|---:|']
for s in seasons:
 a=next(c for c in oldfine['cells'] if c['season']==s);b=next(c for c in fine['cells'] if c['season']==s)
 for z in ['ra','paint','mid','corner','arc']:lines.append(f"| {s} | {z} | {a['summary'][z+':on']['mae']:.4f} | {b['summary'][z+':on']['mae']:.4f} |")
lines+=['','## 採用條件與剩餘工作','','| 條件 | 結果 |','|---|---|']
for k,v in gates.items():lines.append(f"| {k} | {'通過' if v else '未通過'} |")
lines+=['','罰球與進攻誤差仍非全部歸零。隊友兩分、出手量與空間效應需下一階段獨立處理；不能將這次罰球改善算成已量測無球跑動或包夾。原始 on/off 是描述，不能直接當作因果貢獻。OVR 另行處理。','','完整分組與逐人結果見 [scores.json](scores.json)、[fine-scores.json](fine-scores.json)，採用判斷見 [decision.json](decision.json)，來源與輸出完整性見 [results-verification.json](results-verification.json)。']
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps({'adopted':adopted,'gates':gates,'FTmae':ft,'teamPPGmae':ppg,'defenseMAE':defense}))

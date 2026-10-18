import json
from pathlib import Path
root=Path('reports/player-impact-v22');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(root/'scores.json');protocol=read(root/'validation-protocol.json');bench=read(root/'ovr-checkpoint.json');prior=read(root/'putback-prior.json');lines=[];add=lines.append
add('# 2025–26 個人數據與 OVR：補籃命中率修正 v22\n')
add('**已完成四季各3組seed、2025–26全582人對照及31人OVR診斷抽樣。補籃改用單獨來源資料與情境校正；正式模型尚未更換，未發布修正完成的Top50。**\n')
add('[582人對照表](2025-26-player-validation.csv) 列個人得分、籃板、助攻、抄截、阻攻、失誤、投籃與三分、在場球隊／隊友命中率；同時保留整季總量、實際／模擬分鐘、出手分母，以及補籃的實際次數與模擬次數。小樣本也完整保留，零分母才留白。\n')
add('## 找到的缺口與修正\n')
add('一般出手早已做個人命中率與來源情境校正，補籃卻仍走舊公式，繼續承受體格、隊友與防守加成。逐球驗證顯示，目標季同一組1188場比賽中，v21補籃7933次、命中4937次（62.23%），實際同人搶到投籃未進的進攻籃板後0–3秒近距離出手8369次、命中4649次（55.55%）。這是逐球代理定義，不是官方play-type追蹤標籤。\n')
add(f"v22單獨估計補籃的記錄FGA命中率，採{prior['kappaAttempts']:.2f}次出手的共同Beta先驗，強度由2022–23至2024–25整場五折留出概似決定。來源補籃情境只按實際出手加權，使用當時五人陣容、既有防守干擾、模型輪替體力與同季來源曲線，不用進球結果或模擬殘差來調中心。2025–26未參與先驗強度擬合，但曾被歷史實驗看過，不能稱為全新盲測。\n")
add('補籃公式為：當下舊模型機率＋個人補籃後驗命中率−來源投籃曲線−來源補籃情境平均。這保留換隊友、對手或屬性的效果，並移除來源情境已包含的加成。一般出手的所有機率欄位與v21完全一致；失誤、犯規和罰球分支也保持不變。\n')
add('沒有改寫搶籃板的取得與歸屬公式，也沒有替後衛或指定名字加分。命中率改變後，未進球與後續籃板機會自然會改變，不能期待模擬籃板總數逐項相同。平均70隊友使用各自然位置的原始補籃出手池與相同先驗、情境校正，屬性算術平均仍為70。\n')
add('## 補籃分支直接驗證\n')
old=read(root/'putback-runtime-strict-audit.json');candidates=[read(root/f'runs/2025-26-rotation-space-strict-{seed}.json')['putbackAudit'] for seed in protocol['seeds']]
pb={k:sum(x[k] for x in candidates)/len(candidates) for k in ['fga','fgm','expectedMakes']};src=read(root/'2025-26-putback-events.json')['totals']
add('| 同一1188場範圍 | 補籃FGA | 實際取樣命中率 | 模型期望命中率 |\n|---|---:|---:|---:|')
add(f"| 官方逐球代理 | {src['fieldGoalAttempts']} | {100*src['fieldGoalMakes']/src['fieldGoalAttempts']:.2f}% | — |")
add(f"| v21單組seed，被動觀察 | {old['counts']['putback']['fga']} | {100*old['putbackFG']:.2f}% | {100*old['counts']['putback']['expectedMakes']/old['counts']['putback']['fga']:.2f}% |")
add(f"| v22三組seed平均 | {pb['fga']:.1f} | {100*pb['fgm']/pb['fga']:.2f}% | {100*pb['expectedMakes']/pb['fga']:.2f}% |")
add('\nv21被動觀察重跑的全部球隊計數及比賽比分與封存檔完全一致。600組機率測試確認一般出手一致、機率總和守恆、失誤／犯規不變，以及自然位置平均70；96場快取與未快取的所有結果一致。\n')
add('## 四季個人與在場數據\n')
add('| 分鐘加權MAE | v21 | v22 |\n|---|---:|---:|')
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('fgPct','FG 百分點'),('threePct','3P 百分點')]:add(f"| {label} | {scores['aggregate']['v21']['individualMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
add('\n四季等權，主摘要至少500實際分鐘；FG與3P至少100次對應實際出手。這是同季資料重現，平均誤差不代表每個人均精準。CSV包含所有人與所有非零出手率值。\n')
add('| 在場MAE，百分點 | v21 | v22 |\n|---|---:|---:|')
for k,label in [('onTeamFG','在場球隊FG'),('onTeammateFG','排除本人的隊友FG'),('onTeam3P','在場球隊3P'),('onTeammate3P','排除本人的隊友3P'),('teamFGOnOff','球隊FG ON–OFF'),('team3POnOff','球隊3P ON–OFF')]:add(f"| {label} | {scores['aggregate']['v21']['onCourtMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add('\n原始ON–OFF仍受隊友、對手及輪替影響，不當作個人因果能力。\n')
add('## 球隊採用界線\n')
add('| 球季 | 正式控制勝場MAE | v21 | v22 | v22不超過控制+0.5場 |\n|---|---:|---:|---:|---|');failed=[]
for s in protocol['seasons']:
 cells={c['version']:c for c in scores['cells'] if c['season']==s};control=cells['control']['teamMetrics']['winsMAE'];a=cells['v21']['teamMetrics']['winsMAE'];b=cells['rotation-space']['teamMetrics']['winsMAE'];passed=b<=control+.5
 if not passed:failed.append(s)
 add(f'| {s} | {control:.3f} | {a:.3f} | {b:.3f} | {"通過" if passed else "未通過"} |')
add('\n補籃命中率接近來源並不足以通過整個系統的採用條件；正式模型維持原版。\n')
add('## 自然位置OVR診斷樣本\n')
add('| 球員 | v21基準隊勝率 | v22 | v22同位置平均隊 |\n|---|---:|---:|---:|');oldbm={r['result']['playerId']:r for r in read('reports/player-impact-v21/ovr-checkpoint.json')['rows']};bm={r['result']['playerId']:r for r in bench['rows']}
for pid in [1628983,1629029,203999,201939,1629674]:
 r=bm[pid];base=next(p for p in bench['rows'] if p['job']['kind']=='baseline' and p['result']['position']==r['result']['position']);add(f"| {r['result']['name']} | {100*oldbm[pid]['result']['winRate']:.2f}% | {100*r['result']['winRate']:.2f}% | {100*base['result']['winRate']:.2f}% |")
add('\n31名樣本＋5個位置基線，每人只放自然位置、搭配其餘四種平均70隊友，固定30隊雙邊各40組、2400場／人。這是既定樣本，不是全582人排名，不能宣稱Top50的後衛數或指定球員名次。\n')
add('## 未解決事項\n')
add('補籃出手次數仍有個人偏差：新命中率沒有修正「搶到板後選擇自己補」的舊體格公式。已另建立[v23補籃選擇來源](../player-impact-v23/2025-26-putback-choices.json)，但FGA／進攻籃板只是記錄出手發生率；接著可能失誤、犯規或時間結束，不能直接當分支選擇機率。v23已另以來源存活機率推估個人選擇傾向，並列出時鐘／末節政策無法重現的少數出手；目前只接入目標季單組seed試驗，尚未完成四季驗證。\n')
add('新補籃目標排除罰球籃板後出手，因引擎該路徑不選補籃；舊一般出手分割仍排除了每季69至135筆這類快攻代理，這個小幅口徑不一致尚未修復。四項offBall／screen／handle／breakDbl仍為70，跑動、掩護與傳球追蹤只完成來源審查，沒有冒充技巧加分。技術罰球機制、部分球員防守籃板／助攻、球隊防守及在場效果、低分鐘外推與全員Top50仍未完成。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
status={'version':'measured-putback-success-22','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'targetPlayers':582,'teamWinGatesFailed':failed,'ovrSamplePlayers':31,'ovrFullRanking':False,'sourcePutbackContextConservationPassed':True,'cacheExactParityGames':96,'next':'Source putback selection incidence requires opportunity-survival and finite-horizon correction; reconcile FT-rebound fresh partition. Team and individual gates remain incomplete.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2))

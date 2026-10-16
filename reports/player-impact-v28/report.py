import json,csv
from pathlib import Path
root=Path('reports/player-impact-v28');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(root/'scores.json');ledger=read(root/'ledger-verification.json');sv=read(root/'source-verification.json');protocol=read(root/'validation-protocol.json')
with (root/'2025-26-player-validation.csv').open(encoding='utf-8-sig') as f:
 r=csv.DictReader(f);players=list(r);columns=len(r.fieldnames)
assert len(players)==582 and ledger['games']==28023
lines=[];add=lines.append
add('# v28：保留護框來源機率，檢查進攻籃板\n')
add('**四季各3組seed、28,023場完整／嚴格範圍比較完成；本篇未採用，不是新版OVR，整體任務仍未完成。**\n')
add(f'[582人逐項對照](2025-26-player-validation.csv)保留{columns}欄，包含個人計數與總量、分鐘、FG／3P／FT、在場球隊／排除本人隊友／對手FG與3P及ON–OFF、分母與來源護框差異。一般全季與嚴格PBP範圍分別標示，模擬總量、分鐘與分母為三組seed平均。\n')
add('## 進攻籃板不是這次該先砍的項目\n')
add('固定真實攻守五人及每次有個人取得的FG籃板，逐次計算現行隊伍進攻籃板取得機率與個人歸屬。四季365,784個FG籃板中有93,950次個人OREB；FT籃板、團隊籃板分開保留。2025–26另有8次指向heave事件的籃板，保留異常清單，不冒充2pt／3pt出手。每次籃板均唯一映射stint，全部個人OREB與獨立嚴格PBP帳目一致。\n')
add('| 球季 | 個人FG籃板機會 | 實際個人OREB | 現行條件期望 | 個人FG-OREB／36 MAE |\n|---|---:|---:|---:|---:|')
for season in protocol['seasons']:
 a=read(root/f'{season}-oreb-risksets.json');add(f"| {season} | {a['counts']['individualFgRebounds']:,} | {a['counts']['individualFgOreb']:,} | {a['expectedTeamOreb']['fresh']:.2f} | {a['maeFgOreb36']['fresh']:.3f} |")
add('\n這是同季來源重建，條件於真實未進球與已解析的個人籃板，不能證明不同隊友／角色下的可攜能力或盲測準確度。\n')
add('| 2025–26 FG個人OREB | 實際 | 現行條件期望 |\n|---|---:|---:|')
a=read(root/'2025-26-oreb-risksets.json')
for pid in [1629011,1641705,1630595,203999,1629674]:
 p=next(p for p in a['players'] if p['playerId']==pid);add(f"| {p['name']} | {p['fgOreb']} | {p['expectedFresh']:.2f} |")
add('\nRobinson沒有被現行來源公式灌高。沒有因榜單看起來中鋒太多就直接砍籃板或個人份額。另確認applyStamina只降低long／mid／short／drive，籃板與防守輸入不受影響；來源平均疲勞與不疲勞的本條件籃板機率完全一致。「OVR關閉疲勞造成籃板被放大」目前沒有被這個機制支持；短場固定角色的其他外推限制仍存在。\n')
add('## 修正：防守機率經屬性封頂後遺失來源差異\n')
add('既有來源防守差異已按n／(n＋200)收縮，但先轉成40–99屬性再轉回機率，讓12個球員季／區域在99封頂後失真。v28保留原200次出手收縮與240分鐘干擾暴露先驗，直接補回來源機率與原屬性曲線間遺失的差異；沒有新增權重、姓名、ON–OFF或模擬殘差。以原始屬性作錨，後續調整屬性仍會改變機率；缺失追蹤與合成平均70卡沿用原曲線。\n')
add('| 2025–26近框來源 | 已收縮差異 | 原99封頂後差異 | 補回差異 |\n|---|---:|---:|---:|')
audit=read(root/'defense-curve-audit.json')
for s in audit['seasons']:
 if s['season']!='2025-26':continue
 for p in s['rows']:
  if abs(p['difference'])>1e-8:add(f"| {p['name']} | {100*p['sourcePosterior']:.3f}百分點 | {100*p['throughCurve']:.3f}百分點 | {100*p['difference']:.3f}百分點 |")
add('\n這些是最近防守者追蹤的命中率差，仍有對位選擇與樣本混雜，不是完整因果護框能力。換算全隊短區域時仍乘個人干擾頻率、除全隊該區域出手量；不能把每球都算他在防，也不另替阻攻扣第二次命中率。四季270,090個攻守陣容狀態的投籃來源情境同步重建，避免只改防守、沿用舊進攻校正。所有原始屬性與其他失誤／傳球／籃板／犯規機制保持原值，保留v27的budget換人同步修正。\n')
add('## 四季完整結果：改善與退步並列\n')
add('每季至少500實際分鐘、按來源分鐘加權，再四季等權；FG／3P至少100實際出手、FT至少50。所有球員另完整輸出。同季重建與原始ON–OFF不是因果球員價值。\n')
add('| 平均絕對誤差 | v26 | v28 |\n|---|---:|---:|')
for k,label in [('pts36','得分／36'),('ast36','助攻／36'),('tov36','失誤／36'),('stl36','抄截／36'),('blk36','阻攻／36'),('oreb36','進攻籃板／36'),('dreb36','防守籃板／36'),('fga36','出手／36'),('fta36','罰球／36'),('fgPct','FG百分點'),('threePct','3P百分點')]:
 add(f"| {label} | {scores['aggregate']['v26']['individualMAE'][k]:.4f} | {scores['aggregate']['rotation-space']['individualMAE'][k]:.4f} |")
for k,label in [('onTeamFG','在場球隊FG百分點'),('onTeam3P','在場球隊3P百分點'),('onTeammateFG','排除本人隊友FG百分點'),('onTeammate3P','排除本人隊友3P百分點'),('onOpponentFG','在場對手FG百分點'),('onOpponent3P','在場對手3P百分點'),('teamFGOnOff','球隊FG ON–OFF百分點')]:
 add(f"| {label} | {scores['aggregate']['v26']['onCourtMAE'][k]:.4f} | {scores['aggregate']['rotation-space']['onCourtMAE'][k]:.4f} |")
add('\n| 球季勝場MAE | 正式控制 | v26 | v28 | 控制＋0.5場界線 |\n|---|---:|---:|---:|---|');failed=[]
for season in protocol['seasons']:
 c={c['version']:c for c in scores['cells'] if c['season']==season};a=c['control']['teamMetrics']['winsMAE'];b=c['rotation-space']['teamMetrics']['winsMAE'];passed=b<=a+.5
 if not passed:failed.append(season)
 add(f"| {season} | {a:.3f} | {c['v26']['teamMetrics']['winsMAE']:.3f} | {b:.3f} | {'通過' if passed else '未通過'} |")
add('\n## 指定球員仍有哪些誤差\n')
c=next(c for c in scores['cells'] if c['season']=='2025-26' and c['version']=='rotation-space');by={p['playerId']:p for p in c['players']};onc={p['playerId']:p for p in c['onCourtPlayers']}
add('| 2025–26實際／v28 | 得分／36 | 助攻／36 | OREB／36 | 阻攻／36 | 在場對手FG |\n|---|---:|---:|---:|---:|---:|')
for pid in [1641705,1629011,1630595,1628983,1629029,203999]:
 p=by[pid];values=[]
 for k in ['pts36','ast36','oreb36','blk36']:m=p['metrics'][k];values.append(f"{m['actual']:.2f}／{m['predicted']:.2f}")
 m=onc[pid]['metrics']['onOpponentFG'];values.append(f"{m['actual']:.2f}／{m['predicted']:.2f}");add('| '+p['name']+' | '+' | '.join(values)+' |')
add('\n補回來源機率並不等於補足所有護框、抄截、阻攻與輪替情境。傳球供給、傳球失誤、隊友出手品質仍需拆開驗證；不能用助攻數接近就判定組織價值正確，也不能保證這個小範圍修正讓Wemby超過Robinson。\n')
add('最新完整全員OVR仍是[v24](../player-impact-v24/all-2025-26/report.md)，17名PG／SG在前50，SGA1、Luka3、Jokić7；本輪沒有重算完整榜，不冒稱v28排名。未知offBall／screen／handle／breakDbl仍70，正式模型未改。來源核對見[source-verification.json](source-verification.json)，執行與帳目見[ledger-verification.json](ledger-verification.json)。第一個情境重算程序因偵測到來源雜湊路徑錯誤而停止，未寫出情境檔；v2只修正來源路徑後完成，記錄見context-v1-stopped.json。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
(root/'status.json').write_text(json.dumps({'version':'source-defense-probability-roundtrip-28','officialModelAdopted':False,'goalComplete':False,'sourceFgRebounds':365784,'sourceFgOreb':93950,'restoredPlayerZoneCards':12,'sourceContextStates':270090,'fullValidationSeasons':4,'seeds':3,'games':ledger['games'],'failedWinGateSeasons':failed,'targetPlayers':582,'targetPlayerColumns':columns,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'next':'Separate pass supply, pass losses and created shot quality; validate remaining defensive/shot-volume/FT gaps without rank/name residual tuning.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Report/status written; failed win gates',failed)

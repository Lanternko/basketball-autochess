import json
from pathlib import Path
root=Path('reports/player-impact-v27');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
seasons=['2022-23','2023-24','2024-25','2025-26'];audits={s:read(root/f'{s}-source-fga-audit.json') for s in seasons};scores=read(root/'rotation-replay-v2-scores-3-seeds.json')
lines=[];add=lines.append
add('# v27：出手機會與同場輪替，及換人後角色表同步修正\n')
add('**已完成四季真實陣容的出手分配檢查，以及2025–26三種輪替×三組seed，共10,692場歷史暴露診斷。這不是一般全季勝場驗證，尚未採用，整體任務仍未完成。**\n')
add('[582人×三種輪替逐項對照](rotation-replay-v2-all-players-3-seeds.csv)保留1746列、135欄，包含得分、助攻、失誤、抄截、阻攻、進攻／防守／總籃板、出手／罰球、FG／3P、在場球隊／排除本人隊友／對手命中率與ON–OFF。原始計數、分鐘、分母及逐指標樣本標記均保留；模擬總量與分鐘列每組seed平均。\n')
add('## 找到並修正的程式問題\n')
add('budget測試模式會按時鐘中途換人，但原先的進攻角色分配表在觸球開始時計算後保持不變。換人後投籃機率使用新球員，角色表卻可能仍是舊五人的終結／傳球／接球權重。v27的engine.mjs改成在每次budget refresh後，以當前五人與對手壓迫重新建立角色表；保持原有位置交接慣例，沒有替指定球員加權。\n')
add('test/rotation_plan_refresh.js涵蓋人工來源輪替與一般budget輪替，共1129次非補籃refresh、12種五人組合，逐次檢查當前每人的終結流量與當前五人輸入守恆，個人分鐘精確。96場正常固定陣容與v26完全相同；兩場含延長賽的三種輪替探針，通用修正引擎與已同步的replay-v2完全相同。正式模型及舊版凍結來源均未修改。\n')
add('第一批rotation-replay（不含v2）的單組結果包含此同步缺陷，已列入superseded.json，不用來支持結論；兩個未完成的舊seed工作已停止。原始檔保留供追溯。以下僅使用修正後v2的完整三組結果。\n')
add('## 先固定真實五人，檢查舊出手分配\n')
add('終結需求仍含舊的FGA＋0.44×全部FTA＋非傳球抄截TOV近似。不能因公式舊就假定它是所有缺口的原因；先條件於真實攻守五人與當段實際新進攻FGA數，計算現行角色流量與存活後的記錄FGA份額。存活包含非傳球TOV、投籃犯規造成未記FGA的出手、現行自己／接球出手EV選擇；區域抽樣的犯規分母以實際引擎的調和形式處理。\n')
add('排除引擎補籃範圍的FG籃板後同人3秒近框出手，FT籃板後快投保留在一般出手。另排除節末≤1.5秒及第四節／延長賽最後27秒；真實24秒進攻時間與段內出手時點未觀測，疲勞用來源段平均。此檢查固定了隊伍已發生的FGA機會，不能驗證隊伍總產量或因果能力。\n')
add('| 球季 | 合格FGA | 攻守陣容段 | 未計存活的FGA/36 MAE | 計存活後 |\n|---|---:|---:|---:|---:|')
for s,a in audits.items():add(f"| {s} | {a['totals']['eligibleFresh']:,} | {a['totals']['states']:,} | {a['maeFreshFga36']['raw']:.3f} | {a['maeFreshFga36']['survival']:.3f} |")
add('\n| 2025–26球員 | 合格實際FGA | 現行公式存活後期望 |\n|---|---:|---:|')
for pid in [201939,1628983,1629029,203999,1629674]:
 p=next(p for p in audits['2025-26']['players'] if p['playerId']==pid);add(f"| {p['name']} | {p['actual']} | {p['expectedSurvival']:.2f} |")
add('\nCurry合格實際755次、期望749.81次，表示他整季模擬少出手不能只歸咎於這個分配公式；Jokić與SGA仍有來源分配偏高。沒有把這些個人差值直接寫回角色或屬性。\n')
add('## 三種輪替的同範圍比較\n')
add('三者都固定真實比賽的節數與可出賽名單，foulOut=99，使用相同三組seed及v26機率機制。heuristic沿用輪替；synthetic令每人的分鐘完全相同但重新組合五人；observed固定真實五人時間段。兩個精確分鐘組會在比賽時鐘邊界換人並交接原位置，會同時改變隊友、對手與疲勞歷史；不是比賽時序的逐球重播。真實節數已提供歷史資訊，平手亦保留，因此不計算或採用勝場界線。\n')
add('摘要至少500來源分鐘、按來源分鐘加權；FG／3P及在場指標另至少100次來源出手。未刪除低分鐘球員。\n')
add('| 平均絕對誤差 | 原輪替 | 同分鐘重組 | 真實輪替 |\n|---|---:|---:|---:|')
metrics=[('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('fga36','出手/36'),('fta36','罰球出手/36'),('fgPct','FG百分點'),('threePct','3P百分點'),('onTeamFG','在場球隊FG百分點'),('onTeam3P','在場球隊3P百分點'),('onTeammateFG','排除本人隊友FG百分點'),('onTeammate3P','排除本人隊友3P百分點'),('onOpponentFG','在場對手FG百分點'),('teamFGOnOff','球隊FG ON–OFF百分點'),('team3POnOff','球隊3P ON–OFF百分點')]
for k,label in metrics:add('| '+label+' | '+' | '.join(f"{scores['versions'][v]['summary'][k]['minuteWeightedMAE']:.3f}" for v in ['heuristic','synthetic','observed'])+' |')
add('\n真實輪替改善在場命中率、ON–OFF與部分籃板／防守計數，但得分、助攻、失誤與出手量仍有退步。只滿足個人分鐘、任意拼五人，會比原輪替更差，不能把分鐘守恆當作同場情境已準確。\n')
add('| 球員FGA/36 | 來源實際 | 原輪替 | 同分鐘重組 | 真實輪替 |\n|---|---:|---:|---:|---:|')
for pid in [201939,1628983,1629029,203999,1629674]:
 ps=[next(p for p in scores['versions'][v]['players'] if p['playerId']==pid) for v in ['heuristic','synthetic','observed']];add(f"| {ps[0]['name']} | {ps[0]['metrics']['fga36']['actual']:.3f} | "+' | '.join(f"{p['metrics']['fga36']['predicted']:.3f}" for p in ps)+' |')
add('\nCurry出手機會部分補回，但仍不足；真實輪替下SGA在場對手FG仍約46.50%，來源42.70%，Queta約46.49%，來源42.47%。這些防守缺口與Jokić出手量偏高仍在，沒有用輪替或得分結果掩蓋。\n')
add('## 來源及尚未完成部分\n')
add('新建相同1188場的個人PBP基準，582人的FG／3P帳目與獨立在場真值逐人完全一致，DREB與v24真實五人籃板來源逐人完全一致。PBP與所選比賽官方box的PTS有兩筆各1分差異：Cam Thomas 467對468、Michael Porter Jr.1121對1120。兩套值均保留，不把它們暗中改成一致。來源分鐘採嚴格stints；與整季官方分鐘的摘要不能混用。\n')
add('這輪沒有把速度、無球、掩護、控球或破包夾產量轉成技巧分數，四項未知值仍70，也沒有完成新版OVR。最新完整全員排名仍是[v24](../player-impact-v24/all-2025-26/report.md)：17名PG／SG進前50，SGA1、Luka3、Jokić7；它仍是未採用的點估計，不能冒稱v27榜。最新一般四季全季比較仍是[v26](../player-impact-v26/report.md)，兩季勝場界線未過。下一步需修正可驗證的來源終結分配／罰球與防守機制，並保留這些輪替差異作驗證；不按名字或排名補分。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
status={'version':'rotation-role-plan-refresh-27','officialModelAdopted':False,'goalComplete':False,'sourceAllocationAuditSeasons':4,'sourceAllocationEligibleFga':sum(a['totals']['eligibleFresh'] for a in audits.values()),'sourceAllocationStates':sum(a['totals']['states'] for a in audits.values()),'rotationReplaySeason':'2025-26','rotationReplayVersions':3,'rotationReplaySeeds':3,'rotationReplayGames':10692,'targetPlayers':582,'playerDiagnosticRows':1746,'playerDiagnosticColumns':135,'liveBudgetPlanRefreshFixed':True,'ordinaryHeuristicV26ParityGames':96,'ordinarySeasonWinGatesTestedThisVersion':False,'ovrLastCompleteVersion':24,'ovrFullRankingThisVersion':False,'next':'Resolve remaining source terminal share and shooting/FT/defense gaps; retain actual/source and synthetic rotation contrast. No name/rank residual tuning.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2))
(root/'superseded.json').write_text(json.dumps({'files':['rotation-replay-2025-26-20261012.json','rotation-replay-scores.json','rotation-replay-all-players.csv'],'reason':'Initial budget/source replay kept pre-substitution creationPlan after a live-clock change of five. Data retained for traceability; no conclusions use these files. V2 replay and general v27 engine recompute the current-five role plan at each budget refresh.','cancelledSeeds':[20261013,20261014],'cancelledLegacySessions':[45734,65381],'replacement':'rotation-replay-v2-scores-3-seeds.json'},indent=2),encoding='utf-8')

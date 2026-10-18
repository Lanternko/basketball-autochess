"""Render frozen v30 results, including failed adoption gates and unresolved OVR bias."""
import json
from pathlib import Path
ROOT=Path('reports/player-impact-v30')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(ROOT/'scores.json');old=s['aggregate']['v28'];new=s['aggregate']['rotation-space']
probe=read(ROOT/'ovr-probe-summary.json');passing=read(ROOT/'passing-summary.json')
deps=next(x for x in read(ROOT/'dependence-audit.json')['seasons'] if x['season']=='2025-26')
tracking=read(ROOT/'shot-tracking-audit.json')
reliability={p['playerId']:p['reliabilitySensitivity'][-1]['persistentRate'] for p in read('reports/player-impact-v29/reliability-policy.json')['players']}
lines=['# 接球得分依賴與個人數據：v30試驗', '',
'**完成四季28,023場驗證、2025–26全582人170欄對照與10人9,600場負荷配對測試。三季未通過球隊勝場門檻，未採用，沒有新版全員OVR。**', '',
'個人得分、FG與3P誤差縮小，但失誤、部分防守／在場影響與勝場誤差退步。Robinson仍高於Cade、Curry仍出現負貢獻估計；不能宣稱肉C偏高或後衛價值已經修完。', '',
'## 本輪實際改動', '',
'原來以突破與傳球屬性推估「自己完成得分時有多依賴隊友創造空檔」，突破屬性又主要取自罰球率。這會把不同得分角色混為一談：Robinson的舊突破屬性為97.48，卻不能因此推論他能像持球後衛一樣自主創造。', '',
'本輪僅把該依賴項的來源錨點改為既有的接球終結機會／總終結機會。來源角色不是因果技能，也不是單純受助攻率；Jokić自己接到球得分的比例高，不表示他不會組織隊友。原來屬性反事實變化的斜率與既有疲勞作用仍保留，沒有據名次調整係數。', '',
'只在v30隔離模型接入；原始正式模型沒有更換。四季2262個球員季、2581個隊伍名單卡保留原屬性與角色量；270,090個來源陣容情境重算投籃校準，來源分鐘、出手與能量不變。缺少新測量時精確回到舊公式，96場的所有球隊與球員計數和v28相同。', '',
'| 球員 | 舊依賴代理值 | 新來源角色依賴 |', '|---|---:|---:|']
ids=[1629011,1641705,1630595,1628983,1629029,203999,201939]
db={p['playerId']:p for p in deps['rows']}
for pid in ids:
 p=db[pid];lines.append(f"| {p['name']} | {p['oldDependence']:.3f} | {p['sourceDependence']:.3f} |")
lines+=['', '## 四季完整比較', '',
'2022–23至2025–26，各3個相同seed，全年1230場和嚴格PBP配對場次分別模擬，共28,023場。這是使用同季來源的重現驗證，不是盲測未來，也不是因果ON–OFF。主誤差樣本為至少500真實分鐘，季內以真實分鐘加權，再對四季等權平均。FG與3P至少100次真實出手、FT至少50次；在場／不在場比率分母至少100次。全員均保留，沒有刪掉低分鐘球員來美化結果。', '',
'以下計數為每36分鐘MAE，命中率為百分點MAE。總量與分鐘差另外保留在CSV，不能用per36掩蓋輪替量錯誤。', '',
'| 指標 | v28 | v30 | 方向 |', '|---|---:|---:|---|']
names={'pts36':'得分／36','ast36':'助攻／36','tov36':'失誤／36','stl36':'抄截／36','blk36':'阻攻／36','oreb36':'進攻籃板／36','dreb36':'防守籃板／36','fga36':'出手／36','fg3a36':'三分出手／36','fta36':'罰球出手／36','fgPct':'FG命中率','threePct':'三分命中率','ftPct':'罰球命中率','tovPer100Uses':'每100次終結使用的失誤'}
for k,name in names.items():
 a,b=old['individualMAE'][k],new['individualMAE'][k]
 lines.append(f"| {name} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['', '| 在場相關誤差 | v28 | v30 | 方向 |','|---|---:|---:|---|']
names={'onTeamFG':'在場球隊FG','onTeam3P':'在場球隊3P','onTeammateFG':'在場其他四人FG','onTeammate3P':'在場其他四人3P','offTeamFG':'不在場球隊FG','offTeam3P':'不在場球隊3P','onOpponentFG':'在場對手FG','onOpponent3P':'在場對手3P','teamFGOnOff':'球隊FG的ON–OFF','team3POnOff':'球隊3P的ON–OFF'}
for k,name in names.items():
 a,b=old['onCourtMAE'][k],new['onCourtMAE'][k]
 lines.append(f"| {name} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['', f"四季勝場MAE {old['team']['winsMAE']:.4f}→{new['team']['winsMAE']:.4f}，淨分RMSE {old['team']['netRMSE']:.4f}→{new['team']['netRMSE']:.4f}，都退步。每季採用門檻維持正式對照勝場MAE加0.5，不因本輪結果放寬。", '', '| 球季 | 正式對照 | v28 | v30 | v30門檻 |','|---|---:|---:|---:|---|']
failed=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 c={x['version']:x for x in s['cells'] if x['season']==season}
 v={k:c[k]['teamMetrics']['winsMAE'] for k in c};bad=v['rotation-space']>v['control']+.5
 if bad:failed.append(season)
 lines.append(f"| {season} | {v['control']:.4f} | {v['v28']:.4f} | {v['rotation-space']:.4f} | {'未過' if bad else '通過'} |")
lines+=['', '## 健康負荷與反覆傷缺政策保留', '',
'使用者已確認：主要看能上場時的貢獻；孤立一季傷缺不扣，多季明確傷病才小扣；短時間替補不能直接將per36外推成先發能力。依v29，標準負荷由前三季推得34.98分鐘；出賽每場封頂後再平均，缺賽不補零、超額分鐘不再加分。健康時只打來源支持分鐘，其餘由同位置平均70卡補上。', '',
'固定自然位置，其餘四位置為不同形狀、各自屬性算術平均70的球員。有48分鐘、四節、輪替及既有疲勞；球員隊與比較隊的分鐘／換人／對手／seed完全配對。原疲勞只作用於投籃與突破，並未測出長時間籃板、傳球、防守如何改變。', '',
'10名診斷球員，每人30對手×4組seed×兩席次×兩種負荷×球員／基準隊，共9,600場新模擬。v28比較直接取v29凍結結果中相同場景，不重抽有利樣本。新角色依賴也用於平均隊友，因此版本差包含隊友環境的連帶作用。', '',
'下表是來源支持健康負荷下的相對平均隊分差，不是NBA實際淨效率或0–99 OVR。區間僅反映固定模型與輸入下，30對手分層、4組seed、兩席次配對的模擬抽樣；未含來源、參數、負荷或模型不確定性。', '',
'| 球員 | 分鐘 | v28健康貢獻 | v30健康貢獻 | 成對變化［95%］ | v30加可靠度原型後 |','|---|---:|---:|---:|---:|---:|']
for p in probe['players']:
 a=next(a for a in p['arms'] if a['arm']=='supportedHealthy');d=a['pairedChange'];h=a['v30']['mean'];adjusted=h-max(h,0)*.10*reliability[p['playerId']]
 lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v28']['mean']:+.3f} | {h:+.3f} | {d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] | {adjusted:+.3f} |")
lines+=['', '可靠度仍為v29的明列原型：`健康貢獻 − max(健康貢獻,0) × 0.10 × 第二高的合格球季明確傷缺比率`。單一傷缺季恰不扣；負值不因受傷加分；不以缺賽縮短每場分鐘製造休息紅利。0.10是尚未校準的政策權重，不能當成醫療預測。表格只是把既定政策套用到本輪平均估計，沒有推算新精確名次。', '',
'Robinson的健康負荷估計仍高於Cade；Curry與Pritchard仍為負，且健康負荷的所有版本差區間都跨零。假設Robinson能打滿34.98分鐘的反事實甚至由+3.983升至+8.375；這是來源依賴改動會連帶重分隊友空檔、基準隊與校準的結果，不能說提高依賴就一定壓低中鋒價值。這些反例必須保留，不能透過按名字加分或籃板降權消掉。', '',
'## 傳球效果：另做保留配對驗證，沒有塞進模型', '',
'用官方傳球配對的二分／三分M與A，擬合「截距＋接球者效果」和「再加傳球者效果」的收縮二項logit。整個球隊／傳球者／接球者配對一起留出，5折；超參數只由2022–25選擇，2025–26只測已選規格。這是同季留配對測試，不是時間外預測；接球後自己創造、二分距離、空檔、對手與打法仍混在其中。Passed-shot FGA範圍比potential assist更廣，不能把其命中數當助攻，也不能把傳球者係數當技能。', '',
'| 2025–26留出配對 | 出手 | 只含接球者NLL | 加傳球者NLL | NLL改善 |','|---|---:|---:|---:|---:|']
for z in passing['zones']:lines.append(f"| {z['zone']}分 | {z['attempts']:.0f} | {z['receiverOnlyNll']:.3f} | {z['jointNll']:.3f} | {z['heldoutNllGain']:.3f} |")
lines+=['', f"合併改善僅{passing['combinedNllGain']:.3f}，條件配對bootstrap 95%為[{passing['conditionalPairBootstrap95'][0]:.3f}, {passing['conditionalPairBootstrap95'][1]:.3f}]。這只對固定已擬合預測做配對重抽，沒有重擬合，也未包含球隊、球季與參數不確定性。改善很小，不支持直接加一個巨大後衛／傳球紅利；本輪沒有接入額外傳球加成。", '',
'## 新取得的追蹤來源與下一個缺口', '',
'四季突破、接球投、運球急停投共12份官方來源完整保存。活動次數不是能力，條件命中率也不是純無球或控球；突破出手和另外兩類不能相加，分類不互斥。舊季有明顯GP／分鐘範圍差異，部分三分子欄為null，突破得分亦不一定由所列FG／FT精確分解；全部保留來源並標記，沒有硬補成零或強迫等式。', '',
'| 球季 | 球員 | 範圍差異 | 突破得分分解差異 | 三分子欄null |','|---|---:|---:|---:|---:|']
for ss in tracking['seasons']:
 issues=ss['scopeIssues'];lines.append(f"| {ss['season']} | {len(ss['players'])} | {sum('gpDifference' in q for q in issues)} | {sum('trackingPointsResidual' in q for q in issues)} | {sum('nullThreeSubtype' in q for q in issues)} |")
lines+=['', '這些是問題項目數，可重複涉及同一球員；不是全部資料失效。2025–26的突破活動來源中，Robinson只有7次，SGA1752次、Cade1418次、Luka1210次；舊罰球率代理不能直接視為突破能力。新資料目前僅作來源稽核，尚未修改drive／handle／offBall的技能值，也未作額外的OVR加分。', '',
'接下來應先拆開突破活動、持球投籃、運球保護與傳球創造的來源和機制，檢查現有空檔在接球／自主出手的使用及重複計入，再做跨季與來源對手角色驗證。不能只靠再加一個後衛加成解釋失敗。offBall、screen、handle、breakDbl等未量測技能仍有70預設，沒有冒稱已由新追蹤資料辨識完成。', '',
'## 核對與版本狀態', '',
'原始比分、球員／球隊計數、失誤／抄截、助攻與投籃、在場5份／本人1份／隊友4份帳目通過。來源、凍結協定與執行檔雜湊核對，所有個人／在場MAE與CSV逐項重算；配對試驗的均值、標準誤與區間、傳球留出損失與bootstrap、12份追蹤來源逐列亦獨立重算。這些核對證明數字一致，不能證明模型正確。', '',
'正式模型仍為pure-oreb-turnover-time-1；v30未採用。最新完整全員OVR仍是v24，不含本輪健康負荷與可靠度政策，因此不能把舊榜貼成新版。原始個人精準度與OVR修正目標仍未完成。', '',
'檔案：[582人170欄完整對照](2025-26-player-validation.csv)、[四季分數](scores.json)、[10人配對](ovr-probe-summary.json)、[傳球配對](passing-summary.json)、[追蹤來源](shot-tracking-audit.json)、[完整核對](verification.json)、[補充核對](supplement-verification.json)。']
(ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
status=dict(officialModelAdopted=False,goalComplete=False,fullOvrThisVersion=False,latestCompleteOvrVersion=24,
    failedWinGateSeasons=failed,targetPlayerColumns=170,fullValidationSeasons=4,seeds=3,games=28023,
    probePlayers=10,probeGames=9600,sourceRoleCards=2262,sourceContextStates=270090,
    passingFitApplied=False,newTrackingFiles=12,newTrackingApplied=False,
    unresolved=['Source opponent and role selection','Curry/Pritchard contribution estimates','Robinson versus Cade bias','Unmeasured off-ball/screen/handle/double-team skills','Three failed win gates'])
(ROOT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(status,ensure_ascii=False,indent=2))

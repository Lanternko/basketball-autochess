import json
from pathlib import Path

root=Path('reports/player-impact-v25')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(root/'scores.json');protocol=read(root/'validation-protocol.json')
prior=read(root/'contact-recipient-prior.json');audit=read(root/'contact-opportunity-audit.json')
lines=[];add=lines.append
add('# 個人數據驗證 v25：一般非投籃犯規與被犯規者\n')
add('**四季各3組seed、28,023場完整／嚴格範圍驗證完成；本版未採用，整體任務仍未完成。**\n')
add('[2025–26全582人逐項對照](2025-26-player-validation.csv)包含整季總量、每36分鐘、分鐘、出手分母、在場球隊／排除本人後的隊友命中率、ON–OFF，以及新加入的犯規來源與各類模擬罰球。181欄，保留所有低分鐘球員。\n')
add('## 修改與量測範圍\n')
add('舊的一般非投籃犯規頻率把末節落後故意犯規情境也算進去，引擎又另外執行末節犯規策略，存在重複計入。v25按來源事件前比分、節次與剩餘時間，排除符合引擎末節策略條件的事件後，重估一般頻率。這是策略條件分組，並非官方故意犯規標籤；來源事件時間與引擎觸球準備前時間不完全一致，仍是近似。保留原有末節策略。\n')
add('一般非投籃犯規發生後，改從當時五人選擇被犯規者。條件多項模型採零中心高斯先驗；強度由2022–23至2024–25整場五折留出選定，未用2025–26、模擬殘差、勝場、排名、名字或ON–OFF選參數。這是同季來源角色／產量的相對分配，跨隊尺度由先驗決定，不能當作個人的因果技巧。\n')
add('投籃犯規、罰球命中、加罰條件、出手／助攻／失誤／籃板／時鐘／輪替機制均保留前版。offBall、screen、handle、breakDbl仍是未知預設70，沒有把追蹤產量冒充技巧分數。技術罰球與未連結罰球仍未完整生成。\n')
add('## 四季個人與在場誤差\n')
add('主摘要按真實分鐘加權，至少500真實分鐘；FG／3P至少100次真實出手。各季等權平均。這是同季重建，不是跨季預測或因果ON–OFF。\n')
add('| 平均絕對誤差 | v24 | v25 |\n|---|---:|---:|')
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('fta36','罰球出手/36'),('fgPct','FG百分點'),('threePct','3P百分點')]:
 add(f"| {label} | {scores['aggregate']['v24']['individualMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
for k,label in [('onTeamFG','在場球隊FG百分點'),('onTeammateFG','扣掉本人的隊友FG百分點'),('onTeam3P','在場球隊3P百分點'),('onTeammate3P','扣掉本人的隊友3P百分點'),('onOpponentFG','在場對手FG百分點'),('teamFGOnOff','球隊FG ON–OFF百分點'),('team3POnOff','球隊3P ON–OFF百分點')]:
 add(f"| {label} | {scores['aggregate']['v24']['onCourtMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add('\n得分與罰球誤差改善，個人三分與在場隊友命中率則略退步；不能把某一項改善解讀成整個系統已精準。\n')
add('## 球隊勝場檢查\n')
add('| 球季 | 正式控制MAE | v24 | v25 | 控制+0.5場界線 |\n|---|---:|---:|---:|---|')
failed=[]
for s in protocol['seasons']:
 c={c['version']:c for c in scores['cells'] if c['season']==s};a=c['control']['teamMetrics']['winsMAE'];b=c['rotation-space']['teamMetrics']['winsMAE'];passed=b<=a+.5
 if not passed:failed.append(s)
 add(f"| {s} | {a:.3f} | {c['v24']['teamMetrics']['winsMAE']:.3f} | {b:.3f} | {'通過' if passed else '未通過'} |")
add('\n四季勝場MAE平均6.867→6.150，仍有兩季未過固定界線。沒有放寬界線或切換正式模型。\n')
add('## 仍缺少的機會\n')
add('以下固定2025–26的1188場與單一seed，觀察器不改亂數、比分或球隊計數；只能用來定位機制，不能把原始計數差直接當調參數目標。機會指球員在場時隊伍發生一般非投籃犯規，期望被犯規數依當時五人權重累加。\n')
add('| 球員 | 來源隊伍機會 | 模擬隊伍機會 | 來源實際被犯規 | 來源條件期望 | 模擬條件期望 |\n|---|---:|---:|---:|---:|---:|')
for pid in [203999,1628983,1629029,201939,1629674]:
 p=next(p for p in audit['rows'] if p['playerId']==pid)
 add(f"| {p['name']} | {p['sourceOpportunities']} | {p['simulated']['opportunities']} | {p['sourceContacts']} | {p['sourceExpectedContacts']:.2f} | {p['simulated']['expectedContacts']:.2f} |")
add('\nJokić在真實五人的條件歸屬接近實際，但模擬在場時的隊伍機會明顯較少；只修歸屬仍不足。一般犯規的聯盟常數、同場五人／輪替暴露與罰球加罰狀態都可能影響產量。v26已獨立準備四季個人一般犯規、終結事件與同範圍分鐘，後續測試陣容機會強度；本版沒有把這些尚未驗證的量寫回引擎。\n')
add('## OVR與驗證\n')
add('最近完成的全員OVR是[v24完整Top50／582人榜](../player-impact-v24/all-2025-26/report.md)：自然位置、其餘四個位置各自不同且平均70的隊友，每人2400場。17名PG／SG進前50，SGA第1、Luka第3、Jokić第7、Queta第39、Curry第62。前50仍有10名不足500分鐘球員。這是v24的實驗點估計，不能冒稱v25排名，也不能單憑此驗收整套模型。\n')
add('24份結果均通過個人／球隊計數、得分公式、失誤與抄截配對、FT類別與被犯規者帳目；嚴格範圍FG的五人在場、本人一人、隊友四人另由評分器核對。96場固定陣容測試確認快取一致、舊輸入不變、平均隊友屬性不變，關閉一般／故意非投籃犯規後與v24完全一致。所有來源與結果雜湊另由verify.mjs核對。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
status={'version':'ordinary-contact-policy-victim-25','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'targetPlayers':582,'targetPlayerColumns':181,'teamWinGatesFailed':failed,'ovrLastCompleteVersion':24,'ovrFullRankingThisVersion':False,'next':'Test lineup-dependent ordinary-contact intensity using source counts/exposure; resolve FT categories, defense, rotations and low-minute extrapolation. No name/rank residual tuning.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print(json.dumps(status,indent=2))

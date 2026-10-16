import json,csv
from pathlib import Path
root=Path('reports/player-impact-v26');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(root/'scores.json');protocol=read(root/'validation-protocol.json');prior=read(root/'contact-intensity-prior.json');audit=read(root/'contact-opportunity-audit.json');ledger=read(root/'ledger-verification.json')
with (root/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);columns=len(reader.fieldnames);players=list(reader)
assert len(players)==582
lines=[];add=lines.append
add('# 個人數據 v26：陣容一般非投籃犯規強度\n')
add(f'**四季各3組seed、{ledger["games"]:,}場完整／嚴格範圍比較已完成；本版未採用，整體任務仍未完成。**\n')
add(f'[2025–26全582人逐項對照](2025-26-player-validation.csv)共{columns}欄，包含總量、每36分鐘、分鐘、出手分母、在場球隊與排除本人的隊友命中率、ON–OFF、各類罰球與犯規來源強度。全部低分鐘球員保留。CSV中v25Conditional欄是前版來源參考，v26沒有使用它作為犯規歸屬。\n')
add('## 機制與來源\n')
add('v25已把末節策略條件從一般非投籃犯規來源頻率分開，並修正發生犯規後的歸屬，但一般犯規機率仍是聯盟常數。單組被動觀察發現，Jokić來源在場隊伍機會465次，模擬僅339次，單改歸屬補不回缺少的機會。\n')
add('v26以同範圍來源C（一般非投籃被犯規）、N（一般FGA＋TOV＋沒有登記FGA的投籃犯規）、M（在場分鐘）建立Gamma–Poisson後驗事件率：(count＋κ×聯盟率)/(M＋κ)。場上五人的一般犯規機率為ΣC率/(ΣC率＋ΣN率＋未歸屬球隊N率)，歸屬則依各人的C率。其餘投籃／加罰／罰球命中／末節策略／助攻／失誤／籃板／輪替保留前版。\n')
add(f"C、N先驗分別為{prior['fits']['contacts']['priorMinutes']:.3f}與{prior['fits']['terminal']['priorMinutes']:.3f}分鐘，依2022–23至2024–25整場五折留出Poisson概似選定；2025–26未參與先驗選擇。未用名字、OVR、ON–OFF、勝場或模擬殘差選參數。\n")
add('這是來源角色／產量，不能稱為可攜因果技巧。分鐘包含全場暴露，事件則排除來源末節策略條件；一般狀態時間未獨立識別。N包含補籃、傳球失誤與團隊未歸屬失誤，和引擎分支時序仍有近似。來源事件時計與引擎準備前時計不同；技術與未解罰球仍缺少。未知offBall／screen／handle／breakDbl保留70。\n')
add('## 四季個人與在場誤差\n')
add('每季至少500真實分鐘、按真實分鐘加權，FG／3P至少100次真實出手，再四季等權平均。全部球員另完整輸出。這是同季重建，原始ON–OFF受輪替、隊友與對手混雜，不當作因果效果。\n')
add('| 平均絕對誤差 | v25 | v26 |\n|---|---:|---:|')
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('fta36','罰球出手/36'),('fgPct','FG百分點'),('threePct','3P百分點')]:
 add(f"| {label} | {s['aggregate']['v25']['individualMAE'][k]:.3f} | {s['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
for k,label in [('onTeamFG','在場球隊FG百分點'),('onTeammateFG','排除本人隊友FG百分點'),('onTeam3P','在場球隊3P百分點'),('onTeammate3P','排除本人隊友3P百分點'),('onOpponentFG','在場對手FG百分點'),('teamFGOnOff','球隊FG ON–OFF百分點'),('team3POnOff','球隊3P ON–OFF百分點')]:
 add(f"| {label} | {s['aggregate']['v25']['onCourtMAE'][k]:.3f} | {s['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add('\n每項改善與退步均保留。不能因某位指定球員接近就採用整版。\n')
add('## 球隊勝場檢查\n')
add('| 球季 | 正式控制MAE | v25 | v26 | 控制+0.5場界線 |\n|---|---:|---:|---:|---|');failed=[]
for season in protocol['seasons']:
 c={c['version']:c for c in s['cells'] if c['season']==season};a=c['control']['teamMetrics']['winsMAE'];b=c['rotation-space']['teamMetrics']['winsMAE'];passed=b<=a+.5
 if not passed:failed.append(season)
 add(f"| {season} | {a:.3f} | {c['v25']['teamMetrics']['winsMAE']:.3f} | {b:.3f} | {'通過' if passed else '未通過'} |")
add('\n沒有放寬界線或切換正式模型。\n')
add('## 單組被動機會診斷\n')
add('固定2025–26嚴格範圍1188場與seed20261012，觀察器不改亂數、比分、球隊或個人計數。條件期望依實際模擬當時五人的v26事件率累加。\n')
add('| 球員 | 來源隊伍機會 | v26隊伍機會 | 來源被犯規 | v26被犯規 | v26條件期望 |\n|---|---:|---:|---:|---:|---:|')
for pid in [203999,1628983,1629029,201939,1629674]:
 p=next(p for p in audit['rows'] if p['playerId']==pid)
 add(f"| {p['name']} | {p['sourceOpportunities']} | {p['simulated']['opportunities']} | {p['sourceContacts']} | {p['simulated']['contacts']} | {p['simulated']['expectedContacts']:.2f} |")
add('\nJokić的隊伍機會由v25的339提高至472，接近來源465；但其他球員仍有機會與分配差異。這張表僅單組機制檢查，不能以原始計數差直接調參數。\n')
add('## OVR與驗證\n')
add('最新完整OVR仍是[v24的全582人榜與Top50](../player-impact-v24/all-2025-26/report.md)：17名PG／SG進前50，SGA第1、Luka第3、Jokić第7、Queta第39、Curry第62，10名不足500分鐘。每人自然位置、其他四個不同位置的平均70隊友、2400場／人；這是固定模型實驗點估計，不能冒稱v26榜或正式驗收。\n')
add('96場固定陣容測試確認快取一致，關閉新強度機制後所有計數與v25完全一致；舊輸入與平均70屬性沒有變動。四季來源逐場／個人計數與分鐘守恆，沒有零分鐘卻有事件的球員。24份全季／嚴格模擬通過個人／球隊、FT類別與身份帳目，FG五／一／四份由評分器核對；來源與結果雜湊另核對。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
status={'version':'lineup-contact-token-intensity-26','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'targetPlayers':582,'targetPlayerColumns':columns,'teamWinGatesFailed':failed,'ovrLastCompleteVersion':24,'ovrFullRankingThisVersion':False,'next':'Evaluate remaining opportunity, FT, defense and rotation gaps; no name/rank residual tuning.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2))

import json
from pathlib import Path
root=Path('reports/player-impact-v26');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(root/'pilot-scores.json');p=read(root/'contact-intensity-prior.json')
old=read('reports/player-impact-v25/runs/2025-26-rotation-space-strict-20261012.json');new=read(root/'runs/2025-26-rotation-space-strict-20261012.json')
lines=['# v26：陣容一般非投籃犯規頻率，目標季首組診斷\n','**僅2025–26一組seed，全季1230場及嚴格範圍1188場。四季三組驗證另行運算；本版未採用，未產生新版OVR。**\n',
'來源C是一般非投籃被犯規次數，N是一般FGA＋TOV＋沒有登記FGA的投籃犯規，M是相同比賽的在場分鐘。以Gamma–Poisson來源先驗估計C/min與N/min；一般犯規機率改為ΣC率／(ΣC率＋ΣN率＋團隊未歸屬N率)，被犯規者按五人的C率分配。末節策略、投籃罰球、罰球命中與加罰、其餘進攻防守機制保持前版。\n',
f"兩項先驗分別以2022–23至2024–25整場五折留出Poisson概似選定，接觸先驗{p['fits']['contacts']['priorMinutes']:.3f}分鐘、終結先驗{p['fits']['terminal']['priorMinutes']:.3f}分鐘；2025–26不參與先驗選擇。沒有使用球員名字、OVR、勝場、ON–OFF或模擬殘差選參數。\n",
'這是來源角色／產量模型，並非因果技巧。事件排除來源末節策略條件，但分鐘包含全部在場時間；一般狀態暴露沒有獨立辨識。N保留全部FGA與TOV，包含補籃、傳球失誤與球隊未歸屬失誤，和引擎分支時序仍有近似。來源與引擎末節策略的取時點亦不同，技術罰球仍缺少。\n',
'| 平均絕對誤差 | v25同seed | v26 |\n|---|---:|---:|']
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('dreb36','防守籃板/36'),('fta36','罰球出手/36'),('fgPct','FG百分點'),('threePct','3P百分點')]:
 lines.append(f"| {label} | {s['aggregate']['v25']['individualMAE'][k]:.3f} | {s['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
for k,label in [('onTeammateFG','排除本人隊友FG百分點'),('onTeammate3P','排除本人隊友3P百分點')]:
 lines.append(f"| {label} | {s['aggregate']['v25']['onCourtMAE'][k]:.3f} | {s['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
lines+=['\n| 球隊指標 | v25 | v26 |\n|---|---:|---:|']
for k,label in [('winsMAE','82場勝場MAE'),('netRMSE','淨勝分RMSE')]:lines.append(f"| {label} | {s['aggregate']['v25']['team'][k]:.3f} | {s['aggregate']['rotation-space']['team'][k]:.3f} |")
lines+=['\n| 球員 | v25一般被犯規 | v26一般被犯規 | v25總FTA | v26總FTA |\n|---|---:|---:|---:|---:|']
names={str(p['playerId']):p['name'] for p in s['cells'][-1]['players']}
for pid in ['203999','201939','1628983','1629029','1629674']:
 lines.append(f"| {names[pid]} | {old['contactAudit']['players'][pid]['nonShooting']} | {new['contactAudit']['players'][pid]['nonShooting']} | {old['ftAudit']['players'][pid]['fta']} | {new['ftAudit']['players'][pid]['fta']} |")
lines+=['\nJokić來源一般被犯規240次，本組168→235；但整體得分、罰球出手、FG與隊友命中率誤差沒有一起改善。不能只因指定球員接近就採用。單組差異含模擬亂數影響，完整四季三組比較另行完成。\n',
'96場固定陣容快取／未快取完全一致；關閉新強度機制後和v25所有事件及個人計數完全一致；舊輸入與五位置平均70屬性未被改寫。四季來源共2262球員季通過逐場／個人計數與分鐘加總，沒有零分鐘卻有事件的球員。首組2418場通過個人／球隊、罰球類別與身份帳目；FG五／一／四份由評分器核對。\n',
'最新完整OVR仍見[v24全582人與Top50](../player-impact-v24/all-2025-26/report.md)，最新完整個人驗證見[v25四季報告](../player-impact-v25/report.md)。']
(root/'pilot-report.md').write_text('\n'.join(lines),encoding='utf-8')
(root/'pilot-status.json').write_text(json.dumps({'version':'lineup-contact-token-intensity-26','stage':'target-season-one-seed-pilot-complete','fullFourSeasonStatus':'running','officialModelAdopted':False,'goalComplete':False,'ovrLastCompleteVersion':24,'pilotGames':2418},indent=2),encoding='utf-8')
print('pilot report and explicit non-adoption status written')

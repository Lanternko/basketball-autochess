"""Publish all-player diagnostics without declaring a failed candidate adopted."""
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
root=Path('reports/player-impact-v21');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(root/'scores.json');protocol=read(root/'validation-protocol.json');season='2025-26'
current=next(c for c in scores['cells'] if c['season']==season and c['version']=='rotation-space')
previous=next(c for c in scores['cells'] if c['season']==season and c['version']=='v20')
source=read(root/f'{season}-terminal-risk.json');tracking=read(root/f'{season}-tracking.json')
provenance={p['playerId']:p for p in read('reports/player-impact-v20/2025-26-measurement-provenance.json')['rows']}
actual=defaultdict(Counter);pred=defaultdict(Counter);onc=defaultdict(lambda:defaultdict(Counter))
for t in read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams']:
 for p in t['roster']:actual[p['playerId']].update(p['observed'])
for seed in protocol['seeds']:
 for t in read(root/f'runs/{season}-rotation-space-full-{seed}.json')['teams']:
  for p in t['players']:
   pred[p['playerId']].update({k:v/len(protocol['seeds']) for k,v in p['stats'].items() if isinstance(v,(float,int))})
 for p in read(root/f'runs/{season}-rotation-space-strict-{seed}.json')['onCourt']['players']:
  for g in ['on','off','teammates','own']:onc[p['playerId']][g].update(p[g])
truth={p['playerId']:p for p in read(f'reports/player-impact-v1/{season}-on-court-truth.json')['players']}
counts={'pts':'PTS','ast':'AST','oreb':'OREB','dreb':'DREB','stl':'STL','blk':'BLK','tov':'TOV','fga':'FGA','fg3a':'FG3A','fta':'FTA'}
onconfigs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a'),'onOpponentFG':('on','opp_fgm','opp_fga'),'onOpponent3P':('on','opp_fg3m','opp_fg3a')}
rows=[]
for p in current['players']:
 pid=p['playerId'];a=actual[pid];b=pred[pid];risk=source['cards'][str(pid)];tm=tracking['cards'][str(pid)]
 row={'playerId':pid,'name':p['name'],'position':p['position'],'roleLowConfidence':provenance[pid]['role']['lowConfidence'],'actualMinutes':a['MIN'],'simulatedMinutes':b['seconds']/60,'primarySummarySample':a['MIN']>=500,'movementSourceAvailable':tm.get('movement') is not None,'movementUsedAsSkill':False,'unknownOffBall':70,'unknownScreen':70,'unknownHandle':70,'unknownBreakDouble':70,'terminalSourceOpportunities':risk['opportunities'],'terminalDeadProbability':risk['deadProbability'],'terminalNeutralLiveProbability':risk['neutralLiveProbability']}
 def pair(key,av,pv):
  row[key+'_actual']=av;row[key+'_predicted']=pv;row[key+'_error']=pv-av if av is not None and pv is not None else None
 for k,obs in counts.items():
  pair(k+'Total',a[obs],b[k] if b['seconds'] else None)
  pair(k+'36',36*a[obs]/a['MIN'] if a['MIN'] else None,36*b[k]/(b['seconds']/60) if b['seconds'] else None)
 pair('rebTotal',a['OREB']+a['DREB'],b['oreb']+b['dreb'] if b['seconds'] else None)
 pair('reb36',36*(a['OREB']+a['DREB'])/a['MIN'] if a['MIN'] else None,36*(b['oreb']+b['dreb'])/(b['seconds']/60) if b['seconds'] else None)
 for key,am,aa,pm,pa in [('fgPct','FGM','FGA','fgm','fga'),('threePct','FG3M','FG3A','fg3m','fg3a')]:
  pair(key,100*a[am]/a[aa] if a[aa] else None,100*b[pm]/b[pa] if b[pa] else None)
  row[key+'_actualAttempts']=a[aa];row[key+'_simulatedAttempts']=b[pa];row[key+'_primarySummarySample']=a['MIN']>=500 and a[aa]>=100
 for key,(g,m,n) in onconfigs.items():
  ta=truth[pid][g];pr=onc[pid][g]
  pair(key,100*ta.get(m,0)/ta[n] if ta.get(n,0) else None,100*pr[m]/pr[n] if pr[n] else None)
  row[key+'_actualAttempts']=ta.get(n,0);row[key+'_simulatedAttemptsPerSeed']=pr[n]/len(protocol['seeds']);row[key+'_primarySummarySample']=a['MIN']>=500 and ta.get(n,0)>=100
 for key,x,y in [('teamFGOnOff','onTeamFG','offTeamFG'),('team3POnOff','onTeam3P','offTeam3P')]:
  av=row[x+'_actual']-row[y+'_actual'] if row[x+'_actual'] is not None and row[y+'_actual'] is not None else None
  pv=row[x+'_predicted']-row[y+'_predicted'] if row[x+'_predicted'] is not None and row[y+'_predicted'] is not None else None
  pair(key,av,pv)
 rows.append(row)
assert len(rows)==582 and len({r['playerId'] for r in rows})==582
with (root/f'{season}-player-validation.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

bench=read(root/'ovr-checkpoint.json');oldbench=read('reports/player-impact-v20/ovr-checkpoint.json')
bm={r['result']['playerId']:r for r in bench['rows']};oldbm={r['result']['playerId']:r for r in oldbench['rows']};lines=[];add=lines.append
add('# 2025–26 個人數據與 OVR：逐球失誤修正 v21\n')
add('**目標球季已確認為2025–26。已完成四季各3組seed、582人逐項對照，以及31名球員的自然位置OVR抽樣。本版未採用，仍不能稱為修正完成的Top50。**\n')
add('[582人完整對照表](2025-26-player-validation.csv) 同時列出整季總量、每36分鐘、FG／3P、在場球隊與排除本人的隊友命中率，以及原始出手分母。所有人都保留；小樣本只影響摘要資格，不從榜單排除。凡有出手均輸出命中率，零出手留白。總量差可檢查輪替分鐘是否掩蓋率值誤差。\n')
add('## 實際改動\n')
add('原本把箱分比例轉成tovSkill，再經曲線與共用倍率產生持球失誤。本版改用逐球終結機會，分開估計死球失誤與有抄截紀錄的非傳球失誤。分母為記錄FGA、未伴隨同時鐘同球員FGA的投籃犯規、以及排除傳球被抄後的個人失誤。傳球被抄維持原獨立分支；團隊失誤不灌給球員。\n')
fit=read(root/'terminal-risk-prior.json')
add(f"共同先驗強度為{fit['kappaEvents']:.2f}個事件，以2022–23至2024–25的五折整場留出概似決定，未使用2025–26的目標、模擬殘差、名字或排名來調參。活球風險按當時對手五人的抄截壓力正規化；死球風險不隨抄截壓力一起放大。這是來源情境的條件風險，不是假稱已測到運球技能。\n")
add('同時鐘多次出手的犯規連結仍有歧義：四季分別50／24／23／36筆，已保留計數，沒有宣稱逐次犯規完全辨識。來源防守壓力仍用同季完整抄截資料，因此這是條件重現驗證，不是未來球季盲測。近乎不收縮的估計在部分留出資料產生不合法機率，先驗檔的1e100是拒絕該候選的哨兵，並非有效NLL。\n')
add('原本投籃、犯規、籃板及來源命中率中心保持不變。已用3000組條件機率驗證：只改同一終結球員的失誤存活率，在該球員的自主／接球出手條件混合中會相消。96場快取與未快取的比分及個人計數完全一致；改動舊共用失誤倍率與活球比例也完全不影響本版結果。\n')
add('## 四季同組seed的誤差\n')
add('| 分鐘加權MAE | v20 | v21 |\n|---|---:|---:|')
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('fgPct','FG 百分點'),('threePct','3P 百分點')]:
 add(f"| {label} | {scores['aggregate']['v20']['individualMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
add('\n四季等權；主摘要至少500實際分鐘，命中率至少100次對應實際出手。582人的CSV仍包含所有樣本，不能把主樣本平均誤差當作每個人都精準。\n')
add('| 在場指標MAE，百分點 | v20 | v21 |\n|---|---:|---:|')
for k,label in [('onTeamFG','在場球隊FG'),('onTeammateFG','排除本人的隊友FG'),('onTeam3P','在場球隊3P'),('onTeammate3P','排除本人的隊友3P'),('teamFGOnOff','球隊FG ON–OFF'),('team3POnOff','球隊3P ON–OFF')]:
 add(f"| {label} | {scores['aggregate']['v20']['onCourtMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add('\nON–OFF受輪替、隊友和對手影響，本表沒有把原始差當成個人因果效果。\n')
add('## 球隊勝場採用界線\n')
add('| 球季 | 正式控制勝場MAE | v20 | v21 | 不超過控制+0.5場 |\n|---|---:|---:|---:|---|')
failed=[]
for s in protocol['seasons']:
 cells={c['version']:c for c in scores['cells'] if c['season']==s};control=cells['control']['teamMetrics']['winsMAE'];old=cells['v20']['teamMetrics']['winsMAE'];new=cells['rotation-space']['teamMetrics']['winsMAE'];passed=new<=control+.5
 if not passed:failed.append(s)
 add(f'| {s} | {control:.3f} | {old:.3f} | {new:.3f} | {"通過" if passed else "未通過"} |')
add('\n個人失誤改善不能代替球隊與在場命中率驗證；未通過的版本不取代正式模型。\n')
add('## 目標季球員與OVR抽樣\n')
add('| 球員 | 實際失誤/36 | v20 | v21 | v21基準隊勝率 | 同位置平均隊勝率 |\n|---|---:|---:|---:|---:|---:|')
for pid in [1628983,1629029,203999,201939,1629674]:
 p=next(p for p in current['players'] if p['playerId']==pid);o=next(p for p in previous['players'] if p['playerId']==pid);r=bm[pid];slot=r['job'].get('slot')
 baseline=next(z for z in bench['rows'] if z['job']['kind']=='baseline' and z['result']['position']==r['result']['position'])
 add(f"| {p['name']} | {p['metrics']['tov36']['actual']:.3f} | {o['metrics']['tov36']['predicted']:.3f} | {p['metrics']['tov36']['predicted']:.3f} | {100*r['result']['winRate']:.2f}% | {100*baseline['result']['winRate']:.2f}% |")
add('\n每名樣本只放自然位置，搭配其餘四種各位置算術平均屬性70的隊友，對固定30隊雙邊各40組，共2400場／人。這31人是既定代表與舊榜低分鐘異常樣本，不能拿來宣稱新Top50有多少後衛，也不能把SGA、Luka或Jokić的抽樣勝率當成名次。\n')
add('## 新追蹤來源與仍缺少的能力\n')
add('已保存四季官方觸球、持球時間、傳球、移動與傳球配對資料，另串接既有掩護助攻紀錄。2025–26的582人均有前三種追蹤表，581人有hustle表；有移動紀錄不代表跑速已正確進入空間或OVR計算。四個未量測能力offBall／screen／handle／breakDbl仍維持70，沒有拿觸球或掩護助攻的產量直接冒充技巧。\n')
add('| 球季 | 傳球配對數 | 排除自傳列 | 接球後FGA超過官方總FGA的人數 |\n|---|---:|---:|---:|')
for c in read(root/'tracking-coverage.json'):add(f"| {c['season']} | {c['pairRows']} | {c['excludedSelfPairRows']} | {c['passedFgaReceiverOverages']} |")
add('\n歷史配對的FGA不能直接當互斥出手分割；全域傳球接球數也常與配對加總不同。這些來源只完成涵蓋與口徑審查，沒有硬塞入能力或事件機率。來源原檔、URL與雜湊均保留於raw資料及tracking JSON。\n')
add('OVR原輸入會在專用worker內修改上一版的模組快取；本次所有worker均只跑單一版本，完整輸入雜湊與隔離版本完全相同，故本次輸出有效。後續同程序跨版比較應使用[隔離輸入](ovr-input-isolated.mjs)，驗證見[input-isolation-verification.json](input-isolation-verification.json)。原凍結檔沒有覆寫。\n')
add('目前仍待解決：未通過的球隊勝場界線、個別球員籃板與助攻偏差、隊友命中率及空間因果機制、低分鐘外推、技術罰球來源機制，以及四項未量測能力。最新全員排名仍是舊v14診斷，本版沒有完成或發布新的全員Top50。')
(root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
status={'version':'measured-terminal-turnovers-21','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'targetPlayers':582,'teamWinGatesFailed':failed,'ovrSamplePlayers':31,'ovrFullRanking':False,'sourceGameRowsMatched':True,'cacheExactParityGames':96,'unknownSkillsStill70':['offBall','screen','handle','breakDbl'],'movementSourceFetched':True,'movementUsedAsSkill':False,'next':'Resolve team/on-court regressions and individual source-context allocation; tracking pairs require scope reconciliation before use as mutually exclusive event counts.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print(json.dumps(status,indent=2))

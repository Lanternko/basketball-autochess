import json
from pathlib import Path

root=Path('reports/player-impact-v23')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
scores=read(root/'scores.json');protocol=read(root/'validation-protocol.json');fit=read(root/'putback-fit-audit.json');prior=read(root/'choice-prior.json');bench=read(root/'ovr-checkpoint.json')
lines=[];add=lines.append
add('# 2025–26 個人數據與 OVR：補籃選擇傾向 v23\n')
add('**已完成四季各3組seed的完整／逐球嚴格範圍驗證、2025–26全582人對照與31人OVR診斷抽樣。正式模型未更換；本版不是已驗收的Top50。**\n')
add('[582人逐項對照](2025-26-player-validation.csv) 包含得分、助攻、失誤、抄截、阻攻、進攻／防守籃板、FG／3P、在場球隊與排除本人後的隊友命中率、ON–OFF；附實際／模擬分鐘、整季總量、出手分母及補籃來源。所有低分鐘球員保留，零分母才留白。\n')
add('## 修正與資料口徑\n')
add('v22已將補籃命中率改成單獨的來源後驗；但搶到進攻籃板後是否自己補，仍由共用體格／協防公式決定。v23只替換這項選擇傾向，保留v22的補籃命中率，以及取得籃板、失誤、犯規、罰球、一般投籃與時鐘機制。\n')
add('來源代理定義是同一球員搶到投籃未進的進攻籃板後0–3秒內近距離出手，不是官方play-type標籤。記錄FGA／進攻籃板不能直接當選擇機率，因選擇後還可能發生非投籃犯規、失誤或未記錄FGA的投籃犯規。本版用實際當時五人、來源輪替體力與既有失誤／犯規機率估計記錄FGA存活率s，再以P(記錄快補FGA)=θ球員×s估計θ。\n')
add(f"θ採Beta(1+κμ,1+κ(1−μ))先驗，κ={prior['kappaRebounds']:.4f}個籃板機會，μ為當季總快補FGA／總存活率。κ由2022–23至2024–25五折整場留出概似選定，未以2025–26、模擬殘差、勝場、ON–OFF或球員名字／排名擬合。這使用同季完整投籃與防守來源作為協變數，仍是描述性重現，不能稱為盲測或個人因果能力。\n")
add('個人θ代表已觀察的風格／產量傾向，換陣容時固定，不再額外疊加體格倍率；進球、失誤、犯規與取得籃板仍回應情境與屬性。平均70隊友依自然位置合併原始來源機會，使用同一存活率概似與先驗；各項屬性及算術平均均未改動。輸入另做複製，避免污染前一版快取。\n')
add('## 補籃直接驗證\n')
add('| 球季 | 來源FGA／命中率 | v22 FGA／命中率 | v23 FGA／命中率 | 個人次數MAE v22→v23 |\n|---|---:|---:|---:|---:|')
for s,c in fit.items():
 a=c['actual'];v=c['versions'];n=a['fieldGoalAttempts'];m=a['fieldGoalMakes']
 add(f"| {s} | {n}／{100*m/n:.2f}% | {v['22']['fga']:.1f}／{100*v['22']['sampledFG']:.2f}% | {v['23']['fga']:.1f}／{100*v['23']['sampledFG']:.2f}% | {v['22']['allPlayersCountMAE']:.2f}→{v['23']['allPlayersCountMAE']:.2f} |")
add('\n來源為同一嚴格逐球比賽範圍，模擬為三組seed平均；個人次數MAE含全部來源球員，不按分鐘篩掉。來源個人進攻籃板分母與模型產生的籃板機會仍可能不同，因此總FGA接近不代表個人選擇θ已是無偏能力。\n')
add('| 球員 | 實際補籃FGA | v22 | v23 | 推估θ |\n|---|---:|---:|---:|---:|')
bm={r['result']['playerId']:r for r in bench['rows']}
for pid,c in fit['2025-26']['selectedPlayers'].items():
 add(f"| {bm[int(pid)]['result']['name']} | {c['actual']['attempts']} | {c['22']['predicted']:.1f} | {c['23']['predicted']:.1f} | {100*c['sourceChoice']['selectionProbabilityMAP']:.2f}% |")
add('\n以上θ是選擇傾向，不是補籃命中率。來源先驗會造成收縮；2025–26來源條件期望快補FGA與觀察值也不完全相等，沒有以殘差再校正。\n')
add('## 四季個人及在場誤差\n')
add('| 分鐘加權MAE | v22 | v23 |\n|---|---:|---:|')
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('fgPct','FG 百分點'),('threePct','3P 百分點')]:add(f"| {label} | {scores['aggregate']['v22']['individualMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
add('\n四季等權；主摘要至少500實際分鐘，FG／3P另須100次實際對應出手。表中是誤差，不是平均產量；平均值不能證明每個人精準。全員CSV包含摘要門檻外的人。\n')
add('| 在場MAE，百分點 | v22 | v23 |\n|---|---:|---:|')
for k,label in [('onTeamFG','在場球隊FG'),('onTeammateFG','排除本人隊友FG'),('onTeam3P','在場球隊3P'),('onTeammate3P','排除本人隊友3P'),('teamFGOnOff','球隊FG ON–OFF'),('team3POnOff','球隊3P ON–OFF')]:add(f"| {label} | {scores['aggregate']['v22']['onCourtMAE'][k]:.3f} | {scores['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add('\n在場五人、本人一人、其餘隊友四人的出手／進球帳目獨立守恆驗證。原始ON–OFF受輪替、隊友、對手影響，不能直接當作個人空間或控球的因果效果。\n')
add('## 2025–26 指定球員的個人對照\n')
cell=next(c for c in scores['cells'] if c['season']=='2025-26' and c['version']=='rotation-space')
add('| 球員 | 得分/36 實際→模擬 | 助攻/36 | 失誤/36 | 防守籃板/36 | FG% |\n|---|---:|---:|---:|---:|---:|')
for pid in [1628983,1629029,203999,201939,1629674]:
 p=next(p for p in cell['players'] if p['playerId']==pid)
 vals=[f"{p['metrics'][k]['actual']:.2f}→{p['metrics'][k]['predicted']:.2f}" for k in ['pts36','ast36','tov36','dreb36','fgPct']]
 add('| '+p['name']+' | '+' | '.join(vals)+' |')
add('## 球隊採用界線\n')
add('| 球季 | 正式控制勝場MAE | v22 | v23 | v23≤控制+0.5場 |\n|---|---:|---:|---:|---|');failed=[]
for s in protocol['seasons']:
 c={c['version']:c for c in scores['cells'] if c['season']==s};control=c['control']['teamMetrics']['winsMAE'];a=c['v22']['teamMetrics']['winsMAE'];b=c['rotation-space']['teamMetrics']['winsMAE'];passed=b<=control+.5
 if not passed:failed.append(s)
 add(f'| {s} | {control:.3f} | {a:.3f} | {b:.3f} | {"通過" if passed else "未通過"} |')
add('\n本版仍為實驗版本，正式模型未更換。\n')
add('## 自然位置OVR診斷\n')
add('| 球員 | v22基準隊勝率 | v23 | v23條件95%區間 | 同位置平均隊 |\n|---|---:|---:|---:|---:|')
old={r['result']['playerId']:r for r in read('reports/player-impact-v22/ovr-checkpoint.json')['rows']}
for pid in [1628983,1629029,203999,201939,1629674]:
 r=bm[pid]['result'];base=next(p['result'] for p in bench['rows'] if p['job']['kind']=='baseline' and p['result']['position']==r['position']);lo,hi=r['ci95']
 add(f"| {r['name']} | {100*old[pid]['result']['winRate']:.2f}% | {100*r['winRate']:.2f}% | {100*lo:.2f}–{100*hi:.2f}% | {100*base['winRate']:.2f}% |")
add('\n31名既定診斷樣本＋5位置基線，每人自然位置、其餘四個不同位置平均70隊友，30對手雙邊各40組，共2400場／人。區間只反映固定模型／對手下的模擬取樣，不含來源估計與模型錯誤；v22→v23小差值不能當顯著提升。尚未跑本版全582人OVR，不能宣稱Top50後衛數或三人已進前10／20。\n')
add('## 驗證與仍未解決\n')
source_audit=read(root/'source-score-audit.json');unreachable={s:len(read(root/f'{s}-choice-survival.json')['unreachableFastShots']) for s in protocol['seasons']}
add(f"四季共核對{sum(x['checkedRebounds'] for x in source_audit.values())}筆來源籃板的比分欄位，無空值或無效值。來源籃板逐項對應陣容；25季有47次時鐘≤0.3秒、22次末節故意犯規、16次領先耗時狀態未納入θ推估；其中合計17次真實快補出手是現有時鐘／戰術政策無法重現的缺口。四季這類無法重現的快補筆數為{unreachable}，不是刪除失敗比賽。\n")
add('96場OVR快取與未快取的全部結果相同；四季2882張個人／對手／平均隊友卡片驗證θ合法、平均70與前版快取未污染。全部24份完整／嚴格季模擬驗證球員—球隊統計、得分、抄截／被抄失誤及團隊專屬時鐘違例守恆。\n')
add('未修復：舊一般出手分割仍排除每季69–135次罰球籃板後快出手，與目前補籃目標口徑略不一致；四項offBall／screen／handle／breakDbl仍為70，未把跑動、掩護或傳球產量冒充技巧。來源存活率採粗略犯規／末節政策，來源風格在換陣容時固定的假設需再驗證；部分球員防守籃板、助攻、球隊防守及低分鐘OVR外推仍有缺口。Curry的得分／OVR不足仍未解決。後續應先按事件拆分這些誤差，不能按名字或前50後衛配額修分。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
status={'version':'measured-putback-choice-23','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'targetPlayers':582,'teamWinGatesFailed':failed,'ovrSamplePlayers':31,'ovrFullRanking':False,'cacheExactParityGames':96,'next':'Resolve fresh/FT-rebound partition, source-policy survival mismatch and individual allocation/defensive effects before adoption; no rank tuning.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2))

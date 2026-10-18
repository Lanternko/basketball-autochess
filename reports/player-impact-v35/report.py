"""Render the joint-creator hypothesis without claiming source roles are capabilities."""
import csv,json
from pathlib import Path
R=Path('reports/player-impact-v35');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
scores=read(R/'scores.json');before=scores['aggregate']['v30'];current=scores['aggregate']['rotation-space'];floor=read('reports/player-impact-v34/scores.json')['aggregate']['rotation-space']
source=read(R/'source-comparison.json');probe=read(R/'ovr-probe-summary.json');transport=read(R/'transport-verification.json');strata=read(R/'error-strata.json')
with (R/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);players=list(r);columns=len(r.fieldnames)
assert len(players)==582;byName={p['name']:p for p in players};failed=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cells={c['version']:c for c in scores['cells'] if c['season']==season}
 if cells['rotation-space']['teamMetrics']['winsMAE']>cells['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
worse=[k for k,v in current['individualMAE'].items() if v>before['individualMAE'][k]]
lines=['# v35：自主與傳球的共同發動分配','',
'**完成四季各3組seed、28,023場完整／嚴格比賽，以及10人9,600場同負荷配對。全582人保留；這是聯合分配假設試驗，尚未採用，也沒有新版全員OVR。**','',
'## 改動與假設','',
'v33發現接球占滿額度會把自主機會歸零；v34硬保留來源自主量雖消除了零支援，卻壓縮部分組織者的傳球。本輪把每位球員的「自己終結」和「傳給別人終結」同時分配：','',
'- 發動端總量＝來源自主量＋來源傳球量；五人共同按比例縮放，讓發動總量等於原有終結總量。','- 終結端總量仍為每人原有名目終結機會；不額外發明出手。','- 先驗矩陣的對角線為來源自主量，其餘格為來源傳球量×其他人的相對接球需求。以行、列比例平衡同時滿足發動與終結總量。','- 對角線最後解讀為自主進攻，非對角線才是傳球；自己助攻自己仍禁止。來源自主量可以提高或降低，不再是固定上限或下限。','',
'這是明確的模型假設：**合併的發動量也不是已量出的生理能力或可持續負荷。** 來源角色含先驗與從進球助攻比例推估的成分。新分配沒有依球員名字、位置名次、ON–OFF或勝場殘差調係數；原有elastic角色參數、原始屬性、機率公式與v30相同，來源情境重算校準。攔截與觸球失誤沿用原有公式，負荷政策不變。','',
f'582個自然位置平均70隊友陣容通過終結／發動守恆、正自主支援、零自助攻、順序互換及同比例縮放檢查；來源自主量同時存在向上與向下變動。四季全部實際五人另逐一核對守恆。對{transport["sampledLineups"]}個確定性抽樣陣容，用獨立Python對數空間解算重建矩陣，最大元素差{transport["maxAbsoluteDifferenceToIndependentLogSpaceSolve"]:.3g}。受控對稱角色下，24組／48場全部球員與球隊計數與v30相同；不代表實際輸入或缺資料回退相同。','',
'## 個人與在場數據','',
f'輸出全582人、{columns}欄：整季總量／分鐘、per36、FG／3P／FT、在場球隊／其他四人／對手、OFF與ON–OFF及分母。主誤差樣本為真實至少500分鐘，季內按真實分鐘加權，再四季等權；FG／3P至少100次來源出手、FT至少50次。在場只比較同一批嚴格PBP場次；全年與嚴格範圍分鐘分開。低分鐘球員仍輸出，未靠刪人改善誤差。','',
'| 四季MAE | v30 | v34硬自主下限 | v35共同分配 | 相較v30 |','|---|---:|---:|---:|---|']
labels={'pts36':'得分／36','ast36':'助攻／36','tov36':'失誤／36','stl36':'抄截／36','blk36':'阻攻／36','oreb36':'進攻籃板／36','dreb36':'防守籃板／36','fga36':'出手／36','fg3a36':'三分出手／36','fta36':'罰球出手／36','fgPct':'FG百分點','threePct':'3P百分點','ftPct':'FT百分點','tovPer100Uses':'失誤／100次終結使用'}
for k,label in labels.items():
 a,b=before['individualMAE'][k],current['individualMAE'][k];lines.append(f"| {label} | {a:.4f} | {floor['individualMAE'][k]:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['','| 在場相關MAE（百分點） | v30 | v35 | 方向 |','|---|---:|---:|---|']
onLabels={'onTeamFG':'在場球隊FG','onTeam3P':'在場球隊3P','onTeammateFG':'在場其他四人FG','onTeammate3P':'在場其他四人3P','offTeamFG':'不在場球隊FG','offTeam3P':'不在場球隊3P','onOpponentFG':'在場對手FG','onOpponent3P':'在場對手3P','teamFGOnOff':'球隊FG的ON–OFF','team3POnOff':'球隊3P的ON–OFF'}
for k,label in onLabels.items():
 a,b=before['onCourtMAE'][k],current['onCourtMAE'][k];lines.append(f"| {label} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['','以下每格為「實際→v35」，計數per36，FG／3P為百分比；不是能力值或排名。','',
'| 球員 | 得分 | 助攻 | 失誤 | 籃板 | 抄截 | 阻攻 | FG% | 3P% |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Cade Cunningham','Victor Wembanyama','Mitchell Robinson','Stephen Curry','Neemias Queta']:
 p=byName[name];values=[]
 for k in ['pts36','ast36','tov36','reb36','stl36','blk36','fgPct','threePct']:
  if k=='reb36':a=sum(float(p[t+'_actual']) for t in ['oreb36','dreb36']);b=sum(float(p[t+'_predicted']) for t in ['oreb36','dreb36'])
  elif not p[k+'_actual'] or not p[k+'_predicted']:values.append('—');continue
  else:a,b=float(p[k+'_actual']),float(p[k+'_predicted'])
  values.append(f'{a:.2f}→{b:.2f}')
 lines.append('| '+name+' | '+' | '.join(values)+' |')
lines+=['','另有[分鐘與位置分層](error-strata.json)，保留至少500分鐘、少於500分鐘、所有正分鐘球員的G／F／C／全體MAE、帶方向偏差與加權90百分位絕對誤差；每項分母與有效球員數明列。小樣本有來源噪音，不能把per36當先發負荷能力。','',
'| 主要樣本：位置群 | 得分MAE v30→v35 | 得分偏差 v30→v35 | 助攻MAE v30→v35 | 助攻偏差 v30→v35 |','|---|---:|---:|---:|---:|']
for role in ['G','F','C']:
 values=[]
 for metric,stat in [('pts36','mae'),('pts36','signedBias'),('ast36','mae'),('ast36','signedBias')]:
  pair=[]
  for version in ['v30','rotation-space']:
   selected=[r['players'][metric][stat] for r in strata['rows'] if r['version']==version and r['sample']=='primary500' and r['roleGroup']==role];assert len(selected)==4;pair.append(sum(selected)/4)
  values.append(f'{pair[0]:+.4f}→{pair[1]:+.4f}')
 lines.append('| '+role+' | '+' | '.join(values)+' |')
lines+=['','帶方向偏差＝模擬減實際，正值為高估。這些同季重現與ON–OFF不是因果影響。','',
'## 球隊界線','',
f"四季勝場MAE {before['team']['winsMAE']:.4f}→{current['team']['winsMAE']:.4f}；淨分RMSE {before['team']['netRMSE']:.4f}→{current['team']['netRMSE']:.4f}。每季界線仍為既有正式對照勝場MAE加0.5，沒有放寬。",'',
'| 球季 | 正式對照 | v30 | v34 | v35 | v35界線 |','|---|---:|---:|---:|---:|---|']
floorCells=read('reports/player-impact-v34/scores.json')['cells']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 c={x['version']:x for x in scores['cells'] if x['season']==season};v={k:x['teamMetrics']['winsMAE'] for k,x in c.items()};f=next(x for x in floorCells if x['season']==season and x['version']=='rotation-space')['teamMetrics']['winsMAE'];lines.append(f"| {season} | {v['control']:.4f} | {v['v30']:.4f} | {f:.4f} | {v['rotation-space']:.4f} | {'未過' if season in failed else '通過'} |")
lines+=['','## 逐球來源與模擬檢查','',
'四季4,421場原始PBP、270,090個陣容情境、754,914次一般FGA逐次重讀核對，立即補籃沿用v17代理規則排除。來源FGA、非助攻FGM、助攻FGM全部對上原檔；每個重建來源情境的球員都有正自主支援，原891次零支援均消除。實際引擎呼叫與來源機率重建另作逐項一致檢查。','',
'| 球季 | v30零自主支援非助攻FGM | v35 | 同場出手分配NLL收益／FGA［95%］ |','|---|---:|---:|---:|']
for c in source['seasons']:
 lo,hi=c['fixedSourceWholeGameBootstrap95PerAttempt'];lines.append(f"| {c['season']} | {c['scores']['v30']['unsupportedSelfMakes']} | {c['scores']['v35']['unsupportedSelfMakes']} | {c['gainPerAttempt']:+.9f} [{lo:+.9f}, {hi:+.9f}] |")
lines+=['','正收益才代表此條件分配改善；主分數固定同一球員隊伍場次的FGA總量，在該場的陣容間比較相對分配。兩版皆守恆名目終結量，這項分數對自主／接球的替代本來就不敏感，不能單靠它證明或否決組織價值。完整次指標與所有球員分數保留；舊模型零支援的精確事件似然失效，1e-12下限分數只供診斷，沒有把下限加入執行中的機率。','',
'來源描述仍用完整同季FG、角色、犯規等資料，未逐折重建；並非盲測、時間外預測或因果能力估計。每季2,000次整場bootstrap固定來源與機制，不含來源／模型不確定性。','',
'## 自然位置、健康負荷與組織貢獻','',
'10人、30對手、4組seed、兩席次、兩種輪替時序；48分鐘四節、有輪替和既有疲勞，每場搭配完全相同分鐘的同位置平均70基準隊。四名隊友為不同位置形狀且每人屬性算術平均70；原始球員屬性與五張平均卡不變。兩版各自對照其相同分鐘的基準。','',
'保留使用者政策：主要看健康能打時的貢獻；出賽逐場封頂後平均，以舊三季推得34.98分鐘共同標準，缺賽不補零，替補不直接外推滿負荷。單季傷缺不扣、多季才小幅折減正向健康貢獻；0.10可靠度權重仍是待校準政策。下表只列健康貢獻，沒有傷缺轉分鐘的休息紅利。','',
'| 球員 | 支持分鐘 | v30相對平均隊分差 | v35 | 成對變化［95%］ |','|---|---:|---:|---:|---:|']
cross=0
for p in probe['players']:
 a=next(x for x in p['arms'] if x['arm']=='supportedHealthy');v=a['pairedChange'];cross+=v['ci95'][0]<=0<=v['ci95'][1];lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v30']['mean']:+.3f} | {a['v35']['mean']:+.3f} | {v['mean']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] |")
lines+=['',f'10人的健康負荷版本差有{cross}個95%區間跨零。它們是固定模型的分層配對模擬區間，不是實際NBA效率、OVR或名次，不含來源、負荷外推或模型不確定性；20個負荷場景與各球員計數的逐項區間未校正多重比較。', '',
'[完整角色與13項模擬計數](probe-role-diagnostics.json)保留全部20個負荷場景，避免只看分差均值而忽略傳球是否被壓縮。不能把全部分差變化因果歸給單一助攻項目，也不能按這10人的均值排全員榜。','',
'## 判定','',
f'相較v30，14項個人MAE有{len(worse)}項退步，{len(failed)}季未過既有勝場界線。來源零支援與分配守恆只是特定檢查，不能取代個人數據、球隊表現及全員OVR驗證。正式模型仍為pure-oreb-turnover-time-1，最新完整實驗榜仍為v24；v35沒有採用或發表新版OVR。','',
'無球、掩護、控球、破包夾仍有70預設；角色率不是這些技能的直接量測。來源對手強弱、先發負荷的效率可持續性、非投籃疲勞與創造空間的可轉移影響仍未證實。單一球員與OVR修正目標尚未完成，不能依指定球員的理想排名選模型。','',
'全部比賽比分、球員／球隊計數、助攻、抄截／活球失誤、球隊獨立24秒失誤、FT／犯規歸屬、在場5／本人1／隊友4份帳目通過。四季MAE、位置／分鐘分層、582人CSV及配對區間另作重算；來源條件分數與bootstrap由另一套字典分解公式核對。','',
'檔案：[582人176欄](2025-26-player-validation.csv)、[四季分數](scores.json)、[位置與分鐘分層](error-strata.json)、[10人負荷配對](ovr-probe-summary.json)、[來源比較](source-comparison.json)、[來源582人](2025-26-source-comparison.csv)、[機制協定](mechanism-protocol.json)、[獨立矩陣核對](transport-verification.json)、[整體核對](verification.json)。']
f=R/'report.md';assert not f.exists();f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'failedWinGateSeasons':failed,'targetPlayerColumns':columns,'fullValidationSeasons':4,'seeds':3,'games':28023,'probePlayers':10,'probeGames':9600,'sourceRoleCards':2262,'sourceContextStates':270090,'sourceUnsupportedSelfMakesBefore':891,'sourceUnsupportedSelfMakesAfter':0,'worsenedIndividualMetrics':worse,'healthyProbeChangeIntervalsOverlappingZero':cross,'scope':'Joint creator/terminal hypothesis, no source self cap/floor, no fitted ranking coefficient, no full OVR or adoption.'}
(R/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(status,ensure_ascii=False,indent=2))

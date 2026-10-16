"""Report all fixed-flow results, including failures; no ranking substitution."""
import csv,json
from pathlib import Path
R=Path('reports/player-impact-v34');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(R/'scores.json');old=s['aggregate']['v30'];new=s['aggregate']['rotation-space'];source=read(R/'source-comparison.json');probe=read(R/'ovr-probe-summary.json');flow=read(R/'flow-audit.json');strata=read(R/'error-strata.json')
with (R/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);players=list(r);columns=len(r.fieldnames)
assert len(players)==582
byName={p['name']:p for p in players};failed=[];worse=[k for k,v in new['individualMAE'].items() if v>old['individualMAE'][k]]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cells={c['version']:c for c in s['cells'] if c['season']==season}
 if cells['rotation-space']['teamMetrics']['winsMAE']>cells['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
lines=['# v34：接球分配保留來源自主機會的固定假設試驗','',
'**四季各3組seed、28,023場完整／嚴格比賽，以及10人9,600場負荷配對完成；輸出全582人。來源自主機會的零支援891球已消除，但不代表整體個人數據或OVR已準確。未採用，沒有新版全員OVR。**','',
'## 本輪修改','',
'v33查到：當接球分配占滿某人的終結額度，自主機會會被歸零，即使來源角色有自主進攻。本輪固定測試`接球容量 = 名目終結機會 − 來源自主機會`；每位傳球者不能傳給自己，在接球容量不足時降低總傳球供給，再分配到其他接球者。剩餘終結額度仍為自主機會，所以每人、五人總終結量皆守恆。','',
'這與v31把自主量當上限不同：v34把來源自主角色當保留基準，可能增加部分人自主量、減少部分人接球量，也會改變傳球邊際。個人的變動不保證同方向。來源角色仍是描述性估計，含收縮與從進球助攻比例推導的成分；不能當成每次持球的直接觀測或生理下限。固定保留比例1在計算結果之前凍結，沒有按名字、排名、ON–OFF或勝場殘差挑係數。','',
'球員屬性、來源角色、賽程、暴露及機率公式與v30相同；四季270,090個來源情境重新校準，來源分鐘、FGA、平均能量完全保留。受控分配相同時，24組／48場球員與球隊計數與v30逐項相同；四季全部實際五人、582個自然位置平均70隊友陣容的終結／傳球／零自助攻守恆通過。','',
'## 個人與在場數據','',
f'全582人、{columns}欄包含整季總量與分鐘、per36、FG／3P／FT、在場球隊／其餘四人／對手、OFF與ON–OFF及分母，沒有用位置或低分鐘門檻刪除輸出。主要誤差樣本為真實至少500分鐘、季內按真實分鐘加權，再四季等權；FG／3P至少100次來源出手、FT至少50次。在場範圍只比較同一批嚴格PBP場次。','',
'| 四季MAE | v30 | v34 | 方向 |','|---|---:|---:|---|']
labels={'pts36':'得分／36','ast36':'助攻／36','tov36':'失誤／36','stl36':'抄截／36','blk36':'阻攻／36','oreb36':'進攻籃板／36','dreb36':'防守籃板／36','fga36':'出手／36','fg3a36':'三分出手／36','fta36':'罰球出手／36','fgPct':'FG百分點','threePct':'3P百分點','ftPct':'FT百分點','tovPer100Uses':'失誤／100次終結使用'}
for k,label in labels.items():
 a,b=old['individualMAE'][k],new['individualMAE'][k];lines.append(f"| {label} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['','| 在場相關MAE（百分點） | v30 | v34 | 方向 |','|---|---:|---:|---|']
onLabels={'onTeamFG':'在場球隊FG','onTeam3P':'在場球隊3P','onTeammateFG':'在場其他四人FG','onTeammate3P':'在場其他四人3P','offTeamFG':'不在場球隊FG','offTeam3P':'不在場球隊3P','onOpponentFG':'在場對手FG','onOpponent3P':'在場對手3P','teamFGOnOff':'球隊FG的ON–OFF','team3POnOff':'球隊3P的ON–OFF'}
for k,label in onLabels.items():
 a,b=old['onCourtMAE'][k],new['onCourtMAE'][k];lines.append(f"| {label} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['','以下保留指定球員的實際／模擬對照。每格為「實際 → v34」，計數為per36；FG／3P為百分比。不是能力值或排名。','',
'| 球員 | 得分 | 助攻 | 失誤 | 籃板 | 抄截 | 阻攻 | FG% | 3P% |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Cade Cunningham','Victor Wembanyama','Mitchell Robinson','Stephen Curry','Neemias Queta']:
 p=byName[name];values=[]
 for k in ['pts36','ast36','tov36','reb36','stl36','blk36','fgPct','threePct']:
  if k=='reb36':a=sum(float(p[t+'_actual']) for t in ['oreb36','dreb36']);b=sum(float(p[t+'_predicted']) for t in ['oreb36','dreb36'])
  elif not p[k+'_actual'] or not p[k+'_predicted']:values.append('—');continue
  else:a,b=float(p[k+'_actual']),float(p[k+'_predicted'])
  values.append(f'{a:.2f}→{b:.2f}')
 lines.append('| '+name+' | '+' | '.join(values)+' |')
lines+=['','另輸出[分鐘與位置分層](error-strata.json)：至少500分鐘、少於500分鐘、所有正分鐘球員，分別列G／F／C／全體的MAE、帶方向偏差與加權90百分位絕對誤差。少量球員仍受來源噪音影響，投籃分母門檻與每項樣本數明列，不能把低分鐘的per36當先發能力。','',
'| 主要樣本：位置群 | 得分MAE v30→v34 | 得分偏差 v30→v34 | 助攻MAE v30→v34 | 助攻偏差 v30→v34 |','|---|---:|---:|---:|---:|']
for role in ['G','F','C']:
 values=[]
 for metric,stat in [('pts36','mae'),('pts36','signedBias'),('ast36','mae'),('ast36','signedBias')]:
  pair=[]
  for version in ['v30','rotation-space']:
   selected=[r['players'][metric][stat] for r in strata['rows'] if r['version']==version and r['sample']=='primary500' and r['roleGroup']==role];assert len(selected)==4;pair.append(sum(selected)/4)
  values.append(f'{pair[0]:+.4f}→{pair[1]:+.4f}')
 lines.append('| '+role+' | '+' | '.join(values)+' |')
lines+=['','帶方向偏差為模擬減實際；正值代表高估。上述同季重現與ON–OFF並非時間外預測或因果影響。','',
'## 球隊界線','',
f"四季平均勝場MAE {old['team']['winsMAE']:.4f}→{new['team']['winsMAE']:.4f}；淨分RMSE {old['team']['netRMSE']:.4f}→{new['team']['netRMSE']:.4f}。每季採用界線仍為既有正式對照MAE加0.5，沒有為本輪結果放寬。",'',
'| 球季 | 正式對照勝場MAE | v30 | v34 | v34界線 |','|---|---:|---:|---:|---|']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 c={x['version']:x for x in s['cells'] if x['season']==season};v={k:x['teamMetrics']['winsMAE'] for k,x in c.items()};lines.append(f"| {season} | {v['control']:.4f} | {v['v30']:.4f} | {v['rotation-space']:.4f} | {'未過' if season in failed else '通過'} |")
lines+=['','## 逐球來源驗證','',
'四季4,421場原始PBP、754,914次一般FGA逐次重讀核對，立即補籃沿用v17規則排除。所有來源FGA及助攻／非助攻進球對上原檔，未用進球挑主指標樣本。來源平均情境的每位球員均保留正自主支援；原891次零支援全部消除。另4場實際引擎3,054次機率呼叫與診斷重建完全相同，有限值檢查可擋住v32曾發生的漏傳壓迫參數。','',
'| 球季 | 舊模型零支援的非助攻FGM | v34 | 主出手分配NLL收益／FGA［95%］ |','|---|---:|---:|---:|']
for c in source['seasons']:
 lo,hi=c['fixedSourceWholeGameBootstrap95PerAttempt'];lines.append(f"| {c['season']} | {c['scores']['v30']['unsupportedSelfMakes']} | {c['scores']['v34']['unsupportedSelfMakes']} | {c['gainPerAttempt']:+.9f} [{lo:+.9f}, {hi:+.9f}] |")
lines+=['','主分配比較固定同一球員隊伍場次的FGA總數，在該場陣容間比較相對分配；正收益才代表改善。各季微小負收益、整場bootstrap區間均跨零，不能稱出手分配改善。因兩版都守恆每人終結額度，主要FGA差異本來就極小；角色／助攻旗標的差異不能靠這項主分數識別。','',
'非助攻進球與助攻標記的次分數改善，但舊模型的891次零支援使精確事件似然失效；完整檔保留的1e-12下限分數只是診斷，不能拿有限差值當準確的改善幅度。來源描述使用完整同季FG、角色、犯規等資料，沒有逐折重建；bootstrap固定來源與機制，每季2,000次，未涵蓋來源或模型不確定性，並非盲測或因果持球能力估計。','',
'## 自然位置與健康負荷配對','',
'同10人、30對手、4組seed、兩席次、兩種輪替時序、48分鐘四節及既有疲勞；各球員隊與同位置平均70隊以完全相同分鐘比較。其餘四人為不同位置形狀、每人屬性算術平均70；五張平均卡與v30完全一致。原始球員屬性不改，兩版都用各自的同分鐘基準。','',
'保留使用者政策：健康能打時的貢獻為主；出賽逐場封頂後平均約34.98分鐘，缺賽不補零，替補不外推成滿負荷。單季傷缺不扣、多季才小扣正向健康貢獻；0.10可靠度係數仍是待校準原型。以下只列健康貢獻，沒有用受傷少打分鐘取得休息紅利。','',
'| 球員 | 健康支持分鐘 | v30相對平均隊分差 | v34 | 成對變化［95%］ |','|---|---:|---:|---:|---:|']
cross=0
for p in probe['players']:
 a=next(x for x in p['arms'] if x['arm']=='supportedHealthy');v=a['pairedChange'];cross+=v['ci95'][0]<=0<=v['ci95'][1];lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v30']['mean']:+.3f} | {a['v34']['mean']:+.3f} | {v['mean']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] |")
lines+=['',f'10人的健康負荷成對變化有{cross}個95%區間跨零；完整兩種負荷結果均保留。這是固定模型模擬分差，不能讀成NBA淨效率、0–99 OVR或精確排名；區間尚未包含來源、對手選擇、負荷外推及模型不確定性。','',
'## 判定與剩餘工作','',
f'本輪14項個人MAE有{len(worse)}項退步；{len(failed)}季未過既有勝場界線。消除零支援只證明一項特定缺口已處理，不能取代全部個人、球隊與全員OVR驗證。正式模型仍為pure-oreb-turnover-time-1，最新完整實驗榜仍為v24，v34保留為未採用的機制試驗。','',
'未知無球、掩護、控球、破包夾仍為70；來源角色與進球分配不是這些技能的直接量測。短負荷面對的對手強弱、先發負荷可持續效率、非投籃疲勞與位置／組織對隊友命中率的可轉移效果仍需驗證。不能把來源自主角色當固定能力下限，或為指定球員重排榜單。原個人數據與OVR任務仍在進行。','',
'所有比賽比分、球員／球隊計數、助攻、抄截／活球失誤、球隊獨立24秒失誤、FT／犯規歸屬與在場5／本人1／隊友4份帳目通過；四季MAE、帶方向分層誤差、全582人CSV及同負荷配對區間另作獨立核對。來源條件分數、每場分數與bootstrap用另一套字典／分解公式重算，沒有只驗證檔案存在。','',
'檔案：[全582人完整對照](2025-26-player-validation.csv)、[四季分數](scores.json)、[分鐘／位置分層](error-strata.json)、[10人負荷配對](ovr-probe-summary.json)、[來源條件比較](source-comparison.json)、[來源全582人](2025-26-source-comparison.csv)、[固定機制協定](mechanism-protocol.json)、[整體核對](verification.json)。']
roleDiagnostic=read(R/'probe-role-diagnostics.json');j=next(r for r in roleDiagnostic['rows'] if r['playerId']==203999 and r['arm']=='supportedHealthy')
jAst=j['stats']['ast'];jFlow=j['mean70FrozenFlow'];jProbe=next(p for p in probe['players'] if p['playerId']==203999);jArm=next(a for a in jProbe['arms'] if a['arm']=='supportedHealthy')
detail=f"Jokić在平均70隊友的來源角色分配中，傳出機會率{jFlow['previousPass']:.4f}→{jFlow['assignedPass']:.4f}／分鐘；同32.90分鐘負荷的模擬助攻{jAst['v30PerWorkloadGame']:.3f}→{jAst['v34PerWorkloadGame']:.3f}，相對平均隊分差{jArm['v30']['mean']:+.3f}→{jArm['v34']['mean']:+.3f}。這顯示硬性來源下限會壓縮組織者可分配的傳球量；不能把全部分差變化因果歸給單一助攻項目，也不能說真實球員變差。"
lines[lines.index('## 判定與剩餘工作'):lines.index('## 判定與剩餘工作')]=[detail,'','[完整20個負荷場景的角色與13項球員計數](probe-role-diagnostics.json)皆保留。配對區間為多個球員／負荷／指標的逐項95%，未作多重比較校正。下一輪應讓自主終結與傳球的發動總量共同分配，允許自主與接球隨隊友改變，避免把來源角色當硬上限或硬下限。','']
f=R/'report.md';assert not f.exists();f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'failedWinGateSeasons':failed,'targetPlayerColumns':columns,'fullValidationSeasons':4,'seeds':3,'games':28023,'probePlayers':10,'probeGames':9600,'sourceRoleCards':2262,'sourceContextStates':270090,'sourceUnsupportedSelfMakesBefore':891,'sourceUnsupportedSelfMakesAfter':0,'worsenedIndividualMetrics':worse,'healthyProbeChangeIntervalsOverlappingZero':cross,'scope':'Fixed descriptive source-self floor hypothesis; no full OVR, skill certification or adoption.'}
(R/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(status,ensure_ascii=False,indent=2))

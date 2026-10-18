"""Report complete checks and limitations without promoting a ranking target."""
import csv,json
from pathlib import Path
R=Path('reports/player-impact-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(R/'scores.json');old=s['aggregate']['v30'];now=s['aggregate']['rotation-space'];v36=read('reports/player-impact-v36/scores.json')['aggregate']['rotation-space']
flow=read(R/'flow-audit.json');source=read(R/'source-comparison.json');probe=read(R/'ovr-probe-summary.json');transport=read(R/'transport-verification.json');cohorts=read(R/'skill-cohort-errors.json')
with (R/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);players=list(r);columns=len(r.fieldnames)
by={p['name']:p for p in players};failed=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 c={v['version']:v for v in s['cells'] if v['season']==season}
 if c['rotation-space']['teamMetrics']['winsMAE']>c['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
worse=[k for k,v in now['individualMAE'].items() if v>old['individualMAE'][k]]
lines=['# v37：保留傳球總量，另分配自主餘額','',
'完成四季各3組seed、28,023場完整／嚴格比賽，以及10人9,600場健康負荷配對。全582人保留。本輪未採用，沒有新版全員OVR。','',
'**負荷比較撤回有效性：完成後發現OVR輸入重複套用傳球成功率校正，v30與v37的實際傳球角色率不同。因此下方負荷差異與區間只保留為有混淆的歷史記錄，不能歸因於分配機制。四季球隊／個人驗證使用另一條單次校正來源路徑，資料未受此重複組裝影響。見[v38完整輸入稽核與同來源角色重跑](../player-impact-v38/report.md)。**','',
'## 改動','',
'v34至v36補回自主進攻時壓低高助攻球員的傳球量。v37把原有成功傳球矩陣的每列總量與每人終結總量保留，另加一列「自主進攻池」。池的總量等於原本剩餘自主量，以來源自主角色率作形狀先驗，與原傳球矩陣共同平衡到各終結欄。自己的傳球對角線仍為零，自主池不算助攻。','',
'嚴格可行條件：自主池為正，每位球員的傳球量小於其他四人的終結總量（數值容差為1e-10×max(1,總量)）。不能同時守住這些限制的少數陣容，明確改用來源自主／傳球先驗只對終結欄縮放，允許傳球總量改變；自主比例係數固定1，未擬合。迭代未收斂直接報錯，不能偷換成回退分支。','',
'原有角色elastic指數、原始屬性、v30機率公式、出手和疲勞支援均保留；來源情境按相同FGA與平均在場疲勞重新中心化。沒有加入v36的自主係數或傳球選擇診斷係數，也沒有依名字、名次、ON–OFF或勝場殘差調參。來源角色含同季結果與先驗，並不是無球／掩護／控球／破包夾的直接技能量測。','',
'用原v30 OVR卡片做的582個自然位置陣容檢查，全部走保留傳球分支；這份名目分配檢查未使用v37負荷測試重複組裝後的角色率，不能代表該負荷輸入的等值比較。四個隊友分別具不同位置形狀、各自屬性算術平均70。兩分支通過不修改輸入、順序互換、同比例縮放、零自助攻和終結守恆檢查。全來源五人陣容均跑過實際新分配；下表含無出手情境，另列有一般出手的情境。','',
'| 球季 | 所有情境 | 保留傳球 | 明確放寬傳球 | 有出手情境的放寬數 |','|---|---:|---:|---:|---:|']
for a in flow['seasons']:
 d=read(R/(a['season']+'-conditional-data.json'));b=a['flowBranches'];lines.append(f"| {a['season']} | {a['states']} | {b.get('fixed-pass-rows',0)} | {b.get('relaxed-source-columns',0)} | {d['flowBranches'].get('relaxed-source-columns',0)} |")
lines+=['',f"對{transport['sampledLineups']}個確定性抽樣矩陣（包含每個來源非嚴格可行五人陣容），以另一套Python對數空間公式分別重解兩分支，最大元素差{transport['maxAbsoluteDifferenceToIndependentLogSpaceSolve']:.3g}。受控對稱角色的24組／48場比賽與v30所有球隊／個人計數相同；這不代表實際輸入行為相同。",'',
'## 個人與在場數據','',
f'輸出全582人、{columns}欄，包括總量、分鐘、per36、命中率、在場球隊／其他四人／對手、OFF與ON–OFF及分母。主誤差為來源至少500分鐘，季內按來源分鐘加權、四季等權。FG／3P至少100次來源出手，FT至少50次；低分鐘與所有正分鐘樣本另外保留位置分層。全年與嚴格PBP場次的分鐘分開，不刪低分鐘球員。這些是同季重現誤差，不能直接解讀為可轉移或因果能力。','',
'| 個人MAE | v30 | v36 | v37 | 相較v30 |','|---|---:|---:|---:|---|']
labels={'pts36':'得分／36','ast36':'助攻／36','tov36':'失誤／36','stl36':'抄截／36','blk36':'阻攻／36','oreb36':'進攻籃板／36','dreb36':'防守籃板／36','fga36':'出手／36','fg3a36':'三分出手／36','fta36':'罰球出手／36','fgPct':'FG百分點','threePct':'3P百分點','ftPct':'FT百分點','tovPer100Uses':'失誤／100次終結使用'}
for k,label in labels.items():
 a,b=old['individualMAE'][k],now['individualMAE'][k];lines.append(f"| {label} | {a:.4f} | {v36['individualMAE'][k]:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['','| 在場相關MAE（百分點） | v30 | v37 |','|---|---:|---:|']
onlabels={'onTeamFG':'在場球隊FG','onTeam3P':'在場球隊3P','onTeammateFG':'在場其他四人FG','onTeammate3P':'在場其他四人3P','offTeamFG':'不在場球隊FG','offTeam3P':'不在場球隊3P','onOpponentFG':'在場對手FG','onOpponent3P':'在場對手3P','teamFGOnOff':'球隊FG ON–OFF','team3POnOff':'球隊3P ON–OFF'}
for k,label in onlabels.items():lines.append(f"| {label} | {old['onCourtMAE'][k]:.4f} | {now['onCourtMAE'][k]:.4f} |")
lines+=['','下表每格「實際→v37」，計數為per36；FG／3P為百分比。','',
'| 球員 | 得分 | 助攻 | 失誤 | 籃板 | 抄截 | 阻攻 | FG% | 3P% |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Cade Cunningham','Victor Wembanyama','Mitchell Robinson','Stephen Curry','Neemias Queta']:
 p=by[name];values=[]
 for k in ['pts36','ast36','tov36','reb36','stl36','blk36','fgPct','threePct']:
  if k=='reb36':a=sum(float(p[t+'_actual']) for t in ['oreb36','dreb36']);b=sum(float(p[t+'_predicted']) for t in ['oreb36','dreb36'])
  elif not p[k+'_actual'] or not p[k+'_predicted']:values.append('—');continue
  else:a,b=float(p[k+'_actual']),float(p[k+'_predicted'])
  values.append(f'{a:.2f}→{b:.2f}')
 lines.append('| '+name+' | '+' | '.join(values)+' |')
lines+=['','## 高專長族群','',
'探索性分層，來源至少500分鐘。門檻用實際結果，含抽樣噪音與均值回歸；族群重疊，不能當預先登記的調參目標。人數為球員球季數，誤差為四季等權、季內分鐘加權。','',
'| 族群 | 球員球季 | MAE v30→v37 | 偏差 v30→v37 | v37低估數 |','|---|---:|---:|---:|---:|']
for label,desc in [('blocksBelow1','BLK／36<1'),('blocksAtLeast1','BLK／36≥1'),('blocksAtLeast2','BLK／36≥2'),('assistsAtLeast8','AST／36≥8'),('pointsAtLeast25','PTS／36≥25')]:
 a=[x for x in cohorts['rows'] if x['cohort']==label and x['version']=='v30'];b=[x for x in cohorts['rows'] if x['cohort']==label and x['version']=='rotation-space'];avg=lambda rows,k:sum(x[k] for x in rows)/4
 lines.append(f"| {desc} | {sum(x['players'] for x in b)} | {avg(a,'mae'):.4f}→{avg(b,'mae'):.4f} | {avg(a,'signedBias'):+.4f}→{avg(b,'signedBias'):+.4f} | {sum(x['underestimatedPlayers'] for x in b)} |")
lines+=['','## 球隊與來源檢查','',
f"四季勝場MAE {old['team']['winsMAE']:.4f}→{now['team']['winsMAE']:.4f}，淨分RMSE {old['team']['netRMSE']:.4f}→{now['team']['netRMSE']:.4f}。每季沿用正式對照勝場MAE+0.5界線。",'',
'| 球季 | 正式對照 | v30 | v37 | 界線 |','|---|---:|---:|---:|---|']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 c={x['version']:x for x in s['cells'] if x['season']==season};v={k:x['teamMetrics']['winsMAE'] for k,x in c.items()};lines.append(f"| {season} | {v['control']:.4f} | {v['v30']:.4f} | {v['rotation-space']:.4f} | {'未過' if season in failed else '通過'} |")
lines+=['','四季4,421場原始PBP、270,090個陣容情境、754,914次一般FGA逐次核對；即時補籃沿用v17代理規則排除。FGA、非助攻FGM、助攻FGM對回原檔。每個來源情境的自主支援皆為正，原891次非助攻進球的零自主支援全消除；850次來自保留傳球分支，41次來自明確放寬分支。','',
'| 球季 | v30零支援非助攻FGM | v37 | 同場出手分配NLL收益／FGA［95%］ |','|---|---:|---:|---:|']
for c in source['seasons']:
 lo,hi=c['fixedSourceWholeGameBootstrap95PerAttempt'];lines.append(f"| {c['season']} | {c['scores']['v30']['unsupportedSelfMakes']} | {c['scores']['v37']['unsupportedSelfMakes']} | {c['gainPerAttempt']:+.9f} [{lo:+.9f}, {hi:+.9f}] |")
lines+=['','條件分數固定同一球員隊伍場次的FGA總量，對場內陣容分配評分；保留終結總量時，它本來就對自主／接球替代不敏感。正收益才表示這個特定分數改善。舊零支援事件的精確似然無定義；1e-12下限僅供次要診斷，沒有加入引擎。2,000次整場bootstrap固定來源與機制，未包含來源／模型不確定性。完整同季描述含結果，並非盲測。','',
'## 健康負荷與傷病政策','',
'主要看健康能打時的貢獻。逐場出賽分鐘封頂後，只對實際出賽場次取平均，缺賽不補零；共同標準沿用舊三季推得34.98分鐘。替補依實際承擔分鐘測試，不把短時間per36直接外推成先發。單季明確傷病不扣分，至少兩季有明確傷病證據才按第二高傷病比例×0.10，小幅折減正向健康貢獻；0／0.05／0.10敏感度保留。缺賽不等於傷病，此係數是待校準評分政策，非醫療風險。','',
'兩版均使用自然位置、四名不同位置平均70隊友、30對手、4組seed、兩席次、兩輪替時序、48分鐘四節與既有疲勞，另有同分鐘平均70基準。**但是實際球員與對手的傳球角色率不同，負荷版本比較有混淆，不能宣稱傳球量已保留。** 下表保留有問題的歷史數字，未施加傷病可靠度折減，不能用來選模型或排名。','',
'| 球員 | 支持分鐘 | v30 | v37 | 成對差［95%］ |','|---|---:|---:|---:|---:|']
cross=0
for p in probe['players']:
 a=next(x for x in p['arms'] if x['arm']=='supportedHealthy');d=a['pairedChange'];cross+=d['ci95'][0]<=0<=d['ci95'][1];lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v30']['mean']:+.3f} | {a['v37']['mean']:+.3f} | {d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] |")
lines+=['',f'{cross}/10個健康負荷版本差區間跨零。區間是固定模型的分層配對模擬區間，不是實際NBA效率、OVR或名次，未包含來源／負荷外推／模型不確定性；20個負荷場景及逐項計數均未校正多重比較。全分差變化不能因果歸給助攻一項。','',
'## 判定','',
f'14項個人MAE相較v30有{len(worse)}項退步，{len(failed)}季未過勝場界線。正式模型仍為pure-oreb-turnover-time-1，最新完整實驗榜仍為v24；v37不採用。全員OVR、後衛可轉移價值、對手強弱與長負荷效率仍需驗證，目標尚未完成。無球、掩護、控球、破包夾仍有70預設，不能宣稱已由角色率量測補齊。','',
'全部比賽帳目、球員／球隊計數、助攻、抄截／活球失誤、FT／犯規、在場5／本人1／隊友4份帳目核對。四季14項個人與10項在場MAE、582人CSV、144個位置分鐘分層、40個專長族群、20個配對場景13項計數與區間另以獨立公式重算。','',
'檔案：[582人176欄](2025-26-player-validation.csv)、[四季分數](scores.json)、[位置分鐘分層](error-strata.json)、[專長族群](skill-cohort-errors.json)、[配對負荷](ovr-probe-summary.json)、[13項配對計數](probe-role-diagnostics.json)、[來源比較](source-comparison.json)、[機制協定](mechanism-protocol.json)、[獨立矩陣核對](transport-verification.json)、[整體驗證](verification.json)。']
f=R/'report.md';assert not f.exists();f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'failedWinGateSeasons':failed,'targetPlayerColumns':columns,'fullValidationSeasons':4,'seeds':3,'games':28023,'probePlayers':10,'probeGames':9600,'probeComparisonValid':False,'probeInvalidityReason':'Repeated non-idempotent creation-success correction changes actual source passing roles across OVR variants. Numeric ledgers retained; interpretation withdrawn. Canonical-role rerun in v38.','fullSeasonInputsAffectedByRepeatedOvrAssembly':False,'sourceRoleCards':2262,'sourceContextStates':270090,'sourceUnsupportedSelfMakesBefore':891,'sourceUnsupportedSelfMakesAfter':0,'worsenedIndividualMetrics':worse,'healthyProbeChangeIntervalsOverlappingZero':cross,'scope':'Fixed passer rows plus separate own pool; complete source/full-game validation. Original workload comparison confounded by repeated input correction, withdrawn. No full OVR or adoption.'}
(R/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(status,ensure_ascii=False,indent=2))

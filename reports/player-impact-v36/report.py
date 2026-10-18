"""Report conditional calibration separately from general simulation and OVR."""
import csv,json
from pathlib import Path
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(R/'scores.json');a=s['aggregate']['v30'];b=s['aggregate']['rotation-space'];v35=read('reports/player-impact-v35/scores.json')['aggregate']['rotation-space']
fit=read(R/'marked-fit.json');fv=read(R/'marked-fit-verification.json');src=read(R/'source-comparison.json');probe=read(R/'ovr-probe-summary.json');strata=read(R/'error-strata.json')
cohorts=read(R/'skill-cohort-errors.json');passer=read(R/'passer-choice-diagnostic.json');pv=read(R/'passer-choice-verification.json')
with (R/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);players=list(r);cols=len(r.fieldnames)
assert len(players)==582;names={p['name']:p for p in players};failed=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cells={c['version']:c for c in s['cells'] if c['season']==season}
 if cells['rotation-space']['teamMetrics']['winsMAE']>cells['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
worse=[k for k,v in b['individualMAE'].items() if v>a['individualMAE'][k]]
lines=['# v36：以逐球標記校準自主與接球進攻','',
'**完成四季各3組seed、28,023場完整／嚴格比賽，及10人9,600場健康負荷配對；全582人保留。本版尚未採用，沒有新版全員OVR。**','',
'## 為什麼改與如何估計','',
'v35把自主與傳球合為共同發動量，仍壓縮組織者。v36移除這項發動端總量限制，只保留每人原有終結機會。來源自主量與傳球×其他人的相對接球需求形成正的先驗矩陣；對角線為自主，其他格才是傳球。對各接球者的終結預算分別投影，對角線乘一個全聯盟共用正係數。沒有固定自主上限／下限，也不按球員名字或位置加分。','',
f'只用2022–23至2024–25估計一個log係數：自主比例係數 **{fit["selfScale"]:.6f}**；五個整場留出折的估計範圍{min(x["selfScale"] for x in fit["folds"]):.6f}–{max(x["selfScale"] for x in fit["folds"]):.6f}。2025–26未參與選參數。目標是固定球員／陣容出手數下，「未進、自主進球、由各個其他球員助攻進球」的精確多類別NLL；沒有機率下限或名字／OVR／ON–OFF／勝場殘差擬合。','',
'此估計使用凍結v30來源機率與情境，候選執行時再重算來源情境並另行評分，沒有把估計分數冒稱最終模型分數。來源卡仍含完整同季統計，整場留出並未逐折重建來源卡；不是盲測或因果能力。對角線比例只是描述性校準，不能當成已量得的控球技術或生理負荷。','',
'| 凍結v30情境的條件標記比較 | 相對係數1的NLL收益／FGA | 固定來源整場bootstrap 95% |','|---|---:|---:|']
for x in fv['seasons']:
 lo,hi=x['fixedSourceWholeGameBootstrap95'];lines.append(f"| {x['season']} | {x['gainPerFga']:+.8f} | [{lo:+.8f}, {hi:+.8f}] |")
lines+=['','正收益代表較低NLL。2025–26收益很小，區間跨零；區間固定來源與估計參數，不含模型／參數不確定性。這張表比較同一個新機制的係數1與估計係數，並非對舊v30引擎的完整改進證明。[582人條件標記表](2025-26-conditional-mark-scores.csv)另保留581名有嚴格PBP來源者，沒有PBP的一人留空。','',
'四季4,421場原始逐球、270,090個陣容情境、754,914次一般出手及助攻者身分已獨立重讀核對。另以直接類別機率重算全部NLL，用解析分數方程求根核對全樣本與五折共六次估計。','',
'## 個人數據與在場表現','',
f'全582人、{cols}欄包含實際／模擬整季總量、分鐘、per36、FG／3P／FT、在場球隊／其他四人／對手、OFF與ON–OFF及其分母。主MAE以真實至少500分鐘球員，季內按真實分鐘加權，四季等權；FG／3P至少100次來源出手，FT至少50次。全季與嚴格PBP分鐘分開，低分鐘球員未刪除。','',
'| 四季MAE | v30 | v35 | v36 | 相較v30 |','|---|---:|---:|---:|---|']
labels={'pts36':'得分／36','ast36':'助攻／36','tov36':'失誤／36','stl36':'抄截／36','blk36':'阻攻／36','oreb36':'進攻籃板／36','dreb36':'防守籃板／36','fga36':'出手／36','fg3a36':'三分出手／36','fta36':'罰球出手／36','fgPct':'FG百分點','threePct':'3P百分點','ftPct':'FT百分點','tovPer100Uses':'失誤／100次終結使用'}
for k,label in labels.items():
 before,now=a['individualMAE'][k],b['individualMAE'][k];lines.append(f"| {label} | {before:.4f} | {v35['individualMAE'][k]:.4f} | {now:.4f} | {'改善' if now<before else '退步'} |")
lines+=['','| 在場相關MAE（百分點） | v30 | v36 |','|---|---:|---:|']
onLabels={'onTeamFG':'在場球隊FG','onTeam3P':'在場球隊3P','onTeammateFG':'在場其他四人FG','onTeammate3P':'在場其他四人3P','offTeamFG':'不在場球隊FG','offTeam3P':'不在場球隊3P','onOpponentFG':'在場對手FG','onOpponent3P':'在場對手3P','teamFGOnOff':'球隊FG的ON–OFF','team3POnOff':'球隊3P的ON–OFF'}
for k,label in onLabels.items():lines.append(f"| {label} | {a['onCourtMAE'][k]:.4f} | {b['onCourtMAE'][k]:.4f} |")
lines+=['','以下為「實際→v36」，計數per36，命中率百分比；不是OVR或排名。','',
'| 球員 | 得分 | 助攻 | 失誤 | 籃板 | 抄截 | 阻攻 | FG% | 3P% |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Cade Cunningham','Victor Wembanyama','Mitchell Robinson','Stephen Curry','Neemias Queta']:
 p=names[name];values=[]
 for k in ['pts36','ast36','tov36','reb36','stl36','blk36','fgPct','threePct']:
  if k=='reb36':actual=sum(float(p[t+'_actual']) for t in ['oreb36','dreb36']);pred=sum(float(p[t+'_predicted']) for t in ['oreb36','dreb36'])
  elif not p[k+'_actual'] or not p[k+'_predicted']:values.append('—');continue
  else:actual,pred=float(p[k+'_actual']),float(p[k+'_predicted'])
  values.append(f'{actual:.2f}→{pred:.2f}')
 lines.append('| '+name+' | '+' | '.join(values)+' |')
lines+=['','[144個位置／分鐘分層](error-strata.json)包含G／F／C／全體，至少500分鐘、少於500分鐘、所有正分鐘三組，列出每項MAE、模擬減實際偏差、加權90百分位誤差與有效分母。同季在場與ON–OFF誤差不是因果影響。','',
'## 平均誤差掩蓋的高產量球員','',
'另探索實際per36表現的尾端分組；只取至少500分鐘，季內依真實分鐘加權，四季等權。這是看過誤差後的描述性檢查，分組根據實際結果，仍含抽樣噪音與向平均回歸，不能當因果檢定或調榜目標。','',
'| 實際表現組 | 球員季數 | v30 MAE | v36 MAE | v36偏差 | v36低估數 |','|---|---:|---:|---:|---:|---:|']
for key,label in [('blocksBelow1','阻攻／36小於1'),('blocksAtLeast1','阻攻／36至少1'),('blocksAtLeast2','阻攻／36至少2'),('assistsAtLeast8','助攻／36至少8'),('pointsAtLeast25','得分／36至少25')]:
 old=[r for r in cohorts['rows'] if r['version']=='v30' and r['cohort']==key];now=[r for r in cohorts['rows'] if r['version']=='rotation-space' and r['cohort']==key];assert len(old)==len(now)==4
 lines.append(f"| {label} | {sum(x['players'] for x in now)} | {sum(x['mae'] for x in old)/4:.4f} | {sum(x['mae'] for x in now)/4:.4f} | {sum(x['signedBias'] for x in now)/4:+.4f} | {sum(x['underestimatedPlayers'] for x in now)} |")
lines+=['','[完整分組與球員季](skill-cohort-errors.json)顯示高阻攻組並非只有Wembanyama低估；原v30也有同方向問題。現有阻攻先由固定區域基率與屬性調整產生球隊事件，再按個人率分配，這是下一步需查驗的機制。阻攻目前是既有投失的分解；防守FG曲線已含阻攻影響，不能直接再扣一次命中率。','',
'另外用相同來源預測，獨立檢查「已知這是被助攻進球時，助攻該記給誰」：舊beta只估計簡化選擇，本輪把實際接球者、陣容與進球機率納入。此診斷沒有改動v36。','',
f"較早三季的條件身分估計beta {passer['oldBeta']:.6f}→{passer['diagnosticFit']['beta']:.6f}；五折整場留出另保留。2025–26條件選擇NLL每次被助攻進球收益{pv['seasons'][-1]['gainPerAssistedMake']:+.8f}，固定來源整場bootstrap 95% [{pv['seasons'][-1]['fixedSourceWholeGameBootstrap95'][0]:+.8f}, {pv['seasons'][-1]['fixedSourceWholeGameBootstrap95'][1]:+.8f}]。這只支持小幅助攻歸屬修正的後續試驗，不能證明總助攻量、組織能力或OVR提高；不能用它掩蓋高助攻組總量被低估。見[診斷](passer-choice-diagnostic.json)與[獨立直接機率核對](passer-choice-verification.json)。",'',
'## 球隊界線','',
f"四季勝場MAE {a['team']['winsMAE']:.4f}→{b['team']['winsMAE']:.4f}，淨分RMSE {a['team']['netRMSE']:.4f}→{b['team']['netRMSE']:.4f}。每季門檻仍為正式對照勝場MAE加0.5；沒有放寬。",'',
'| 球季 | 正式對照 | v30 | v36 | v36門檻 |','|---|---:|---:|---:|---|']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cells={x['version']:x for x in s['cells'] if x['season']==season};vals=[cells[v]['teamMetrics']['winsMAE'] for v in ['control','v30','rotation-space']];lines.append(f"| {season} | {vals[0]:.4f} | {vals[1]:.4f} | {vals[2]:.4f} | {'未過' if season in failed else '通過'} |")
lines+=['','## 重算情境後的來源檢查','',
'下表比較候選最終機率與v30；同場相對出手分配固定每個球員／隊伍／場次FGA總量，對自主與傳球替代本來就不敏感。','',
'| 球季 | 舊零自主支援的非助攻FGM | v36 | 條件出手NLL收益／FGA［95%］ |','|---|---:|---:|---:|']
beforeZero=afterZero=0
for x in src['seasons']:
 old=x['scores']['v30']['unsupportedSelfMakes'];new=x['scores']['v36']['unsupportedSelfMakes'];beforeZero+=old;afterZero+=new;lo,hi=x['fixedSourceWholeGameBootstrap95PerAttempt'];lines.append(f"| {x['season']} | {old} | {new} | {x['gainPerAttempt']:+.9f} [{lo:+.9f}, {hi:+.9f}] |")
lines+=['','來源零支援消失只證明特定結構問題修正。舊模型零支援使某些標記的精確似然失效，次指標的1e-12下限分數只是診斷，沒有把下限加進引擎。來源比較、bootstrap與582人來源表另獨立重算。','',
'## 健康負荷貢獻','',
'10人、30對手、4組seed、兩席次、兩種輪替時序，完整48分鐘四節、疲勞開啟。球員只放自然位置，其他四人分別是不同位置形狀、屬性算術平均70的隊友；原始球員屬性與平均卡不變。各版分別對照完全相同分鐘／輪替／對手／seed的同位置平均70基準。','',
'主要看健康可上場時的貢獻；每次出賽分鐘逐場封頂後平均，舊三季資料給出共同34.98分鐘標準，缺賽不補零。替補不靠per36外推先發負荷，單季傷病不扣、多季才小幅折減正向健康貢獻；0.10可靠度權重仍為未校準政策，未作為排名擬合係數。傷缺不換成每場更少分鐘，以免休息反而加分。','',
'| 球員 | 支持分鐘 | v30相對平均隊分差 | v36 | 成對變化［95%］ |','|---|---:|---:|---:|---:|']
cross=0
for p in probe['players']:
 arm=next(x for x in p['arms'] if x['arm']=='supportedHealthy');change=arm['pairedChange'];cross+=change['ci95'][0]<=0<=change['ci95'][1];lo,hi=change['ci95'];lines.append(f"| {p['name']} | {arm['minutes']:.2f} | {arm['v30']['mean']:+.3f} | {arm['v36']['mean']:+.3f} | {change['mean']:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
lines+=['',f'10人的健康負荷版本差有{cross}個區間跨零；僅含固定模型模擬誤差，不含來源／模型／負荷外推不確定性，未校正多重比較，不能當全員榜。[全部20場景的13項球員計數與區間](probe-role-diagnostics.json)保留，不把整個分差變化歸因給單一助攻項目。','',
'## 判定與未完成範圍','',
f'相較v30，14項個人誤差有{len(worse)}項退步，{len(failed)}季未過勝場門檻。逐球條件標記、正自主支援、守恆、機率一致性都不能替代完整個人／球隊／OVR驗證。正式模型仍是pure-oreb-turnover-time-1，最新完整實驗榜仍為v24；本版未採用、沒有新版全員OVR，目標尚未完成。','',
'無球、掩護、控球、破包夾仍有70預設，來源角色不是這些技能的直接量測。對手強弱、短時間效率移轉到先發負荷、非投籃疲勞、空間影響的可轉移性仍未證實。不能依SGA、Luka、Jokić或肉C的理想名次調參數。','',
'驗證包含全比賽比分／個人／球隊帳目，助攻與進球上限，抄截／活球失誤，獨立24秒失誤，FT／犯規歸屬；在場5／本人1／其他隊友4份帳目，以及四季所有誤差、全582人176欄、位置／分鐘分層、配對區間均獨立重算。受控角色下48場與v30計數相同，實際機率閉包逐項比對；這些是實作正確性證據，不是模型已精準的證明。','',
'檔案：[全582人176欄](2025-26-player-validation.csv)、[四季分數](scores.json)、[負荷貢獻](ovr-probe-summary.json)、[標記估計協定](marked-protocol.json)、[標記估計核對](marked-fit-verification.json)、[來源計數核對](marked-data-verification.json)、[最終核對](verification.json)。']
p=R/'report.md';assert not p.exists();p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'failedWinGateSeasons':failed,'targetPlayerColumns':cols,'fullValidationSeasons':4,'seeds':3,'games':28023,'probePlayers':10,'probeGames':9600,'sourceRoleCards':2262,'sourceContextStates':270090,'sourceUnsupportedSelfMakesBefore':beforeZero,'sourceUnsupportedSelfMakesAfter':afterZero,'worsenedIndividualMetrics':worse,'healthyProbeChangeIntervalsOverlappingZero':cross,'fittedGlobalSelfScale':fit['selfScale'],'scope':'Terminal-column positive prior with older-only conditional mark calibration; no full OVR or adoption.'}
(R/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2))

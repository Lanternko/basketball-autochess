"""Render the source-self restriction experiment without equating source roles with ability caps."""
import csv
import json
from pathlib import Path
ROOT=Path('reports/player-impact-v31');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
s=read(ROOT/'scores.json');old=s['aggregate']['v30'];new=s['aggregate']['rotation-space']
probe=read(ROOT/'ovr-probe-summary.json');audit=read(ROOT/'flow-audit.json')
with (ROOT/'2025-26-player-validation.csv').open(encoding='utf-8-sig') as f:r=csv.DictReader(f);rows=list(r);cols=len(r.fieldnames)
assert len(rows)==582
lines=['# v31：未收到的終結機會，是否應自動變成自主出手？','',
'**四季各3組seed、28,023場完整／嚴格比賽，以及10名球員9,600場負荷配對完成。這是模型假設試驗，沒有採用，也沒有新版全員OVR。**','',
'## 要驗證的假設','',
'v30及之前的傳球分配會先安排接球者，再把每人的「名目終結機會 − 實際收到的機會」全部當成自己的自主出手機會。因此隊友較少創造時，模型會自動假設接球者完全補回自主出手。這是先前未驗證的角色適應假設，並不是資料已證明的能力。','',
'本輪另測保留來源自主角色的版本：`自主機會 = min(來源自主機會, 名目終結機會 − 實際收到的機會)`。來源角色量、傳球矩陣、攔截、屬性與v30投籃／防守公式不改；只有不足的接球機會不再全部自動補成自主機會。來源角色先沿用相同elastic分配，再套這項限制，沒有加上後衛或特定名字的係數。','',
'**來源自主出手量不是能力上限。** 球員可能在隊友不在時增加持球與出手，本試驗的限制也可能太強。不能因為舊公式有假設，就把相反的假設直接當成修正成功。來源角色中還有收縮先驗、同季重建與助攻轉機會的估計，並非每次真實持球的直接量測。','',
'2262個球員季／2581張隊伍名單卡的原屬性、角色、選項、賽程和暴露均保留；270,090個來源情境重算校準，來源分鐘、FGA與能量相同。來源傳球矩陣及邊際逐個實際五人核對不變。以下是2025–26的模型機會率，單位為每在場分鐘，不能讀成真實FGA。','',
'| 球員 | 真實輪替：原分配自主 | 真實輪替：受限自主 | 平均70隊友：原自主 | 平均70隊友：受限自主 |','|---|---:|---:|---:|---:|']
source={p['playerId']:p for ss in audit['seasons'] if ss['season']=='2025-26' for p in ss['players']}
mean={p['playerId']:next(r for r in p['rows'] if r['playerId']==p['playerId']) for p in audit['mean70']}
for pid in [1629011,1641705,1630595,1628983,1629029,203999,201939]:
 a=source[pid];b=mean[pid];lines.append(f"| {a['name']} | {a['rates']['previousAssignedSelf']:.4f} | {a['rates']['supportedSelf']:.4f} | {b['previousAssignedSelf']:.4f} | {b['supportedSelf']:.4f} |")
lines+=['', 'Curry、Wemby在平均70隊友下的自主機會反而受限制較多；Robinson變化較小。這已反駁「補回自主機會只在放大替補中鋒」的簡單解釋，必須保留這個結果。','',
'## 四季個人與在場數據','',
'使用同季來源的重現驗證，並非時間外預測或因果ON–OFF。真實至少500分鐘為主要誤差樣本，季內依真實分鐘加權，再四季等權。計數按各自分鐘換算每36分鐘；FG／3P至少100次來源出手、FT至少50次；在場／不在場每個比率至少100次來源出手。所有低分鐘球員仍輸出，沒有靠刪人改善誤差。','',
f'CSV保留全582人、{cols}欄：個人總量與分鐘、per36、FG／3P／FT、在場球隊／其他四人／對手、OFF與ON–OFF、分母、防守來源與本輪自主分配。全年和嚴格PBP範圍分開，模擬總量／分鐘為三組seed平均。','',
'| MAE | v30 | v31 | 方向 |','|---|---:|---:|---|']
labels={'pts36':'得分／36','ast36':'助攻／36','tov36':'失誤／36','stl36':'抄截／36','blk36':'阻攻／36','oreb36':'進攻籃板／36','dreb36':'防守籃板／36','fga36':'出手／36','fg3a36':'三分出手／36','fta36':'罰球出手／36','fgPct':'FG百分點','threePct':'3P百分點','ftPct':'FT百分點','tovPer100Uses':'失誤／100次終結使用'}
for k,label in labels.items():
 a,b=old['individualMAE'][k],new['individualMAE'][k];lines.append(f"| {label} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['','| 在場相關MAE（百分點） | v30 | v31 | 方向 |','|---|---:|---:|---|']
labels={'onTeamFG':'在場球隊FG','onTeam3P':'在場球隊3P','onTeammateFG':'在場其他四人FG','onTeammate3P':'在場其他四人3P','offTeamFG':'不在場球隊FG','offTeam3P':'不在場球隊3P','onOpponentFG':'在場對手FG','onOpponent3P':'在場對手3P','teamFGOnOff':'球隊FG的ON–OFF','team3POnOff':'球隊3P的ON–OFF'}
for k,label in labels.items():
 a,b=old['onCourtMAE'][k],new['onCourtMAE'][k];lines.append(f"| {label} | {a:.4f} | {b:.4f} | {'改善' if b<a else '退步'} |")
lines+=['',f"四季勝場MAE {old['team']['winsMAE']:.4f}→{new['team']['winsMAE']:.4f}；淨分RMSE {old['team']['netRMSE']:.4f}→{new['team']['netRMSE']:.4f}。採用界線仍為每季正式對照MAE加0.5，不依本輪結果放寬。",'',
'| 球季 | 正式對照勝場MAE | v30 | v31 | v31採用界線 |','|---|---:|---:|---:|---|']
failed=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cs={c['version']:c for c in s['cells'] if c['season']==season};v={k:c['teamMetrics']['winsMAE'] for k,c in cs.items()};bad=v['rotation-space']>v['control']+.5
 if bad:failed.append(season)
 lines.append(f"| {season} | {v['control']:.4f} | {v['v30']:.4f} | {v['rotation-space']:.4f} | {'未過' if bad else '通過'} |")
lines+=['','## 同負荷成對實驗','',
'同一批10人、30對手、4組seed、兩席次和兩種輪替時序；每場球員隊都與同位置平均70隊作相同分鐘的比較。48分鐘四節、有輪替及既有疲勞；球員只放自然位置，其他四位置為不同形狀且各自屬性算術平均70的卡。新版和v30用各自相同條件的基準，所以隊友／基準隊受到新機制的連帶作用也包括在版本差中。','',
'健康負荷仍是v29的出賽逐場封頂後平均，約34.98分鐘為共同標準；缺賽不補零，短時間替補不外推滿負荷。單季傷缺不扣、多季才小幅折減正向健康貢獻的政策不變。下表先列健康貢獻，沒有加傷缺轉分鐘的休息紅利。','',
'單位為相對平均隊分差，不是NBA淨效率或0–99 OVR。95%區間只涵蓋固定模型下的分層配對模擬抽樣，不含來源、參數、負荷和模型不確定性。','',
'| 球員 | 支持分鐘 | v30健康貢獻 | v31健康貢獻 | 成對變化［95%］ |','|---|---:|---:|---:|---:|']
for p in probe['players']:
 a=next(a for a in p['arms'] if a['arm']=='supportedHealthy');d=a['pairedChange'];lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v30']['mean']:+.3f} | {a['v31']['mean']:+.3f} | {d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] |")
lines+=['',
'這10人的兩種負荷版本差區間全部跨零，不能宣稱某個球員改善，也不能拿均值排精確名次。Robinson仍高於Cade，Curry健康估計仍略為負；Wemby的均值亦下降，沒有證據宣稱肉C／後衛偏差已修完。','',
'## 核對及採用決定','',
'全部比賽的比分、球員／球隊帳目、抄截／活球失誤、球隊獨立24秒失誤、助攻與投籃以及在場5／本人1／隊友4份帳目通過。2262個來源球員季、270,090個情境及582個平均隊友陣容完成限制與來源不變核對。控制角色使新舊自主分配相同時，24組／48場的全部球員與球隊計數精確相同。五個位置平均卡與v30完全一致，所有原始球員屬性均相同。配對均值、標準誤與區間另外重算；核對能證明帳目一致，不能證明模型正確。','']
worse=[k for k,v in new['individualMAE'].items() if v>old['individualMAE'][k]]
lines.append(f"本輪有{len(worse)}項個人MAE退步，{len(failed)}季未過勝場門檻。無論有限樣本均值的名次方向如何，都不足以採用這個限制。正式模型仍為pure-oreb-turnover-time-1，v31保留為未採用假設試驗。")
lines+=['',
'下一步需要用真實隊友變動時的自主終結資料，檢查補償幅度；不能再在「全部自動補回」和「來源量直接當上限」之間憑排名選一個。接球投、運球急停與官方助攻／potential assist的定義不同，也不能把追蹤模式直接等同引擎的助攻旗標。[官方統計詞彙](https://www.nba.com/stats/help/glossary)可核對其欄位定義。','',
'最新完整全員OVR仍為v24，沒有把10人試驗冒稱582人排名。未量測的無球、掩護、控球、破包夾仍有70預設，來源對手／教練選擇、長時間非投籃疲勞及持球模式的能力拆分仍未解。原個人數據與OVR修正目標持續進行。','',
'檔案：[582人176欄](2025-26-player-validation.csv)、[四季分數](scores.json)、[10人配對](ovr-probe-summary.json)、[來源角色分配](flow-audit.json)、[核對](verification.json)、[來源核對](source-verification.json)。']
(ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
status=dict(officialModelAdopted=False,goalComplete=False,fullOvrThisVersion=False,latestCompleteOvrVersion=24,
 failedWinGateSeasons=failed,targetPlayerColumns=cols,fullValidationSeasons=4,seeds=3,games=28023,probePlayers=10,probeGames=9600,
 sourceRoleCards=2262,sourceContextStates=270090,sourceSelfRestrictionAdopted=False,worsenedIndividualMetrics=worse,
 scope='Hypothesis experiment; source self rate is not a demonstrated capability maximum. All 10 paired version-change intervals overlap zero.')
(ROOT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(status,ensure_ascii=False,indent=2))

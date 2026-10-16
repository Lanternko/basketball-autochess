"""Report completed diagnostics without adopting or assigning sample ranks."""
import json,hashlib
from pathlib import Path
root=Path('reports/player-impact-v19');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
a=read('reports/player-impact-v14/scores.json');b=read(root/'scores.json');bench=read(root/'ovr-checkpoint.json');protocol=read(root/'validation-protocol.json')
lines=[]
def add(x=''):lines.append(x)
add('# 2025–26個人數據與OVR：助攻參考及罰球分類修正')
add()
add('**四季各3 seed及代表球員OVR已完成，正式模型仍未更換。** 助攻明顯改善，罰球來源範圍重疊已修正；球隊勝場界線與個人估值仍未通過，不能發布完成版Top50。目標季為2025–26。')
add()
add('四季2,262個球員季，完整賽程14,760場、嚴格在場子集13,263場；主樣本至少500實際分鐘、按實際分鐘加權，各季等權。計數為各自分鐘的每36分鐘，FG/3P門檻100次實際出手。四季資料都已看過，屬同季重現與機制檢查，並非盲測、事前預測或個人因果價值。')
add()
add('## 本次處理的來源問題')
add()
add('1. 原投籃情境按上場秒數平均，改成每人每區域實際新出手加權；自主／接球混合也改按記錄FGA生存率條件化。')
add('2. 組織機會原用舊的全聯盟成功率換算，與更新後接球者機率不一致。改用來源真實輪替推算的接球成功率，60分鐘聯盟先驗，並重算角色變更後的情境。不是以球員名字、OVR、ON–OFF或個人模擬殘差調整。')
add('3. 投籃犯規原以全部FTA/FGA作目標，非投籃犯規卻仍另外產生罰球。現在投籃流程只用分類shooting的FTA；非投籃犯規接觸率由來源事件數估計，保留原罰則流程。小樣本先驗33.0602個FGA由2022–25五折比賽分割選出；FTA成串出現，工作分數不提供獨立試驗或後驗信賴區間。')
add()
add('投籃、非投籃、技術與未連結FT逐季／逐人守恆；未連結者約0.25–0.31%，保留標記並排除投籃目標。同秒多個FGA匹配採保守接觸率下界，沒有把模糊事件當確定追蹤。原始能力值與四項未知70未更改。')
add()
add('## 與v14相同三組seed比較')
add()
add('| 四季平均絕對誤差 | v14 | 本次v19 |')
add('|---|---:|---:|')
labels={'pts36':'得分','ast36':'助攻','tov36':'失誤','stl36':'抄截','blk36':'阻攻','oreb36':'進攻籃板','dreb36':'防守籃板','fga36':'出手','fta36':'罰球出手','fgPct':'FG%（百分點）','threePct':'3P%（百分點）'}
for k,label in labels.items():add(f"| {label} | {a['aggregate']['rotation-space']['individualMAE'][k]:.3f} | {b['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
add()
add('| 在場相關平均誤差（百分點） | v14 | 本次v19 |')
add('|---|---:|---:|')
for k,label in [('onTeamFG','在場團隊FG'),('onTeammateFG','排除本人的隊友FG'),('onTeam3P','在場團隊3P'),('onTeammate3P','排除本人的隊友3P'),('teamFGOnOff','團隊FG ON–OFF'),('team3POnOff','團隊3P ON–OFF')]:add(f"| {label} | {a['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} | {b['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add()
add('在場/隊友/本人帳本逐場守恆：每個團隊出手有5份ON、4份隊友及1份本人。OFF限相同球隊且球員有出賽的同一組比賽；仍受隊友、對手與輪替混雜。控制個人失誤另扣原掛到個人的24秒違例，使兩版都採球隊失誤口徑；控制球隊總量與比分不變。')
add()
add('## 球隊勝場界線')
add()
add('| 球季 | 控制勝場MAE | v19 | 差 | 不超過+0.5 |')
add('|---|---:|---:|---:|---|')
failed=[]
for season in protocol['seasons']:
 old=next(c for c in b['cells'] if c['season']==season and c['version']=='control')['teamMetrics'];new=next(c for c in b['cells'] if c['season']==season and c['version']=='rotation-space')['teamMetrics'];delta=new['winsMAE']-old['winsMAE'];passed=delta<=.5
 if not passed:failed.append(season)
 add(f"| {season} | {old['winsMAE']:.3f} | {new['winsMAE']:.3f} | {delta:+.3f} | {'通過點估計' if passed else '未通過'} |")
add()
add('三組seed的點估計不能當等效證明；尚未完成本版本20 seed擴大確認。各季獨立判斷，不以四季平均掩蓋失敗。')
macro={}
for folder,label in [(Path('reports/player-impact-v14'),'v14'),(root,'v19')]:
 sums={k:0. for k in ['pts','ast','fga','fgm','fta','ftm','fg3m','fg3a']}
 for seed in protocol['seeds']:
  run=read(folder/f'runs/2025-26-rotation-space-full-{seed}.json')
  for t in run['teams']:
   for k in sums:sums[k]+=t['stats'][k]/(len(protocol['seeds'])*2460)
 macro[label]=sums
bundle=read('reports/defense-tenth/step4-t0/2025-26/bundle.json');macro['actual']={k.lower():sum(p['observed'][k] for t in bundle['league']['teams'] for p in t['roster'])/2460 for k in ['PTS','AST','FGA','FGM','FTA','FTM','FG3M','FG3A']}
(root/'2025-26-macro-comparison.json').write_text(json.dumps(macro,indent=2),encoding='utf-8')
add()
add('| 2025–26每隊每場，3 seed | 官方 | v14 | v19 |')
add('|---|---:|---:|---:|')
for k in ['pts','ast','fga','fta']:add(f"| {k} | {macro['actual'][k]:.3f} | {macro['v14'][k]:.3f} | {macro['v19'][k]:.3f} |")
add()
add('助攻與罰球總量接近不代表個人全部準確：得分仍偏高，在場隊友FG比v14退步，源於命中率、出手分配與來源情境仍需進一步驗證。')
add()
add('## OVR代表樣本')
add()
add('31位球員與五個位置基準各2,400場。每人僅放自然位置，其他四位為不同位置形狀且屬性算術平均70的隊友；30隊對手、主客順序互換，同等14.4分鐘，不使用出場分鐘倍數。真實球員、對手與合成隊友均改為相同投籃犯規FTA口徑，合成隊友另按位置池更新組織率；96場驗證快取與未快取的所有比分及個人計數完全相同。')
add()
add('| 球員 | 此固定基準勝率 | 模擬邊際95%區間 |')
add('|---|---:|---:|')
for pid in [1628983,1629029,203999,201939,1629674]:
 r=next(r['result'] for r in bench['rows'] if r['job'].get('id')==pid);add(f"| {r['name']} | {100*r['winRate']:.2f}% | {100*r['ci95'][0]:.2f}–{100*r['ci95'][1]:.2f}% |")
add()
add('這是勝率機制抽樣，沒有本版本582人全員榜，無法聲稱Jokić仍前20或有幾位後衛進前50。Queta仍高於Jokić，個人估值問題未解決。區間只涵蓋模擬亂數，沒有包含來源估計、缺測或模型選擇不確定性，也不是排名區間。先前v14全員榜僅供舊版診斷，不能套給本版。')
add()
add('## 剩餘問題與檔案')
add()
add('球隊勝率界線、個人命中率與出手角色、在場隊友FG及低分鐘外推仍待修正；技術罰球沒有完整來源事件機制，v18的組織成功率參考仍基於修正前罰球生存率。未知的無球、掩護、控球、破包夾仍為70，來源沒有速度量測；產量／角色代理不能冒稱實測能力。')
add()
add('正式仍為pure-oreb-turnover-time-1，沒有把不同引擎混用成已通過的OVR。完整資料：`scores.json`、`all-players.csv`、`all-players-on-court.csv`、`validation-protocol.json`、`validation-manifest.json`、`ovr-protocol.json`、`ovr-checkpoint.json`、`diagnostic.md`。')
(root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(root/'status.json').write_text(json.dumps({'version':'source-ft-categories-19','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'teamWinGatesFailed':failed,'ledgerConservationPassed':True,'sourceFTCategoryConservationPassed':True,'ovrSamplePlayers':31,'ovrFullRanking':False,'cacheExactParityGames':96,'unresolved':['team win gates','individual FG/attempt accuracy','teammate FG regression fromv14','low-minute extrapolation','technical FT source mechanism','creator reference with new FTR survival','four missing skills remain70 and speed missing']},indent=2),encoding='utf-8')
print(json.dumps({'failedSeasons':failed,'2025-26':macro['v19']},ensure_ascii=True))

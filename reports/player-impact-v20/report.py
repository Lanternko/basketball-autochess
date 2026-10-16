"""Report measured-contest experiment without adopting it or ranking a sample."""
import csv,json,hashlib
from pathlib import Path
root=Path('reports/player-impact-v20')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
old=read('reports/player-impact-v19/scores.json');new=read(root/'scores.json')
bench=read(root/'ovr-checkpoint.json');protocol=read(root/'validation-protocol.json')
provenance=read(root/'2025-26-measurement-provenance.json')
source={p['playerId']:p for p in provenance['rows']}
selected=lambda data,s:next(c for c in data['cells'] if c['season']==s and c['version']=='rotation-space')
current=selected(new,'2025-26');on={p['playerId']:p for p in current['onCourtPlayers']}
assert len(current['players'])==582
for p in current['players']:
 a,b=p['metrics']['oreb36'],p['metrics']['dreb36']
 p['metrics']['reb36']={k:a[k]+b[k] for k in ['actual','predicted']} if a and b else None
fields=['playerId','name','position','actualMinutes','simulatedMinutes','primarySample','roleLowConfidence','unknownOffBall','unknownScreen','unknownHandle','unknownBreakDouble','speedMeasured']
keys=['pts36','ast36','reb36','oreb36','dreb36','stl36','blk36','tov36','fga36','fg3a36','fta36','fgPct','threePct']
onkeys=['onTeamFG','onTeam3P','onTeammateFG','onTeammate3P','onOpponentFG','onOpponent3P','teamFGOnOff','team3POnOff']
columns=fields+[k+'_'+v for k in keys+onkeys for v in ['actual','predicted','error']]
with (root/'2025-26-player-validation.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
 for p in current['players']:
  pid=p['playerId'];row=dict(playerId=pid,name=p['name'],position=p['position'],actualMinutes=p['minutes'],simulatedMinutes=p['predictedMinutes'],primarySample=p['minutes']>=500,roleLowConfidence=source[pid]['role']['lowConfidence'],unknownOffBall=70,unknownScreen=70,unknownHandle=70,unknownBreakDouble=70,speedMeasured=False)
  for k in keys+onkeys:
   q=p['metrics'].get(k) if k in keys else on[pid]['metrics'].get(k)
   if q:row.update({k+'_actual':q['actual'],k+'_predicted':q['predicted'],k+'_error':q['predicted']-q['actual']})
  w.writerow(row)
lines=[]
def add(s=''):lines.append(s)
add('# 2025–26 個人數據與 OVR：防守干擾範圍實驗 v20')
add()
add('**已完成四季各3組 seed、582名目標季球員的逐人對照與31名球員的OVR機制抽樣；本版沒有通過採用條件，正式模型未更換。** 目標球季確定為2025–26（2026年結束）。最新完整582人排名仍是舊v14的暫定診斷，不能當成本版Top50。')
add()
add('[582人逐項對照表](2025-26-player-validation.csv) 包含得分、助攻、總籃板、進攻／防守籃板、抄截、阻攻、失誤、出手、FG%、3P%、在場球隊及排除本人後隊友的命中率，並列實際值、模擬值及差。計數採各自分鐘的每36分鐘；命中率誤差單位是百分點。所有人都匯出，至少500實際分鐘者才進入主摘要，沒有用分鐘門檻替榜單隱藏球員。低出手率指標留白表示未達實際出手門檻，不等於精準或誤差為零。')
add()
add('## 這一輪改動與驗證')
add()
add('舊算法把前兩名協防者的能力與體格合成值用在幾乎所有近距離投籃；來源追蹤的命中率差卻只描述「由該球員最近防守的出手」。本版以「每分鐘干擾次數 × 該條件命中率差 ÷ 每隊每分鐘該區出手數」合成五人的防守效果。六呎內追蹤的次數除以整個近距離區域出手量，因此沒有假定每次近距離投籃都由護框者干擾。中距離仍是明示的代理值。')
add()
add('保留原防守能力曲線、200次出手的差值收縮、獨立體格效果及已驗證的籃板取得／歸屬機制；干擾頻率採240分鐘聯盟活動先驗。沒有改球員名字、排名、位置分數或依模擬殘差加減能力。來源追蹤是描述性關聯，不能直接當作個人因果防守。')
add()
add('五人全70時與中立舊事件樹完全一致；干擾量加倍時效果加倍；打亂球員順序不改結果。失誤、犯規、罰球命中率及籃板機率未被這個修正直接改動。96場快取／未快取驗證的全部比分與個人計數一致。來源每區FGA涵蓋及5份ON／4份隊友／1份本人的出手帳本守恆通過。四季完整賽程14,760場、嚴格在場子集13,263場；同季重現、非盲測。')
add()
add('## 四季同組亂數的個人誤差')
add()
add('| 分鐘加權 MAE | 前版v19 | 本版v20 |')
add('|---|---:|---:|')
labels={'pts36':'得分/36','ast36':'助攻/36','tov36':'失誤/36','stl36':'抄截/36','blk36':'阻攻/36','oreb36':'進攻籃板/36','dreb36':'防守籃板/36','fgPct':'FG% 百分點','threePct':'3P% 百分點'}
for k,label in labels.items():add(f"| {label} | {old['aggregate']['rotation-space']['individualMAE'][k]:.3f} | {new['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
add()
add('四季等權；主樣本至少500實際分鐘，FG及3P摘要至少100次相應實際出手。得分、助攻略改善，FG、3P及防守籃板略退步，不能以平均誤差接近宣稱每名球員都準確。')
add()
add('| 在場指標 MAE（百分點） | v19 | v20 |')
add('|---|---:|---:|')
for k,label in [('onTeamFG','在場球隊FG'),('onTeammateFG','排除本人的隊友FG'),('onTeam3P','在場球隊3P'),('onTeammate3P','排除本人的隊友3P'),('teamFGOnOff','球隊FG ON–OFF'),('team3POnOff','球隊3P ON–OFF')]:add(f"| {label} | {old['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} | {new['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add()
add('ON–OFF仍受隊友、對手與輪替影響；有傳球／投射代理機制不代表已測到跑速、無球跑動或空間的因果效果。')
add()
add('## 球隊勝場與採用條件')
add()
add('| 球季 | 正式控制勝場MAE | v19 | v20 | v20不超過控制+0.5場 |')
add('|---|---:|---:|---:|---|')
failed=[]
for season in protocol['seasons']:
 a=next(c for c in new['cells'] if c['season']==season and c['version']=='control')['teamMetrics']['winsMAE'];b=selected(old,season)['teamMetrics']['winsMAE'];c=selected(new,season)['teamMetrics']['winsMAE'];ok=c<=a+.5
 if not ok:failed.append(season)
 add(f"| {season} | {a:.3f} | {b:.3f} | {c:.3f} | {'通過點估計' if ok else '未通過'} |")
add()
add('前三季勝場與淨分表現改善，2025–26勝場與淨分退步。三組seed尚非20組擴大確認，且已存在明確失敗；不能採用，也不能以其他球季的平均掩蓋目標季退步。')
add()
add('## OVR怎麼算，以及現在能說到哪裡')
add()
add('每位球員只放自然位置，其餘四人是不同位置形狀、16項能力算術平均70的隊友。與固定30隊先發陣容交手，每隊40組亂數，每組互換主客順序，共2,400場、同等14.4分鐘、停用疲勞和換人。勝=1、和=0.5、敗=0；先將互換順序兩場平均，再對每隊及所有重複等權平均。這是陣容替換後的基準勝率，沒有直接把籃板、體格或16項能力加權相加成OVR。')
add()
add('合成隊友的出手、組織、抄截、籃板等輔助活動率按位置池保留，並非全部一樣。平均屬性70不代表該隊模擬勝率必為50%，也不代表已校準成0–99的OVR。本次沒有新錨點及全員重排，只報可檢查的勝率。自然位置仍有133人使用原身高區間備援、248人的位置信心不足，逐人表已標示。')
add()
add('| 代表球員 | v19勝率 | v20勝率 | v20模擬邊際95%區間 |')
add('|---|---:|---:|---:|')
oldbench=read('reports/player-impact-v19/ovr-checkpoint.json')
for pid in [1628983,1629029,203999,201939,1629674]:
 a=next(r['result'] for r in oldbench['rows'] if r['job'].get('id')==pid);b=next(r['result'] for r in bench['rows'] if r['job'].get('id')==pid)
 add(f"| {b['name']} | {a['winRate']*100:.2f}% | {b['winRate']*100:.2f}% | {b['ci95'][0]*100:.2f}–{b['ci95'][1]*100:.2f}% |")
add()
add('Jokić點估計略高於Queta，區間重疊；沒有足夠證據稱已排除低分鐘球員外推問題。31人樣本包含舊榜11名低分鐘前50，部分仍高於多名主力。這不是582人排名，不能聲稱SGA、Luka、Jokić已達本版前10／20，或有幾位後衛進前50。區間只包含模擬亂數，不含缺測、來源估計與模型選擇不確定性。')
add()
add('## 體格與預設70的核對')
add()
add('把同一球員的體格單獨改成70，其他能力、來源情境、輔助率、隊友、對手及seed固定，得到以下機制介入；這不是現實身高體重的因果估計，也沒有用來選擇新參數。')
add()
add('| 球員 | 原勝率 | 體格改70後 | 原體格帶來的差（百分點） |')
add('|---|---:|---:|---:|')
for r in read(root/'physique-audit.json')['rows']:
 a,b=r['original'],r['result'];add(f"| {a['name']} | {a['winRate']*100:.2f}% | {b['winRate']*100:.2f}% | {(a['winRate']-b['winRate'])*100:+.2f} |")
add()
add('體格確實影響估值；但Jokić的體格值及這項介入差都比Queta高，兩人的原估值顛倒不能單獨歸因於體格。模型仍有獨立投籃與防守籃板的體格假設，尚未被這輪實驗驗證成真實增益。')
add()
add('全部582人的無球、掩護、控球、破包夾仍是70，沒有偽造補值。助攻／持球產量與3PM產量現在有進入角色、傳球與空間代理機制，與「測到這四項能力」是兩件事。控球失誤使用盒分比率及傳球被抄活動，沒有運球追蹤；速度缺測；耐力值源於每場分鐘而非生理量測。完整來源與缺測旗標見 [measurement-provenance](2025-26-measurement-provenance.json)。')
add()
audit=root/'v20-simulation-ft-audit.json'
if audit.exists():
 add('## 罰球流程再核對')
 add()
 source_ft=read('reports/player-impact-v19/2025-26-ft-kinds.json');source_team_games=2*len(source_ft['games'])
 add(f"嚴格來源子集：投籃罰球每隊每場{source_ft['totals']['shooting']/source_team_games:.3f}次、非投籃{source_ft['totals']['nonshooting']/source_team_games:.3f}次、技術{source_ft['totals']['technical']/source_team_games:.3f}次、未連結{source_ft['totals']['unresolved']/source_team_games:.3f}次。此子集與完整1230場的分母不同，供分類頻率比較。")
 add()
 for version in ['v19','v20']:
  a=read(root/f'{version}-simulation-ft-audit.json');add(f"{version}同一組seed：投籃犯規及and-one每隊每場{a['sourceShootingFTAPerGame']:.3f}次FTA，其他罰球{a['otherFTAPerGame']:.3f}次；被動觀察器與原整季全部球隊及比賽完全一致。")
 add()
 add('v19只有3次技術罰球、v20為0次，來源子集卻有1,050次；技術罰球機制仍不完整。其他罰球類型可能抵銷漏項，因此總FTA接近不能當作逐類驗證通過。')
 add()
add('## 尚未完成')
add()
add('目標季球隊勝率、個人命中率及出手角色、隊友FG、低分鐘外推與缺測能力仍未解決。v18組織成功率參考仍是舊生存率近似；本版來源審計平均成功率0.4113，不能直接用近似時鐘的預測助攻總量當重新校準目標。正式仍為pure-oreb-turnover-time-1，這輪修正僅在可重現的實驗引擎中。')
add()
add('重現檔：`validation-protocol.json`、`validation-manifest.json`、`scores.json`、`all-players.csv`、`all-players-on-court.csv`、`ovr-protocol.json`、`ovr-checkpoint.json`、`physique-audit.json`、`2025-26-creation-audit.json`。')
(root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(root/'status.json').write_text(json.dumps(dict(version='measured-contest-exposure-20',officialModelAdopted=False,goalComplete=False,fullSeasonSeeds=3,strictOnCourtSeeds=3,seasons=4,targetSeason='2025-26',targetPlayers=582,fullSeasonGames=14760,strictGames=13263,ovrSamplePlayers=31,ovrFullRanking=False,teamWinGatesFailed=failed,cacheExactParityGames=96,ledgerConservationPassed=True,unknownSkillsRemain70=True,sourceCreationAuditApproximate=True,technicalFreeThrowMechanismIncomplete=True),indent=2),encoding='utf-8')
print(json.dumps(dict(players=582,failedSeasons=failed,report=str(root/'report.md'))))

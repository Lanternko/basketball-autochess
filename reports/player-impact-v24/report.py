import json
from pathlib import Path

root=Path('reports/player-impact-v24')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
scores=read(root/'scores.json');protocol=read(root/'validation-protocol.json');prior=read(root/'dreb-prior.json');old_source=read(root/'old-source-allocation-audit.json')['seasons'];parity=read(root/'season-parity.json');ft=read(root/'free-throw-audit.json')
lines=[];add=lines.append
add('# 2025–26 個人數據：按實際五人競爭的防守籃板分配 v24\n')
add('**四季各3組seed、24份完整／嚴格範圍模擬及582人對照已完成。本版只修正防守籃板的個人歸屬；正式模型未更換，OVR與Top50尚未驗收。**\n')
add('[582人逐項對照](2025-26-player-validation.csv) 包含得分、助攻、失誤、抄截、阻攻、進攻／防守籃板、FG／3P、在場球隊／排除本人後的隊友命中率與ON–OFF；保留所有低分鐘球員、原始計數、分鐘及出手分母，另列來源籃板機會與分配權重。\n')
add('## 確認的根因與修改\n')
add('舊分配把五人的同季DREB／分鐘加上240分鐘先驗後正規化；不同球員同場競爭與球隊真正贏到的籃板機會沒有直接進入估計。將舊公式套在完全真實的五人、真實球隊防守籃板上，2025–26仍把Jokić的633個分成584.5個，表示分配公式本身就有一部分偏差，不能全部歸因於模擬球隊搶板不足。\n')
add(f"v24從四季{sum(read(root/f'{s}-dreb-risksets.json')['counts']['individualDreb'] for s in protocol['seasons']):,}個個人防守籃板事件，逐筆取得當時五人。以P(歸屬i|球隊已贏到個人DREB、當時五人)=exp(z_i)／Σexp(z_j)估計相對分配強度。z採零中心高斯先驗，L2強度{prior['l2Precision']:.6f}由2022–23至2024–25整場五折留出概似決定，2025–26未用於選強度。沒有使用模擬殘差、勝場、名字、排名或ON–OFF擬合。\n")
add('這是給定球隊贏板後的歸屬模型，不是個人造成球隊贏板的能力。互不連通球隊的強度尺度無法由這些條件資料辨識，由零中心先驗選定尺度；跨隊可攜性未獲因果驗證。沒有把它轉成rebound屬性或疊加體格。阻攻分配、進攻籃板、團隊贏板機率及投籃／罰球／失誤／助攻／時鐘／輪替均保留前版。\n')
add(f"來源整場留出NLL為{prior['nll']['fitted']:.2f}，弱正則化λ=0.1為{prior['nll']['weakRegularizationPrecision0_1']:.2f}，五人均分為{prior['nll']['uniform']:.2f}。這是選參數的條件資料檢查，不能當作整個比賽引擎的盲測準確率。\n")
add('## 真實籃板機會下的歸屬檢查\n')
add('| 球員 | 實際DREB | 舊公式期望 | v24期望 |\n|---|---:|---:|---:|')
rates=read(root/'2025-26-dreb-rates.json')['cards'];names={str(p['playerId']):p['name'] for p in old_source['2025-26']['players']}
for pid in ['203999','1628983','1629029','201939','1629674']:
 p=rates[pid];old=next(p for p in old_source['2025-26']['players'] if p['playerId']==pid)
 add(f"| {old['name']} | {p['sourceDreb']} | {old['expectedOldAllocation']:.2f} | {p['sourceExpectedDreb']:.2f} |")
add('\n這張表固定真實機會，僅驗證分配；不是季模擬產量。正則化會收縮估計，來源期望值不強制等於實際數量。\n')
add('## 放回完整模擬後的防守籃板誤差\n')
add('| 球季 | v23 DREB/36 MAE | v24 |\n|---|---:|---:|')
for s in protocol['seasons']:
 cells={c['version']:c for c in scores['cells'] if c['season']==s};add(f"| {s} | {cells['v23']['summary']['ALL']['dreb36']['mae']:.3f} | {cells['rotation-space']['summary']['ALL']['dreb36']['mae']:.3f} |")
add(f"\n四季等權平均：{scores['aggregate']['v23']['individualMAE']['dreb36']:.3f}→{scores['aggregate']['rotation-space']['individualMAE']['dreb36']:.3f}。主摘要至少500實際分鐘，按實際分鐘加權；CSV不刪低分鐘球員。\n")
add('| 2025–26球員 | 實際DREB/36 | v23 | v24 |\n|---|---:|---:|---:|')
cells={c['version']:c for c in scores['cells'] if c['season']=='2025-26'}
for pid in [203999,1628983,1629029,201939,1629674]:
 a=next(p for p in cells['v23']['players'] if p['playerId']==pid);b=next(p for p in cells['rotation-space']['players'] if p['playerId']==pid)
 add(f"| {b['name']} | {b['metrics']['dreb36']['actual']:.2f} | {a['metrics']['dreb36']['predicted']:.2f} | {b['metrics']['dreb36']['predicted']:.2f} |")
add('\n歸屬改善仍不等於完全重現。球隊可搶板總量、輪替陣容與機會暴露仍會讓個人模擬值與來源不同；沒有用個人補差值把結果硬拉回。\n')
add('## 其他個人數據、在場命中率及球隊\n')
add(f"已逐項比較全部{parity['games']:,}場完整／嚴格範圍結果：每場比分、全部球隊計數、所有球員的非DREB計數、在場五人／本人一人／其他隊友四人的FG帳目與補籃觀察量，都與v23完全相同。個人REB僅隨DREB歸屬變動；沒有以其他項目吸收誤差。\n")
add('| 指標，四季平均MAE | v24 |\n|---|---:|')
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','阻攻/36'),('oreb36','進攻籃板/36'),('fgPct','FG百分點'),('threePct','3P百分點')]:add(f"| {label} | {scores['aggregate']['rotation-space']['individualMAE'][k]:.3f} |")
for k,label in [('onTeamFG','在場球隊FG百分點'),('onTeammateFG','排除本人隊友FG百分點'),('onTeam3P','在場球隊3P百分點'),('onTeammate3P','排除本人隊友3P百分點')]:add(f"| {label} | {scores['aggregate']['rotation-space']['onCourtMAE'][k]:.3f} |")
add('\n原始ON–OFF仍受輪替、隊友及對手影響，不能直接讀成個人因果影響。\n')
add('| 球季 | 正式控制勝場MAE | v24（等同v23） | 控制+0.5場界線 |\n|---|---:|---:|---|');failed=[]
for s in protocol['seasons']:
 c={c['version']:c for c in scores['cells'] if c['season']==s};a=c['control']['teamMetrics']['winsMAE'];b=c['rotation-space']['teamMetrics']['winsMAE'];passed=b<=a+.5
 if not passed:failed.append(s)
 add(f'| {s} | {a:.3f} | {b:.3f} | {"通過" if passed else "未通過"} |')
add('\n本版未通過正式採用條件，沒有更換正式模型。\n')
add('## OVR與仍需修正的得分來源\n')
add('本報告不把籃板歸屬修正當作OVR改善證據。96場自然位置對照確認改變個人DREB歸屬時，比分、其餘球員統計與快取結果均完全一致；全季也確認相同。DREB歸屬沒有進入球權、機率或輪替決策，因此這項修正本身不會補回後衛的OVR影響。全582人、每人2400場的新版OVR另由[獨立協定](all-2025-26/protocol.json)運算；完整榜單完成前，上一版[31人診斷](../player-impact-v23/report.md)仍是最近已完成的抽樣，不冒充全員榜。\n')
add('平均70隊友的各項屬性保留原值，僅按自然位置合併來源機會加權的幾何分配強度；舊版輸入快取未被修改。四項offBall／screen／handle／breakDbl仍為70，沒有把追蹤產量當技巧分數。\n')
add('另以被動觀察器拆開目標季1188場的罰球類別，所有球隊／比賽與封存完全一致。來源罰球以逐球犯規連結分類，未連結者保持未解；模擬依當次犯規分支分類。兩者不是官方逐球技能標籤。\n')
add('| 球員 | 來源投籃／非投籃／技術／未解FTA | 模擬投籃／非投籃／故意／技術／未解FTA |\n|---|---:|---:|')
for pid in [201939,203999,1628983,1629029,1629674]:
 p=next(p for p in ft['rows'] if p['playerId']==pid);a=p['source'];b=p['simulated'];src='/'.join(str(a.get(k,0)) for k in ['shooting','nonshooting','technical','unresolved']);sim='/'.join(str(b.get(k,0)) for k in ['nonShooting','intentional','technical','unresolved']);shot=b.get('shooting',0)+b.get('andOne',0)
 add(f"| {p['name']} | {src} | {shot}/{sim} |")
add('\n以上單組seed，來源與模擬分鐘仍須分開看，不能只拿原始總量相減調參數。下一步要把Curry等人的出手機會、投籃罰球、非投籃與技術罰球分開核對，同時解決團隊防守與低分鐘OVR外推；目前尚未證明所有個人數據精準，也未達到後衛Top50及SGA／Luka／Jokić前10或前20的完整驗收。\n')
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
status={'version':'conditional-dreb-recipient-24','officialModelAdopted':False,'goalComplete':False,'seasons':4,'fullSeasonSeeds':3,'strictOnCourtSeeds':3,'targetPlayers':582,'teamWinGatesFailed':failed,'ovrFullRanking':False,'ovrLastSampleVersion':23,'conditionalRecipientOnly':True,'teamAndNonDrebParityGames':parity['games'],'counterfactualParityGames':96,'next':'Separate Curry/all-player FGA and FT categories; resolve team defense, fresh/FT-rebound partition and low-minute OVR extrapolation. No name/rank residual tuning.'}
(root/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2))

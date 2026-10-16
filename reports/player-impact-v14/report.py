"""Summarize completed artifacts without promoting an unvalidated model."""
import csv,hashlib,json
from pathlib import Path

root=Path('reports/player-impact-v14')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
strict=read(root/'scores.json')
confirmed=(root/'confirmation-scores.json').exists()
box=read(root/'confirmation-scores.json') if confirmed else strict
seeds=20 if confirmed else 3
versions=['control','rotation-space']
def average(metric,version):
 cs=[c for c in box['cells'] if c['version']==version]
 return sum(c['summary']['ALL'][metric]['mae'] for c in cs)/len(cs)
def court(metric,version):
 return strict['aggregate'][version]['onCourtMAE'][metric]

lines=[]
def add(s=''):lines.append(s)
add('# 2025–26個人數據與OVR：來源情境及輪替修正')
add()
add('**個人數據與在場隊友FG的重現已改善；三分ON–OFF、部分球隊勝率與低分鐘外推仍未解決，因此尚未替換正式模型。** 使用者已確認榜單目標為2025–26，其他三季用於穩定性檢查。')
add()
add(f'四季2,262個球員季；個人box與球隊表為每季{seeds}個相同seed的對照，嚴格ON/OFF為每季3 seed、共13,263場。每一位球員均輸出；主樣本為實際至少500分鐘，按實際分鐘加權，各季等權。計數使用各自分鐘的每36分鐘，投籃率保留原出手門檻。這是同季實績重現，四季答案均已看過，不是事前預測或因果驗證。')
add()
add('## 為什麼隊伍準確，個人仍會失真')
add()
add('球隊總和只限制總量，無法保證事件分給正確的人。舊流程先抽發動者、再抽接球者，又以當前效率篩選，會集中給接球高效率內線；發動者的成功組織量也曾被接球端既有被助攻份額封頂。每人的出手與助攻都可能錯，隊伍加總卻仍接近。')
add()
add('新版保留每人的來源終結需求，以零對角的聯合流量分配創造與接球機會；不能自己助攻自己，不能憑空增加出手。組織者可以增加全隊接球創造量，接球傾向是分配先驗，不再封住團隊組織供給。全局角色彈性來自實際逐球出手／助攻者選擇，沒有以球員名字、OVR或ON–OFF擬合。')
add()
add('空間改參考實際三分產量，自主得分引力與組織效果參考來源角色產量；避免只靠體格或少量高命中率三分便取得強大外線引力。這些明確標為角色代理，沒有冒稱無球、速度、掩護、控球或破包夾的實測能力。四項未知能力仍70，沒有速度資料。')
add()
add('投籃輸入另修正40–99屬性反算的資訊流失，並以實際嚴格輪替重建的模型平均能量及來源隊友情境中心化。賽季FG原已包含平時疲勞，不能再重複扣一次，也不能把未來疲勞全部刪掉。相對來源多休息或多疲勞仍會改變命中率。此能量是模型參考，不是生理量測。')
add()
add('球隊24秒違例已改為球隊失誤，個人不背此責任；保留已驗證的防守籃板、阻攻條件歸屬修正。沒有為後衛排名直接削減籃板或加上位置分數。')
add()
add('## 個人平均絕對誤差')
add()
add(f'下表為四季{seeds} seed。低誤差不代表每個人都準，原始分鐘／總量另行輸出。')
add()
add('| 指標 | 原控制 | rotation-space | 單位 |')
add('|---|---:|---:|---|')
for key,label in [('pts36','得分'),('ast36','助攻'),('tov36','失誤'),('stl36','抄截'),('blk36','阻攻'),('oreb36','進攻籃板'),('dreb36','防守籃板'),('fga36','出手'),('fg3a36','三分出手'),('fta36','罰球出手'),('fgPct','FG%'),('threePct','3P%')]:
 unit='百分點' if key.endswith('Pct') else '每36分鐘'
 add(f'| {label} | {average(key,versions[0]):.3f} | {average(key,versions[1]):.3f} | {unit} |')
add()
add('## 在場與隊友命中率')
add()
add('嚴格相同比賽、3 seed。ON包含本人，隊友欄排除本人；OFF限制相同球隊且球員實際出賽的比賽。原始ON–OFF受輪替、隊友與對手混雜，不能直接寫成個人因果價值。')
add()
add('| 平均絕對誤差（百分點） | 原控制 | rotation-space |')
add('|---|---:|---:|')
for key,label in [('onTeamFG','在場團隊FG'),('onTeammateFG','扣掉本人之隊友FG'),('onTeam3P','在場團隊3P'),('onTeammate3P','扣掉本人之隊友3P'),('teamFGOnOff','團隊FG的ON–OFF'),('team3POnOff','團隊3P的ON–OFF')]:
 add(f'| {label} | {court(key,versions[0]):.3f} | {court(key,versions[1]):.3f} |')
add()
add('## 球隊檢查')
add()
add(f'每季{seeds} seed；沿用勝場MAE最多退步0.5的點估計界線，逐季揭露，不能用四季平均掩蓋失敗。')
add()
add('| 球季 | 控制勝場MAE | 候選勝場MAE | 控制淨勝分RMSE | 候選淨勝分RMSE | 勝場界線 |')
add('|---|---:|---:|---:|---:|---|')
failures=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 a=next(c for c in box['cells'] if c['season']==season and c['version']=='control')['teamMetrics']
 b=next(c for c in box['cells'] if c['season']==season and c['version']=='rotation-space')['teamMetrics']
 passed=b['winsMAE']<=a['winsMAE']+.5
 if not passed:failures.append(season)
 add(f'| {season} | {a["winsMAE"]:.3f} | {b["winsMAE"]:.3f} | {a["netRMSE"]:.3f} | {b["netRMSE"]:.3f} | {"通過點估計" if passed else "未通過"} |')
if confirmed:
 add()
 add('20 seed的paired-seed bootstrap只涵蓋模擬亂數，不包含卡片估計、資料缺漏與模型選擇不確定性。詳細區間見`confirmation-scores.json`，點估計通過不等於已證明等效。')
add()
add('## 全員OVR檢查')
add()
rankfile=root/'all-2025-26/ranking.json'
rank=read(rankfile) if rankfile.exists() else None
if rank:
 add(f'全582名球員，各600場：30隊對手、交換席次、10組seed；固定14.4分鐘、不疲勞不換人，只放自然位置，其他四位為不同位置且屬性算術平均70的隊友。角色輔助頻率採既有位置池政策，四個未知能力仍70。勝率是此固定對照的條件結果。前50有{rank["guardCountTop50"]}名後衛、{rank["lowMinutesTop50"]}名不足500分鐘。')
 add()
 add('| 球員 | 全員初篩名次 | 至少500分鐘池 | 對照勝率95%區間 |')
 add('|---|---:|---:|---|')
 for pid in [1628983,1629029,203999,201939,1629674]:
  p=next(p for p in rank['players'] if p['playerId']==pid)
  add(f'| {p["name"]} | {p["rank"]} | {p.get("qualifiedRank","—")} | {p["ci95"][0]*100:.1f}%–{p["ci95"][1]*100:.1f}% |')
 add()
 add('這是機制初篩，不能保證確切名次。低分鐘卡的輸入不確定性尚未傳入；排名重疊範圍也不是同時有效的排名信賴區間。不會為了指定球星進前20而加姓名偏移量。全員與500分鐘池同時保留，不刪掉低分鐘球員來美化結果。')
 add()
 add('低分鐘另查到具體的不一致：角色頻率與FG有先驗收縮，但射擊犯規使用的FT/FGA仍為原始比值。例如Alex Antetokounmpo只有約21分鐘、8FGA／15FTA，原始比值1.875，使犯規與drive代理可能大幅外推。此球員只是診斷案例；應針對所有球員用來源資料估計曝光先驗，再重新驗證，不加姓名修正，也不更動已凍結v14來掩蓋問題。完整11人見`low-minute-top50-audit.json`。')
else:add('全員測試尚未完成，不發布這個版本的名次。')
add()
add('## 可重現性與限制')
add()
add('新增6個測試檔全部通過：4000種陣容的創造守恆、角色代理及空間路徑、四季自然位置輸入、連續能量與恢復、來源FG還原及額外疲勞／能力變動。固定陣容96場快取與未快取結果及全部個人計數完全相同。投射威脅提高可改善隊友外線與單一內線機率，但這不構成速度或真實因果空間效果的驗證。')
add()
add('逐人資料：`all-players.csv`、`all-players-on-court.csv`、`turnover-scores.json`；`high-usage-3-seeds.json`單列實際使用量前20%的球員。20 seed完成時另有`all-players-20-seeds.csv`與`high-usage-20-seeds.json`，均保留原始分鐘、總量與低分鐘標記。傳球／運球失誤比較以每36分鐘呈現；缺少真實傳球／觸球分母，不能宣稱每次傳球或運球風險已準確。')
add()
add('參數與來源：`validation-protocol.json`、`validation-manifest.json`，擴大確認為`confirmation-protocol.json`、`confirmation-manifest.json`。所有來源雜湊固定；既有正式模型與先前85個來源檔未改。正式模型尚未被本候選取代，這次任務仍有未通過項目。')
add()
add('可執行候選：`node scripts/simulate_player_impact_season.mjs --version rotation-space --season 2025-26 --strict --out <新路徑.json>`；可加`--games 2`作短測試。來源雜湊與輸出不覆寫檢查保留；預設仍是既有terminal-flow診斷版。新版2場與已存全季對應比賽完全一致，舊預設2場的全輸出亦與改CLI前一致（僅lineage有更新）。')
add()
add('另外試驗v15以嚴格實際五人陣容反算個人出手／防守籃板條件權重。出手的保留比賽交叉熵1.56103，反而高於既有全局彈性1.56004；籃板1.54389亦高於原率1.54302。雖能拉高部分球星，兩項均未套用；這是已知賽季率輸入下的條件選擇檢查，不是盲測或顯著性結論。')
(root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

protocol=read(root/'validation-protocol.json')
frozen=read('reports/player-box-audit/source-hashes.json')
for f,h in {**frozen,**protocol['hashes']}.items():
 assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
status={'version':'rotation-source-context-14','targetSeason':'2025-26','sameSeasonOnly':True,'diagnosticRunnable':True,'boxSeedsPerSeason':seeds,'onCourtSeedsPerSeason':3,'playerSeasons':2262,'sourceHashesVerified':len(protocol['hashes']),'previous85SourcesUnchanged':True,'individualBoxImproved':True,'onCourtFgImproved':True,'teamWinsPointMarginFailures':failures,'threePointOnOffImproved':court('team3POnOff','rotation-space')<=court('team3POnOff','control'),'allPlayerOvrFinished':rank is not None,'officialModelReplaced':False,'goalComplete':False}
(root/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(status,ensure_ascii=False))

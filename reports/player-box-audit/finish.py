"""Publish measured outcomes only after complete scoring and exact parity."""
import json,hashlib,csv
from pathlib import Path
root=Path('reports/player-box-audit');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
b=read(root/'baseline.json');first=read(root/'experiment/scores.json')['cells'];second=read(root/'round2/scores.json')['cells']
alloc=read(root/'allocation/scores.json')['cells'];confirm=read(root/'allocation/confirmation/scores.json')['cells'];parity=read(root/'allocation/parity.json')
assert parity['passed'] and parity['runs']==48 and parity['games']==59040
def get(cells,season,version):return next(c for c in cells if c['season']==season and c['version']==version)
seasons=b['protocol']['seasons'];gates=[]
for cells,phase in [(alloc,'developmentSeeds'),(confirm,'confirmationSeeds')]:
  for s in seasons:
    old=get(cells,s,'control');new=get(cells,s,'box-allocation')
    for k in ['dreb36','blk36']:
      a=old['summary']['ALL'][k]['mae'];z=new['summary']['ALL'][k]['mae'];gates.append({'phase':phase,'season':s,'metric':k,'old':a,'new':z,'passed':z<a})
    assert old['teamMetrics']==new['teamMetrics']
accepted=all(g['passed'] for g in gates);assert accepted,'Recipient correction did not pass all seasons'
hashfiles=['src/individual_box_allocation.js','reports/player-box-audit/allocation/adapter.mjs','reports/player-box-audit/allocation/worker.mjs']
status={'conditionalBoxAllocationAccepted':accepted,'boxReconstructionVersion':'pure-oreb-turnover-time-individual-allocation-1',
 'gameplayBaseline':'pure-oreb-turnover-time-1','runner':'scripts/simulate_individual_box_season.mjs',
 'scope':'Same-season conditional DREB/BLK recipient allocation only; no change to game outcomes, team event probabilities, OREB or other individual statistics.',
 'offenseInterventionsPromoted':False,'individualOffenseAndSpacingValidated':False,'ovrRankingValidated':False,
 'limits':['All four seasons previously seen; random-seed confirmation is not future-season validation.','Same-season observed rates are inputs, not independently identified abilities.','OffBall, screen, handle and breakDbl remain unmeasured70; no independent speed attribute.','PTS/AST opportunity errors and spacing effect size remain unresolved.'],
 'parity':parity,'acceptanceGates':gates,'sourceSHA256':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in hashfiles}}
(root/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
last=b['seasons'][-1];su=last['summary'];lines=[
 '# 個人數據驗證與分配修正', '',
 '已完成全體球員核對。球隊平均接近真實，不能證明個人分配正確。先前個人進攻籃板的修正有保留；目前得分、助攻、防守籃板、火鍋仍有不同程度偏差。', '',
 f'基準：`{b["protocol"]["model"]}`；四季、20個seed、98,400場，合計 {sum(len(s["players"]) for s in b["seasons"]):,} 人季；2025–26 全部 {len(last["players"])} 人。交易先依球員ID合併。表內主要統計採真實分鐘至少500的球員、真實分鐘加權；個人計數換算每36分鐘，模擬與真實各用自己的分鐘。所有低分鐘球員仍匯出，不填成零或刪掉。', '',
 '分鐘誤差獨立列在CSV，並非假定每個人的模擬分鐘完全正確。三分命中率只計真實至少100次三分出手者。四季都是已看過答案的同季重現，不能宣稱是資料外能力估計或未來預測。', '',
 '| 2025–26 個人指標 | 真實平均 | 模擬平均 | 平均絕對誤差 |', '|---|---:|---:|---:|']
for k,label in [('pts36','得分/36'),('ast36','助攻/36'),('tov36','失誤/36'),('stl36','抄截/36'),('blk36','火鍋/36'),('oreb36','進攻籃板/36'),('dreb36','防守籃板/36'),('threePct','三分命中率（%／誤差pp）')]:
 x=su['ALL'][k];lines.append(f'| {label} | {x["actual"]:.3f} | {x["predicted"]:.3f} | {x["mae"]:.3f} |')
lines+=['','後衛得分與助攻偏低、中鋒得分偏高；抄截與進攻籃板相對準，不能按位置把所有數據加強。角色由官方先發位置及分鐘決定；先發不足者標示低信心，另提供至少5次先發的敏感度結果。','','| 類型 | 得分/36 真實→模擬 | 助攻/36 真實→模擬 |','|---|---:|---:|']
for group in ['G','F','C']:
 p=su[group]['pts36'];a=su[group]['ast36'];lines.append(f'| {group} | {p["actual"]:.2f}→{p["predicted"]:.2f} | {a["actual"]:.2f}→{a["predicted"]:.2f} |')
lines+=['','| 球員 | 得分/36 真實→模擬 | 助攻/36 真實→模擬 | 進攻籃板/36 真實→模擬 |','|---|---:|---:|---:|']
for name in ['Stephen Curry','Shai Gilgeous-Alexander','Nikola Jokić','Neemias Queta']:
 p=next(p for p in last['players'] if p['name']==name);v=[p['metrics'][k] for k in ['pts36','ast36','oreb36']];lines.append('| '+name+' | '+' | '.join(f'{m["actual"]:.2f}→{m["predicted"]:.2f}' for m in v)+' |')
t=last['teamSummary'];lines+=['',f'球隊端也不是所有項目都準：2025–26 助攻每隊每場真實 {t["ast"]["actual"]:.2f}，模型 {t["ast"]["predicted"]:.2f}。總得分 {t["pts"]["actual"]:.2f}→{t["pts"]["predicted"]:.2f} 接近，不代表得分與助攻歸屬正確。','','已實作並通過的修正：防守籃板、火鍋改用場上球員的實測每分鐘事件率分配，低樣本沿用防守測量的240分鐘聯盟先驗；交易球員先合併數據。不調球隊產生事件的機率、不新增命中率懲罰、不調個別球員偏移量。這和既有進攻籃板分配修正是同類型的條件分配校正。','','| 球季／階段 | DREB個人MAE 舊→新 | BLK個人MAE 舊→新 |','|---|---:|---:|']
for cells,phase in [(alloc,'三個診斷seed'),(confirm,'另外三個seed確認')]:
 for s in seasons:
  a=get(cells,s,'control')['summary']['ALL'];z=get(cells,s,'box-allocation')['summary']['ALL'];lines.append(f'| {s}／{phase} | {a["dreb36"]["mae"]:.3f}→{z["dreb36"]["mae"]:.3f} | {a["blk36"]["mae"]:.3f}→{z["blk36"]["mae"]:.3f} |')
lines+=['',f'逐筆對照 {parity["games"]:,} 場：比分、勝負、完整球隊統計及所有非目標個人統計完全一致。這能確認本次分配修正沒有破壞原有比賽結果；也表示它本身不會提高後衛OVR。單獨DREB、單獨BLK與合併三版皆有測試，並以另三個seed確認合併版。','','進攻機制診斷：每版四季、相同三個seed；表內為四季個人MAE等權平均。只供機制比較，沒有挑球員補分或按勝率調參。','','| 候選 | 得分/36 MAE | 助攻/36 MAE |','|---|---:|---:|']
for cells,v,label in [(first,'control','採用基準'),(first,'creator-touch','發動權重加入AST'),(first,'pass-credit','放寬最後傳球助攻記帳'),(second,'hazard-balance','接球權重除以出手意願'),(second,'creator-hazard','加入AST＋修正接球權重'),(second,'creator-only-hazard','以AST選發動者＋修正接球權重')]:
 av=lambda k:sum(get(cells,s,v)['summary']['ALL'][k]['mae'] for s in seasons)/len(seasons)
 lines.append(f'| {label} | {av("pts36"):.3f} | {av("ast36"):.3f} |')
lines+=['','助攻記帳候選與原版助攻數完全相同，否定「此處漏記造成當前偏差」的猜測。加入AST可減輕發動者分配偏差。原來已按真實FGA給球，後續又用EV決定留下球出手，會再偏向高效率終結者；逆出手意願只測這一層，仍未處理傳球失敗、失誤、犯規、時限與補籃造成的最終機會差異。純AST發動者也是角色代理，不是量測的控球能力。', '',
 '這些進攻候選沒有升為正式比賽基準：雖有個人指標改善，助攻量仍不足，且沒有完成新的跨情境、跨樣本進攻驗收。保留全部候選、完整四季分數與輸出，不把局部改善宣稱為整個系統修好。', '',
 '空間測試：固定同一SG或唯一C，防守與出手狀態不變，只改PG隊友一個屬性。採用版 `contextLongScale=0`，三分命中率的直接隊友情境加成確實為零；投射威脅仍改變出手區域、協防、引力與禁區命中率。測試中PG的long由40改100，SG三分命中機率保持38.3883%，唯一C近框命中機率59.3201%→62.0343%。這是機制反應，不是從NBA識別出的因果效應。三分出手占比不是必然增加：禁區變好也會吸走部分出手。', '',
 '所有實際球員卡的offBall、screen、handle、breakDbl仍是70，沒有獨立速度屬性，所以尚不能把真實跑動、無球掩護、持球與破包夾差異還原。不能因此直接給後衛補分，也不能把三分情境係數任意打開就當驗證完成。', '',
 '失誤細項：`pbp-truth.json`使用本機官方1,227/1,230場逐球資料，缺場0022500029、0022501229、0022501230未補值。`turnover-types.json`以引擎既有活死球分解恢復進攻方傳球被抄與運球被抄，並明列與完整模擬的覆蓋差異。聯盟平均接近，但後衛失球偏少、中鋒偏多，仍是角色分配問題；總失誤不能忽略球權與傳球量一律要求後衛較少。模擬另有將團隊24秒違例記給個人的口徑問題，已列出其個人貢獻，這批未悄悄扣掉。', '',
 '完整資料：`2025-26-readable.csv`、`all-seasons-readable.csv`（真實／模擬／差值分欄）；`baseline.json`含角色低信心敏感度；各實驗目錄的scores.json、players.csv；`allocation/parity.json`；`status.json`。', '',
 '重跑：`python -X utf8 reports/player-box-audit/audit.py`；`node reports/player-box-audit/experiment/run.mjs`；`node reports/player-box-audit/round2/run.mjs`；`node reports/player-box-audit/allocation/run.mjs`；`node reports/player-box-audit/allocation/confirm.mjs`；各目錄以`experiment/score.py <目錄>`評分；`node reports/player-box-audit/allocation/parity.mjs`；最後`python -X utf8 reports/player-box-audit/finish.py`。已存在實驗會驗證來源與規格；來源變更須另建版本。', '',
 '新同季個人數據重現入口：`node scripts/simulate_individual_box_season.mjs 2025-26 20261018`。原歷史runner與採用結果不覆寫，新入口明確只接上本次通過的DREB/BLK條件分配修正。']
(root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
latest=get(confirm,'2025-26','box-allocation')
keys=list(latest['players'][0]['metrics']);fields=['playerId','name','position','roleGroup','minutes','predictedMinutes']+[k+'_'+z for k in keys for z in ['actual','simulated','difference']]
with (root/'2025-26-corrected-readable.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for p in latest['players']:
  row={k:p[k] for k in fields if k in p}
  for k,m in p['metrics'].items():
   for z,v in [('actual',m['actual'] if m else None),('simulated',m['predicted'] if m else None),('difference',m['predicted']-m['actual'] if m else None)]:row[k+'_'+z]=round(v,5) if v is not None else ''
  w.writerow(row)
print(json.dumps({'accepted':accepted,'parityGames':parity['games'],'gates':gates},indent=2))

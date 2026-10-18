import json,sys
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-v46');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));seasons=sys.argv[1:] or read(ROOT/'protocol.json')['seasons'];prefix='' if len(seasons)==4 else '-'.join(seasons)+'-';new=read(ROOT/(prefix+'scores.json'));cells=[c for v in [44,45] for c in read(f'reports/player-impact-v{v}/scores.json')['cells'] if c['season'] in seasons and c['variant']==f'v{v}']+[c for c in new['cells'] if c['variant']=='v46'];versions=['v44','v45','v46'];keys=['onshortFGpct','onlongFGpct','onshortShare','onlongShare','onFGA48','deltashortFGpct','deltalongFGpct','deltashortShare','deltalongShare'];labels=['在場對手禁區命中率','在場對手三分命中率','在場對手禁區出手占比','在場對手三分出手占比','在場對手 FGA／48','禁區命中率 on−off','三分命中率 on−off','禁區出手占比 on−off','三分出手占比 on−off'];aggregate={v:{k:float(np.mean([c['defenseSummary']['ALL'][k]['mae'] for c in cells if c['variant']==v])) for k in keys} for v in versions};selection=read(ROOT/'selection.json')
lines=['# v46：共用禁區防守效果與細區偏移','','## 這次改了什麼','','v46 接續 v45，將限制區與其他油漆區的防守係數聯合估計。每位防守者有共用禁區效果與一個正負細區偏移；兩區仍保有獨立的射手能力、截距與訓練場次火鍋活動斜率。沒有姓名特例，也沒有把個人 on/off 殘差直接加回能力。','','出手選擇、中距離及三分命中模型、來源能量、犯規、籃板與補籃皆沿用 v45。來源中性情境只依原屬性、陣容、能量、曝光及未改的出手選擇，與細區 make 係數無關，因此直接重用已凍結的 v45 參考值；驗證已確認只有兩區 make 係數改變。','','較早三季整場五折交叉驗證選擇共用收縮與偏移收縮；**主要判準改為球員在場合併禁區命中率 MAE**，逐球細區 NLL 作次要比較並完整保留。這是依使用者的個人數據目標選擇；不將較低的彙總誤差宣稱為所有逐球預測也更好。2025–26 未參與此次超參數選擇。','','選定參數：'+json.dumps(selection['selected'])+'。選定值位於此次搜尋範圍上界，僅表示本次網格中最佳，不能宣稱全域最優。','','四季均為已看過賽季的同季重建；不同 seed 只檢查模擬穩定性，不是新的真實測試季。原始 on/off 含對手、隊友及輪替，不能當個人因果防守。','','## 相同口徑：完整模擬防守誤差','','至少 500 來源分鐘；區域命中率至少 100 該區真實出手；來源分鐘加權。三 seed 計數合併再算命中率；四季 MAE 對季等權。百分比單位為百分點，含補籃。','','| 指標 | v44 | v45 | v46 |','|---|---:|---:|---:|']
for k,label in zip(keys,labels):lines.append('| '+label+' | '+' | '.join(f'{aggregate[v][k]:.4f}' for v in versions)+' |')
lines+=['','## 各季禁區防守命中率 MAE','','| 球季 | v44 | v45 | v46 |','|---|---:|---:|---:|']
for s in seasons:lines.append('| '+s+' | '+' | '.join(f"{next(c for c in cells if c['season']==s and c['variant']==v)['defenseSummary']['ALL']['onshortFGpct']['mae']:.4f}" for v in versions)+' |')
lines+=['','## 球隊得分 MAE','','每隊三 seed 整季得分平均後除 82，再計算 30 隊 MAE。依使用者授權可暫時退步，但完整追蹤。','','| 球季 | v44 | v45 | v46 |','|---|---:|---:|---:|']
for s in seasons:lines.append('| '+s+' | '+' | '.join(f"{next(c for c in cells if c['season']==s and c['variant']==v)['teamPPG']['mae']:.4f}" for v in versions)+' |')
lines+=['','## 位置分組：在場對手禁區命中率 MAE','','| 位置 | v44 | v45 | v46 |','|---|---:|---:|---:|']
for g in ['G','F','C']:lines.append('| '+g+' | '+' | '.join(f"{np.mean([c['defenseSummary'][g]['onshortFGpct']['mae'] for c in cells if c['variant']==v]):.4f}" for v in versions)+' |')
comparisons=[]
for s in seasons:
 for baseline in ['v44','v45']:
  a=next(c for c in cells if c['season']==s and c['variant']==baseline);b=next(c for c in cells if c['season']==s and c['variant']=='v46');lookup={p['playerId']:p for p in b['players']}
  for k in keys:
   pairs=[(p,lookup[p['playerId']]) for p in a['players'] if p['minutes']>=500 and p['metrics'][k] and lookup[p['playerId']]['metrics'][k]];comparisons.append({'season':s,'baseline':baseline,'metric':k,'improved':sum(abs(q['metrics'][k]['error'])<abs(p['metrics'][k]['error']) for p,q in pairs),'worsened':sum(abs(q['metrics'][k]['error'])>abs(p['metrics'][k]['error']) for p,q in pairs)})
if '2025-26' in seasons:
 lines+=['','## Wembanyama：2025–26 完整模擬','','| 指標 | 真實 | v44 | v45 | v46 |','|---|---:|---:|---:|---:|'];ps={v:next(p for c in cells if c['season']=='2025-26' and c['variant']==v for p in c['players'] if p['playerId']==1641705) for v in versions}
 for k,label in zip(keys,labels):lines.append('| '+label+f" | {ps['v44']['metrics'][k]['actual']:.3f} | "+' | '.join(f"{ps[v]['metrics'][k]['predicted']:.3f}" for v in versions)+' |')
 lines+=['','## 個人進攻誤差：2025–26','','| 指標 | v44 | v45 | v46 |','|---|---:|---:|---:|'];cs={v:next(c for c in cells if c['season']=='2025-26' and c['variant']==v) for v in versions}
 for k in cs['v46']['individualSummary']['ALL']:lines.append('| '+k+' | '+' | '.join(f"{cs[v]['individualSummary']['ALL'][k]['mae']:.4f}" for v in versions)+' |')
source=read(ROOT/'source-evaluation.json');lines+=['','## 固定真實出手與陣容：交叉驗證','','此處是新鮮出手固定區域的來源預測，與完整輪替模擬分開。新模型的細區逐球 NLL 略退步，但較符合此次優先的球員數據目標。','','| 球季 | v45 合併禁區 MAE | v46 | v45 細區 NLL | v46 |','|---|---:|---:|---:|---:|']
for c in source['seasons']:
 if c['season'] in seasons:lines.append(f"| {c['season']} | {c['summary']['short:on']['v45']:.4f} | {c['summary']['short:on']['v46']:.4f} | {c['heldoutNLL']['v45']:.3f} | {c['heldoutNLL']['v46']:.3f} |")
finepath=ROOT/(prefix+'fine-scores.json')
if finepath.exists():
 fine=read(finepath);oldfine=read('reports/player-impact-v45/fine-scores.json');lines+=['','## 五區新鮮出手：完整模擬命中率 MAE','','| 球季 | 區域 | v45 | v46 |','|---|---|---:|---:|']
 for c in fine['cells']:
  if c['season'] not in seasons:continue
  a=next(s for s in oldfine['cells'] if s['season']==c['season'])
  for z,label in [('ra','限制區'),('paint','其他油漆區'),('mid','中距離'),('corner','底角三分'),('arc','弧頂及其他三分')]:lines.append(f"| {c['season']} | {label} | {a['summary'][z+':on']['mae']:.4f} | {c['summary'][z+':on']['mae']:.4f} |")
 lines+=['','五區命中率表只含新鮮出手，與含補籃的上方合併禁區表口徑不同。犯規與籃板幾何仍為三區，總出手率威懾尚未獨立建模。','']
 if '2025-26' in seasons:
  p=next(p for c in fine['cells'] if c['season']=='2025-26' for p in c['players'] if p['playerId']==1641705);q=next(p for c in oldfine['cells'] if c['season']=='2025-26' for p in c['players'] if p['playerId']==1641705)
  lines+=['','### Wembanyama 細區 on/off，避免合併結果抵銷','','| 區域 | 真實命中率差 | v45 | v46 | 真實出手占比差 | v45 | v46 |','|---|---:|---:|---:|---:|---:|---:|']
  for z,label in [('ra','限制區'),('paint','其他油漆區'),('mid','中距離'),('corner','底角三分'),('arc','弧頂及其他三分')]:
   m=p['metrics'][z]['delta'];s=p['shareMetrics'][z]['delta'];lines.append('| '+label+' | '+' | '.join(f'{v:.3f}' for v in [m['actual'],q['metrics'][z]['delta']['predicted'],m['predicted'],s['actual'],q['shareMetrics'][z]['delta']['predicted'],s['predicted']])+' |')
  lines+=['','**個別細區仍未修準。** Wembanyama 的限制區命中率 on/off 仍估得過強，其他油漆區則偏弱；兩區會部分抵銷。合併禁區 on/off 接近真實，不能取代這張細區表。','']
lines+=['','## 更多球員是否改善','','| 球季 | 相對版本 | 禁區命中率改善人數 | 退步人數 |','|---|---|---:|---:|']
for c in comparisons:
 if c['metric']=='onshortFGpct':lines.append(f"| {c['season']} | {c['baseline']} | {c['improved']} | {c['worsened']} |")
if (ROOT/'decision.json').exists():lines+=['','## 判斷','',read(ROOT/'decision.json')['summaryZh'],'','本輪未重新計算 OVR，亦未取代既有遊戲預設。完整資料見 [scores.json](scores.json)、[source-evaluation.json](source-evaluation.json) 與 [decision.json](decision.json)。','']
(ROOT/(prefix+'report.md')).write_text('\n'.join(lines),encoding='utf-8');result={'seasons':seasons,'aggregateDefenseMAE':aggregate,'comparisons':comparisons,'teamPPGMeanMAE':{v:float(np.mean([c['teamPPG']['mae'] for c in cells if c['variant']==v])) for v in versions}};(ROOT/(prefix+'comparison.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'aggregateDefenseMAE':aggregate,'teamPPGMeanMAE':result['teamPPGMeanMAE']}))

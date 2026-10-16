import json,sys
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));seasons=sys.argv[1:] or read(ROOT/'protocol.json')['seasons'];prefix='' if len(seasons)==4 else '-'.join(seasons)+'-';new=read(ROOT/(prefix+'scores.json'))
cells=[c for version in [42,44] for c in read(f'reports/player-impact-v{version}/scores.json')['cells'] if c['season'] in seasons and c['variant']==f'v{version}']+[c for c in new['cells']];versions=['v41','v42','v44','v45']
keys=['onshortShare','onlongShare','onshortFGpct','onlongFGpct','onFGA48','deltashortShare','deltalongShare','deltashortFGpct','deltalongFGpct'];labels=['在場對手禁區出手占比','在場對手三分出手占比','在場對手禁區命中率','在場對手三分命中率','在場對手 FGA／48','禁區出手占比 on−off','三分出手占比 on−off','禁區命中率 on−off','三分命中率 on−off'];aggregate={v:{k:float(np.mean([c['defenseSummary']['ALL'][k]['mae'] for c in cells if c['variant']==v])) for k in keys} for v in versions}
lines=['# v45：五區命中率與出手分布、實測防守活動','','## 改動與資料界線','','- 全員共用模型，無 Wembanyama 或其他球員姓名特例。限制區、其他油漆區、中距離、底角三分、弧頂及其他三分分開估計。','- 較早三季整場留出選擇模型；2025–26 不參與超參數選擇。命中率的限制區、其他油漆區及中距離採用訓練場次的球員火鍋／對手該區出手機會；出手分布的四個條件分支亦採用此類活動特徵。','- 上一季最近防守者追蹤資料有實際測試，但未勝出，未接入此次候選。全季 DFG 結果沒有偷放進同季留出特徵。底角選擇的活動特徵僅有極小留出增益，不能解讀為強證據。','- 新防守係數取代舊基準，未疊加兩套防守或把火鍋從命中率再扣一次。以實際來源出手、陣容及能量置中後承接至模擬。','- 引擎的犯規與籃板幾何仍用內／中／外三區。五區的新鮮出手命中聯合機率精確合併；細區標籤使用獨立觀測亂數，沒有額外改變比賽亂數。補籃沿用原規則。','- 四季都是已看過賽季的重建。整場交叉驗證不是未來預測，原始 on/off 也不是球員單獨的因果效果。模型估計相對出手分布；不代表已單獨辨識所有「不敢出手」的總出手率效應。','','## 相同口徑的防守誤差','','至少 500 來源分鐘；命中率至少 100 該區來源出手；來源分鐘加權。三種子計數先合併，多季 MAE 對季等權。百分比項目單位為百分點。含補籃，與歷版相同。','','| 指標 | v41 | v42 | v44 | v45 |','|---|---:|---:|---:|---:|']
for k,label in zip(keys,labels):lines.append('| '+label+' | '+' | '.join(f'{aggregate[v][k]:.4f}' for v in versions)+' |')
lines+=['','## 位置分組','','| 在場對手命中率 MAE | v41 | v42 | v44 | v45 |','|---|---:|---:|---:|---:|']
for role in ['G','F','C']:
 for k in ['onshortFGpct','onlongFGpct']:
  lines.append('| '+role+' '+k+' | '+' | '.join(f"{np.mean([c['defenseSummary'][role][k]['mae'] for c in cells if c['variant']==v]):.4f}" for v in versions)+' |')
lines+=['','## 球隊得分誤差','','每隊三種子總得分先平均再除 82，30 隊 MAE。依使用者授權，暫時變差仍完整保留，非硬性否決條件。','','| 球季 | v41 | v42 | v44 | v45 |','|---|---:|---:|---:|---:|']
for s in seasons:lines.append('| '+s+' | '+' | '.join(f"{next(c for c in cells if c['season']==s and c['variant']==v)['teamPPG']['mae']:.4f}" for v in versions)+' |')
comparisons=[]
for s in seasons:
 a=next(c for c in cells if c['season']==s and c['variant']=='v44');b=next(c for c in cells if c['season']==s and c['variant']=='v45');lookup={p['playerId']:p for p in b['players']}
 for k in keys:
  pairs=[(p,lookup[p['playerId']]) for p in a['players'] if p['minutes']>=500 and p['metrics'][k] and lookup[p['playerId']]['metrics'][k]];comparisons.append({'season':s,'metric':k,'improved':sum(abs(q['metrics'][k]['error'])<abs(p['metrics'][k]['error']) for p,q in pairs),'worsened':sum(abs(q['metrics'][k]['error'])>abs(p['metrics'][k]['error']) for p,q in pairs)})
if '2025-26' in seasons:
 lines+=['','## Wembanyama：2025–26 完整輪替模擬','','| 指標 | 實際 | v41 | v42 | v44 | v45 |','|---|---:|---:|---:|---:|---:|'];ps={v:next(p for c in cells if c['season']=='2025-26' and c['variant']==v for p in c['players'] if p['playerId']==1641705) for v in versions}
 for k in keys+['offshortShare','offshortFGpct','offlongFGpct']:
  lines.append(f"| {k} | {ps['v41']['metrics'][k]['actual']:.3f} | "+' | '.join(f"{ps[v]['metrics'][k]['predicted']:.3f}" for v in versions)+' |')
 lines+=['','## 目標季個人進攻誤差','','| 指標 | v41 | v42 | v44 | v45 |','|---|---:|---:|---:|---:|'];cs={v:next(c for c in cells if c['season']=='2025-26' and c['variant']==v) for v in versions}
 for k in cs['v45']['individualSummary']['ALL']:lines.append('| '+k+' | '+' | '.join(f"{cs[v]['individualSummary']['ALL'][k]['mae']:.4f}" for v in versions)+' |')
 lines+=['','## 有多少球員改善：v44 → v45','','| 球季 | 指標 | 改善人數 | 變差人數 |','|---|---|---:|---:|']
 for p in comparisons:
  if p['metric'] in ['onshortFGpct','onlongFGpct','onshortShare','onlongShare']:lines.append(f"| {p['season']} | {p['metric']} | {p['improved']} | {p['worsened']} |")
for kind in ['make','choice']:
 source=read(ROOT/(kind+'-evaluation.json'));lines+=['',f'## 固定真實陣容與出手的 {kind} 交叉驗證','','這部分不是完整模擬結果，不與上表誤差混用。','']
 for c in source['seasons']:
  if c['season'] not in seasons:continue
  nll=c['heldoutNLL'];values={k:(v['total'] if isinstance(v,dict) else v) for k,v in nll.items()};lines.append('- '+c['season']+' NLL：'+', '.join(f'{k} {v:.3f}' for k,v in values.items()))
 if kind=='make' and '2025-26' in seasons:
  p=next(p for c in source['seasons'] if c['season']=='2025-26' for p in c['players'] if p['playerId']==1641705);lines+=['','Wembanyama 的固定真實新鮮出手禁區命中率 on−off：實際 '+f"{p['metrics']['short']['delta']['actual']:.3f}"+' pp，舊三區 '+f"{p['metrics']['short']['delta']['coarse']:.3f}"+'，新五區 '+f"{p['metrics']['short']['delta']['selected']:.3f}"+'。限制區與其他油漆區仍須分看，合併接近不能視為各區都準。']
finepath=ROOT/(prefix+'fine-scores.json')
if finepath.exists():
 fine=read(finepath);lines+=['','## 五區完整模擬：新鮮出手','','沒有舊版五區模擬對照，不能以固定真實陣容交叉驗證數字充當舊版。下列為 v45 對真實資料的在場命中率 MAE。','','| 球季 | 限制區 | 其他油漆區 | 中距離 | 底角 | 弧頂及其他三分 |','|---|---:|---:|---:|---:|---:|']
 for c in fine['cells']:
  if c['season'] in seasons:lines.append('| '+c['season']+' | '+' | '.join(f"{c['summary'][z+':on']['mae']:.4f}" for z in ['ra','paint','mid','corner','arc'])+' |')
 lines+=['','在場出手占比 MAE（百分點）：','','| 球季 | 限制區 | 其他油漆區 | 中距離 | 底角 | 弧頂及其他三分 |','|---|---:|---:|---:|---:|---:|']
 for c in fine['cells']:
  if c['season'] in seasons:lines.append('| '+c['season']+' | '+' | '.join(f"{c['summary'][z+':onShare']['mae']:.4f}" for z in ['ra','paint','mid','corner','arc'])+' |')
 if '2025-26' in seasons:
  p=next(p for c in fine['cells'] if c['season']=='2025-26' for p in c['players'] if p['playerId']==1641705)
  lines+=['','Wembanyama 五區明細（新鮮出手）：','','| 區域 | 在場命中率：實際 | v45 | 不在場命中率：實際 | v45 | 出手占比 on−off：實際 | v45 |','|---|---:|---:|---:|---:|---:|---:|']
  for z,label in zip(['ra','paint','mid','corner','arc'],['限制區','其他油漆區','中距離','底角三分','弧頂及其他三分']):
   m=p['metrics'][z];s=p['shareMetrics'][z];lines.append('| '+label+' | '+' | '.join(f'{x:.3f}' for x in [m['on']['actual'],m['on']['predicted'],m['off']['actual'],m['off']['predicted'],s['delta']['actual'],s['delta']['predicted']])+' |')
lines+=['','## 狀態','','這是防守候選版本驗證，不宣稱個人與球隊所有數據已足夠準，也沒有用 OVR 排名反向調係數。本輪未重算 582 人 OVR。','']
if (ROOT/'decision.json').exists():
 lines+=['**v45 不升為正式基準。** 四季的全體禁區命中率 MAE 都比 v44 大，四季平均從 1.2048 增至 1.3629 個百分點；三分命中率則從 1.4149 降至 1.2514。球隊得分 MAE 四季平均 2.3335 → 2.3695 分，2025–26 為 2.1690 → 2.0701 分。暫時的球隊退步已獲允許，並非本次不採用的主因。','','固定真實陣容與出手的交叉驗證也出現全體禁區命中率 MAE 退步：舊三區平均 0.9373、新五區 1.0644 個百分點。因此問題並非只有模擬亂數；逐球五區預測較好，不保證每位球員合併禁區數據較好。歸屬、收縮與區域合併的影響仍需消融確認，不能直接宣稱因果。','','下一個候選應比較「共用禁區防守係數＋限制區／其他油漆區偏移」，以較早三季留出選擇；並分離細區進攻基準、活動先驗及輪替的影響。Wembanyama 在場數據接近，但下場時的限制區被模擬得太容易得分；不以他的原始 on/off 殘差加補丁。','','完整判斷見 [decision.json](decision.json)。','']
(ROOT/(prefix+'report.md')).write_text('\n'.join(lines),encoding='utf-8');(ROOT/(prefix+'comparison.json')).write_text(json.dumps({'aggregateDefenseMAE':aggregate,'comparisons':comparisons,'seasons':seasons,'temporaryTeamRegressionAuthorized':True},indent=2),encoding='utf-8');print(json.dumps({'report':str(ROOT/(prefix+'report.md')),'aggregateDefenseMAE':aggregate}))

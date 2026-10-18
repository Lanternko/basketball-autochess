import json,hashlib,sys
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-v44');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
seasons=sys.argv[1:] or read(ROOT/'protocol.json')['seasons'];prefix='' if len(seasons)==4 else '-'.join(seasons)+'-'
new=read(ROOT/(prefix+'scores.json'));old=read('reports/player-impact-v42/scores.json')
cells=[c for c in old['cells'] if c['season'] in seasons]+[c for c in new['cells'] if c['variant']=='v44'];versions=['v41','v42','v44']
keys=['onshortShare','onlongShare','onshortFGpct','onlongFGpct','onFGA48','deltashortFGpct','deltalongFGpct']
labels=['在場禁區出手占比','在場三分出手占比','在場禁區命中率','在場三分命中率','在場對手 FGA／48','禁區命中率 on−off','三分命中率 on−off']
aggregate={v:{k:float(np.mean([c['defenseSummary']['ALL'][k]['mae'] for c in cells if c['variant']==v])) for k in keys} for v in versions}
lines=['# v44：命中率改以同一 logit 尺度轉換','','使用原 v41 係數、v42 出手選擇；未放大任何球員的防守係數。v43 的較早三季留出比較不支持放寬禁區收縮，因此未採用。v44 以來源模型估得的進攻基準承接防守係數，情境偏移也在 logit 尺度置中；補籃不變。','','所有球季均為已看過的同季重建，並非未來預測。原始 on/off 含隊友、對手、輪替及運氣，不能視為個人因果效果。球隊得分誤差依使用者最新指示容許暫時擴大，仍完整追蹤。','','## 個人防守誤差','','至少 500 來源分鐘；命中率至少 100 該區來源出手；來源分鐘加權；多季表格對季 MAE 等權平均。百分比誤差單位為百分點。','','| 指標 | v41 | v42 | v44 |','|---|---:|---:|---:|']
for k,label in zip(keys,labels):lines.append('| '+label+' | '+' | '.join(f'{aggregate[v][k]:.4f}' for v in versions)+' |')
lines+=['','## 位置分組：在場禁區命中率 MAE','','| 位置 | v41 | v42 | v44 |','|---|---:|---:|---:|']
for role in ['G','F','C']:
 values=[float(np.mean([c['defenseSummary'][role]['onshortFGpct']['mae'] for c in cells if c['variant']==v])) for v in versions]
 lines.append('| '+role+' | '+' | '.join(f'{x:.4f}' for x in values)+' |')
lines+=['','## 球隊得分誤差','','每隊三種子整季得分先平均再除 82；30 隊 MAE，沒有以聯盟平均抵銷。','','| 球季 | v41 | v42 | v44 |','|---|---:|---:|---:|']
for s in seasons:lines.append('| '+s+' | '+' | '.join(f"{next(c for c in cells if c['season']==s and c['variant']==v)['teamPPG']['mae']:.4f}" for v in versions)+' |')
if '2025-26' in seasons:
 lines+=['','## Wembanyama：2025–26','','| 指標 | 實際 | v41 | v42 | v44 |','|---|---:|---:|---:|---:|']
 ps={v:next(p for c in cells if c['season']=='2025-26' and c['variant']==v for p in c['players'] if p['playerId']==1641705) for v in versions}
 for k in ['onshortShare','offshortShare','deltashortShare','onlongShare','deltalongShare','onshortFGpct','offshortFGpct','deltashortFGpct','onlongFGpct','deltalongFGpct','onFGA48']:
  lines.append(f"| {k} | {ps['v41']['metrics'][k]['actual']:.3f} | "+' | '.join(f"{ps[v]['metrics'][k]['predicted']:.3f}" for v in versions)+' |')
 lines+=['','## 目標季個人進攻誤差','','| 指標 | v41 | v42 | v44 |','|---|---:|---:|---:|']
 cs={v:next(c for c in cells if c['season']=='2025-26' and c['variant']==v) for v in versions}
 for k in cs['v44']['individualSummary']['ALL']:
  lines.append('| '+k+' | '+' | '.join(f"{cs[v]['individualSummary']['ALL'][k]['mae']:.4f}" for v in versions)+' |')
comparisons=[]
for season in seasons:
 a=next(c for c in cells if c['variant']=='v42' and c['season']==season);b=next(c for c in cells if c['variant']=='v44' and c['season']==season)
 for k in keys:
  pairs=[(p,q) for p in a['players'] if p['minutes']>=500 for q in b['players'] if q['playerId']==p['playerId'] and p['metrics'][k] and q['metrics'][k]]
  comparisons.append({'season':season,'metric':k,'improved':sum(abs(q['metrics'][k]['error'])<abs(p['metrics'][k]['error']) for p,q in pairs),'worsened':sum(abs(q['metrics'][k]['error'])>abs(p['metrics'][k]['error']) for p,q in pairs)})
result={'adopted':False,'aggregateDefenseMAE':aggregate,'comparisons':comparisons,'temporaryTeamRegressionAuthorized':True,'scope':seasons}
(ROOT/(prefix+'comparison.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
lines+=['','## 採用狀態','','實驗版，尚未取代正式模型；完整數值見 scores.json、defense-players.csv 與 comparison.json。未重算 582 人 OVR；排名不能當作防守驗證。']
(ROOT/(prefix+'report.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'aggregateDefenseMAE':aggregate,'scope':seasons}))

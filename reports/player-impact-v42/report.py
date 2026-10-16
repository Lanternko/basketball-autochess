import json,hashlib,csv
from pathlib import Path
ROOT=Path('reports/player-impact-v42');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));s=read(ROOT/'scores.json');choice=read(ROOT/'choice-verification.json');context=read(ROOT/'context-verification.json')
for name in ['baseline-run-verification.json','candidate-run-verification.json']:
 v=read(ROOT/name);assert v['passed']
 for job in v['jobs']:assert hashlib.sha256(Path(job['file']).read_bytes()).hexdigest()==job['sha256']
old=read('reports/player-impact-v41/scores.json')
for c in s['cells']:
 if c['variant']=='v41':
  archived=next(a for a in old['cells'] if a['season']==c['season'] and a['version']=='rotation-space')
  for k,m in c['individualSummary']['ALL'].items():assert abs(m['mae']-archived['summary']['ALL'][k]['mae'])<1e-9,k
  for k,m in c['teamMetrics'].items():assert abs(m-archived['teamMetrics'][k])<1e-9,k

names=['onshortShare','onlongShare','onshortFGpct','onlongFGpct','onFGA48'];labels={'onshortShare':'在場對手禁區出手占比','onlongShare':'在場對手三分出手占比','onshortFGpct':'在場對手禁區命中率','onlongFGpct':'在場對手三分命中率','onFGA48':'在場對手出手／48分鐘'}
lines=['# v42：防守對出手選擇的影響','','四季均為已看過的球季，是同季重建驗證，不是未來預測。未改正式引擎或任何歷史榜單。', '', '## 四季個人防守誤差','','至少500來源在場分鐘；命中率至少100來源區域出手；以來源分鐘加權。三種子合併計數後計算每人誤差。百分比指標的誤差單位為百分點。','','| 指標 | v41 MAE | v42 MAE |','|---|---:|---:|']
for k in names:lines.append(f"| {labels[k]} | {s['aggregateDefenseMAE']['v41'][k]:.4f} | {s['aggregateDefenseMAE']['v42'][k]:.4f} |")
lines+=['','## 球隊得分誤差硬門檻','','每季先對相同三種子的每隊整季得分取平均，再除82場；對30隊計算PPG MAE，沒有用聯盟平均抵銷。','','| 球季 | v41 | v42 | 不擴大 |','|---|---:|---:|---|']
for g in s['gates']:lines.append(f"| {g['season']} | {g['baselinePPGMAE']:.4f} | {g['candidatePPGMAE']:.4f} | {'通過' if g['teamPPGNonRegression'] else '未過'} |")
ppgPass=all(g['teamPPGNonRegression'] for g in s['gates']);core=names[:4];improved=sum(s['aggregateDefenseMAE']['v42'][k]<s['aggregateDefenseMAE']['v41'][k] for k in core)
lines+=['','## Wembanyama：2025–26','','| 指標 | 來源實績 | v41 | v42 |','|---|---:|---:|---:|']
cells={c['variant']:c for c in s['cells'] if c['season']=='2025-26'};ps={v:next(p for p in c['players'] if p['playerId']==1641705) for v,c in cells.items()}
for k in ['onshortShare','offshortShare','deltashortShare','onlongShare','offlongShare','deltalongShare','onshortFGpct','offshortFGpct','deltashortFGpct','onlongFGpct','offlongFGpct','deltalongFGpct','onFGA48']:
 a=ps['v41']['metrics'][k];b=ps['v42']['metrics'][k]
 suffix=k.removeprefix('on').removeprefix('off').removeprefix('delta')
 label={'shortShare':'對手禁區出手占比','longShare':'對手三分出手占比','shortFGpct':'對手禁區命中率','longFGpct':'對手三分命中率','FGA48':'對手出手／48分鐘'}[suffix]
 prefix='在場' if k.startswith('on') else '不在場' if k.startswith('off') else '在場減不在場'
 lines.append(f"| {prefix}{label} | {a['actual']:.3f} | {a['predicted']:.3f} | {b['predicted']:.3f} |")
counts={}
for variant in ['v41','v42']:
 count={k:0. for k in ['pts','fgm','fg3m','ftm']}
 for seed in [20261012,20261013,20261014]:
  path=f'reports/player-impact-v41/runs/2025-26-rotation-space-full-{seed}.json' if variant=='v41' else ROOT/f'runs/2025-26-v42-full-{seed}.json'
  for t in read(path)['teams']:
   for k in count:count[k]+=t['stats'][k]/(3*2460)
 counts[variant]=count
d={k:counts['v42'][k]-counts['v41'][k] for k in counts['v41']};assert abs(d['pts']-(2*d['fgm']+d['fg3m']+d['ftm']))<1e-10
lines+=['',f"2025–26聯盟每隊每場得分變化 {d['pts']:+.4f} = 兩倍FGM變化 {2*d['fgm']:+.4f} ＋三分額外分變化 {d['fg3m']:+.4f} ＋罰球命中變化 {d['ftm']:+.4f}。這是記帳分解，不能把亂數連鎖或特定得分變化直接稱為防守機制的因果效果。未以降低全隊得分乘數或模擬殘差補差硬壓過關。"]
lines+=['','## 各位置與其他球員','','| 位置 | 指標 | v41四季MAE | v42四季MAE |','|---|---|---:|---:|']
for group in ['G','F','C']:
 for k in core:
  values={v:sum(c['defenseSummary'][group][k]['mae'] for c in s['cells'] if c['variant']==v)/4 for v in ['v41','v42']};lines.append(f"| {group} | {labels[k]} | {values['v41']:.4f} | {values['v42']:.4f} |")
changes=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 a=next(c for c in s['cells'] if c['season']==season and c['variant']=='v41');b=next(c for c in s['cells'] if c['season']==season and c['variant']=='v42');lookup={p['playerId']:p for p in b['players']}
 for p in a['players']:
  q=lookup[p['playerId']]
  for k in core:
   x=p['metrics'][k];y=q['metrics'][k]
   if x is None or y is None:continue
   changes.append({'season':season,'playerId':p['playerId'],'name':p['name'],'roleGroup':p['roleGroup'],'sourceMinutes':p['minutes'],'primary':p['minutes']>=500,'metric':k,'actual':x['actual'],'v41':x['predicted'],'v42':y['predicted'],'absoluteErrorChange':abs(y['error'])-abs(x['error'])})
with (ROOT/'defense-changes.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(changes[0]));w.writeheader();w.writerows(changes)
lines+=['','| 指標（四季球員季、至少500來源分鐘） | 誤差減少人次 | 誤差增加人次 |','|---|---:|---:|']
for k in core:
 rs=[r for r in changes if r['primary'] and r['metric']==k];lines.append(f"| {labels[k]} | {sum(r['absoluteErrorChange']<0 for r in rs)} | {sum(r['absoluteErrorChange']>0 for r in rs)} |")
lines+=['','## 判讀與限制','',f'球隊得分不擴大門檻：{"全部通過" if ppgPass else "未全部通過"}；四項主要防守平均誤差有{improved}項下降。實驗結果不會自動採用為正式模型。','', '新機制同時控制投籃者與五位防守者，分三分／兩分、兩分中的禁區／中距離兩個條件模型。先驗由較早三季整場五折留出選定；2025–26留出只供診斷。保留v41命中防守與補籃、犯規、失誤、籃板、負荷。來源投籃情境重新校準，但沒有用模擬得分殘差補差。', '', '禁區定義為限制區及非限制區油漆區兩分球；非僅籃下六呎。一般出手區域會隨防守五人改變，補籃沿用原模型。總出手頻率有量測，但未憑空另加總FGA抑制參數；這不是心理意願或因果防守能力的直接量測。', '', '五人陣容關聯仍有戰術、隊友與對手混雜；完整賽季輸入含同季實績。嚴格樣本代表同一批PBP完整場次，不代表模擬逐秒沿用真實輪替。故即使源資料留出改善，也不保證所有球員原始ON/OFF都重現。', '', '原始全員誤差：defense-players.csv；完整個人14項、分位置與球隊逐隊誤差：scores.json；來源/擬合/情境/比分核對：choice-verification.json、context-verification.json、baseline-run-verification.json、candidate-run-verification.json。']
(ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
verification={'passed':True,'baselineScoreParityPassed':True,'runHashesPassed':True,'choiceFitPassed':choice['passed'],'sourceContextPassed':context['passed'],'teamPPGNonRegressionPassed':ppgPass,'coreDefenseMetricsImproved':improved,'adopted':False,'reason':'Research candidate; adoption requires scoring non-regression and broader validation, not a named-player ranking change.'}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8');print(json.dumps(verification),flush=True)

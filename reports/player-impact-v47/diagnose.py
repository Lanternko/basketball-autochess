"""Read-only offense baseline: full-season box and strict same-game on/off.

No fitted offsets or player-specific parameter changes. All evidence stays v46.
"""
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np

ROOT=Path('reports/player-impact-v47');BASE=Path('reports/player-impact-v46')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
hashes={}
def source(p):
 p=Path(p);hashes[p.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest();return read(p)
score=source(BASE/'scores.json');protocol=source(BASE/'protocol.json')
keys=['fga','fgm','fg3a','fg3m']
def rates(p):
 out={}
 for arm in ['on','off','teammates']:
  c=p[arm];a=c['fga'];three=c['fg3a'];two=a-three
  for suffix,m,n in [('FGpct',c['fgm'],a),('threePct',c['fg3m'],three),('twoPct',c['fgm']-c['fg3m'],two),('threeShare',three,a),('eFGpct',c['fgm']+.5*c['fg3m'],a)]:out[arm+suffix]=100*m/n if n else None
 for suffix in ['FGpct','threePct','twoPct','threeShare','eFGpct']:
  a,b=out['on'+suffix],out['off'+suffix];out['delta'+suffix]=a-b if a is not None and b is not None else None
 return out
def scoring_parts(m):
 def state(which):
  get=lambda k:m[k][which];fga=get('fga36');ta=get('fg3a36');tp=get('threePct')/100;ft=get('fta36');fp=get('ftPct')/100
  two=fga-ta;two_p=(fga*get('fgPct')/100-ta*tp)/two
  return {'two':(two,two_p,2),'three':(ta,tp,3),'freeThrow':(ft,fp,1)}
 a,b=state('actual'),state('predicted');parts={}
 for k in a:
  av,ap,pts=a[k];bv,bp,_=b[k]
  parts[k]={'volume':pts*(bv-av)*(ap+bp)/2,'accuracy':pts*(bp-ap)*(av+bv)/2}
 assert abs(sum(sum(p.values()) for p in parts.values())-(m['pts36']['predicted']-m['pts36']['actual']))<1e-8
 return parts
cells=[]
for season in protocol['seasons']:
 c=next(c for c in score['cells'] if c['season']==season and c['variant']=='v46')
 truth=source(f'reports/player-impact-v1/{season}-on-court-truth.json');pred=defaultdict(lambda:{k:Counter() for k in ['on','off','teammates']});seedrates=defaultdict(list)
 for seed in protocol['seeds']:
  run=source(BASE/f'runs/{season}-v46-strict-{seed}.json');assert len(run['matches'])==truth['strictGames'];assert {m['id'] for m in run['matches']}==set(truth['gameIds'])
  for k in keys:
   total=sum(t['stats'][k] for t in run['teams']);assert sum(p['own'][k] for p in run['onCourt']['players'])==total
   assert sum(p['on'][k] for p in run['onCourt']['players'])==5*total
   assert sum(p['teammates'][k] for p in run['onCourt']['players'])==4*total
  for p in run['onCourt']['players']:
   for arm in ['on','off','teammates']:pred[p['playerId']][arm].update(p[arm])
   seedrates[p['playerId']].append(rates(p))
 players=[]
 for p in truth['players']:
  pid=p['playerId']
  if pid not in pred:continue
  actual=rates(p);estimate=rates(pred[pid]);metrics={}
  for k,v in actual.items():
   if v is None or estimate[k] is None:continue
   seeds=[r[k] for r in seedrates[pid] if r[k] is not None]
   metrics[k]={'actual':v,'predicted':estimate[k],'error':estimate[k]-v,'seedMin':min(seeds),'seedMax':max(seeds)}
  players.append({'playerId':pid,'name':p['name'],'minutes':p['on']['seconds']/60,'metrics':metrics,'actualCounts':{k:p[k] for k in ['on','off','teammates']},'predictedPooledCounts':{k:dict(v) for k,v in pred[pid].items()}})
 summary={}
 for k in players[0]['metrics']:
  rs=[p for p in players if p['minutes']>=500 and k in p['metrics'] and p['actualCounts']['on']['fg3a']>=100 and p['actualCounts']['off']['fg3a']>=100 and p['actualCounts']['teammates']['fg3a']>=100]
  if not rs:continue
  w=np.array([p['minutes'] for p in rs]);w=w/w.sum();errors=np.array([p['metrics'][k]['error'] for p in rs]);summary[k]={'players':len(rs),'mae':float(w@abs(errors)),'bias':float(w@errors)}
 curry=next(p for p in c['individualPlayers'] if p['playerId']==201939)
 cells.append({'season':season,'curryBox':curry,'curryScoringErrorParts36':scoring_parts(curry['metrics']),'curryOnCourt':next(p for p in players if p['playerId']==201939),'onCourtSummary':summary,'onCourtPlayers':players,'allPlayerBoxSummary':c['individualSummary'],'teamPPG':c['teamPPG'],'defenseSummary':c['defenseSummary']})
result={'status':'diagnostic-only','baseline':'v46','candidateImplemented':False,'scope':'Same-season reconstruction, not prospective accuracy. Box is full-season; on/off is strict PBP games only. On/off includes own attempts; teammates excludes own. Off uses same team-games as each player played. Raw on/off is descriptive, not a causal gravity estimate. Seed ranges measure simulation variability, not real-data confidence intervals. Two-point rates combine paint and midrange; no rim-only or pull-up/catch-and-shoot claim.','onCourtSummaryEligibility':'At least500 source strict minutes and100 actual three attempts in each of on, off and teammates; common eligible set across metrics. Source-minute weighted.','cells':cells,'sourceSHA256':hashes}
(ROOT/'diagnosis.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
lines=['# v47 進攻診斷：以 v46 為固定基準','','狀態：僅完成診斷，尚未實作或採用新的進攻係數。v46 防守階段已收束。','','## Curry 個人數據','','每 36 分鐘供比較使用，不代表 OVR 直接依 per36 決定。下表來自完整球季重建；命中率單位為百分比。','','| 球季 | 數據 | 實際 | v46 | 偏差 |','|---|---|---:|---:|---:|']
for c in cells:
 for k in ['pts36','fga36','fg3a36','threePct','fta36','ftPct','ast36','tov36']:
  m=c['curryBox']['metrics'][k];lines.append(f"| {c['season']} | {k} | {m['actual']:.3f} | {m['predicted']:.3f} | {m['predicted']-m['actual']:+.3f} |")
lines+=['','## 得分誤差拆解','','每 36 分鐘得分差，量與準度以對稱分解計算，加總恰等於總得分偏差；這是記帳分解，不能單獨證明機制因果。','','| 球季 | 兩分量 | 兩分準度 | 三分量 | 三分準度 | 罰球量 | 罰球準度 |','|---|---:|---:|---:|---:|---:|---:|']
for c in cells:
 p=c['curryScoringErrorParts36'];vals=[p[k][j] for k in ['two','three','freeThrow'] for j in ['volume','accuracy']];lines.append('| '+c['season']+' | '+' | '.join(f'{v:+.3f}' for v in vals)+' |')
lines+=['','## Curry 在場的隊友及球隊','','只比較 strict PBP 場次，與上方完整球季的樣本不同。隊友欄排除 Curry 自己；on/off 欄含本人。原始差距包含輪換、對手與隊友的影響，不能直接解讀為 Curry 的因果空間價值。','','| 球季 | 指標 | 實際 | v46 | 偏差（百分點） | 三種子範圍 |','|---|---|---:|---:|---:|---|']
for c in cells:
 for k in ['teammatesthreePct','teammatesthreeShare','teammatestwoPct','deltaeFGpct','deltathreePct']:
  m=c['curryOnCourt']['metrics'][k];lines.append(f"| {c['season']} | {k} | {m['actual']:.3f} | {m['predicted']:.3f} | {m['error']:+.3f} | {m['seedMin']:.3f}–{m['seedMax']:.3f} |")
lines+=['','## 後續修正的邊界','','先追蹤出手與罰球的生成，再辨識隊友空間誤差。不能因 Curry 低估就直接提高三分命中率，也不以原始 on/off 殘差製造姓名加成。現有 spacing 使用 3PM/min 等產量代理，並非直接量測跑動、包夾或重力。尚未量測 pull-up／catch-and-shoot 分類與純禁區的隊友進攻，不能宣稱已解決。','','任何候選都需對照四季全體及位置分組個人誤差、球隊得分、v46 粗區與細區防守。優先收回防守階段增加的得分誤差；若暫時退步仍須明列，不能自動採用。OVR 待模擬貢獻定位後另外處理。','','完整全體數值、原始分母、種子範圍與來源雜湊見 [diagnosis.json](diagnosis.json)。']
(ROOT/'diagnosis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'seasons':len(cells),'sourceFiles':len(hashes),'ledgerAndScoringIdentityChecksPassed':True}))

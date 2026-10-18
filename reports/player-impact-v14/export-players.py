"""Export raw exposure/totals together with normalized player errors."""
import csv,json
from pathlib import Path
root=Path('reports/player-impact-v14')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
confirmed=(root/'confirmation-scores.json').exists()
d=read(root/('confirmation-scores.json' if confirmed else 'scores.json'))
cells=[c for c in d['cells'] if c['version']=='rotation-space']
truth={s['season']:{p['playerId']:p for p in s['players']} for s in read('reports/player-box-audit/baseline.json')['seasons']}
counts=['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']
keys=list(cells[0]['players'][0]['metrics'])
output=root/f'all-players-{20 if confirmed else 3}-seeds.csv'
with output.open('w',newline='',encoding='utf-8-sig') as f:
 fields=['season','playerId','name','position','roleGroup','minutes','predictedMinutes','minuteError','primarySample']+[k+'_'+z for k in keys for z in ['actual','predicted','error']]+[k+'_total_'+z for k in counts for z in ['actual','predicted','error']]
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for c in cells:
  for p in c['players']:
   row={k:p[k] for k in fields[:7] if k in p}
   row.update(season=c['season'],primarySample=p['minutes']>=500,minuteError=p['predictedMinutes']-p['minutes'])
   for k,q in p['metrics'].items():
    if q:row.update({k+'_actual':q['actual'],k+'_predicted':q['predicted'],k+'_error':q['predicted']-q['actual']})
   for k in counts:
    actual=truth[c['season']][p['playerId']]['actualCounts'][k]
    q=p['metrics'][k+'36'];pred=q['predicted']*p['predictedMinutes']/36 if q else (0 if p['predictedMinutes']==0 else None)
    row[k+'_total_actual']=actual
    if pred is not None:row.update({k+'_total_predicted':pred,k+'_total_error':pred-actual})
   w.writerow(row)
print(output)
rankfile=root/'all-2025-26/ranking.json'
if rankfile.exists():
 ranking=read(rankfile);lookup={p['playerId']:p for p in ranking['players']}
 latest=next(c for c in cells if c['season']=='2025-26')
 joined=[{**p,'rank':lookup[p['playerId']]['rank'],'primarySample':p['minutes']>=500} for p in latest['players']]
 (root/'2025-26-individual-and-ovr.json').write_text(json.dumps({'boxSeeds':20 if confirmed else 3,'ovrGamesPerPlayer':600,'adopted':False,'warning':'Same-season reconstruction; individual box and OVR use different lineup/exposure experiments. A mean error or target rank does not prove accuracy for every player. OVR input uncertainty is not propagated.','players':joined},ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# 2025–26前50：OVR機制初篩，非正式榜單','','版本rotation-space。對照勝率是固定14.4分鐘、自然位置、四位不同位置平均70隊友對30隊的條件結果；不是已校準的0–99 OVR。每人600場，換席次配對；區間僅涵蓋模擬亂數，缺少卡片／角色估計不確定性。全員不刪低分鐘，分鐘以來源賽季為準。正式模型尚未採用此版本。','','| 名次 | 球員 | 位置 | 實際分鐘 | 對照勝率 | 95%區間 |','|---:|---|---|---:|---:|---|']
 for p in ranking['players'][:50]:
  lines.append(f'| {p["rank"]} | {p["name"]} | {p["position"]} | {p["minutes"]:.0f}{"＊" if p["minutes"]<500 else ""} | {100*p["winRate"]:.1f}% | {100*p["ci95"][0]:.1f}%–{100*p["ci95"][1]:.1f}% |')
 lines+=['',f'前50有{ranking["guardCountTop50"]}名後衛、{ranking["lowMinutesTop50"]}人不足500分鐘（＊）。全582人與至少500分鐘池的名次均見all-2025-26/ranking.csv，不能藉門檻刪人來宣稱排名已修好。']
 (root/'top50-provisional.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

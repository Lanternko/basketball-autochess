"""Publish complete provisional OVR only after every player/baseline finished."""
import json,csv,hashlib
from pathlib import Path

root=Path('reports/player-impact-v24/all-2025-26')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
protocol=read(root/'protocol.json');state=read(root/'checkpoint.json');manifest=read(root/'manifest.json')
assert len(state['rows'])==protocol['players']+protocol['baselines']==587
assert state['fingerprint']==protocol['fingerprint']==manifest['fingerprint']
assert hashlib.sha256((root/'checkpoint.json').read_bytes()).hexdigest()==manifest['checkpointSHA256']
source=next(s for s in read('reports/player-box-audit/baseline.json')['seasons'] if s['season']=='2025-26');actual={p['playerId']:p for p in source['players']}
roles={p['playerId']:p['role'] for p in read('reports/player-impact-v20/2025-26-measurement-provenance.json')['rows']}
rows=[]
for r in state['rows']:
 if r['job']['kind']!='player':continue
 p=r['result'];rows.append({**p,'actualMinutes':actual[p['playerId']]['minutes'],'sourceRoleGroup':actual[p['playerId']]['roleGroup'],'roleLowConfidence':roles[p['playerId']]['lowConfidence']})
assert len(rows)==582 and {p['playerId'] for p in rows}==set(actual)
rows.sort(key=lambda p:(-p['winRate'],p['playerId']))
for i,p in enumerate(rows):
 p['rank']=i+1;p['rankIntervalMarginal95']=[1+sum(q['ci95'][0]>p['ci95'][1] for q in rows),len(rows)-sum(q['ci95'][1]<p['ci95'][0] for q in rows)]
out={'label':'Experimental full all-player conditional win-probability ranking. All four team-win adoption gates remain failed. No minute threshold or named-player adjustment. CI is fixed-model simulation sampling only, not input/model uncertainty. Marginal rank-overlap bounds are not simultaneous confidence intervals or a final Top50 guarantee.','season':'2025-26','samplesPerOpponent':protocol['samples'],'gamesPerPlayer':2400,'players':rows,'guardCountTop50':sum(p['position'] in ['PG','SG'] for p in rows[:50]),'sourceRoleGroupGuardCountTop50':sum(p['sourceRoleGroup']=='G' for p in rows[:50]),'lowMinutesUnder500Top50':sum(p['actualMinutes']<500 for p in rows[:50]),'protocolFingerprint':protocol['fingerprint']}
(root/'ranking.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'ranking.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=['rank','playerId','name','position','sourceRoleGroup','actualMinutes','roleLowConfidence','winRate','standardError','ci95','rankIntervalMarginal95'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
lines=['# 2025–26 最新實驗模型：全582人OVR對照\n', '**這是未驗收的實驗排名。球隊勝場與部分個人數據仍有缺口，不能稱為已修正完成的正式Top50。**\n',f"每人自然位置，搭配其餘四個不同位置、算術平均70的隊友；30個固定對手、兩邊座位各40組，共2400場／人。所有582人完整列入，前50有{out['guardCountTop50']}名PG／SG，其中上場少於500分鐘者{out['lowMinutesUnder500Top50']}人，沒有用分鐘門檻刪除。\n",'表中列直接模擬的基準隊勝率，沒有另加名字／位置加分或事後OVR倍率。95%區間只涵蓋固定模型下的取樣誤差，沒有涵蓋來源與模型不確定性；名次是點估計，不能把區間重疊解讀成已分出高下。\n','[完整582人CSV](ranking.csv)／[個人統計驗證](../report.md)\n','| 名次 | 球員 | 自然位置 | 勝率 | 條件95%區間 | 實際分鐘 |\n|---:|---|---|---:|---:|---:|']
for p in rows[:50]:lines.append(f"| {p['rank']} | {p['name']} | {p['position']} | {100*p['winRate']:.2f}% | {100*p['ci95'][0]:.2f}–{100*p['ci95'][1]:.2f}% | {p['actualMinutes']:.0f} |")
lines+=['\n指定球員全員排名：\n','| 球員 | 名次 | 勝率 | 邊際區間重疊名次範圍 |\n|---|---:|---:|---|']
for pid in [1628983,1629029,203999,201939,1629674]:
 p=next(p for p in rows if p['playerId']==pid);lines.append(f"| {p['name']} | {p['rank']} | {100*p['winRate']:.2f}% | {p['rankIntervalMarginal95'][0]}–{p['rankIntervalMarginal95'][1]} |")
lines+=['\n邊際重疊範圍不是同時名次信賴區間。低分鐘球員來源樣本小，未知技巧仍為70，這些外推問題完整保留在榜單與資料中；沒有為了讓指定名字進前20而改參數。']
(root/'report.md').write_text('\n'.join(lines),encoding='utf-8')
print({k:v for k,v in out.items() if k!='players'})
for p in rows:
 if p['playerId'] in [1628983,1629029,203999,201939,1629674]:print({k:p[k] for k in ['name','rank','winRate','ci95','actualMinutes']})

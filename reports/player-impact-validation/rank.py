import json,csv
from pathlib import Path
ROOT=Path('reports/player-impact-validation');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
state=read(ROOT/'ovr-all-checkpoint.json');base=next(s for s in read('reports/player-box-audit/baseline.json')['seasons'] if s['season']=='2025-26');players={p['playerId']:p for p in base['players']}
rows=[]
for r in state['rows']:
 if r['job']['kind']!='player':continue
 p=r['result'];rows.append({**p,'minutes':players[p['playerId']]['minutes'],'roleGroup':players[p['playerId']]['roleGroup']})
assert len(rows)==582
rows.sort(key=lambda p:(-p['winRate'],p['playerId']))
for i,p in enumerate(rows):
 p['rank']=i+1;p['rankIntervalMarginal95']=[1+sum(q['ci95'][0]>p['ci95'][1] for q in rows),len(rows)-sum(q['ci95'][1]<p['ci95'][0] for q in rows)]
qualified=[p for p in rows if p['minutes']>=500]
for i,p in enumerate(qualified):p['qualifiedRank']=i+1
result={'label':'Provisional 10-sample-per-opponent screen, NOT final Top50 or validated OVR. Marginal CI overlaps are not simultaneous rank confidence. Input uncertainty not propagated. Raw win rate from equal exposure, no minutes multiplier. All 582 retained; 500-minute qualified table uses the preexisting audit threshold, not chosen to favor positions.','players':rows,'guardCountTop50':sum(p['roleGroup']=='G' for p in rows[:50]),'lowMinutesTop50':sum(p['minutes']<500 for p in rows[:50]),'qualifiedPlayers':len(qualified),'qualifiedGuardCountTop50':sum(p['roleGroup']=='G' for p in qualified[:50])}
(ROOT/'ovr-all-screen.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'ovr-all-screen.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=['rank','qualifiedRank','playerId','name','position','roleGroup','minutes','winRate','standardError','ci95','rankIntervalMarginal95'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
print({k:v for k,v in result.items() if k!='players'})
for p in rows:
 if p['name'] in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Stephen Curry','Neemias Queta']:print({k:p.get(k) for k in ['name','rank','qualifiedRank','winRate','ci95','rankIntervalMarginal95']})

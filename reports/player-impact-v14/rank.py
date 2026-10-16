import json,csv,sys
from pathlib import Path
season=sys.argv[1] if len(sys.argv)>1 else '2025-26';ROOT=Path(f'reports/player-impact-v14/all-{season}');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
state=read(ROOT/'checkpoint.json');base=next(s for s in read('reports/player-box-audit/baseline.json')['seasons'] if s['season']==season);players={p['playerId']:p for p in base['players']};rows=[]
for r in state['rows']:
 if r['job']['kind']=='player':
  p=r['result'];rows.append({**p,'minutes':players[p['playerId']]['minutes'],'roleGroup':players[p['playerId']]['roleGroup']})
assert len(rows)==len(players),'All players must finish before assigning full-pool ranks'
rows.sort(key=lambda p:(-p['winRate'],p['playerId']))
for i,p in enumerate(rows):
 p['rank']=i+1;p['rankIntervalMarginal95']=[1+sum(q['ci95'][0]>p['ci95'][1] for q in rows),len(rows)-sum(q['ci95'][1]<p['ci95'][0] for q in rows)]
qualified=[p for p in rows if p['minutes']>=500]
for i,p in enumerate(qualified):p['qualifiedRank']=i+1
out={'label':'Provisional all-player screen; not final Top50 or validated OVR. The 500-minute threshold is the original audit threshold; all-player and qualified ranks are both exported. Marginal overlap ranges are not simultaneous rank confidence.','season':season,'players':rows,'guardCountTop50':sum(p['roleGroup']=='G' for p in rows[:50]),'qualifiedGuardCountTop50':sum(p['roleGroup']=='G' for p in qualified[:50]),'qualifiedPlayers':len(qualified),'lowMinutesTop50':sum(p['minutes']<500 for p in rows[:50])}
(ROOT/'ranking.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'ranking.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=['rank','qualifiedRank','playerId','name','position','roleGroup','minutes','winRate','standardError','ci95','rankIntervalMarginal95'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
print({k:v for k,v in out.items() if k!='players'})
for p in rows:
 if p['playerId'] in [1628983,1629029,203999,201939,1629674]:print({k:p.get(k) for k in ['name','rank','qualifiedRank','minutes','winRate','ci95']})

import json,hashlib
from pathlib import Path
R=Path('reports/model-evolution-20261016');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
rows=[]
for n in range(1,42):
 f=Path(f'reports/player-impact-v{n}/scores.json')
 if not f.exists():continue
 d=read(f);cells=d.get('cells',[])
 rows.append({'v':n,'keys':list(d),'aggregate':list(d.get('aggregate',{})),'cells':[{k:c.get(k) for k in ['season','version','seeds']} for c in cells],'teamMetricKeys':list(cells[0].get('teamMetrics',{})) if cells else []})
ranks=[]
for f in Path('reports').glob('player-impact-v*/all-2025-26/ranking.json'):
 d=read(f);ranks.append({'file':str(f).replace('\\','/'),'keys':list(d),'players':len(d.get('players',[])),'games':d.get('gamesPerPlayer',d['players'][0].get('games')),'label':d.get('label'),'firstRowKeys':list(d['players'][0])})
(R/'inventory.json').write_text(json.dumps({'scores':rows,'rankings':ranks},indent=2),encoding='utf-8')
for r in rows:print(json.dumps({'v':r['v'],'aggregate':r['aggregate'],'target':[{k:c[k] for k in ['version','seeds']} for c in r['cells'] if c['season']=='2025-26'],'teamMetricKeys':r['teamMetricKeys']},ensure_ascii=False))
print('RANKINGS',json.dumps(ranks,ensure_ascii=False))

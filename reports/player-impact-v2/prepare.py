"""Official passing-loss rates, with matched PBP minutes and fixed shrinkage."""
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('reports/player-impact-v2');ROOT.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
hashes={}
for season in ['2022-23','2023-24','2024-25','2025-26']:
 b=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
 base=Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')
 manifest=read(base/'manifest.json');counts=defaultdict(Counter);minutes=Counter();games=set()
 for spec in manifest['sources']:
  f=Path(spec['file']);hashes[str(f).replace('\\','/')]=hashlib.sha256(f.read_bytes()).hexdigest();raw=read(f);games.add(spec['id'])
  for e in raw['data']['game']['actions']:
   if e.get('actionType')!='turnover' or not e.get('personId'):continue
   pid=e['personId'];sub=e.get('subType');desc=e.get('descriptor')
   cat='pass' if sub=='bad pass' or (sub=='out-of-bounds' and desc=='bad pass') else 'handle' if sub=='lost ball' or (sub=='out-of-bounds' and desc=='lost ball') else 'other'
   counts[pid]['turnovers']+=1
   counts[pid][cat+('Stolen' if e.get('stealPersonId') else 'Dead')]+=1
 for g in b['exposure']['games']:
  if g['id'] in games:
   for t in g['teams']:
    for p in t['players']:minutes[p['playerId']]+=p['seconds']/60
 totals=sum(counts.values(),Counter());prior=totals['passStolen']/sum(minutes.values())
 cards={pid:{'minutes':m,'passStolen':counts[pid]['passStolen'],'passStolenPerMinute':(counts[pid]['passStolen']+240*prior)/(m+240),'counts':dict(counts[pid])} for pid,m in minutes.items()}
 for t in b['league']['teams']:
  for p in t['roster']:cards.setdefault(p['playerId'],{'minutes':0,'passStolen':0,'passStolenPerMinute':prior,'counts':{}})
 (ROOT/f'{season}-risk.json').write_text(json.dumps({'season':season,'games':len(games),'method':'Bad pass with recorded stealPersonId; 240-minute league-rate prior; matched PBP exposure minutes. This is a measured loss rate, not a guessed handle rating.','leaguePassStolenPerMinute':prior,'cards':cards},ensure_ascii=False,indent=2),encoding='utf-8')
 print(season,len(games),len(cards),prior,flush=True)
(ROOT/'risk-source-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')

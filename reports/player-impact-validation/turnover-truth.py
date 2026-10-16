import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('reports/player-impact-validation');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
for season in ['2022-23','2023-24','2024-25','2025-26']:
 on=read(f'reports/player-impact-v1/{season}-on-court-truth.json');valid=set(on['gameIds']);base=Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}');counts=defaultdict(Counter);types=Counter();games=0
 for spec in read(base/'manifest.json')['sources']:
  if spec['id'] not in valid:continue
  games+=1
  for e in read(spec['file'])['data']['game']['actions']:
   if e.get('actionType')!='turnover':continue
   pid=e.get('personId');sub=e.get('subType');desc=e.get('descriptor');types[str(sub)+'|'+str(desc)]+=1
   if not pid:continue
   cat='pass' if sub=='bad pass' or (sub=='out-of-bounds' and desc=='bad pass') else 'handle' if sub=='lost ball' or (sub=='out-of-bounds' and desc=='lost ball') else 'other'
   live=bool(e.get('stealPersonId'));q=counts[pid];q['tov']+=1;q['liveTov' if live else 'deadTov']+=1;q[cat+'Tov']+=1
   if live:q[cat+'StolenAgainst']+=1
 assert games==len(valid)
 rows=[{'playerId':p['playerId'],'name':p['name'],'minutes':p['on'].get('seconds',0)/60,'counts':dict(counts[p['playerId']])} for p in on['players']]
 (ROOT/f'{season}-turnover-truth.json').write_text(json.dumps({'season':season,'games':games,'method':'Strict matching games; offensive bad-pass/lost-ball turnover categories and stealPersonId, team turnovers excluded. Minutes from independently reconstructed strict lineups.','types':dict(types),'players':rows},ensure_ascii=False,indent=2),encoding='utf-8')
 print(season,games,flush=True)

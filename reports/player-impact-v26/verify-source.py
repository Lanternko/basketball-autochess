import json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
r=Path('reports/player-impact-v26');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=read(r/'contact-intensity-prior.json');checks=[]
for f,h in p['sourceHashes'].items():assert sha(f)==h,(f,'drift')
for name,v in p['fits'].items():assert v['trainingSeasons']==['2022-23','2023-24','2024-25'] and v['wholeGameFolds']==5
for season in ['2022-23','2023-24','2024-25','2025-26']:
 s=read(r/f'{season}-contact-intensities.json');rates=read(r/f'{season}-contact-rates.json');g=defaultdict(Counter)
 assert len(s['games'])==len({x['id'] for x in s['games']})
 for game in s['games']:
  assert game['fold']==int(game['id'])%5
  for pid,c in game['players'].items():g[pid].update(c)
 for pid,c in s['cards'].items():
  for key in ['contacts','terminal','minutes']:assert abs(c.get(key,0)-g[pid][key])<1e-6,(season,pid,key)
  assert c.get('minutes',0)>0 or c.get('contacts',0)+c.get('terminal',0)==0
  q=rates['cards'][pid];assert q['sourceContacts']==c.get('contacts',0) and q['sourceTerminal']==c.get('terminal',0)
  assert all(math.isfinite(q[k]) and q[k]>0 for k in ['contactRate','terminalRate'])
 assert sum(c.get('contacts',0) for c in s['cards'].values())==s['totals']['contacts']
 assert sum(c.get('terminal',0) for c in s['cards'].values())+s['totals']['unassignedTerminal']==sum(s['totals'][k] for k in ['fga','tov','unrecordedShootingFouls'])
 checks.append({'season':season,'players':len(s['cards']),'games':len(s['games']),'sourceLedgersConserved':True,'zeroMinuteEvents':0})
out={'sourceFilesHashed':len(p['sourceHashes']),'seasons':checks,'priorSelectionExcludesTargetSeason':True,'allRatesPositiveFinite':True,'hashes':{str(f):sha(f) for f in list(r.glob('*-contact-rates.json'))+[r/'contact-intensity-prior.json']}}
(r/'source-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out['seasons'],indent=2))

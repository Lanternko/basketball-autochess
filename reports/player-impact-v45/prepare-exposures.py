import json,re,hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));zones=['ra','paint','mid','corner','arc']
def clock(c):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',c);return int(m[1] or 0)*60+float(m[2])
for season in read(ROOT/'protocol.json')['seasons']:
 output=ROOT/f'{season}-exposures.json'
 if output.exists():continue
 data=read(ROOT/f'{season}-fga-data.json');valid={r[0] for r in data['minutes']};frames=defaultdict(list)
 sf=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');mf=Path(('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json');files={s['id']:s['file'] for s in read(mf)['sources']}
 for line in sf.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:frames[s['id']].append(s)
 games={};totals=Counter()
 for gid,stints in frames.items():
  actions=read(files[gid])['data']['game']['actions'];pb=set();pending=None
  for i,e in enumerate(actions):
   kind=e.get('actionType');sub=e.get('subType')
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    if pending and e.get('personId')==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and kind=='2pt' and e.get('area')!='Mid-Range' and 0<=clock(pending['clock'])-clock(e['clock'])<=3:pb.add(i)
    pending=None
   elif kind=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
   elif kind in ['turnover','freethrow','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None
  game={}
  for s in stints:
   counts=defaultdict(Counter)
   for i in range(s['startIndex'],s['endIndex']):
    e=actions[i]
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt'] or i in pb:continue
    area=e.get('area');z='corner' if area in ['Left Corner 3','Right Corner 3'] else 'arc' if e['actionType']=='3pt' else 'ra' if area=='Restricted Area' else 'mid' if area=='Mid-Range' else 'paint'
    counts[str(e['personId'])][z]+=1;totals[z]+=1
   game[str(s['startIndex'])+':'+str(s['endIndex'])]={k:dict(v) for k,v in counts.items()}
  games[gid]=game
 assert all(totals[z]==data['coverage'][z+'A'] for z in zones)
 output.write_text(json.dumps({'season':season,'games':games,'totals':dict(totals),'fineCountParityPassed':True,'sourceDataSHA256':hashlib.sha256((ROOT/f'{season}-fga-data.json').read_bytes()).hexdigest()}),encoding='utf-8');print(json.dumps({'season':season,'fineCountParityPassed':True}),flush=True)

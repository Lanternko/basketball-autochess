"""Strict source FGA by player, zone and actual lineup interval; no makes."""
import json,re,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v17');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def sec(c):
 m=re.match(r'PT(?:(\d+)M)?([\d.]+)S',c);return int(m[1] or 0)*60+float(m[2])
for season in sys.argv[1:] or ['2022-23','2023-24','2024-25','2025-26']:
 output=root/f'{season}-shot-exposures.json'
 if output.exists():raise RuntimeError('Preserve existing source exposure artifact')
 valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);stints=defaultdict(list)
 sf=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
 for line in sf.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid:stints[s['id']].append(s)
 manifest=read(Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')/'manifest.json');games={};hashes={};totals=Counter()
 for spec in manifest['sources']:
  if spec['id'] not in valid:continue
  f=Path(spec['file']);actions=read(f)['data']['game']['actions'];hashes[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest();pending=None;putbacks=set()
  for i,e in enumerate(actions):
   k=e.get('actionType');sub=e.get('subType')
   if k in ['2pt','3pt'] and e.get('isFieldGoal'):
    if pending and e.get('personId')==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and k=='2pt' and e.get('area')!='Mid-Range' and 0<=sec(pending['clock'])-sec(e['clock'])<=3:putbacks.add(i)
    pending=None
   elif k=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
   elif k in ['turnover','freethrow','foul','period','jumpball'] or k=='rebound' and sub=='defensive':pending=None
  rows={}
  for s in stints[spec['id']]:
   teams={t['teamId']:set(t['players']) for t in s['teams']};counts=defaultdict(Counter)
   for i in range(s['startIndex'],s['endIndex']):
    e=actions[i]
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt'] or i in putbacks:continue
    pid=e['personId'];assert pid in teams[e['teamId']]
    z='long' if e['actionType']=='3pt' else 'mid' if e.get('area')=='Mid-Range' else 'short'
    counts[str(pid)][z]+=1;totals[z]+=1;totals['all']+=1
    if s['seconds']==0:totals['zeroSecondStintShots']+=1
   rows[f'{s["startIndex"]}:{s["endIndex"]}']={pid:dict(n) for pid,n in counts.items()}
  games[spec['id']]=rows
 expected=next(c['freshShotsJoined'] for c in read('reports/player-impact-v8/usage-fit.json')['coverage'] if c['season']==season)
 assert totals['all']==expected,(totals,expected)
 out={'season':season,'design':__doc__,'totals':dict(totals),'games':games,'sources':{'stints':str(sf),'stintsSHA256':hashlib.sha256(sf.read_bytes()).hexdigest(),'pbpHashes':hashes,'scriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
 output.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,dict(totals),flush=True)

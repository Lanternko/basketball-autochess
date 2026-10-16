"""Strict PBP conditional defensive rebound recipient risk sets, no rank fitting."""
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict

root=Path('reports/player-impact-v24');root.mkdir(exist_ok=True)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
for season in ['2022-23','2023-24','2024-25','2025-26']:
 output=root/f'{season}-dreb-risksets.json'
 if output.exists():raise RuntimeError('Preserve frozen source risksets')
 truth=f'reports/player-impact-v1/{season}-on-court-truth.json';valid=set(read(truth)['gameIds'])
 sf='reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl'
 mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json'
 stints=defaultdict(list)
 for line in Path(sf).read_text(encoding='utf-8').splitlines():
  row=json.loads(line)
  if row['id'] in valid:stints[row['id']].append(row)
 bundle=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
 players={p['playerId']:p['name'] for t in bundle['league']['teams'] for p in t['roster']}
 games=[];counts=Counter();issues=[];hashes={f:digest(f) for f in [truth,sf,mf,str(Path(__file__))]}
 for spec in read(mf)['sources']:
  if spec['id'] not in valid:continue
  actions=read(spec['file'])['data']['game']['actions'];hashes[spec['file']]=digest(spec['file']);rows=[]
  for index,e in enumerate(actions):
   if e.get('actionType')!='rebound' or e.get('subType')!='defensive':continue
   pid=e.get('personId')
   if not pid or 'team' in e.get('qualifiers',[]):counts['teamDreb']+=1;continue
   counts['individualDreb']+=1
   matches=[s for s in stints[spec['id']] if s['startIndex']<=index<s['endIndex']]
   if len(matches)!=1:
    issues.append({'game':spec['id'],'index':index,'playerId':pid,'reason':'stint cardinality','matches':len(matches)});continue
   ss=matches[0];teams=[t for t in ss['teams'] if t['teamId']==e['teamId']]
   if len(teams)!=1 or pid not in teams[0]['players']:
    issues.append({'game':spec['id'],'index':index,'playerId':pid,'reason':'recipient outside team lineup'});continue
   lineup=teams[0]['players'];assert len(lineup)==5 and len(set(lineup))==5 and all(p in players for p in lineup)
   rows.append([pid,*lineup]);counts['mappedDreb']+=1
  games.append({'id':spec['id'],'fold':int(spec['id'])%5,'rows':rows})
 assert not issues,issues[:10]
 output.write_text(json.dumps({'season':season,'design':'Conditional individual DREB recipient given a team-won individual defensive rebound and actual five-player lineup. Team rebounds excluded. Same strict PBP game set as on-court truth. Counts describe source allocation, not causal rebound skill or defensive impact. No per-player simulation residual/OVR fit.','rowFields':['recipientId','lineup0','lineup1','lineup2','lineup3','lineup4'],'counts':dict(counts),'players':players,'games':games,'hashes':hashes},separators=(',',':')),encoding='utf-8')
 print(season,len(games),dict(counts),flush=True)

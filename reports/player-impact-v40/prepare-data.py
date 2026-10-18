"""Fresh recorded FGA outcomes and actual source fives; no assisted-make feature."""
import json,hashlib,re
from pathlib import Path
from collections import defaultdict,Counter
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clock(c):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',c);assert m;return int(m[1] or 0)*60+float(m[2])
for season in ['2022-23','2023-24','2024-25','2025-26']:
 f=R/(season+'-fga-data.json');assert not f.exists();old=read(f'reports/player-impact-v39/{season}-miss-data.json');frames=defaultdict(list)
 tf=f'reports/player-impact-v1/{season}-on-court-truth.json';valid=set(read(tf)['gameIds']);sf='reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl';mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json';specs={s['id']:s for s in read(mf)['sources']};ef=f'reports/player-impact-v17/{season}-shot-exposures.json';exposure=read(ef);hashes={p:sha(p) for p in [tf,sf,mf,ef,str(R/'prepare-data.py').replace('\\','/')]}
 for line in Path(sf).read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:frames[s['id']].append(s)
 rows=[];minutes=[];total=Counter()
 for gid,stints in frames.items():
  path=specs[gid]['file'];hashes[path]=sha(path);actions=read(path)['data']['game']['actions'];pending=None;pb=set();fold=int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5
  for i,e in enumerate(actions):
   kind=e.get('actionType');sub=e.get('subType')
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    if pending and e.get('personId')==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and kind=='2pt' and e.get('area')!='Mid-Range' and 0<=clock(pending['clock'])-clock(e['clock'])<=3:pb.add(i)
    pending=None
   elif kind=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
   elif kind in ['turnover','freethrow','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None
  grouped={};minute=defaultdict(float)
  for s in stints:
   lineups=[tuple(sorted(t['players'])) for t in s['teams']];counts=defaultdict(Counter)
   for ls in lineups:
    assert len(ls)==len(set(ls))==5
    for pid in ls:minute[pid]+=s['seconds']/60
   for i in range(s['startIndex'],s['endIndex']):
    e=actions[i]
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt'] or i in pb:continue
    off=[t['teamId'] for t in s['teams']].index(e['teamId']);pid=e['personId'];assert pid in lineups[off];z=0 if e['actionType']=='3pt' else 1 if e.get('area')=='Mid-Range' else 2;key=(z,pid,lineups[off],lineups[1-off]);g=grouped.setdefault(key,[0,0]);g[0]+=1;g[1]+=int(e['shotResult']=='Made');assert e['shotResult'] in ['Made','Missed'];counts[str(pid)][['long','mid','short'][z]]+=1;total[['long','mid','short'][z]]+=1;total['fga']+=1;total['fgm']+=int(e['shotResult']=='Made')
   expected=exposure['games'][gid][str(s['startIndex'])+':'+str(s['endIndex'])];assert {pid:dict(c) for pid,c in counts.items()}==expected,(season,gid,s['startIndex'])
  for (z,pid,own,ds),(n,m) in grouped.items():rows.append([gid,fold,z,pid,list(own),list(ds),n,m])
  minutes.append([gid,fold,list(minute.items())])
 assert len(frames)==len(valid) and total['fga']==exposure['totals']['all'];assert all(total[z]==exposure['totals'][z] for z in ['long','mid','short'])
 out={'season':season,'columns':['gameId','fold','zone','shooterId','offensiveFive','defensiveFive','fga','fgm'],'players':old['players'],'zones':['long','mid','short'],'coverage':{'games':len(frames),'rows':len(rows),**dict(total)},'minutes':minutes,'rows':rows,'hashes':hashes};f.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,out['coverage'],flush=True)

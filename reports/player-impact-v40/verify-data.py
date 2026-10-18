"""Independent full PBP/stint reconstruction of fresh FG groups and minutes."""
import json,re,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();results=[];hashes={}
def seconds(c):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',c);return int(m[1] or 0)*60+float(m[2])
for season in ['2022-23','2023-24','2024-25','2025-26']:
 path=R/(season+'-fga-data.json');d=read(path);hashes[str(path).replace('\\','/')]=sha(path)
 for p,h in d['hashes'].items():assert sha(p)==h,p
 oldpath=f'reports/player-impact-v39/{season}-miss-data.json';hashes[oldpath]=sha(oldpath);assert d['players']==read(oldpath)['players']
 sf='reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl';valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json';specs={r['id']:r['file'] for r in read(mf)['sources']};stints=defaultdict(list)
 for line in Path(sf).read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:stints[s['id']].append(s)
 assert set(stints)==valid;expected={};minutes={};counts=Counter();sourceMissing=set()
 for gid,frames in stints.items():
  events=read(specs[gid])['data']['game']['actions'];previous=None;excluded=set();fold=int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5
  for index,event in enumerate(events):
   kind=event.get('actionType');subtype=event.get('subType')
   if event.get('isFieldGoal') and kind in ['2pt','3pt']:
    if previous is not None:
     rebound=events[previous];same=event.get('personId')==rebound.get('personId') and event.get('teamId')==rebound.get('teamId') and event.get('period')==rebound.get('period');delay=seconds(rebound['clock'])-seconds(event['clock'])
     if same and kind=='2pt' and event.get('area')!='Mid-Range' and 0<=delay<=3:excluded.add(index)
    previous=None
   elif kind=='rebound' and subtype=='offensive' and event.get('personId') and 'team' not in event.get('qualifiers',[]):previous=index
   elif kind in ['turnover','freethrow','foul','period','jumpball'] or kind=='rebound' and subtype=='defensive':previous=None
  exposure=defaultdict(float);seen=set()
  for s in frames:
   for t in s['teams']:
    for pid in t['players']:exposure[pid]+=s['seconds']/60
   for index in range(s['startIndex'],s['endIndex']):
    event=events[index]
    if index in excluded or not event.get('isFieldGoal') or event.get('actionType') not in ['2pt','3pt']:continue
    assert index not in seen;seen.add(index);off=next(i for i,t in enumerate(s['teams']) if t['teamId']==event['teamId']);own=tuple(sorted(s['teams'][off]['players']));defense=tuple(sorted(s['teams'][1-off]['players']));assert len(set(own))==len(set(defense))==5 and not set(own)&set(defense);assert event['personId'] in own
    zone=0 if event['actionType']=='3pt' else 1 if event.get('area')=='Mid-Range' else 2;key=(gid,fold,zone,event['personId'],own,defense);x=expected.setdefault(key,[0,0]);x[0]+=1;x[1]+=event['shotResult']=='Made';counts['fga']+=1;counts['fgm']+=event['shotResult']=='Made';counts[['long','mid','short'][zone]]+=1
  sourceFga={i for i,e in enumerate(events) if e.get('isFieldGoal') and e.get('actionType') in ['2pt','3pt'] and i not in excluded};assert seen==sourceFga,(season,gid,len(seen),len(sourceFga));minutes[gid]=(fold,dict(exposure))
 assert len(expected)==len(d['rows'])
 for gid,fold,zone,pid,own,defense,n,m in d['rows']:assert expected[(gid,fold,zone,pid,tuple(own),tuple(defense))]==[n,m]
 assert len(minutes)==len(d['minutes'])
 for gid,fold,ps in d['minutes']:
  f,expectedMinutes=minutes[gid];assert fold==f and set(expectedMinutes)=={pid for pid,_ in ps}
  for pid,value in ps:assert math.isclose(expectedMinutes[pid],value,abs_tol=1e-8,rel_tol=1e-12)
 coverage={'games':len(stints),'rows':len(expected),**dict(counts)};assert coverage==d['coverage'];results.append({'season':season,**coverage});print(results[-1],flush=True)
hashes[str(R/'verify-data.py').replace('\\','/')]=sha(R/'verify-data.py');out={'passed':True,'seasons':results,'sourceGames':sum(r['games'] for r in results),'freshFga':sum(r['fga'] for r in results),'madeFga':sum(r['fgm'] for r in results),'scope':'Every fresh recorded FGA outcome, actor, actual own/defensive five and minute exposure independently rejoined. No source makes, actors or games dropped. Putback exclusion is the frozen v17 three-second PBP proxy, not tracking classification.','hashes':hashes};(R/'data-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

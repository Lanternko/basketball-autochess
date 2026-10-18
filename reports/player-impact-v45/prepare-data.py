import json,hashlib,re
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
zones=['ra','paint','mid','corner','arc'];coarse=[2,2,1,0,0]
def clock(c):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',c);assert m;return int(m[1] or 0)*60+float(m[2])
for season in read(ROOT/'protocol.json')['seasons']:
 output=ROOT/f'{season}-fga-data.json'
 if output.exists():continue
 old=read(f'reports/player-impact-v40/{season}-fga-data.json');valid={g for g,*_ in old['minutes']};frames=defaultdict(list)
 sf=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
 mf=Path(('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json');specs={s['id']:s for s in read(mf)['sources']}
 for line in sf.read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:frames[s['id']].append(s)
 rows=[];total=Counter();collapsed=defaultdict(lambda:[0,0]);hashes={str(p):sha(p) for p in [sf,mf,ROOT/'prepare-data.py',ROOT/'protocol.json']}
 for gid,stints in frames.items():
  file=specs[gid]['file'];hashes[file]=sha(file);actions=read(file)['data']['game']['actions'];pending=None;putbacks=set()
  for i,e in enumerate(actions):
   kind=e.get('actionType');sub=e.get('subType')
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    if pending and e.get('personId')==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and kind=='2pt' and e.get('area')!='Mid-Range' and 0<=clock(pending['clock'])-clock(e['clock'])<=3:putbacks.add(i)
    pending=None
   elif kind=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
   elif kind in ['turnover','freethrow','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None
  fold=int(hashlib.sha256(gid.encode()).hexdigest()[:8],16)%5;grouped={}
  for s in stints:
   lineups=[tuple(sorted(t['players'])) for t in s['teams']]
   for i in range(s['startIndex'],s['endIndex']):
    e=actions[i]
    if not e.get('isFieldGoal') or e.get('actionType') not in ['2pt','3pt'] or i in putbacks:continue
    off=[t['teamId'] for t in s['teams']].index(e['teamId']);pid=e['personId'];own=lineups[off];ds=lineups[1-off];assert pid in own
    area=e.get('area');z=3 if area in ['Left Corner 3','Right Corner 3'] else 4 if e['actionType']=='3pt' else 0 if area=='Restricted Area' else 2 if area=='Mid-Range' else 1
    if e['actionType']=='2pt' and area not in ['Restricted Area','In The Paint (Non-RA)','Mid-Range']:
     # Preserve the frozen legacy short-zone assignment, flag rather than
     # silently infer a restricted-area label from shot distance.
     total['unknown2ptArea']+=1
    made=int(e['shotResult']=='Made');block=e.get('blockPersonId') or 0
    if block:assert not made and block in ds,(gid,i,block,ds)
    key=(z,pid,own,ds);g=grouped.setdefault(key,[0,0,Counter()]);g[0]+=1;g[1]+=made
    if block:g[2][block]+=1
    total[zones[z]+'A']+=1;total[zones[z]+'M']+=made;total['fga']+=1;total['fgm']+=made;total['blocks']+=bool(block)
  for (z,pid,own,ds),(n,m,blocks) in grouped.items():
   rows.append([gid,fold,z,pid,list(own),list(ds),n,m,[[p,b] for p,b in blocks.items()]])
   key=(gid,fold,coarse[z],pid,own,ds);collapsed[key][0]+=n;collapsed[key][1]+=m
 expected={(r[0],r[1],r[2],r[3],tuple(r[4]),tuple(r[5])):r[6:8] for r in old['rows']}
 assert dict(collapsed)==expected;assert total['fga']==old['coverage']['fga'] and total['fgm']==old['coverage']['fgm']
 result={'season':season,'zones':zones,'players':old['players'],'minutes':old['minutes'],'rows':rows,'columns':['game','fold','zone','shooter','ownFive','defFive','fga','fgm','blockedByCounts'],'coverage':{'games':len(frames),'rows':len(rows),**total},'unknownAreaPolicy':'Unclassified 2pt remains in legacy short, under paint residual, never silently called RA; count reported. Arc includes non-corner threes including backcourt.','coarseLedgerParityPassed':True,'hashes':hashes}
 output.write_text(json.dumps(result,separators=(',',':')),encoding='utf-8');print(json.dumps({'season':season,**result['coverage'],'coarseLedgerParityPassed':True}),flush=True)

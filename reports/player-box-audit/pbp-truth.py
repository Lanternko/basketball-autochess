"""Local official PBP: assist and turnover-type truth, coverage explicit."""
import json, hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('reports/player-box-audit')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
b=read('reports/defense-tenth/step4-t0/2025-26/bundle.json')
truth=next(s for s in read(ROOT/'baseline.json')['seasons'] if s['season']=='2025-26')
known={p['playerId']:p for p in truth['players']}
players=defaultdict(Counter);minutes=Counter();files={};missing=[];types=Counter();games=[]
for g in b['exposure']['games']:
    f=Path('data/defense-a-source/pbp')/(str(g['id'])+'.json')
    if not f.exists():missing.append(g['id']);continue
    raw=f.read_bytes();files[str(f).replace('\\','/')]=hashlib.sha256(raw).hexdigest()
    a=json.loads(raw)['data']['game']['actions'];games.append(g['id'])
    for t in g['teams']:
      for p in t['players']:minutes[p['playerId']]+=p['seconds']/60
    orders=[x['actionNumber'] for x in a];assert len(orders)==len(set(orders)),g['id']
    for x in a:
      pid=x.get('personId');typ=x.get('actionType');sub=x.get('subType','');desc=x.get('descriptor','')
      if typ=='turnover':
        if pid not in known:types['teamOrUnknownTurnover']+=1;continue
        q=players[pid];q['tov']+=1;types[sub+'|'+desc]+=1
        cat='pass' if sub=='bad pass' or (sub=='out-of-bounds' and desc=='bad pass') else 'handle' if sub=='lost ball' or (sub=='out-of-bounds' and desc=='lost ball') else 'other'
        q[cat+'Tov']+=1
        q['liveTov' if x.get('stealPersonId') else 'deadTov']+=1
        if x.get('stealPersonId'):q[cat+'StolenAgainst']+=1
      if x.get('isFieldGoal') and typ in ['2pt','3pt']:
        q=players[pid];q['fga']+=1
        if x.get('shotResult')=='Made':
          q['fgm']+=1
          if x.get('assistPersonId'):
            players[x['assistPersonId']]['ast']+=1;q['assistedFgm']+=1
          else:q['unassistedFgm']+=1
          q['fg3m' if typ=='3pt' else 'fg2m']+=1
        if x.get('blockPersonId'):players[x['blockPersonId']]['blk']+=1
rows=[]
for pid,p in known.items():
    c=players[pid];m=minutes[pid]
    rows.append(dict(playerId=pid,name=p['name'],position=p['position'],roleGroup=p['roleGroup'],matchedMinutes=m,counts=dict(c),per36={k:36*v/m for k,v in c.items()} if m else {},assistedFgmShare=c['assistedFgm']/c['fgm'] if c['fgm'] else None))
summary={}
for role in ['ALL','G','F','C']:
    rs=[r for r in rows if role=='ALL' or r['roleGroup']==role];m=sum(r['matchedMinutes'] for r in rs);c=sum((Counter(r['counts']) for r in rs),Counter())
    summary[role]={'minutes':m,'counts':dict(c),'per36':{k:36*v/m for k,v in c.items()},'assistShare':c['assistedFgm']/c['fgm'] if c['fgm'] else None}
result={'season':'2025-26','source':'Locally cached official play-by-play; no missing games imputed','games':len(games),'missingGames':missing,'coverage':len(games)/len(b['exposure']['games']),'turnoverSubtypes':dict(types),'summary':summary,'players':rows,'gamesUsed':games}
(ROOT/'pbp-truth.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'pbp-source-hashes.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['games','missingGames','summary']},ensure_ascii=False,indent=2))

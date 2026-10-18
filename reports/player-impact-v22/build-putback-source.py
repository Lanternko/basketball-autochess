"""Audit legacy three-second OREB proxy; expose FT-rebound scope separately."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v22');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seconds(s):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',s);return int(m[1] or 0)*60+float(m[2])
for season in ['2022-23','2023-24','2024-25','2025-26']:
 output=root/f'{season}-putback-events.json'
 if output.exists():raise RuntimeError('Preserve source audit')
 mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json'
 truth=f'reports/player-impact-v1/{season}-on-court-truth.json';valid=set(read(truth)['gameIds'])
 old=read(f'reports/player-impact-v6/{season}-cards.json')['cards'];totals=Counter();full=Counter();players=defaultdict(Counter);games=[]
 hashes={str(root/'build-putback-source.py'):sha(root/'build-putback-source.py'),mf:sha(mf),truth:sha(truth),f'reports/player-impact-v6/{season}-cards.json':sha(f'reports/player-impact-v6/{season}-cards.json')}
 for spec in read(mf)['sources']:
  hashes[spec['file']]=sha(spec['file']);actions=read(spec['file'])['data']['game']['actions'];pending=None;miss=None;events=[];counts=Counter()
  for index,e in enumerate(actions):
   kind=e.get('actionType');sub=e.get('subType');pid=e.get('personId')
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    z='long' if kind=='3pt' else 'mid' if e.get('area')=='Mid-Range' else 'short';made=int(e.get('shotResult')=='Made')
    pb=pending and pid==pending['personId'] and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and z=='short' and 0<=seconds(pending['clock'])-seconds(e['clock'])<=3
    if pb:
     full['legacyAttempts']+=1;full['legacyMakes']+=made
     if spec['id'] in valid:
      counts['legacyAttempts']+=1;counts['legacyMakes']+=made
      scope=pending['precedingMiss'];counts[scope+'Attempts']+=1;counts[scope+'Makes']+=made
      if scope=='fieldGoal':
       players[pid].update({'attempts':1,'makes':made});events.append({'index':index,'playerId':pid,'teamId':e['teamId'],'made':made,'secondsAfterRebound':seconds(pending['clock'])-seconds(e['clock'])})
    pending=None;miss='fieldGoal' if not made else None
   elif kind=='freethrow':miss='freeThrow' if e.get('shotResult')=='Missed' else None;pending=None
   elif kind=='rebound' and sub=='offensive' and pid and 'team' not in e.get('qualifiers',[]):
    pending={**e,'precedingMiss':miss or 'unknown'}
    if spec['id'] in valid:counts['offensiveRebounds']+=1;counts[(miss or 'unknown')+'OffensiveRebounds']+=1
   elif kind in ['turnover','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None;miss=None
  if spec['id'] in valid:
   totals.update(counts);games.append({'id':spec['id'],'fold':int(spec['id'])%5,'counts':dict(counts),'events':events})
 assert full['legacyAttempts']==sum(m.get('putbackProxyCounts',{}).get('shortA',0) for m in old.values())
 assert full['legacyMakes']==sum(m.get('putbackProxyCounts',{}).get('shortM',0) for m in old.values())
 assert totals['fieldGoalAttempts']==sum(p['attempts'] for p in players.values())
 assert totals['fieldGoalMakes']==sum(p['makes'] for p in players.values())
 cards={pid:{'attempts':players[int(pid)]['attempts'],'makes':players[int(pid)]['makes']} for pid in old}
 out={'season':season,'design':'Recorded short FGA by same OREB player within 0-3 seconds; pending reset on next FGA, foul/FT/TOV/period/jumpball/defensive rebound, same definition as frozen fresh/putback partition. All-source legacy counts verified exactly. New measured putback FG target further requires preceding missed FIELD GOAL, since engine never chooses putback branch after FT rebound. FT and unknown predecessors audited separately, not silently merged. This is a PBP proxy, not official tracking play-type classification. Strict usable games only for model target and contexts.','totals':dict(totals),'fullLegacyTotals':dict(full),'cards':cards,'games':games,'hashes':hashes}
 output.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,dict(totals),'fullLegacy',dict(full),flush=True)
